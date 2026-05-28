"""
chart_aggregator.py — Data aggregation engine for smart business charts.
"""

from __future__ import annotations

import pandas as pd

from .chart_helpers import (
    detect_column_type,
    is_categorical_series,
    is_datetime_series,
    is_numeric_series,
    normalize_chart_type,
    sample_dataframe,
    top_n_categories,
)


def _choose_aggregation(chart_type: str, x_col: str | None, y_col: str | None, df: pd.DataFrame) -> str:
    chart_type = normalize_chart_type(chart_type)

    if chart_type == "count_plot":
        return "count"
    if chart_type == "pie":
        return "sum"
    if chart_type == "line":
        return "sum"
    if chart_type == "bar":
        if x_col and y_col:
            metric = y_col.lower()
            if any(token in metric for token in ("avg", "average", "mean", "rate", "ratio", "pct", "percent", "score")):
                return "mean"
            return "sum"
        return "sum"
    if chart_type == "histogram":
        return "none"
    if chart_type == "scatter":
        return "none"
    if chart_type == "heatmap":
        return "corr"
    return "sum"


def _apply_top_n(df: pd.DataFrame, x_col: str, y_col: str | None, n: int) -> pd.DataFrame:
    if y_col:
        grouped = df.groupby(x_col, observed=True)[y_col].sum().nlargest(n).reset_index()
        top_values = grouped[x_col].tolist()
    else:
        counts = df.groupby(x_col, observed=True).size().nlargest(n).reset_index(name="count")
        top_values = counts[x_col].tolist()
    return df[df[x_col].isin(top_values)].copy()


def aggregate_data(
    df: pd.DataFrame,
    x_col: str | None,
    y_col: str | None,
    chart_type: str,
    aggregation: str | None = None,
    top_n: int = 15,
) -> tuple[pd.DataFrame, str]:
    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame(), aggregation or ""

    chart_type = normalize_chart_type(chart_type)
    work = df.copy()
    agg_method = aggregation or _choose_aggregation(chart_type, x_col, y_col, work)

    if chart_type == "heatmap":
        numeric_cols = work.select_dtypes(include=["number"]).columns.tolist()
        return work[numeric_cols].dropna(axis=1, how="all"), "corr"

    if chart_type == "count_plot":
        if x_col is None:
            return work, "count"
        cleaned = work.dropna(subset=[x_col])
        if cleaned[x_col].nunique() > top_n:
            cleaned = _apply_top_n(cleaned, x_col, None, top_n)
        grouped = (
            cleaned.groupby(x_col, observed=True)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        return grouped, "count"

    if chart_type == "histogram":
        target = y_col or x_col
        if target is None:
            return work, "none"
        if not is_numeric_series(work[target]):
            return work, "none"
        cleaned = work[[target]].dropna()
        if len(cleaned) > 10000:
            cleaned = sample_dataframe(cleaned, max_rows=5000)
        return cleaned, "none"

    if chart_type == "scatter":
        if x_col is None or y_col is None:
            return work, "none"
        cleaned = work[[x_col, y_col]].dropna()
        if len(cleaned) > 10000:
            cleaned = sample_dataframe(cleaned, max_rows=5000)
        return cleaned, "none"

    if x_col is None or y_col is None:
        return work, agg_method

    x_series = work[x_col]
    y_series = work[y_col]
    x_type = detect_column_type(x_series)
    y_type = detect_column_type(y_series)

    if chart_type == "line" and is_datetime_series(x_series) and is_numeric_series(y_series):
        cleaned = work[[x_col, y_col]].dropna()
        cleaned[x_col] = pd.to_datetime(cleaned[x_col], errors="coerce")
        cleaned = cleaned.dropna(subset=[x_col])
        grouped = (
            cleaned.groupby(pd.Grouper(key=x_col, freq="D"))[y_col]
            .agg("sum")
            .reset_index()
        )
        return grouped, "sum"

    if is_categorical_series(x_series) and is_numeric_series(y_series):
        cleaned = work[[x_col, y_col]].dropna()
        if cleaned[x_col].nunique() > top_n:
            cleaned = _apply_top_n(cleaned, x_col, y_col, top_n)
        grouped = cleaned.groupby(x_col, observed=True)[y_col].agg(agg_method).reset_index()
        grouped = grouped.sort_values(y_col, ascending=False)
        return grouped, agg_method

    if is_numeric_series(x_series) and is_numeric_series(y_series):
        cleaned = work[[x_col, y_col]].dropna()
        if len(cleaned) > 5000:
            cleaned = sample_dataframe(cleaned, max_rows=5000)
        return cleaned, "none"

    cleaned = work[[x_col, y_col]].dropna()
    return cleaned, agg_method
