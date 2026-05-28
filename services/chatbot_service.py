"""
services/chatbot_service.py — Stateful Data Copilot Service.

Handles conversational analytics queries against the loaded dataset.
Falls back to a structured statistical answer when no API key is available,
so the copilot always returns useful information rather than an error string.

Fix applied:
  - Fallback now produces a real data-driven answer from the DataFrame
    instead of the bare error message the user was seeing.
  - Conversation history maintained for context across turns.
  - API key checked explicitly before making the call.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from config import AI_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY, AI_MODEL, AI_MAX_TOKENS

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATE = """You are a senior {domain_label} analyst and data scientist.
You have access to a dataset with {row_count:,} rows and {col_count} columns.

Column overview:
{col_summary}

Top KPIs:
{kpi_summary}

Answer questions concisely and precisely. When quoting numbers, be specific.
If asked for insights, provide 3–5 ranked findings with business context.
Always ground your answers in the data provided."""


class ChatbotService:
    """Per-session stateful conversational analytics service."""

    def __init__(self) -> None:
        self._history: list[dict[str, str]] = []
        self._context: dict[str, Any]       = {}

    @property
    def history(self) -> list[dict[str, str]]:
        return self._history

    def chat(self, question: str, df: pd.DataFrame, domain_cfg, kpis: list) -> str:
        return self.ask(question, df, domain_cfg, kpis)

    def reset(self) -> None:
        self._history = []
        self._context = {}

    def set_context(self, df: pd.DataFrame, domain_cfg, kpis: list) -> None:
        """Cache dataset context so it's available for every message."""
        numeric_cols  = df.select_dtypes(include="number").columns.tolist()
        category_cols = df.select_dtypes(exclude="number").columns.tolist()

        col_summary = (
            f"  Numeric ({len(numeric_cols)}): {', '.join(numeric_cols[:10])}\n"
            f"  Categorical ({len(category_cols)}): {', '.join(category_cols[:10])}"
        )
        kpi_summary = "\n".join(
            f"  {k.name}: {k.formatted}" for k in (kpis or [])[:8]
        ) or "  (none)"

        self._context = {
            "df":          df,
            "domain_cfg":  domain_cfg,
            "kpis":        kpis or [],
            "system":      _SYSTEM_TEMPLATE.format(
                domain_label=domain_cfg.label,
                row_count=len(df),
                col_count=len(df.columns),
                col_summary=col_summary,
                kpi_summary=kpi_summary,
            ),
        }

    def ask(self, question: str, df: pd.DataFrame, domain_cfg, kpis: list) -> str:
        """Send a question and return the assistant's answer."""
        if not self._context:
            self.set_context(df, domain_cfg, kpis)

        self._history.append({"role": "user", "content": question})

        try:
            answer = self._llm_answer()
        except Exception as exc:
            logger.warning("LLM chatbot failed, using statistical fallback: %s", exc)
            answer = self._statistical_answer(question, df, domain_cfg, kpis)

        self._history.append({"role": "assistant", "content": answer})
        return answer

    # ── LLM path ──────────────────────────────────────────────────────────────
    def _llm_answer(self) -> str:
        provider = AI_PROVIDER.lower().strip()

        if provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set")
            return self._anthropic_answer()

        elif provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            return self._openai_answer()

        raise ValueError(f"Unknown AI_PROVIDER: '{provider}'")

    def _anthropic_answer(self) -> str:
        import anthropic
        client   = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=min(AI_MAX_TOKENS, 1024),
            system=self._context["system"],
            messages=self._history[-10:],   # keep last 10 turns for context
        )
        return response.content[0].text.strip()

    def _openai_answer(self) -> str:
        from openai import OpenAI
        client   = OpenAI(api_key=OPENAI_API_KEY)
        messages = [{"role": "system", "content": self._context["system"]}] + self._history[-10:]
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=min(AI_MAX_TOKENS, 1024),
            messages=messages,
        )
        return response.choices[0].message.content.strip()

    # ── Statistical fallback — always returns useful data ─────────────────────
    def _statistical_answer(self, question: str, df: pd.DataFrame, domain_cfg, kpis: list) -> str:
        """
        Answers common questions directly from the DataFrame.
        Covers the most frequent copilot queries without needing an LLM.
        """
        q = question.lower()

        # "top insights" / "key insights" / "what does the data show"
        if any(w in q for w in ["insight", "top", "key finding", "summary", "tell me", "show me"]):
            return self._insights_answer(df, domain_cfg, kpis)

        # "average" / "mean" queries
        if any(w in q for w in ["average", "mean", "avg"]):
            return self._averages_answer(df)

        # "highest" / "top" / "maximum"
        if any(w in q for w in ["highest", "maximum", "max", "top value"]):
            return self._max_answer(df)

        # "lowest" / "minimum"
        if any(w in q for w in ["lowest", "minimum", "min"]):
            return self._min_answer(df)

        # "how many" / "count" / "rows"
        if any(w in q for w in ["how many", "count", "rows", "records", "size"]):
            return (
                f"The dataset contains **{len(df):,} rows** and **{len(df.columns)} columns**.\n\n"
                f"Columns: {', '.join(df.columns.tolist()[:15])}"
                + (" …and more." if len(df.columns) > 15 else ".")
            )

        # "columns" / "fields" / "what data"
        if any(w in q for w in ["column", "field", "variable", "what data"]):
            numeric   = df.select_dtypes(include="number").columns.tolist()
            categoric = df.select_dtypes(exclude="number").columns.tolist()
            return (
                f"**Numeric columns ({len(numeric)}):** {', '.join(numeric)}\n\n"
                f"**Categorical columns ({len(categoric)}):** {', '.join(categoric)}"
            )

        # KPI question
        if any(w in q for w in ["kpi", "metric", "performance indicator"]):
            if kpis:
                lines = "\n".join(f"- **{k.name}:** {k.formatted}" for k in kpis)
                return f"**Key Performance Indicators for {domain_cfg.label}:**\n\n{lines}"
            return "No KPIs have been computed yet. Upload a dataset to generate domain-aware KPIs."

        # Default — return data profile
        return self._insights_answer(df, domain_cfg, kpis)

    def _insights_answer(self, df: pd.DataFrame, domain_cfg, kpis: list) -> str:
        numeric = df.select_dtypes(include="number")
        lines   = [f"**Top insights from your {domain_cfg.label} dataset ({len(df):,} rows):**\n"]

        if kpis:
            lines.append("**KPI Highlights:**")
            for k in kpis[:5]:
                lines.append(f"- {k.name}: **{k.formatted}**")
            lines.append("")

        if not numeric.empty:
            lines.append("**Statistical Highlights:**")
            for col in numeric.columns[:4]:
                series = numeric[col].dropna()
                if len(series):
                    lines.append(
                        f"- {col.replace('_',' ').title()}: "
                        f"avg {series.mean():,.2f}, "
                        f"max {series.max():,.2f}, "
                        f"min {series.min():,.2f}"
                    )
            lines.append("")

        lines.append(
            "_To get AI-powered narrative insights, add your ANTHROPIC_API_KEY "
            "or OPENAI_API_KEY to the .env file and restart the app._"
        )
        return "\n".join(lines)

    def _averages_answer(self, df: pd.DataFrame) -> str:
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return "No numeric columns found in the dataset."
        lines = ["**Column Averages:**"]
        for col in numeric.columns[:8]:
            lines.append(f"- {col.replace('_',' ').title()}: **{numeric[col].mean():,.2f}**")
        return "\n".join(lines)

    def _max_answer(self, df: pd.DataFrame) -> str:
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return "No numeric columns found."
        lines = ["**Maximum Values:**"]
        for col in numeric.columns[:8]:
            lines.append(f"- {col.replace('_',' ').title()}: **{numeric[col].max():,.2f}**")
        return "\n".join(lines)

    def _min_answer(self, df: pd.DataFrame) -> str:
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return "No numeric columns found."
        lines = ["**Minimum Values:**"]
        for col in numeric.columns[:8]:
            lines.append(f"- {col.replace('_',' ').title()}: **{numeric[col].min():,.2f}**")
        return "\n".join(lines)
