"""
smart_chart_service.py — Profile-driven chart selection with optional LLM refinement.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go

from services.chart_service import (
    ChartService,
    ChartPlan,
    orchestrate_chart_plans,
    prepare_chart_dataframe,
    profile_dataframe,
)
from services.domain_service import DomainConfig
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)


@dataclass
class ChartSpec:
    """Selected chart specification (alias of orchestration output for callers)."""

    title: str
    chart_type: str
    x_col: str | None
    y_col: str | None
    color_col: str | None
    rationale: str

    @classmethod
    def from_plan(cls, plan: ChartPlan) -> ChartSpec:
        """Convert a ChartPlan into a ChartSpec."""
        return cls(
            title=plan.title,
            chart_type=plan.chart_type,
            x_col=plan.x_col,
            y_col=plan.y_col,
            color_col=plan.color_col,
            rationale=plan.rationale,
        )


class SmartChartService:
    """Picks insightful chart types using profiling + orchestration, optional AI filter."""

    def __init__(self):
        self._chart_svc = ChartService()

    def generate_charts(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        max_charts: int = 6,
        use_ai: bool = True,
    ) -> list[tuple[str, go.Figure]]:
        """
        Return (title, figure) pairs: profile → orchestrate → render.
        """
        if df is None or df.empty:
            return []

        profile = profile_dataframe(df)
        work = prepare_chart_dataframe(df, profile)
        plans = orchestrate_chart_plans(work, domain, max_charts)

        if use_ai:
            plans = self._maybe_refine_plans(work, domain, plans)

        charts: list[tuple[str, go.Figure]] = []
        for plan in plans:
            try:
                fig = self._chart_svc.build_chart(work, plan)
                if fig is not None:
                    charts.append((plan.title, fig))
            except Exception as exc:
                logger.warning("Smart chart build failed: %s", exc)

        if not charts:
            return self._chart_svc.build_from_plans(work, domain, max_charts)

        return charts

    def _maybe_refine_plans(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        plans: list[ChartPlan],
    ) -> list[ChartPlan]:
        """Optional LLM filter; falls back to orchestrated plans on failure."""
        if not plans:
            return plans

        spec_text = "\n".join(
            f"- {p.chart_type}: {p.title} ({p.rationale})" for p in plans
        )
        prompt = (
            f"For a {domain.label} dataset with columns: {', '.join(df.columns.tolist()[:20])}\n"
            f"Candidate charts:\n{spec_text}\n\n"
            f"Reply with ONLY a comma-separated list of chart types to keep "
            f"(line, bar, pie, scatter, histogram, heatmap), max 6, most insightful first."
        )
        reply = call_llm(prompt, system_prompt=domain.analyst_persona, max_tokens=128)
        if not reply:
            return plans

        allowed = {t.strip().lower() for t in reply.replace("\n", ",").split(",")}
        order = ["line", "bar", "pie", "scatter", "histogram", "heatmap"]
        ranked = sorted(
            plans,
            key=lambda p: order.index(p.chart_type) if p.chart_type in allowed else 99,
        )
        filtered = [p for p in ranked if p.chart_type in allowed]
        return filtered or plans
