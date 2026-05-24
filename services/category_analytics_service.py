"""
category_analytics_service.py — V3 category-wise Plotly chart generation.

Profiles categorical channels and builds a complete chart suite per category column.
Pure Python; no Streamlit.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd
import plotly.graph_objects as go

from config import (
    V3_MAX_CATEGORY_COLUMNS,
    V3_CHARTS_PER_CATEGORY,
    V3_CATEGORY_TOP_N,
)
from services.chart_service import (
    ChartService,
    orchestrate_category_plans,
    prepare_chart_dataframe,
    profile_dataframe,
    chart_groupby_cols,
    _rank_metric_columns,
)
from services.domain_service import DomainConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CategoryChartSet:
    """All charts generated for one categorical column."""

    category_column: str
    cardinality: int
    metric_column: str
    charts: tuple[tuple[str, str], ...]  # (title, chart_type) metadata only


@dataclass
class CategoryAnalyticsResult:
    """Full V3 category-wise analytics output."""

    category_sets: list[CategoryChartSet] = field(default_factory=list)
    charts: list[tuple[str, go.Figure]] = field(default_factory=list)
    summary: str = ""


class CategoryAnalyticsService:
    """Builds complete category-wise Plotly visualisations from profiled data."""

    def __init__(self):
        self._chart_svc = ChartService()

    def generate(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        max_categories: int | None = None,
    ) -> CategoryAnalyticsResult:
        """
        Profile data and render bar, pie, box, treemap, and temporal-by-category charts.

        Returns:
            CategoryAnalyticsResult with flat chart list and per-category metadata.
        """
        if df is None or df.empty:
            return CategoryAnalyticsResult(summary="No data available for category analytics.")

        max_cat = max_categories or V3_MAX_CATEGORY_COLUMNS
        profile = profile_dataframe(df)
        work = prepare_chart_dataframe(df, profile)
        metrics = _rank_metric_columns(work, profile, domain)

        if not metrics:
            return CategoryAnalyticsResult(
                summary="No numeric metrics found for category breakdowns.",
            )

        groupbys = chart_groupby_cols(profile, max_cardinality=200)
        if not groupbys:
            return CategoryAnalyticsResult(
                summary="No categorical columns with chartable cardinality (2–200 unique values).",
            )

        plans = orchestrate_category_plans(
            work, domain, max_categories=max_cat, charts_per_category=V3_CHARTS_PER_CATEGORY,
        )

        charts: list[tuple[str, go.Figure]] = []
        sets: list[CategoryChartSet] = []
        primary = metrics[0]

        for cat_prof in groupbys[:max_cat]:
            cat_plans = [p for p in plans if p.x_col == cat_prof.name or p.color_col == cat_prof.name]
            if not cat_plans:
                cat_plans = [p for p in plans if cat_prof.name.replace("_", " ") in p.title]

            set_charts: list[tuple[str, str]] = []
            for plan in cat_plans[: V3_CHARTS_PER_CATEGORY + 2]:
                try:
                    fig = self._chart_svc.build_chart(work, plan)
                    if fig is not None:
                        charts.append((plan.title, fig))
                        set_charts.append((plan.title, plan.chart_type))
                except Exception as exc:
                    logger.warning(
                        "Category chart failed [%s / %s]: %s",
                        cat_prof.name, plan.chart_type, exc,
                    )

            if set_charts:
                sets.append(CategoryChartSet(
                    category_column=cat_prof.name,
                    cardinality=cat_prof.cardinality,
                    metric_column=primary,
                    charts=tuple(set_charts),
                ))

        summary = (
            f"Generated **{len(charts)}** category-wise charts across "
            f"**{len(sets)}** columns (Top-{V3_CATEGORY_TOP_N} truncation applied). "
            f"Primary metric: **{primary.replace('_', ' ').title()}**."
        )

        return CategoryAnalyticsResult(
            category_sets=sets,
            charts=charts,
            summary=summary,
        )
