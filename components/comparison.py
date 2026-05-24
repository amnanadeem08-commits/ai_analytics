"""
comparison.py — Dual-dataset comparison upload and results UI.
"""

import streamlit as st
import pandas as pd

from components.uploader import _parse_file
from config import MAX_UPLOAD_MB
from services.comparison_service import ComparisonReport


def render_comparison_upload() -> tuple[pd.DataFrame | None, str]:
    """Second file uploader for comparison mode."""
    uploaded = st.file_uploader(
        "Upload comparison dataset (CSV/XLSX)",
        type=["csv", "xlsx", "xls"],
        key="compare_upload",
    )
    if uploaded is None:
        return None, ""

    size_mb = uploaded.size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        st.error(f"File too large ({size_mb:.1f}MB). Max: {MAX_UPLOAD_MB}MB.")
        return None, ""

    df, error = _parse_file(uploaded)
    if error:
        st.error(error)
        return None, ""
    return df, uploaded.name


def render_comparison_results(report: ComparisonReport) -> None:
    """Render side-by-side KPI comparison table."""
    st.markdown(report.summary)
    if not report.kpi_comparisons:
        st.warning("No shared KPIs found between the two datasets.")
        return

    rows = []
    for c in report.kpi_comparisons:
        delta = f"{c.delta_pct:+.1f}%" if c.delta_pct is not None else "—"
        icon = "🟢" if c.direction == "better" else ("🔴" if c.direction == "worse" else "⚪")
        rows.append({
            "Metric": c.name,
            report.baseline_label: c.baseline_value,
            report.compare_label: c.compare_value,
            "Change": delta,
            "": icon,
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
