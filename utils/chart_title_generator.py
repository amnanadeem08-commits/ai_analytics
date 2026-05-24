"""
chart_title_generator.py — Professional chart title synthesis for BI dashboards.
"""

from __future__ import annotations

from .chart_helpers import format_label, normalize_chart_type


def generate_chart_title(
    x_col: str | None,
    y_col: str | None,
    chart_type: str,
    aggregation: str | None = None,
) -> str:
    chart_type = normalize_chart_type(chart_type)
    x_label = format_label(x_col) if x_col else None
    y_label = format_label(y_col) if y_col else None
    aggregation = (aggregation or "").strip().title()

    if aggregation in {"Sum", "Total"}:
        aggregation = "Total"
    elif aggregation in {"Mean", "Average"}:
        aggregation = "Average"
    elif aggregation == "Count":
        aggregation = "Count"
    elif aggregation == "Median":
        aggregation = "Median"
    elif aggregation in {"Min", "Max"}:
        aggregation = aggregation.title()

    if chart_type == "line":
        if x_label and y_label:
            prefix = aggregation or "Trend"
            return f"{prefix} {y_label} by {x_label}"
        if y_label:
            return f"Trend of {y_label}"
        return "Time Series Trend"

    if chart_type == "bar":
        if x_label and y_label:
            prefix = aggregation or "Total"
            return f"{prefix} {y_label} by {x_label}"
        if y_label:
            return f"{aggregation or 'Bar'} {y_label}"
        return "Category Comparison"

    if chart_type == "scatter":
        if x_label and y_label:
            return f"{y_label} vs {x_label}"
        return "Scatter Plot"

    if chart_type == "pie":
        if x_label and y_label:
            return f"Share of {y_label} by {x_label}"
        if x_label:
            return f"Part-to-Whole by {x_label}"
        return "Pie Chart"

    if chart_type == "histogram":
        label = y_label or x_label or "Values"
        return f"Distribution of {label}"

    if chart_type == "count_plot":
        if x_label:
            return f"{x_label} Count"
        return "Count Distribution"

    if chart_type == "heatmap":
        return "Correlation Matrix"

    return f"{y_label or x_label or 'Chart'}"
