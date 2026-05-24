"""
insights.py — Premium insight components for the AI Analytics dashboard.

Renders executive summaries, anomaly alerts, trend analysis, and data previews
with modern SaaS-style formatting inspired by Power BI and Tableau.
"""

import streamlit as st
import pandas as pd
from services.analytics_service import AnalyticsReport, AnomalyResult
from services.domain_service import DomainConfig
from services.anomaly_narration_service import AnomalyNarration
from services.forecasting_service import ForecastResult


# ─── CSS Styling ───────────────────────────────────────────────────────────────

INSIGHTS_CSS = """
<style>
    /* Executive Summary Box */
    .executive-summary-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E2E8F0;
        position: relative;
        overflow: hidden;
    }
    
    .executive-summary-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #5046E4 0%, #7C3AED 50%, #0E9F6E 100%);
    }
    
    .executive-summary-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .executive-summary-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px rgba(80, 70, 228, 0.3);
    }
    
    .executive-summary-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
    }
    
    .executive-summary-domain {
        font-size: 0.75rem;
        color: #6B7280;
        font-weight: 500;
        margin-top: 2px;
    }
    
    .executive-summary-content {
        font-size: 0.95rem;
        color: #374151;
        line-height: 1.7;
        max-width: 800px;
    }
    
    /* Alert Banners */
    .alert-banner-wrapper {
        margin-bottom: 1rem;
    }
    
    .alert-banner {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border: 1px solid;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .alert-banner.critical {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-color: #FECACA;
    }
    
    .alert-banner.high {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        border-color: #FED7AA;
    }
    
    .alert-banner.medium {
        background: linear-gradient(135deg, #FFFBEB 0%, #FDE68A 100%);
        border-color: #FDE68A;
    }
    
    .alert-icon-wrapper {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    
    .alert-banner.critical .alert-icon-wrapper {
        background: #FEE2E2;
    }
    
    .alert-banner.high .alert-icon-wrapper {
        background: #FFEDD5;
    }
    
    .alert-banner.medium .alert-icon-wrapper {
        background: #FEF3C7;
    }
    
    .alert-content {
        flex: 1;
    }
    
    .alert-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.375rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alert-banner.critical .alert-title {
        color: #991B1B;
    }
    
    .alert-banner.high .alert-title {
        color: #9A3412;
    }
    
    .alert-banner.medium .alert-title {
        color: #92400E;
    }
    
    .alert-count-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 22px;
        height: 22px;
        padding: 0 6px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .alert-banner.critical .alert-count-badge {
        background: #DC2626;
        color: white;
    }
    
    .alert-banner.high .alert-count-badge {
        background: #EA580C;
        color: white;
    }
    
    .alert-message {
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    .alert-banner.critical .alert-message {
        color: #7F1D1D;
    }
    
    .alert-banner.high .alert-message {
        color: #7C2D12;
    }
    
    .alert-banner.medium .alert-message {
        color: #78350F;
    }
    
    /* Expandable Insight Sections */
    .insight-section {
        margin-bottom: 1.25rem;
    }
    
    .insight-section-header {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.75rem;
    }
    
    .insight-section-icon {
        font-size: 1.1rem;
    }
    
    /* Trend Items */
    .trend-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        background: #F9FAFB;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: background 0.2s;
    }
    
    .trend-item:hover {
        background: #F3F4F6;
    }
    
    .trend-indicator {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    
    .trend-indicator.up {
        background: #D1FAE5;
    }
    
    .trend-indicator.down {
        background: #FEE2E2;
    }
    
    .trend-indicator.neutral {
        background: #F3F4F6;
    }
    
    .trend-text {
        font-size: 0.875rem;
        color: #4B5563;
        line-height: 1.5;
        flex: 1;
    }
    
    /* Category Cards */
    .category-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        transition: all 0.2s;
    }
    
    .category-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #C7D2FE;
    }
    
    .category-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.75rem;
    }
    
    .category-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.375rem 0;
        border-bottom: 1px solid #F3F4F6;
    }
    
    .category-item:last-child {
        border-bottom: none;
    }
    
    .category-item-name {
        font-size: 0.825rem;
        color: #6B7280;
    }
    
    .category-item-value {
        font-size: 0.825rem;
        font-weight: 700;
        color: #5046E4;
    }
    
    /* Forecast Items */
    .forecast-item {
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #7C3AED;
    }
    
    .forecast-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.375rem;
    }
    
    .forecast-summary {
        font-size: 0.825rem;
        color: #4B5563;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .forecast-points {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .forecast-point {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        background: #FFFFFF;
        border-radius: 6px;
        font-size: 0.725rem;
        color: #6B7280;
        border: 1px solid #E5E7EB;
    }
    
    .forecast-point-value {
        font-weight: 600;
        color: #7C3AED;
    }
    
    /* Data Preview */
    .data-preview-container {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
    }
    
    .data-preview-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.25rem;
        background: #F9FAFB;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .data-preview-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #374151;
    }
    
    .data-preview-stats {
        display: flex;
        gap: 1rem;
    }
    
    .data-preview-stat {
        font-size: 0.75rem;
        color: #6B7280;
        background: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #E5E7EB;
    }
    
    .data-preview-stat strong {
        color: #111827;
    }
    
    /* Cleaning Report */
    .cleaning-report {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .cleaning-report pre {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.775rem;
        line-height: 1.6;
        color: #374151;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .executive-summary-box {
            padding: 1.25rem 1.5rem;
        }
        
        .alert-banner {
            padding: 0.875rem 1rem;
        }
    }
</style>
"""


def render_executive_summary(summary_text: str, domain: DomainConfig) -> None:
    """Render the AI-generated executive summary with premium styling."""
    st.markdown(INSIGHTS_CSS, unsafe_allow_html=True)
    
    # Convert markdown to HTML
    html_content = _md_to_html(summary_text)
    
    st.markdown(
        f"""
        <div class="executive-summary-box">
            <div class="executive-summary-header">
                <div class="executive-summary-icon">📋</div>
                <div>
                    <div class="executive-summary-title">Executive Summary</div>
                    <div class="executive-summary-domain">AI-Powered Analysis · {domain.label}</div>
                </div>
            </div>
            <div class="executive-summary-content">
                {html_content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analytics_insights(
    report: AnalyticsReport,
    domain: DomainConfig,
    anomaly_narrations: list[AnomalyNarration] | None = None,
    forecasts: list[ForecastResult] | None = None,
) -> None:
    """Render structured insights with modern card-based layout."""
    st.markdown(INSIGHTS_CSS, unsafe_allow_html=True)
    
    # ── Forecasts ──────────────────────────────────────────────────────────────
    if forecasts:
        st.markdown("### 🔮 Forecast Predictions")
        for fc in forecasts[:3]:
            fc_points_html = ""
            if fc.forecast_points:
                points = ", ".join(
                    f'<span class="forecast-point">{p.period_label}: <span class="forecast-point-value">{p.value:,.2f}</span></span>'
                    for p in fc.forecast_points[:6]
                )
                fc_points_html = f'<div class="forecast-points">{points}</div>'
            
            st.markdown(
                f"""
                <div class="forecast-item">
                    <div class="forecast-title">{fc.column.replace('_', ' ').title()}</div>
                    <div class="forecast-summary">{fc.summary}</div>
                    {fc_points_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    # ── Trend Analysis ─────────────────────────────────────────────────────────
    if report.trends:
        st.markdown("### 📈 Trend Analysis")
        for trend in report.trends[:5]:
            if trend.direction == "up":
                indicator = "↑"
                indicator_class = "up"
            elif trend.direction == "down":
                indicator = "↓"
                indicator_class = "down"
            else:
                indicator = "→"
                indicator_class = "neutral"
            
            st.markdown(
                f"""
                <div class="trend-item">
                    <div class="trend-indicator {indicator_class}">{indicator}</div>
                    <div class="trend-text">{trend.summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    # ── Anomalies ──────────────────────────────────────────────────────────────
    if report.anomalies or anomaly_narrations:
        st.markdown("### ⚠️ Anomalies Detected")
        narr_map = {n.column: n for n in (anomaly_narrations or [])}
        
        for anomaly in report.anomalies[:5]:
            narr = narr_map.get(anomaly.column)
            if narr:
                if narr.severity == "high":
                    indicator = "🔴"
                    indicator_class = "down"
                elif narr.severity == "medium":
                    indicator = "🟡"
                    indicator_class = "neutral"
                else:
                    indicator = "🟢"
                    indicator_class = "up"
                
                st.markdown(
                    f"""
                    <div class="trend-item">
                        <div class="trend-indicator {indicator_class}">{indicator}</div>
                        <div class="trend-text"><strong>{anomaly.column.replace('_', ' ').title()}</strong>: {narr.narration}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="trend-item">
                        <div class="trend-indicator neutral">⚪</div>
                        <div class="trend-text"><strong>{anomaly.column.replace('_', ' ').title()}</strong>: {len(anomaly.anomaly_indices)} outlier(s) detected (threshold ±{anomaly.threshold_upper:.2f})</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    
    # ── Top Categories ─────────────────────────────────────────────────────────
    if report.top_categories:
        st.markdown("### 🏆 Top Categories")
        cols = st.columns(min(3, len(report.top_categories)))
        
        for i, (col_name, series) in enumerate(list(report.top_categories.items())[:3]):
            with cols[i]:
                items_html = ""
                for val, count in series.head(5).items():
                    items_html += f"""
                    <div class="category-item">
                        <span class="category-item-name">{val}</span>
                        <span class="category-item-value">{count:,}</span>
                    </div>
                    """
                
                st.markdown(
                    f"""
                    <div class="category-card">
                        <div class="category-card-title">{col_name.replace('_', ' ').title()}</div>
                        {items_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    
    # ── Distribution Insights ──────────────────────────────────────────────────
    if report.distribution_skew:
        st.markdown("### 📊 Distribution Insights")
        for col, skew_desc in list(report.distribution_skew.items())[:6]:
            st.markdown(f"- **{col.replace('_', ' ').title()}**: {skew_desc}")


def render_data_preview(df: pd.DataFrame, cleaning_summary: str) -> None:
    """Renders data preview and cleaning report with modern styling."""
    st.markdown(INSIGHTS_CSS, unsafe_allow_html=True)
    
    with st.expander("🗂 Data Preview & Cleaning Report", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**📄 Cleaning Summary**")
            st.markdown(
                f"""
                <div class="cleaning-report">
                    <pre>{cleaning_summary}</pre>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        with col2:
            st.markdown("**📋 Column Types**")
            dtype_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Non-Null": df.notna().sum().values,
                "Unique": df.nunique().values,
            })
            st.dataframe(dtype_df, use_container_width=True, height=200)
        
        st.markdown("**📊 Sample Data**")
        st.dataframe(df.head(20), use_container_width=True)


def _md_to_html(text: str) -> str:
    """Minimal markdown bold/bullet to HTML for st.markdown inside html blocks."""
    import re
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    lines = text.split("\n")
    html_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            html_lines.append(f"<li style='margin-bottom:4px'>{stripped[2:]}</li>")
        elif stripped:
            html_lines.append(f"<p style='margin:0 0 8px'>{stripped}</p>")
    result = "\n".join(html_lines)
    if "<li" in result:
        result = "<ul style='padding-left:1.2rem;margin:0 0 8px'>" + result + "</ul>"
    return result


def render_anomaly_alerts(
    anomalies: list[AnomalyResult] | None = None,
    anomaly_narrations: list[AnomalyNarration] | None = None,
) -> None:
    """Render alert banner at top of dashboard if critical/high anomalies detected."""
    st.markdown(INSIGHTS_CSS, unsafe_allow_html=True)
    
    if not anomalies:
        return
    
    critical = [a for a in anomalies if getattr(a, 'severity', 'medium') == 'critical']
    high = [a for a in anomalies if getattr(a, 'severity', 'medium') == 'high']
    
    if not critical and not high:
        return
    
    alert_count = len(critical) + len(high)
    
    if critical:
        alert_level = "CRITICAL"
        alert_class = "critical"
        alert_icon = "🔴"
    else:
        alert_level = "HIGH PRIORITY"
        alert_class = "high"
        alert_icon = "🟠"
    
    narr_map = {n.column: n for n in (anomaly_narrations or [])}
    
    # Build alert messages
    messages_html = ""
    for anomaly in (critical or []) + (high or [])[:5]:
        narr = narr_map.get(anomaly.column)
        col_name = anomaly.column.replace('_', ' ').title()
        if narr:
            messages_html += f"<div>• <strong>{col_name}</strong>: {narr.narration}</div>"
        else:
            messages_html += f"<div>• <strong>{col_name}</strong>: {len(anomaly.anomaly_indices)} outlier(s) detected</div>"
    
    st.markdown(
        f"""
        <div class="alert-banner-wrapper">
            <div class="alert-banner {alert_class}">
                <div class="alert-icon-wrapper">{alert_icon}</div>
                <div class="alert-content">
                    <div class="alert-title">
                        {alert_level} — {alert_count} Anomal{"y" if alert_count == 1 else "ies"} Detected
                        <span class="alert-count-badge">{alert_count}</span>
                    </div>
                    <div class="alert-message">
                        {messages_html}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Details button
    col_btn, col_space = st.columns([1, 8])
    with col_btn:
        if st.button("🔎 View Details", key="anomaly_details_btn", type="secondary"):
            st.session_state.show_anomaly_details = True