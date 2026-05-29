"""
storytelling_engine.py — Phase 5 Storytelling Engine (Tableau/Power-BI style insights).

Turns analysis outputs into a business narrative:
    Overview → Key trends → Anomalies → Recommendations
    framed as: What is happening? · Why is it happening? · What should be done?

Design:
    - Independent of the SQL and RAG layers. It consumes their *outputs* as plain
      data (passed in via StoryContext) and never imports/calls those engines.
    - The only external dependency is the shared LLM client.
    - Always degrades to a deterministic statistical narrative when AI is offline.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Inputs
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class StoryContext:
    """Plain-data inputs for the story. All fields optional/duck-typed."""

    dataset_name: str = "the dataset"
    domain_label: str = "General"
    row_count: int = 0
    column_count: int = 0
    kpis: list[tuple[str, str]] = field(default_factory=list)       # (name, formatted)
    trends: list[str] = field(default_factory=list)                 # trend summaries
    anomalies: list[str] = field(default_factory=list)              # anomaly summaries
    stats_summary: str = ""                                         # numeric describe text
    rag_summary: str = ""                                           # from RAG insight
    rag_findings: list[str] = field(default_factory=list)
    sql_findings: list[str] = field(default_factory=list)           # optional NL→SQL takeaways
    columns: list[str] = field(default_factory=list)

    def to_prompt_block(self) -> str:
        def block(label: str, items: list[str]) -> str:
            if not items:
                return f"{label}: none detected."
            return f"{label}:\n" + "\n".join(f"  - {x}" for x in items[:8])

        kpi_lines = [f"{n}: {v}" for n, v in self.kpis[:8]]
        parts = [
            f"Dataset: {self.dataset_name}",
            f"Domain: {self.domain_label}",
            f"Size: {self.row_count:,} rows x {self.column_count} columns",
            f"Columns: {', '.join(map(str, self.columns[:30])) or 'n/a'}",
            block("KPIs", kpi_lines),
            block("Detected trends", self.trends),
            block("Detected anomalies", self.anomalies),
            block("RAG key findings", self.rag_findings),
            block("SQL-derived takeaways", self.sql_findings),
        ]
        if self.rag_summary:
            parts.append(f"RAG summary: {self.rag_summary}")
        if self.stats_summary:
            parts.append(f"Statistical summary: {self.stats_summary[:1200]}")
        return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Outputs
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class StorySection:
    """A single narrative unit: headline + explanation + recommendation."""

    headline: str
    explanation: str
    recommendation: str
    category: str = "insight"  # "trend" | "anomaly" | "opportunity" | "risk" | "insight"


@dataclass
class ChartSuggestion:
    title: str
    chart_type: str
    columns: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class DataStory:
    title: str = ""
    overview: str = ""
    what_is_happening: str = ""
    why_it_is_happening: str = ""
    what_should_be_done: list[str] = field(default_factory=list)
    sections: list[StorySection] = field(default_factory=list)
    chart_suggestions: list[ChartSuggestion] = field(default_factory=list)
    generated_with_ai: bool = False
    success: bool = True
    error: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────────────────────────────────────
class StorytellingEngine:
    """Generates a business data story from pre-computed analysis outputs."""

    def build_context(
        self,
        *,
        dataset_name: str = "the dataset",
        domain_label: str = "General",
        df: Any = None,
        analytics_report: Any = None,
        data_understanding_report: Any = None,
        kpis: Any = None,
        rag_result: Any = None,
        sql_findings: list[str] | None = None,
    ) -> StoryContext:
        """
        Assemble a StoryContext from common app objects using duck typing,
        so this module stays decoupled from concrete service classes.
        """
        ctx = StoryContext(dataset_name=dataset_name, domain_label=domain_label)

        if df is not None:
            try:
                ctx.row_count = int(len(df))
                ctx.column_count = int(df.shape[1])
                ctx.columns = [str(c) for c in df.columns]
            except Exception:
                pass

        # KPIs (objects with .name/.formatted, or tuples)
        if kpis:
            parsed: list[tuple[str, str]] = []
            for k in kpis:
                name = getattr(k, "name", None)
                formatted = getattr(k, "formatted", None)
                if name is not None and formatted is not None:
                    parsed.append((str(name), str(formatted)))
                elif isinstance(k, (tuple, list)) and len(k) >= 2:
                    parsed.append((str(k[0]), str(k[1])))
            ctx.kpis = parsed

        # Analytics report → trends + anomalies + stats
        if analytics_report is not None:
            for t in getattr(analytics_report, "trends", []) or []:
                summary = getattr(t, "summary", None)
                if summary:
                    ctx.trends.append(str(summary))
            for a in getattr(analytics_report, "anomalies", []) or []:
                col = getattr(a, "column", "?")
                values = getattr(a, "anomaly_values", []) or []
                sev = getattr(a, "severity", "medium")
                ctx.anomalies.append(
                    f"{col}: {len(values)} outlier(s), severity {sev}"
                )
            numeric_summary = getattr(analytics_report, "numeric_summary", None)
            if numeric_summary is not None:
                try:
                    ctx.stats_summary = numeric_summary.round(3).to_string()
                except Exception:
                    pass

        # Data understanding → fill columns/stats if still empty
        if data_understanding_report is not None and not ctx.stats_summary:
            summary = getattr(data_understanding_report, "summary", None)
            if summary:
                ctx.stats_summary = str(summary)

        # RAG insight result
        if rag_result is not None:
            ctx.rag_summary = str(getattr(rag_result, "summary", "") or "")
            ctx.rag_findings = [str(x) for x in (getattr(rag_result, "key_findings", []) or [])]

        if sql_findings:
            ctx.sql_findings = [str(x) for x in sql_findings]

        return ctx

    def generate(self, context: StoryContext) -> DataStory:
        """Produce a DataStory; uses LLM when available, else statistical fallback."""
        if context.row_count == 0 and not context.columns:
            return DataStory(success=False, error="No dataset available to narrate.")

        story = self._llm_story(context)
        if story is not None:
            return story
        return self._fallback_story(context)

    # ── LLM path ─────────────────────────────────────────────────────────────
    def _llm_story(self, context: StoryContext) -> DataStory | None:
        from utils.llm_client import call_llm

        system = (
            "You are a senior analytics storyteller (Tableau/Power BI style). "
            "Use ONLY the provided analysis context. Produce a clear business narrative. "
            "Respond strictly as minified JSON with keys: "
            '"title" (string), "overview" (2-3 sentences), '
            '"what_is_happening" (2-3 sentences), '
            '"why_it_is_happening" (2-3 sentences), '
            '"what_should_be_done" (array of 3-5 short action strings), '
            '"sections" (array of 3-5 objects, each with "headline", "explanation", '
            '"recommendation", "category" in [trend,anomaly,opportunity,risk,insight]), '
            '"chart_suggestions" (array of up to 4 objects with "title", "chart_type", '
            '"columns" array, "rationale"). '
            "No text outside the JSON."
        )
        user = (
            f"Analysis context:\n{context.to_prompt_block()}\n\n"
            "Generate the data story JSON now."
        )

        raw = call_llm(user, system_prompt=system, max_tokens=1200)
        if not raw:
            return None

        parsed = _parse_json_block(raw)
        if parsed is None:
            return DataStory(
                title=f"Data Story — {context.domain_label}",
                overview=raw.strip(),
                generated_with_ai=True,
                success=True,
            )

        return self._story_from_dict(parsed, context, ai=True)

    def _story_from_dict(self, data: dict, context: StoryContext, ai: bool) -> DataStory:
        sections = []
        for s in data.get("sections", []) or []:
            if not isinstance(s, dict):
                continue
            sections.append(StorySection(
                headline=str(s.get("headline", "")).strip(),
                explanation=str(s.get("explanation", "")).strip(),
                recommendation=str(s.get("recommendation", "")).strip(),
                category=str(s.get("category", "insight")).strip().lower() or "insight",
            ))

        charts = []
        for c in data.get("chart_suggestions", []) or []:
            if not isinstance(c, dict):
                continue
            charts.append(ChartSuggestion(
                title=str(c.get("title", "")).strip(),
                chart_type=str(c.get("chart_type", "")).strip(),
                columns=[str(x) for x in (c.get("columns", []) or [])],
                rationale=str(c.get("rationale", "")).strip(),
            ))

        return DataStory(
            title=str(data.get("title", f"Data Story — {context.domain_label}")).strip(),
            overview=str(data.get("overview", "")).strip(),
            what_is_happening=str(data.get("what_is_happening", "")).strip(),
            why_it_is_happening=str(data.get("why_it_is_happening", "")).strip(),
            what_should_be_done=[str(x).strip() for x in (data.get("what_should_be_done", []) or []) if str(x).strip()],
            sections=sections,
            chart_suggestions=charts,
            generated_with_ai=ai,
            success=True,
        )

    # ── Deterministic fallback ───────────────────────────────────────────────
    def _fallback_story(self, context: StoryContext) -> DataStory:
        overview = (
            f"This {context.domain_label} dataset contains {context.row_count:,} rows "
            f"across {context.column_count} columns. "
            f"{len(context.trends)} trend(s) and {len(context.anomalies)} anomaly group(s) were detected."
        )

        happening_bits = []
        if context.kpis:
            happening_bits.append(
                "Headline metrics: " + "; ".join(f"{n} = {v}" for n, v in context.kpis[:3])
            )
        if context.trends:
            happening_bits.append("Trends: " + "; ".join(context.trends[:3]))
        what_is_happening = " ".join(happening_bits) or "The dataset has been profiled across its key columns."

        why_bits = []
        if context.anomalies:
            why_bits.append("Anomalies suggest data variability or operational events: " + "; ".join(context.anomalies[:3]) + ".")
        if context.rag_summary:
            why_bits.append(context.rag_summary)
        why_it_is_happening = " ".join(why_bits) or "Underlying drivers require deeper segmentation to confirm causation."

        actions = []
        for t in context.trends[:2]:
            actions.append(f"Monitor and act on the trend: {t}")
        for a in context.anomalies[:2]:
            actions.append(f"Investigate anomaly — {a}")
        if not actions:
            actions = [
                "Validate data completeness for the key measures.",
                "Segment the top KPI by the main category to find drivers.",
                "Set up periodic monitoring on leading indicators.",
            ]

        sections: list[StorySection] = []
        for t in context.trends[:3]:
            sections.append(StorySection(
                headline=t[:80],
                explanation=f"A measurable trend was detected: {t}.",
                recommendation="Track this trend over time and align targets accordingly.",
                category="trend",
            ))
        for a in context.anomalies[:2]:
            sections.append(StorySection(
                headline=f"Anomaly in {a.split(':')[0]}",
                explanation=f"Outliers detected — {a}.",
                recommendation="Review source records to confirm whether this is signal or noise.",
                category="anomaly",
            ))
        if not sections and context.rag_findings:
            for f in context.rag_findings[:3]:
                sections.append(StorySection(
                    headline=f[:80],
                    explanation=f,
                    recommendation="Quantify and validate this finding with a focused query.",
                    category="insight",
                ))

        return DataStory(
            title=f"Data Story — {context.domain_label}",
            overview=overview,
            what_is_happening=what_is_happening,
            why_it_is_happening=why_it_is_happening,
            what_should_be_done=actions,
            sections=sections,
            chart_suggestions=[],
            generated_with_ai=False,
            success=True,
        )


def _parse_json_block(raw: str) -> dict | None:
    text = raw.strip()
    block = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if block:
        text = block.group(1).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except Exception:
        return None
