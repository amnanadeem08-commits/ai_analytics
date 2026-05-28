"""
chart_validator.py — Business-grade chart validation and recommendations.
"""

from __future__ import annotations

import pandas as pd

from .chart_aggregator import aggregate_data
from .chart_helpers import (
    detect_column_type,
    is_categorical_series,
    is_datetime_series,
    is_numeric_series,
    is_ordered_numeric,
    normalize_chart_type,
)
from .chart_title_generator import generate_chart_title


VALID_CHART_TYPES = {
    "line",
    "bar",
    "scatter",
    "pie",
    "histogram",
    "heatmap",
    "count_plot",
}


def validate_chart_selection(
    x_col: str | None,
    y_col: str | None,
    chart_type: str,
    df: pd.DataFrame,
) -> dict:
    chart_type = normalize_chart_type(chart_type)
    title = generate_chart_title(x_col, y_col, chart_type)
    cleaned_df = df.copy() if df is not None else pd.DataFrame()
    warnings: list[str] = []
    is_valid = True
    aggregation = None

    if chart_type not in VALID_CHART_TYPES:
        warnings.append(f"Unsupported chart type '{chart_type}'.")
        is_valid = False

    if cleaned_df is None or cleaned_df.empty:
        warnings.append("Dataset is empty or unavailable.")
        is_valid = False

    if x_col and x_col not in cleaned_df.columns:
        warnings.append(f"X axis column '{x_col}' is not available in the dataset.")
        is_valid = False

    if y_col and y_col not in cleaned_df.columns:
        warnings.append(f"Y axis column '{y_col}' is not available in the dataset.")
        is_valid = False

    if x_col and x_col in cleaned_df.columns:
        cleaned_df = cleaned_df.dropna(subset=[x_col])
    if y_col and y_col in cleaned_df.columns and chart_type not in {"histogram", "count_plot", "heatmap"}:
        cleaned_df = cleaned_df.dropna(subset=[y_col])

    if chart_type == "histogram":
        target = y_col or x_col
        if target is None or target not in cleaned_df.columns or not is_numeric_series(cleaned_df[target]):
            warnings.append("Histogram requires a single numeric column.")
            is_valid = False

    elif chart_type == "heatmap":
        numeric_cols = cleaned_df.select_dtypes(include=["number"]).columns.tolist()
        if len(numeric_cols) < 2:
            warnings.append("Heatmap requires at least two numeric columns for correlation analysis.")
            is_valid = False

    elif chart_type == "count_plot":
        if x_col is None or x_col not in cleaned_df.columns or not is_categorical_series(cleaned_df[x_col]):
            warnings.append("Count Plot requires a categorical or boolean column.")
            is_valid = False
        elif cleaned_df[x_col].nunique(dropna=True) > 50:
            warnings.append("Count Plot requires 50 or fewer categories. Use a grouped Top-N bar chart instead.")
            is_valid = False

    elif chart_type == "line":
        if x_col is None or y_col is None or x_col not in cleaned_df.columns or y_col not in cleaned_df.columns:
            warnings.append("Line charts require both X and Y columns.")
            is_valid = False
        else:
            if not is_numeric_series(cleaned_df[y_col]):
                warnings.append("Line chart Y-axis must be numeric.")
                is_valid = False
            if not (is_datetime_series(cleaned_df[x_col]) or is_ordered_numeric(cleaned_df[x_col])):
                warnings.append("Line chart X-axis must be datetime or ordered numeric.")
                is_valid = False

    elif chart_type == "bar":
        if x_col is None or y_col is None or x_col not in cleaned_df.columns or y_col not in cleaned_df.columns:
            warnings.append("Bar charts require both X and Y columns.")
            is_valid = False
        else:
            if not is_categorical_series(cleaned_df[x_col]):
                warnings.append("Bar chart X-axis should be categorical.")
                is_valid = False
            if not is_numeric_series(cleaned_df[y_col]):
                warnings.append("Bar chart Y-axis must be numeric.")
                is_valid = False
            elif cleaned_df[x_col].nunique(dropna=True) > 20:
                warnings.append("More than 20 categories detected; horizontal bar chart is recommended.")

    elif chart_type == "scatter":
        if x_col is None or y_col is None or x_col not in cleaned_df.columns or y_col not in cleaned_df.columns:
            warnings.append("Scatter plots require both X and Y numeric columns.")
            is_valid = False
        else:
            if not is_numeric_series(cleaned_df[x_col]) or not is_numeric_series(cleaned_df[y_col]):
                warnings.append("Scatter plot requires numeric values on both axes.")
                is_valid = False

    elif chart_type == "pie":
        if x_col is None or y_col is None or x_col not in cleaned_df.columns or y_col not in cleaned_df.columns:
            warnings.append("Pie charts require one categorical column and one numeric column.")
            is_valid = False
        else:
            if not is_categorical_series(cleaned_df[x_col]) or not is_numeric_series(cleaned_df[y_col]):
                warnings.append("Pie chart requires a categorical X and numeric Y.")
                is_valid = False
            elif cleaned_df[x_col].nunique(dropna=True) > 10:
                warnings.append("Pie charts require 10 or fewer categories. Use a Top-N bar chart instead.")
                is_valid = False

    if is_valid:
        aggregated_df, aggregation = aggregate_data(cleaned_df, x_col, y_col, chart_type)
        if chart_type == "heatmap" and aggregation == "corr":
            aggregation = "correlation"
    else:
        aggregation = ""

    recommended_chart = None
    recommended_title = None
    if not is_valid:
        recommended_chart = _recommend_chart_type(x_col, y_col, cleaned_df)
        if recommended_chart:
            recommended_title = generate_chart_title(x_col, y_col, recommended_chart)

    return {
        "is_valid": is_valid,
        "warnings": warnings,
        "recommended_chart": recommended_chart,
        "recommended_title": recommended_title,
        "cleaned_df": cleaned_df,
        "title": title,
        "chart_type": chart_type,
        "aggregation": aggregation,
    }


def _recommend_chart_type(x_col: str | None, y_col: str | None, df: pd.DataFrame) -> str | None:
    if x_col and y_col and x_col in df.columns and y_col in df.columns:
        x_type = detect_column_type(df[x_col])
        y_type = detect_column_type(df[y_col])
        if x_type == "datetime" and y_type == "numeric":
            return "line"
        if x_type == "categorical" and y_type == "numeric":
            return "bar"
        if x_type == "numeric" and y_type == "numeric":
            return "scatter"
        if x_type == "categorical" and y_type == "categorical":
            return "count_plot"
    if x_col and x_col in df.columns:
        x_type = detect_column_type(df[x_col])
        if x_type == "numeric":
            return "histogram"
        if x_type == "categorical":
            return "count_plot"
        if x_type == "datetime":
            return "line"
    return None
