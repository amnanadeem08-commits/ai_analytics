"""
storytelling_service.py — AI-generated narrative walking through charts in sequence.
"""

import logging
from dataclasses import dataclass, field

import pandas as pd
import plotly.graph_objects as go

from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)


@dataclass
class StoryBeat:
    """One narrative step tied to a chart or section."""

    order: int
    chart_title: str
    narrative: str


@dataclass
class StoryNarrative:
    """Full storytelling dashboard content."""

    title: str
    introduction: str
    beats: list[StoryBeat] = field(default_factory=list)
    conclusion: str = ""


class StorytellingService:
    """Builds a guided analytics story from KPIs and charts."""

    def generate(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        charts: list[tuple[str, go.Figure]],
        df: pd.DataFrame | None = None,
    ) -> StoryNarrative:
        """
        Produce an ordered narrative; uses LLM when available, else statistical fallback.
        """
        kpi_block = "\n".join(f"- {k.name}: {k.formatted}" for k in kpis[:8])
        chart_titles = [t for t, _ in charts[:6]]

        prompt = (
            f"You are writing a data story for {domain.label}.\n\n"
            f"KPIs:\n{kpi_block}\n\n"
            f"Charts in order: {', '.join(chart_titles) or 'none'}\n\n"
            f"Write:\n"
            f"1. A 2-sentence introduction\n"
            f"2. For each chart, one sentence explaining what the reader should notice\n"
            f"3. A 2-sentence conclusion with recommendations\n\n"
            f"Format exactly:\nINTRO: ...\nCHART1: ...\nCHART2: ...\nCONCLUSION: ..."
        )

        reply = call_llm(prompt, system_prompt=domain.analyst_persona)
        if reply:
            return self._parse_llm_reply(reply, chart_titles, domain.label)

        return self._fallback(domain, kpis, chart_titles)

    def _parse_llm_reply(
        self, reply: str, chart_titles: list[str], domain_label: str
    ) -> StoryNarrative:
        """Parse structured LLM response into StoryNarrative."""
        lines = {k.strip(): v.strip() for k, v in (
            line.split(":", 1) for line in reply.split("\n") if ":" in line
        )}

        intro = lines.get("INTRO", "Let's walk through the key findings in your data.")
        conclusion = lines.get("CONCLUSION", "Review the charts above for actionable next steps.")

        beats: list[StoryBeat] = []
        for i, title in enumerate(chart_titles):
            key = f"CHART{i + 1}"
            narrative = lines.get(key, f"This chart highlights patterns in {title.lower()}.")
            beats.append(StoryBeat(order=i + 1, chart_title=title, narrative=narrative))

        return StoryNarrative(
            title=f"Data Story — {domain_label}",
            introduction=intro,
            beats=beats,
            conclusion=conclusion,
        )

    def _fallback(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        chart_titles: list[str],
    ) -> StoryNarrative:
        """Statistical fallback when AI is offline."""
        intro = (
            f"This {domain.label} dataset shows {len(kpis)} key metrics. "
            f"Top highlight: {kpis[1].name if len(kpis) > 1 else kpis[0].name} "
            f"at {kpis[1].formatted if len(kpis) > 1 else kpis[0].formatted}."
        )
        beats = [
            StoryBeat(
                order=i + 1,
                chart_title=title,
                narrative=f"Examine {title} for domain-relevant patterns and outliers.",
            )
            for i, title in enumerate(chart_titles)
        ]
        return StoryNarrative(
            title=f"Data Story — {domain.label}",
            introduction=intro,
            beats=beats,
            conclusion="Use the Copilot tab to drill deeper into any chart or metric.",
        )
