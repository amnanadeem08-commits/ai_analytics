"""
chart_helpers.py — Shared chart utility helpers for BI-grade visualization.
"""

from __future__ import annotations

import pandas as pd

NUMERIC_TYPES = ("numeric",)
CATEGORY_THRESHOLD = 20
HIGH_CARDINALITY_THRESHOLD = 50


def normalize_chart_type(chart_type: str) -> str:
    normalized = (chart_type or "").strip().lower().replace(" ", "_")
    aliases = {
        "count-plot": "count_plot",
        "timeseries": "line",
        "date_line": "line",
        "vertical_bar": "bar",
        "horizontal_bar": "bar",
    }
    return aliases.get(normalized, normalized)


def format_label(column_name: str | None) -> str:
    if not column_name:
        return "Metric"
    return column_name.replace("_", " ").title()


def is_boolean_series(series: pd.Series) -> bool:
    if pd.api.types.is_bool_dtype(series):
        return True
    values = series.dropna().unique()
    if len(values) == 0 or len(values) > 3:
        return False
    normalized = {str(v).strip().lower() for v in values}
    return normalized <= {"0", "1", "true", "false", "yes", "no"}


def is_datetime_series(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        parsed = pd.to_datetime(series.dropna(), errors="coerce")
        return float(parsed.notna().mean()) >= 0.8 if len(parsed) else False
    return False


def is_numeric_series(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def is_categorical_series(series: pd.Series) -> bool:
    if pd.api.types.is_categorical_dtype(series):
        return True
    if is_boolean_series(series):
        return True
    return not is_numeric_series(series) and not is_datetime_series(series)


def detect_column_type(series: pd.Series) -> str:
    if is_boolean_series(series):
        return "boolean"
    if is_datetime_series(series):
        return "datetime"
    if is_numeric_series(series):
        return "numeric"
    return "categorical"


def is_ordered_numeric(series: pd.Series) -> bool:
    if not is_numeric_series(series):
        return False
    if pd.api.types.is_integer_dtype(series) and series.dropna().nunique() <= 20:
        return True
    values = series.dropna().unique()
    if len(values) < 3:
        return False
    try:
        return bool((pd.Series(sorted(values)).diff().dropna() >= 0).all())
    except Exception:
        return False


def top_n_categories(df: pd.DataFrame, cat_col: str, y_col: str | None = None, n: int = 15) -> pd.DataFrame:
    group = df.groupby(cat_col, observed=True)
    if y_col:
        agg = group[y_col].sum().nlargest(n).reset_index()
        categories = agg[cat_col].tolist()
        return df[df[cat_col].isin(categories)].copy()
    else:
        counts = group.size().nlargest(n).reset_index(name="count")
        categories = counts[cat_col].tolist()
        return df[df[cat_col].isin(categories)].copy()


def sample_dataframe(df: pd.DataFrame, max_rows: int = 5000) -> pd.DataFrame:
    if len(df) <= max_rows:
        return df.copy()
    return df.sample(n=max_rows, random_state=42).reset_index(drop=True)
