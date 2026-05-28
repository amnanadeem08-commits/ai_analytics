"""
tabs/dashboard.py — Dashboard tab.

Renders: executive summary → anomaly banner → dataset intelligence
         → data quality → KPI cards → charts grid → analytics insights.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.data_quality import render_data_quality
from components.insights import (
    render_analytics_insights,
    render_anomaly_alerts,
    render_executive_summary,
)
from components.kpi_cards import render_kpi_cards
from config import CHART_HEIGHT


_PLOTLY_CONFIG = {"displayModeBar": True, "responsive": True}


def render_chart(fig, key: str, height: int = CHART_HEIGHT) -> None:
    """Render a Plotly figure at a fixed height so Streamlit does not collapse it."""
    fig.update_layout(height=height, autosize=False)
    st.plotly_chart(fig, use_container_width=True, key=key, config=_PLOTLY_CONFIG)


def _guess_chart_columns(title: str, df: pd.DataFrame) -> list[str]:
    """Infer column names referenced in a chart title for the Explain button."""
    if df is None or df.empty:
        return []
    title_lower = title.lower()
    return [c for c in df.columns if c.lower().replace("_", " ") in title_lower][:3]


def _render_data_understanding(report) -> None:
    """BI-oriented semantic profiling panel."""
    if report is None:
        return

    st.caption(report.summary)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Measures",       len(report.measures))
    c2.metric("Dimensions",     len(report.dimensions))
    c3.metric("Date Fields",    len(report.date_columns))
    c4.metric("KPI Candidates", len(report.kpi_candidates))

    for label, values in [
        ("KPI candidates",  report.kpi_candidates),
        ("Dates",           report.date_columns),
        ("Top-N required",  report.high_cardinality_dimensions[:6]),
    ]:
        if values:
            st.markdown(
                f"**{label}:** "
                + ", ".join(v.replace("_", " ").title() for v in values)
            )

    with st.expander("Column roles and chart readiness", expanded=False):
        st.dataframe(
            pd.DataFrame([
                {
                    "Column":         d.name,
                    "Role":           d.role,
                    "Type":           d.dtype,
                    "Unique":         d.unique_count,
                    "Missing %":      d.missing_pct,
                    "Business Score": d.business_score,
                    "Notes":          "; ".join(d.notes),
                }
                for d in report.column_details
            ]),
            use_container_width=True,
            hide_index=True,
        )


def render(
    filtered_df,
    domain_cfg,
    kpis,
    charts,
    ai_summary,
    analytics_report,
    anomaly_narrations,
    forecasts,
    data_quality_report,
    data_understanding_report,
    column_insight_svc,
) -> None:
    """Entry point called from app.py."""

    # File info bar
    col_fn, col_btn = st.columns([5, 1])
    with col_fn:
        st.caption(
            f"📁 **{st.session_state.filename}** · "
            f"{len(filtered_df):,} rows · Domain: **{domain_cfg.label}**"
        )
    with col_btn:
        if st.button("Upload new file"):
            st.session_state.raw_df          = None
            st.session_state.processing_done = False
            st.rerun()

    render_executive_summary(ai_summary, domain_cfg)
    render_anomaly_alerts(analytics_report.anomalies, anomaly_narrations)

    st.markdown('<div class="section-header">Dataset Intelligence</div>', unsafe_allow_html=True)
    _render_data_understanding(data_understanding_report)

    if data_quality_report:
        st.markdown('<div class="section-header">✅ Data Quality Score</div>', unsafe_allow_html=True)
        render_data_quality(data_quality_report)

    st.markdown('<div class="section-header">📌 Key Metrics</div>', unsafe_allow_html=True)
    render_kpi_cards(kpis, columns=4)

    if charts:
        st.markdown('<div class="section-header">📊 Visualisations</div>', unsafe_allow_html=True)
        chart_cols = st.columns(2)
        for i, (title, fig) in enumerate(charts[:6]):
            with chart_cols[i % 2]:
                st.markdown(f"**{title}**")
                render_chart(fig, key=f"dash_chart_{i}")
                if st.button("💡 Explain chart", key=f"explain_chart_{i}"):
                    cols_guess = _guess_chart_columns(title, filtered_df)
                    insight    = column_insight_svc.explain(
                        filtered_df, domain_cfg, title, cols_guess
                    )
                    st.session_state.chart_insights[title] = insight.insight
                if title in st.session_state.get("chart_insights", {}):
                    st.info(st.session_state.chart_insights[title])

    st.markdown('<div class="section-header">🔎 Analytics Insights</div>', unsafe_allow_html=True)
    render_analytics_insights(analytics_report, domain_cfg, anomaly_narrations, forecasts)
