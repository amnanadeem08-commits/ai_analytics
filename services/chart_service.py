"""
chart_service.py — Auto-selects chart types and returns Plotly figures.

Layout & channel orchestration:
    Column profiles are built before chart selection so dtype, cardinality,
    and ordering are resolved deterministically (no raw pandas dtype leakage).
"""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.chart_aggregator import aggregate_data
from utils.chart_insights import generate_chart_insight
from utils.chart_title_generator import generate_chart_title
from utils.chart_validator import validate_chart_selection
from utils.chart_helpers import detect_column_type, format_label, normalize_chart_type

from config import (
    CHART_COLORS,
    CHART_HEIGHT,
    CHART_MAX_CATEGORY_CARDINALITY,
    V3_CATEGORY_TOP_N,
)
from services.domain_service import DomainConfig

ChartType = Literal[
    "line", "bar", "pie", "scatter", "histogram", "heatmap",
    "count_plot", "box", "treemap", "stacked_bar", "grouped_bar", "category_line",
]

logger = logging.getLogger(__name__)

# ── Structural profiling schemas (V2 layout / channel orchestration) ─────────

ColumnChannel = Literal["numeric", "categorical", "temporal", "spatial"]
CHANNEL_NUMERIC: ColumnChannel = "numeric"
CHANNEL_CATEGORICAL: ColumnChannel = "categorical"
CHANNEL_TEMPORAL: ColumnChannel = "temporal"
CHANNEL_SPATIAL: ColumnChannel = "spatial"
VALID_CHANNELS: frozenset[str] = frozenset(
    {CHANNEL_NUMERIC, CHANNEL_CATEGORICAL, CHANNEL_TEMPORAL, CHANNEL_SPATIAL}
)


@dataclass(frozen=True)
class ColumnProfile:
    """Distribution and semantic metadata for a single DataFrame column."""

    name: str
    dtype: str          # Must resolve explicitly to: 'numeric', 'categorical', 'temporal', 'spatial'
    cardinality: int    # Number of unique values
    missing_pct: float  # Missing value ratio (0.0 to 1.0)
    is_ordered: bool    # True for sequential dates/ordinals


@dataclass(frozen=True)
class DatasetProfile:
    """Row-level snapshot plus per-column profiles for orchestration decisions."""

    row_count: int
    columns: tuple[ColumnProfile, ...]

    def by_channel(self, channel: ColumnChannel) -> tuple[ColumnProfile, ...]:
        """Return all columns matching a resolved channel type."""
        return tuple(c for c in self.columns if c.dtype == channel)

    def get(self, name: str) -> ColumnProfile | None:
        """Lookup a single column profile by name."""
        return next((c for c in self.columns if c.name == name), None)


@dataclass(frozen=True)
class ChartPlan:
    """Orchestrated chart definition before Plotly figure construction."""

    title: str
    chart_type: ChartType
    x_col: str | None
    y_col: str | None
    color_col: str | None
    rationale: str


PLOTLY_TEMPLATE = "plotly_white"
BASE_LAYOUT = dict(
    template=PLOTLY_TEMPLATE,
    font_family="Inter, system-ui, sans-serif",
    font_color="#1a1a2e",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=48, r=24, t=40, b=48),
    colorway=CHART_COLORS,
    height=CHART_HEIGHT,
    autosize=False,
)

_JUNK_NUMERIC_NAMES = frozenset({"index", "unnamed", "unnamed_0", "row", "row_number", "serial"})
_SPATIAL_NAME_HINTS = frozenset({
    "lat", "latitude", "lon", "lng", "long", "longitude", "geo", "geocode",
})
_TEMPORAL_NAME_HINTS = frozenset({
    "date", "datetime", "timestamp", "time", "month", "year", "week", "day",
})


def chart_layout(**overrides) -> dict:
    """Return a fresh layout dict for dashboard charts (never mutate BASE_LAYOUT)."""
    layout = {**BASE_LAYOUT, **overrides}
    return layout


def _is_row_index_column(df: pd.DataFrame, col: str) -> bool:
    """True if column looks like an exported row index, not a business metric."""
    lower = col.lower()
    if lower in _JUNK_NUMERIC_NAMES or lower.startswith("unnamed"):
        return True

    index_like = lower in ("id", "row", "num", "number", "serial") or lower.endswith(
        ("_id", "_index", "_row")
    )
    if not index_like:
        return False

    series = df[col].dropna()
    if len(series) < 3 or series.nunique() / len(series) < 0.9:
        return False
    sorted_vals = np.sort(series.values.astype(float))
    expected = np.arange(sorted_vals[0], sorted_vals[0] + len(sorted_vals))
    return len(sorted_vals) == len(expected) and np.allclose(sorted_vals, expected, atol=1.5)


def _missing_ratio(series: pd.Series) -> float:
    """Return fraction of null values in a column (0.0–1.0)."""
    if len(series) == 0:
        return 0.0
    return float(series.isna().mean())


def _name_hints_spatial(col_name: str) -> bool:
    """True when column name suggests latitude/longitude coordinates."""
    tokens = col_name.lower().replace("-", "_").split("_")
    return bool(_SPATIAL_NAME_HINTS & set(tokens)) or any(
        h in col_name.lower() for h in ("latitude", "longitude")
    )


def _name_hints_temporal(col_name: str) -> bool:
    """True when column name suggests a date/time field."""
    lower = col_name.lower()
    return any(h in lower for h in _TEMPORAL_NAME_HINTS)


def _series_is_temporal(series: pd.Series) -> bool:
    """Detect temporal data via dtype or high-confidence string parsing."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype == object or isinstance(series.dtype, pd.StringDtype):
        sample = series.dropna().head(200)
        if sample.empty:
            return False
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Could not infer format, so each element will be parsed individually, falling back to `dateutil`",
                )
                parsed = pd.to_datetime(sample, errors="coerce", utc=False)
            return float(parsed.notna().mean()) >= 0.8
        except (ValueError, TypeError):
            return False
    return False


def _series_is_ordered(series: pd.Series, channel: ColumnChannel) -> bool:
    """True for monotonic dates, ordered categoricals, or low-cardinality ordinals."""
    if channel == CHANNEL_TEMPORAL:
        return True
    if channel == CHANNEL_SPATIAL:
        return False
    if isinstance(series.dtype, pd.CategoricalDtype) and series.dtype.ordered:
        return True
    if channel == CHANNEL_NUMERIC:
        s = series.dropna()
        if len(s) < 2:
            return False
        if s.nunique() <= 20 and pd.api.types.is_integer_dtype(s):
            return True
        try:
            return bool(np.all(np.diff(np.sort(s.unique())) >= 0))
        except (TypeError, ValueError):
            return False
    return False


def _resolve_channel(col_name: str, series: pd.Series, df: pd.DataFrame) -> ColumnChannel:
    """
    Map a pandas Series to exactly one orchestration channel.

    Resolution order: spatial → temporal → numeric → categorical.
    """
    if _name_hints_spatial(col_name):
        return CHANNEL_SPATIAL
    if _series_is_temporal(series) or _name_hints_temporal(col_name):
        return CHANNEL_TEMPORAL
    if pd.api.types.is_numeric_dtype(series):
        if _is_row_index_column(df, col_name):
            return CHANNEL_CATEGORICAL
        return CHANNEL_NUMERIC
    return CHANNEL_CATEGORICAL


def profile_column(df: pd.DataFrame, col_name: str) -> ColumnProfile:
    """
    Build a frozen ColumnProfile for one column using distribution inspection.

    Returns:
        ColumnProfile with channel resolved to numeric | categorical | temporal | spatial.
    """
    series = df[col_name]
    channel = _resolve_channel(col_name, series, df)
    cardinality = int(series.nunique(dropna=True))
    missing_pct = round(_missing_ratio(series), 4)
    is_ordered = _series_is_ordered(series, channel)

    if channel not in VALID_CHANNELS:
        channel = CHANNEL_CATEGORICAL

    return ColumnProfile(
        name=col_name,
        dtype=channel,
        cardinality=cardinality,
        missing_pct=missing_pct,
        is_ordered=is_ordered,
    )


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    """
    Profile every column in a DataFrame for layout and channel orchestration.

    Returns:
        DatasetProfile with one ColumnProfile per column. Empty DataFrame yields
        an empty profile safely.
    """
    if df is None or df.empty:
        return DatasetProfile(row_count=0, columns=())

    profiles: list[ColumnProfile] = []
    for col in df.columns:
        try:
            profiles.append(profile_column(df, col))
        except Exception as exc:
            logger.warning("Could not profile column '%s': %s", col, exc)

    return DatasetProfile(row_count=len(df), columns=tuple(profiles))


def chart_numeric_cols(df: pd.DataFrame) -> list[str]:
    """Numeric channel columns suitable for charts (excludes row-index noise)."""
    profile = profile_dataframe(df)
    return [
        c.name for c in profile.by_channel(CHANNEL_NUMERIC)
        if not _is_row_index_column(df, c.name)
    ]


def chart_categorical_cols(df: pd.DataFrame) -> list[str]:
    """Categorical channel columns with usable cardinality for bar/pie charts."""
    profile = profile_dataframe(df)
    return [
        c.name for c in profile.by_channel(CHANNEL_CATEGORICAL)
        if 2 <= c.cardinality <= CHART_MAX_CATEGORY_CARDINALITY
    ]


def chart_temporal_cols(df: pd.DataFrame) -> list[str]:
    """Temporal channel columns detected via profiling."""
    return [c.name for c in profile_dataframe(df).by_channel(CHANNEL_TEMPORAL)]


def chart_groupby_cols(
    profile: DatasetProfile,
    max_cardinality: int = 100,
    min_cardinality: int = 2,
) -> list[ColumnProfile]:
    """Categorical columns usable as breakdown axes (Top-N truncation applied at render)."""
    return [
        c for c in profile.by_channel(CHANNEL_CATEGORICAL)
        if min_cardinality <= c.cardinality <= max_cardinality
    ]


def prepare_chart_dataframe(df: pd.DataFrame, profile: DatasetProfile) -> pd.DataFrame:
    """Coerce temporal channels to datetime64 so Plotly line charts render correctly."""
    work = df.copy()
    for col in profile.by_channel(CHANNEL_TEMPORAL):
        if not pd.api.types.is_datetime64_any_dtype(work[col.name]):
            work[col.name] = pd.to_datetime(work[col.name], errors="coerce")
    return work


def _rank_metric_columns(
    df: pd.DataFrame,
    profile: DatasetProfile,
    domain: DomainConfig,
    limit: int = 4,
) -> list[str]:
    """Pick the most meaningful numeric columns using domain hints and variance."""
    numerics = [c.name for c in profile.by_channel(CHANNEL_NUMERIC)]
    if not numerics:
        return []

    scored: list[tuple[float, str]] = []
    for col in numerics:
        if _is_row_index_column(df, col):
            continue
        score = 0.0
        lower = col.lower()
        for frag in domain.kpi_columns:
            if frag in lower:
                score += 10.0
        std = float(df[col].std()) if len(df[col].dropna()) else 0.0
        score += min(std, 1_000.0) / 10.0
        scored.append((score, col))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [col for _, col in scored[:limit]]


def orchestrate_chart_plans(
    df: pd.DataFrame,
    domain: DomainConfig,
    max_charts: int = 6,
) -> list[ChartPlan]:
    """
    Deterministic layout & channel orchestration: profile data, then emit ChartPlans.

    Inspects distributions before assigning chart types or axes.
    """
    if df is None or df.empty:
        return []

    profile = profile_dataframe(df)
    temporal = [c.name for c in profile.by_channel(CHANNEL_TEMPORAL)]
    metrics = _rank_metric_columns(df, profile, domain)
    groupbys = chart_groupby_cols(profile)
    prefs = domain.chart_preferences
    plans: list[ChartPlan] = []

    if not metrics:
        return plans

    primary = metrics[0]

    # Temporal × metric → line
    if temporal:
        for metric in metrics[:2]:
            plans.append(ChartPlan(
                title=f"{metric.replace('_', ' ').title()} Over Time",
                chart_type="line",
                x_col=temporal[0],
                y_col=metric,
                color_col=None,
                rationale="Temporal channel paired with numeric metric.",
            ))

    # Categorical × metric → bar or pie (cardinality-aware)
    for cat in groupbys[:2]:
        prof = profile.get(cat.name)
        if not prof:
            continue
        metric = primary
        if prof.cardinality <= 8 and "pie" in prefs:
            plans.append(ChartPlan(
                title=f"{metric.replace('_', ' ').title()} by {cat.name.replace('_', ' ').title()}",
                chart_type="pie",
                x_col=cat.name,
                y_col=metric,
                color_col=None,
                rationale=f"Low cardinality ({prof.cardinality}) — part-to-whole view.",
            ))
        else:
            plans.append(ChartPlan(
                title=f"{metric.replace('_', ' ').title()} by {cat.name.replace('_', ' ').title()}",
                chart_type="bar",
                x_col=cat.name,
                y_col=metric,
                color_col=None,
                rationale=f"Category breakdown (Top-N, cardinality={prof.cardinality}).",
            ))

    # Distribution of primary metric
    plans.append(ChartPlan(
        title=f"Distribution: {primary.replace('_', ' ').title()}",
        chart_type="histogram",
        x_col=None,
        y_col=primary,
        color_col=None,
        rationale="Numeric distribution for skew and outlier detection.",
    ))

    # Two-metric relationship
    if len(metrics) >= 2:
        try:
            corr = abs(float(df[metrics[0]].corr(df[metrics[1]])))
        except Exception:
            corr = 0.0
        color = groupbys[0].name if groupbys else None
        plans.append(ChartPlan(
            title=(
                f"{metrics[0].replace('_', ' ').title()} vs "
                f"{metrics[1].replace('_', ' ').title()}"
            ),
            chart_type="scatter",
            x_col=metrics[0],
            y_col=metrics[1],
            color_col=color,
            rationale=f"Numeric pair (|r|={corr:.2f}).",
        ))

    # Correlation heatmap
    if len(metrics) >= 3:
        plans.append(ChartPlan(
            title="Correlation Matrix",
            chart_type="heatmap",
            x_col=None,
            y_col=None,
            color_col=None,
            rationale="Three or more metrics — multivariate correlation view.",
        ))

    return plans[:max_charts]


def orchestrate_category_plans(
    df: pd.DataFrame,
    domain: DomainConfig,
    max_categories: int = 8,
    charts_per_category: int = 4,
) -> list[ChartPlan]:
    """
  V3: emit full category-wise chart plans for every eligible breakdown column.
    """
    if df is None or df.empty:
        return []

    profile = profile_dataframe(df)
    metrics = _rank_metric_columns(df, profile, domain)
    if not metrics:
        return []

    primary = metrics[0]
    temporal = [c.name for c in profile.by_channel(CHANNEL_TEMPORAL)]
    groupbys = chart_groupby_cols(profile, max_cardinality=150)
    plans: list[ChartPlan] = []

    for cat_prof in groupbys[:max_categories]:
        cat = cat_prof.name
        card = cat_prof.cardinality

        plans.append(ChartPlan(
            title=f"{primary.replace('_', ' ').title()} by {cat.replace('_', ' ').title()}",
            chart_type="bar",
            x_col=cat,
            y_col=primary,
            color_col=None,
            rationale=f"Category total (Top-{V3_CATEGORY_TOP_N}, n={card}).",
        ))

        if card <= 12:
            plans.append(ChartPlan(
                title=f"Share of {primary.replace('_', ' ').title()} — {cat.replace('_', ' ').title()}",
                chart_type="pie",
                x_col=cat,
                y_col=primary,
                color_col=None,
                rationale="Part-to-whole breakdown for low-cardinality category.",
            ))

        plans.append(ChartPlan(
            title=f"Distribution of {primary.replace('_', ' ').title()} by {cat.replace('_', ' ').title()}",
            chart_type="box",
            x_col=cat,
            y_col=primary,
            color_col=None,
            rationale="Spread and outliers per category.",
        ))

        if temporal:
            plans.append(ChartPlan(
                title=f"{primary.replace('_', ' ').title()} Over Time by {cat.replace('_', ' ').title()}",
                chart_type="category_line",
                x_col=temporal[0],
                y_col=primary,
                color_col=cat,
                rationale="Temporal trend split by category.",
            ))
        elif len(groupbys) >= 2 and groupbys[0].name == cat:
            sub = groupbys[1].name
            if groupbys[1].cardinality <= 15:
                plans.append(ChartPlan(
                    title=(
                        f"{primary.replace('_', ' ').title()} — "
                        f"{cat.replace('_', ' ').title()} × {sub.replace('_', ' ').title()}"
                    ),
                    chart_type="stacked_bar",
                    x_col=cat,
                    y_col=primary,
                    color_col=sub,
                    rationale="Two-dimensional category composition.",
                ))

        plans.append(ChartPlan(
            title=f"Treemap: {primary.replace('_', ' ').title()} by {cat.replace('_', ' ').title()}",
            chart_type="treemap",
            x_col=cat,
            y_col=primary,
            color_col=None,
            rationale="Hierarchical share of total metric.",
        ))

    # Cap total plans while keeping sets per category
    per_cat = charts_per_category + 1
    return plans[: max_categories * per_cat]


class ChartService:
    """Generates domain-aware Plotly charts from a DataFrame."""

    def auto_charts(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        max_charts: int = 6,
    ) -> list[tuple[str, go.Figure]]:
        """Return list of (title, figure) tuples via layout orchestration."""
        return self.build_from_plans(df, domain, max_charts)

    def build_from_plans(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        max_charts: int = 6,
    ) -> list[tuple[str, go.Figure]]:
        """Profile, orchestrate, and render charts from ChartPlans."""
        profile = profile_dataframe(df)
        work = prepare_chart_dataframe(df, profile)
        plans = orchestrate_chart_plans(work, domain, max_charts)
        charts: list[tuple[str, go.Figure]] = []

        for plan in plans:
            try:
                fig = self.build_chart(work, plan)
                if fig is not None:
                    charts.append((plan.title, fig))
            except Exception as exc:
                logger.warning("Chart render failed for '%s': %s", plan.title, exc)

        return charts

    def build_chart(self, df: pd.DataFrame, plan: ChartPlan) -> go.Figure | None:
        """Render a single orchestrated ChartPlan to a Plotly figure."""
        if plan.chart_type == "line" and plan.x_col and plan.y_col:
            return self.line_chart(df, plan.x_col, plan.y_col, plan.color_col)
        if plan.chart_type == "bar" and plan.x_col and plan.y_col:
            return self.top_n_bar(df, plan.x_col, plan.y_col)
        if plan.chart_type == "pie" and plan.x_col and plan.y_col:
            return self.pie_chart(df, plan.x_col, plan.y_col)
        if plan.chart_type == "scatter" and plan.x_col and plan.y_col:
            return self.scatter(df, plan.x_col, plan.y_col, plan.color_col)
        if plan.chart_type == "histogram" and plan.y_col:
            return self.histogram(df, plan.y_col)
        if plan.chart_type == "heatmap":
            nums = chart_numeric_cols(df)[:10]
            if len(nums) >= 3:
                return self.correlation_heatmap(df, nums)
        if plan.chart_type == "box" and plan.x_col and plan.y_col:
            return self.box_by_category(df, plan.x_col, plan.y_col)
        if plan.chart_type == "treemap" and plan.x_col and plan.y_col:
            return self.treemap_by_category(df, plan.x_col, plan.y_col)
        if plan.chart_type == "stacked_bar" and plan.x_col and plan.y_col and plan.color_col:
            return self.stacked_bar_categories(df, plan.x_col, plan.color_col, plan.y_col)
        if plan.chart_type == "grouped_bar" and plan.x_col and plan.y_col and plan.color_col:
            return self.grouped_bar_categories(df, plan.x_col, plan.color_col, plan.y_col)
        if plan.chart_type == "category_line" and plan.x_col and plan.y_col and plan.color_col:
            return self.line_by_category(df, plan.x_col, plan.y_col, plan.color_col)
        if plan.chart_type == "count_plot" and plan.x_col:
            return self.count_plot(df, plan.x_col)
        return None

    def normalize_chart_type(self, chart_type: str) -> str:
        return normalize_chart_type(chart_type)

    def format_label(self, col_name: str | None) -> str:
        return format_label(col_name)

    def detect_column_type(self, df: pd.DataFrame, col_name: str) -> str:
        return detect_column_type(df[col_name])

    def generate_chart_title(
        self,
        x_col: str | None,
        y_col: str | None,
        chart_type: str,
        aggregation: str | None = None,
    ) -> str:
        return generate_chart_title(x_col, y_col, chart_type, aggregation)

    def validate_chart_selection(
        self,
        x_col: str | None,
        y_col: str | None,
        chart_type: str,
        df: pd.DataFrame,
    ) -> dict:
        return validate_chart_selection(x_col, y_col, chart_type, df)

    def generate_chart_insight(
        self,
        df: pd.DataFrame,
        x_col: str | None,
        y_col: str | None,
        chart_type: str,
        aggregation: str | None = None,
    ) -> str:
        return generate_chart_insight(df, x_col, y_col, chart_type, aggregation)

    def build_custom_chart(
        self,
        chart_type: str,
        df: pd.DataFrame,
        x_col: str | None = None,
        y_col: str | None = None,
        color_col: str | None = None,
    ) -> go.Figure | None:
        chart_type = self.normalize_chart_type(chart_type)
        work, aggregation = aggregate_data(df, x_col, y_col, chart_type)

        if chart_type == "line" and x_col and y_col:
            return self.line_chart(work, x_col, y_col, color_col)
        if chart_type == "bar" and x_col and y_col:
            long_labels = work[x_col].astype(str).str.len().max() > 18 if len(work) else False
            orientation = "h" if len(work) > 8 or long_labels else "v"
            return self.bar_chart(work, x_col, y_col, orientation=orientation)
        if chart_type == "scatter" and x_col and y_col:
            return self.scatter(work, x_col, y_col)
        if chart_type == "histogram":
            target = y_col or x_col
            if target:
                return self.histogram(work, target)
        if chart_type == "pie" and x_col and y_col:
            return self.pie_chart(work, x_col, y_col)
        if chart_type == "heatmap":
            cols = work.select_dtypes(include=["number"]).columns.tolist()[:10]
            if len(cols) >= 2:
                return self.correlation_heatmap(work, cols)
        if chart_type == "count_plot" and x_col:
            return self.count_plot(work, x_col)
        return None

    def count_plot(self, df: pd.DataFrame, cat_col: str, top_n: int = 10) -> go.Figure:
        grouped = (
            df.groupby(cat_col, observed=True)
            .size()
            .nlargest(top_n)
            .reset_index(name="count")
        )
        fig = px.bar(
            grouped,
            x="count",
            y=cat_col,
            orientation="h",
            text="count",
            color="count",
            color_continuous_scale=["#EEF2FF", "#5046E4"],
        )
        fig.update_layout(**chart_layout(coloraxis_showscale=False))
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        return fig

    # ── Individual chart builders ───────────────────────────────────────────────

    def line_chart(self, df: pd.DataFrame, x: str, y: str, color: str | None = None) -> go.Figure:
        work = df[[x, y] + ([color] if color else [])].dropna().sort_values(x)
        if pd.api.types.is_datetime64_any_dtype(work[x]) and len(work) > 100:
            work = work.groupby(pd.Grouper(key=x, freq="D"))[y].mean().reset_index()
        fig = px.line(work, x=x, y=y, color=color, markers=True)
        fig.update_layout(**chart_layout(title=None))
        fig.update_traces(line_width=2.5)
        fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
        fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
        return fig

    def bar_chart(self, df: pd.DataFrame, x: str, y: str, orientation: str = "v") -> go.Figure:
        fig = px.bar(df, x=x, y=y, orientation=orientation, color_discrete_sequence=CHART_COLORS)
        fig.update_layout(**chart_layout())
        if orientation == "v":
            fig.update_xaxes(tickangle=-30, automargin=True)
        else:
            fig.update_yaxes(automargin=True)
        fig.update_yaxes(showgrid=True, gridcolor="#F3F4F6")
        fig.update_xaxes(showgrid=True, gridcolor="#F3F4F6")
        return fig

    def top_n_bar(
        self, df: pd.DataFrame, cat_col: str, value_col: str, n: int | None = None
    ) -> go.Figure:
        """Horizontal bar of metric totals by category (Top-N truncated)."""
        n = n or V3_CATEGORY_TOP_N
        grouped = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(n)
            .reset_index()
            .sort_values(value_col)
        )
        fig = px.bar(
            grouped, x=value_col, y=cat_col, orientation="h",
            color=value_col, color_continuous_scale=["#EEF2FF", "#5046E4"],
            text=value_col,
        )
        fig.update_layout(**chart_layout(coloraxis_showscale=False))
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        return fig

    def box_by_category(
        self, df: pd.DataFrame, cat_col: str, value_col: str, top_n: int | None = None
    ) -> go.Figure:
        """Box plot of a numeric metric across Top-N categories."""
        top_n = top_n or V3_CATEGORY_TOP_N
        top_cats = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        work = df[df[cat_col].isin(top_cats)]
        fig = px.box(
            work, x=cat_col, y=value_col, color=cat_col,
            color_discrete_sequence=CHART_COLORS,
            points="outliers",
        )
        fig.update_layout(**chart_layout(showlegend=False))
        fig.update_xaxes(tickangle=-35)
        return fig

    def treemap_by_category(
        self, df: pd.DataFrame, cat_col: str, value_col: str, top_n: int | None = None
    ) -> go.Figure:
        """Treemap showing relative share of a metric by category."""
        top_n = top_n or V3_CATEGORY_TOP_N
        grouped = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(top_n)
            .reset_index()
        )
        grouped["label"] = grouped[cat_col].astype(str)
        fig = px.treemap(
            grouped, path=["label"], values=value_col,
            color=value_col, color_continuous_scale=["#EEF2FF", "#5046E4"],
        )
        fig.update_layout(**chart_layout(coloraxis_showscale=False))
        return fig

    def stacked_bar_categories(
        self,
        df: pd.DataFrame,
        cat_col: str,
        sub_col: str,
        value_col: str,
        top_n: int = 12,
    ) -> go.Figure:
        """Stacked bar: primary category on X, sub-category as stack."""
        top_cats = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        work = df[df[cat_col].isin(top_cats)]
        grouped = (
            work.groupby([cat_col, sub_col], observed=True)[value_col]
            .sum()
            .reset_index()
        )
        fig = px.bar(
            grouped, x=cat_col, y=value_col, color=sub_col,
            color_discrete_sequence=CHART_COLORS,
            barmode="stack",
        )
        fig.update_layout(**chart_layout(barmode="stack"))
        fig.update_xaxes(tickangle=-25)
        return fig

    def grouped_bar_categories(
        self,
        df: pd.DataFrame,
        cat_col: str,
        sub_col: str,
        value_col: str,
        top_n: int = 10,
    ) -> go.Figure:
        """Grouped bar comparing sub-categories within each primary category."""
        top_cats = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        work = df[df[cat_col].isin(top_cats)]
        grouped = (
            work.groupby([cat_col, sub_col], observed=True)[value_col]
            .sum()
            .reset_index()
        )
        fig = px.bar(
            grouped, x=cat_col, y=value_col, color=sub_col,
            color_discrete_sequence=CHART_COLORS,
            barmode="group",
        )
        fig.update_layout(**chart_layout(barmode="group"))
        fig.update_xaxes(tickangle=-25)
        return fig

    def line_by_category(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        cat_col: str,
        top_n: int = 8,
    ) -> go.Figure:
        """Multi-series line chart: metric over time, one line per Top-N category."""
        top_cats = (
            df.groupby(cat_col, observed=True)[value_col]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        work = df[df[cat_col].isin(top_cats)].copy()
        if pd.api.types.is_datetime64_any_dtype(work[date_col]):
            work = (
                work.groupby([pd.Grouper(key=date_col, freq="W"), cat_col], observed=True)[value_col]
                .sum()
                .reset_index()
            )
        else:
            work = work.groupby([date_col, cat_col], observed=True)[value_col].sum().reset_index()

        fig = px.line(
            work, x=date_col, y=value_col, color=cat_col,
            color_discrete_sequence=CHART_COLORS,
            markers=True,
        )
        fig.update_layout(**chart_layout(title=None))
        fig.update_traces(line_width=2)
        return fig

    def histogram(self, df: pd.DataFrame, col: str, bins: int = 30) -> go.Figure:
        fig = px.histogram(df, x=col, nbins=bins, color_discrete_sequence=[CHART_COLORS[0]])
        fig.update_layout(**chart_layout())
        fig.update_traces(marker_line_width=0.5, marker_line_color="white")
        return fig

    def scatter(
        self, df: pd.DataFrame, x: str, y: str, color: str | None = None, size: str | None = None
    ) -> go.Figure:
        sample = df.sample(min(2000, len(df)), random_state=42)
        fig = px.scatter(
            sample, x=x, y=y, color=color, size=size,
            color_discrete_sequence=CHART_COLORS, opacity=0.7,
        )
        fig.update_layout(**chart_layout())
        return fig

    def pie_chart(self, df: pd.DataFrame, names: str, values: str, top_n: int = 8) -> go.Figure:
        grouped = df.groupby(names)[values].sum().nlargest(top_n).reset_index()
        fig = px.pie(
            grouped, names=names, values=values, hole=0.42,
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_layout(**chart_layout())
        fig.update_traces(textposition="outside", textinfo="percent+label")
        return fig

    def correlation_heatmap(self, df: pd.DataFrame, cols: list[str]) -> go.Figure:
        corr = df[cols].corr().round(2)
        fig = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.values,
            texttemplate="%{text}",
            hoverongaps=False,
        ))
        fig.update_layout(**chart_layout())
        return fig

    def kpi_trend_sparkline(self, series: pd.Series) -> go.Figure:
        """Minimal sparkline for KPI cards."""
        fig = go.Figure(go.Scatter(
            y=series.values, mode="lines",
            line=dict(color=CHART_COLORS[0], width=2),
            fill="tozeroy", fillcolor="rgba(80,70,228,0.1)",
        ))
        fig.update_layout(
            **chart_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=60,
                showlegend=False,
            ),
        )
        return fig
