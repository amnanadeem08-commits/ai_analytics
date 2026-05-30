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
from components.kpi_cards import KPI_CARD_CSS, _get_icon_for_kpi
from config import CHART_HEIGHT
from services.chart_service import ChartService


_PLOTLY_CONFIG = {"displayModeBar": True, "responsive": True}

# ── Cross-filter: map a KPI to the DataFrame column charts should filter on ──
# Keyed by lowercase tokens found in KPI names. Extend freely; the resolver
# below also falls back to matching any df column name inside the KPI label.
KPI_COLUMN_MAP = {
    "revenue":   "revenue",
    "sales":     "sales",
    "profit":    "profit",
    "margin":    "margin",
    "orders":    "order_id",
    "order":     "order_id",
    "customers": "customer_id",
    "customer":  "customer_id",
    "users":     "user_id",
    "region":    "region",
    "product":   "product_name",
    "units":     "units",
    "quantity":  "quantity",
    "amount":    "amount",
    "price":     "price",
}


def _kpi_key(name: str) -> str:
    """Stable identifier for a KPI derived from its display name."""
    return str(name).strip().lower()


def _resolve_kpi_column(kpi_name: str, df: pd.DataFrame) -> str | None:
    """Resolve the numeric df column a KPI should cross-filter on (best effort)."""
    if df is None or df.empty:
        return None
    name = str(kpi_name).lower()
    # 1) token map (e.g. "Total Revenue" → revenue)
    for token, col in KPI_COLUMN_MAP.items():
        if token in name and col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            return col
    # 2) fallback: any df column whose name appears in the KPI label
    for col in df.columns:
        if col.lower().replace("_", " ") in name and pd.api.types.is_numeric_dtype(df[col]):
            return col
    return None


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


def _render_clickable_kpis(kpis, columns: int = 4) -> None:
    """Render KPI cards as clickable cross-filter controls (Power BI-style)."""
    st.markdown(KPI_CARD_CSS, unsafe_allow_html=True)
    if not kpis:
        render_kpi_empty_state()
        return

    actual_cols = len(kpis) if len(kpis) <= 2 else min(columns, len(kpis)) if len(kpis) <= 4 else columns

    for start in range(0, len(kpis), actual_cols):
        batch = list(enumerate(kpis))[start:start + actual_cols]
        cols = st.columns(len(batch))
        for col, (i, kpi) in zip(cols, batch):
            with col:
                key = _kpi_key(kpi.name)
                is_active = st.session_state.get("active_kpi") == key
                icon = _get_icon_for_kpi(kpi.name)

                if kpi.delta_pct is not None:
                    up = kpi.delta_pct >= 0
                    color = "#34D399" if up else "#FF6B6B"
                    arrow = "▲" if up else "▼"
                    trend = (
                        f'<div style="font-size:0.72rem;font-weight:700;color:{color};'
                        f'margin-top:0.5rem;">{arrow} {abs(kpi.delta_pct):.1f}% '
                        f'<span style="color:#6B7280;font-weight:500;">vs prev period</span></div>'
                    )
                else:
                    trend = ('<div style="font-size:0.72rem;color:#6B7280;margin-top:0.5rem;">'
                             '— no prior period</div>')

                active_border = "rgba(108,99,255,0.7)" if is_active else "rgba(255,255,255,0.08)"
                active_glow = (
                    "box-shadow:0 0 0 1px rgba(108,99,255,0.55),0 10px 30px rgba(108,99,255,0.22);"
                    if is_active else "box-shadow:0 8px 28px rgba(0,0,0,0.35);"
                )
                active_badge = (
                    '<div style="display:inline-flex;align-items:center;gap:5px;margin-top:0.6rem;'
                    'padding:3px 9px;border-radius:20px;font-size:0.62rem;font-weight:800;'
                    'letter-spacing:0.06em;background:rgba(108,99,255,0.18);color:#A89FF0;'
                    'border:1px solid rgba(108,99,255,0.4);">● ACTIVE FILTER</div>'
                    if is_active else ""
                )

                st.markdown(
                    f"""
                    <div style="background:rgba(255,255,255,0.04);border-radius:16px;
                                border:1px solid {active_border};{active_glow}
                                padding:1.2rem 1.4rem;position:relative;overflow:hidden;
                                transition:all 0.2s ease-in-out;">
                        <div style="display:flex;align-items:center;justify-content:space-between;">
                            <span style="font-size:0.72rem;font-weight:700;color:#9CA3AF;
                                         text-transform:uppercase;letter-spacing:0.08em;">{kpi.name}</span>
                            <div style="width:34px;height:34px;border-radius:10px;display:flex;
                                        align-items:center;justify-content:center;font-size:1rem;
                                        background:rgba(108,99,255,0.16);
                                        border:1px solid rgba(108,99,255,0.3);">{icon}</div>
                        </div>
                        <div style="font-family:'JetBrains Mono',ui-monospace,monospace;
                                    font-size:1.9rem;font-weight:700;color:#F3F4F6;line-height:1.1;
                                    letter-spacing:-0.02em;margin:0.35rem 0;">{kpi.formatted}</div>
                        {trend}
                        {active_badge}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                btn_label = "✓ Filtering — clear" if is_active else "🔎 Filter by this"
                if st.button(
                    btn_label,
                    key=f"kpi_btn_{i}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.active_kpi = None if is_active else key
                    st.rerun()


def render_kpi_empty_state() -> None:
    """Empty state when no KPIs are available."""
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 2rem;background:rgba(255,255,255,0.03);
                    border-radius:16px;border:2px dashed rgba(255,255,255,0.12);">
            <div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.6;">📊</div>
            <div style="font-size:1rem;font-weight:600;color:#E5E7EB;">No Metrics Available</div>
            <div style="font-size:0.875rem;color:#9CA3AF;">
                Upload data with numeric columns to generate KPIs
            </div>
        </div>
        """,
        unsafe_allow_html=True,
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

    if "active_kpi" not in st.session_state:
        st.session_state.active_kpi = None

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
    st.caption("Click a metric to cross-filter the charts below · click again to clear")
    _render_clickable_kpis(kpis, columns=4)

    # ── KPI cross-filter → derive the DataFrame the charts should use ────────
    active_kpi_key = st.session_state.active_kpi
    chart_df = filtered_df
    charts_to_render = charts

    if active_kpi_key:
        kpi_col = _resolve_kpi_column(active_kpi_key, filtered_df)
        if kpi_col and not filtered_df.empty:
            try:
                top_idx = filtered_df[kpi_col].nlargest(10).index
                chart_df = filtered_df.loc[top_idx]
            except Exception:
                chart_df = filtered_df

        target = kpi_col.replace("_", " ").title() if kpi_col else None
        scope = (
            f"top {len(chart_df)} rows by <b>{target}</b>"
            if target and chart_df is not filtered_df
            else "this metric (no linked column found — showing full data)"
        )
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.6rem;margin:0.4rem 0 0.9rem;
                        padding:0.65rem 0.95rem;background:rgba(108,99,255,0.12);
                        border:1px solid rgba(108,99,255,0.35);border-radius:12px;">
                <span style="font-size:1.05rem;color:#A89FF0;">⬡</span>
                <span style="font-size:0.82rem;color:#C7CBD4;">
                    Filtering by
                    <b style="color:#FFFFFF;">{active_kpi_key.title()}</b>
                    — {scope}
                    <span style="color:#9CA3AF;">· click the card again to clear</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Rebuild charts from the cross-filtered slice (figures arrive pre-built).
        if chart_df is not filtered_df and not chart_df.empty:
            try:
                rebuilt = ChartService().auto_charts(chart_df, domain_cfg, max_charts=6)
                if rebuilt:
                    charts_to_render = rebuilt
            except Exception:
                charts_to_render = charts

    if charts_to_render:
        st.markdown('<div class="section-header">📊 Visualisations</div>', unsafe_allow_html=True)
        chart_cols = st.columns(2)
        for i, (title, fig) in enumerate(charts_to_render[:6]):
            with chart_cols[i % 2]:
                st.markdown(f"**{title}**")
                render_chart(fig, key=f"dash_chart_{i}")
                if st.button("💡 Explain chart", key=f"explain_chart_{i}"):
                    cols_guess = _guess_chart_columns(title, chart_df)
                    insight    = column_insight_svc.explain(
                        chart_df, domain_cfg, title, cols_guess
                    )
                    st.session_state.chart_insights[title] = insight.insight
                if title in st.session_state.get("chart_insights", {}):
                    st.info(st.session_state.chart_insights[title])

    st.markdown('<div class="section-header">🔎 Analytics Insights</div>', unsafe_allow_html=True)
    render_analytics_insights(analytics_report, domain_cfg, anomaly_narrations, forecasts)
