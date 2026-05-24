"""
column_insight_service.py — Focused AI explanation for a specific chart/column context.
"""

import logging
from dataclasses import dataclass

import pandas as pd

from services.domain_service import DomainConfig
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)


@dataclass
class ColumnInsight:
    """AI or statistical insight for one chart focus area."""

    chart_title: str
    columns: list[str]
    insight: str


class ColumnInsightService:
    """Generates focused explanations when a user inspects a chart."""

    def explain(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        chart_title: str,
        columns: list[str],
    ) -> ColumnInsight:
        """
        Return a focused insight for the given chart title and column list.
        """
        if df is None or df.empty:
            return ColumnInsight(
                chart_title=chart_title,
                columns=columns,
                insight="No data loaded to analyse this chart.",
            )

        stats_lines: list[str] = []
        for col in columns:
            if col not in df.columns:
                continue
            series = df[col].dropna()
            if pd.api.types.is_numeric_dtype(series):
                stats_lines.append(
                    f"{col}: mean={series.mean():.2f}, std={series.std():.2f}, "
                    f"min={series.min():.2f}, max={series.max():.2f}"
                )
            else:
                top = series.value_counts().head(3)
                stats_lines.append(
                    f"{col}: top values {', '.join(str(v) for v in top.index)}"
                )

        prompt = (
            f"Chart: '{chart_title}'\n"
            f"Columns: {', '.join(columns)}\n"
            f"Stats:\n" + "\n".join(stats_lines) + "\n\n"
            f"In 3-4 sentences, explain what this chart reveals for a {domain.label} "
            f"stakeholder and one recommended action."
        )

        reply = call_llm(prompt, system_prompt=domain.analyst_persona, max_tokens=400)
        if reply:
            return ColumnInsight(chart_title=chart_title, columns=columns, insight=reply.strip())

        fallback = (
            f"**{chart_title}** covers {', '.join(columns)}. "
            + (" ".join(stats_lines[:3]) if stats_lines else "Limited stats available.")
            + " Open the Copilot tab to ask follow-up questions about this view."
        )
        return ColumnInsight(chart_title=chart_title, columns=columns, insight=fallback)
