"""
chart_insights.py — Short business insights generated for chart annotations.
"""

from __future__ import annotations

import pandas as pd

from .chart_helpers import detect_column_type, format_label, is_categorical_series, is_datetime_series, is_numeric_series


def generate_chart_insight(
    df: pd.DataFrame,
    x_col: str | None,
    y_col: str | None,
    chart_type: str,
    aggregation: str | None = None,
) -> str:
    if df is None or df.empty:
        return "No insight available for empty data."

    x_label = format_label(x_col) if x_col else "Category"
    y_label = format_label(y_col) if y_col else "Value"
    chart_type = (chart_type or "").strip().lower()
    agg_label = (aggregation or "").capitalize()

    if chart_type == "line" and x_col and y_col and is_datetime_series(df[x_col]) and is_numeric_series(df[y_col]):
        series = df.sort_values(x_col).dropna(subset=[x_col, y_col])[y_col]
        if len(series) >= 2:
            direction = "upward" if series.iloc[-1] >= series.iloc[0] else "downward"
            return f"{y_label} shows a {direction} trend over time."
        return f"{y_label} trend is visible over time."

    if chart_type == "bar" and x_col and y_col:
        grouped = df.groupby(x_col, observed=True)[y_col].mean().reset_index()
        top = grouped.sort_values(y_col, ascending=False).head(1)
        if not top.empty:
            return f"{top.iloc[0][x_col]} has the highest {agg_label or 'average'} {y_label}."
        return f"{y_label} varies by {x_label}."

    if chart_type == "pie" and x_col and y_col:
        grouped = df.groupby(x_col, observed=True)[y_col].sum().reset_index()
        top = grouped.sort_values(y_col, ascending=False).head(1)
        if not top.empty:
            return f"{top.iloc[0][x_col]} accounts for the largest share of {y_label}."
        return f"The chart shows relative share by {x_label}."

    if chart_type == "count_plot" and x_col:
        counts = df[x_col].value_counts(dropna=True)
        if not counts.empty:
            return f"{counts.idxmax()} is the most common {x_label}."
        return f"Counts are distributed across {x_label}."

    if chart_type == "histogram" and (y_col or x_col):
        target = y_col or x_col
        if is_numeric_series(df[target]):
            return f"Distribution of {format_label(target)} reveals shape and spread."
        return f"Histogram shows the distribution of {format_label(target)}."

    if chart_type == "scatter" and x_col and y_col:
        return f"Relationship between {x_label} and {y_label} is displayed."

    if chart_type == "heatmap":
        return "Correlation heatmap highlights the strongest numeric relationships."

    return f"Chart insight for {y_label} by {x_label}."
