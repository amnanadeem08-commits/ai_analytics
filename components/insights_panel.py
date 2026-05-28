"""
insights_panel.py — UI components for AI-powered business insights.

Renders insight cards, anomaly alerts, recommendations, and executive summaries
with professional styling including colored cards, KPI panels, and severity badges.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import textwrap
from services.insight_engine import InsightEngineReport, ExecutiveInsight
from services.recommendation_engine import RecommendationReport, Recommendation
from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from services.analytics_service import AnalyticsReport


# ─── CSS Styling ─────────────────────────────────────────────────────────────

def _get_insight_styles() -> str:
    """Return CSS styles for insight components."""
    return """
    <style>
        /* Insight Card Base - Premium SaaS styling */
        .insight-card {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
            transition: all 0.25s ease-in-out;
            position: relative;
            overflow: hidden;
        }
        .insight-card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Severity-based border colors with gradients */
        .insight-critical {
            border-left-color: #DC2626;
            background: linear-gradient(90deg, #FEF2F2 0%, #FFFFFF 100%);
        }
        .insight-high {
            border-left-color: #EA580C;
            background: linear-gradient(90deg, #FFF7ED 0%, #FFFFFF 100%);
        }
        .insight-medium {
            border-left-color: #CA8A04;
            background: linear-gradient(90deg, #FFFBEB 0%, #FFFFFF 100%);
        }
        .insight-low {
            border-left-color: #2563EB;
            background: linear-gradient(90deg, #EFF6FF 0%, #FFFFFF 100%);
        }
        
        /* Severity badges - pill style */
        .severity-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .badge-critical {
            background: #FEE2E2;
            color: #991B1B;
        }
        .badge-high {
            background: #FFEDD5;
            color: #9A3412;
        }
        .badge-medium {
            background: #FEF9C3;
            color: #854D0E;
        }
        .badge-low {
            background: #DBEAFE;
            color: #1E40AF;
        }
        
        /* Category badges */
        .category-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 500;
            margin-left: 8px;
        }
        .cat-risk { background: #FEE2E2; color: #991B1B; }
        .cat-anomaly { background: #FEF3C7; color: #92400E; }
        .cat-trend { background: #E0E7FF; color: #3730A3; }
        .cat-performance { background: #D1FAE5; color: #065F46; }
        .cat-opportunity { background: #F3E8FF; color: #6B21A8; }
        
        /* Insight headline */
        .insight-headline {
            font-size: 0.95rem;
            font-weight: 600;
            color: #111827;
            margin: 8px 0 4px;
            line-height: 1.4;
        }
        
        /* Insight description */
        .insight-description {
            font-size: 0.85rem;
            color: #6B7280;
            line-height: 1.5;
            margin: 6px 0;
        }
        
        /* Impact statement */
        .insight-impact {
            font-size: 0.82rem;
            color: #4B5563;
            background: #F9FAFB;
            padding: 8px 12px;
            border-radius: 8px;
            margin-top: 8px;
            line-height: 1.4;
        }
        
        /* Confidence score */
        .confidence-bar {
            display: inline-block;
            height: 4px;
            background: #E5E7EB;
            border-radius: 2px;
            width: 80px;
            margin: 0 6px;
            vertical-align: middle;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            border-radius: 2px;
            background: linear-gradient(90deg, #5046E4, #7C3AED);
        }
        
        /* Data support metrics */
        .data-support {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 8px;
        }
        .support-metric {
            font-size: 0.75rem;
            color: #6B7280;
            background: #F3F4F6;
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        /* Recommendation card */
        .recommendation-card {
            background: white;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .rec-immediate { border-left: 4px solid #DC2626; }
        .rec-short-term { border-left: 4px solid #EA580C; }
        .rec-strategic { border-left: 4px solid #059669; }
        .rec-investigation { border-left: 4px solid #7C3AED; }
        
        /* Recommendation title */
        .rec-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 6px;
        }
        
        /* Recommendation meta */
        .rec-meta {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 8px 0;
        }
        .rec-meta-item {
            font-size: 0.75rem;
            color: #6B7280;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* Success metrics */
        .success-metrics {
            margin-top: 8px;
            padding: 8px 12px;
            background: #F0FDF4;
            border-radius: 8px;
        }
        .success-metrics-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #166534;
            margin-bottom: 4px;
        }
        .success-metric {
            font-size: 0.78rem;
            color: #15803D;
            padding-left: 12px;
            line-height: 1.6;
        }
        
        /* Alert banner */
        .alert-banner {
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 16px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .alert-critical {
            background: #FEF2F2;
            border: 1px solid #FECACA;
        }
        .alert-high {
            background: #FFF7ED;
            border: 1px solid #FED7AA;
        }
        .alert-medium {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
        }
        .alert-title {
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 2px;
        }
        .alert-critical .alert-title { color: #991B1B; }
        .alert-high .alert-title { color: #9A3412; }
        .alert-medium .alert-title { color: #92400E; }
        .alert-desc {
            font-size: 0.82rem;
            line-height: 1.5;
        }
        .alert-critical .alert-desc { color: #7F1D1D; }
        .alert-high .alert-desc { color: #7C2D12; }
        .alert-medium .alert-desc { color: #78350F; }
        
        /* Summary box */
        .summary-box {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            border: 1px solid #E2E8F0;
        }
        .summary-title {
            font-size: 1rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .summary-content {
            font-size: 0.88rem;
            color: #475569;
            line-height: 1.6;
        }
        
        /* Key findings list */
        .findings-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .findings-list li {
            padding: 6px 0 6px 24px;
            position: relative;
            font-size: 0.85rem;
            color: #374151;
            line-height: 1.5;
            border-bottom: 1px solid #F3F4F6;
        }
        .findings-list li:last-child { border-bottom: none; }
        .findings-list li::before {
            content: "→";
            position: absolute;
            left: 0;
            color: #5046E4;
            font-weight: 600;
        }
        
        /* Data quality score */
        .quality-score {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 1.2rem;
            font-weight: 700;
        }
        .quality-good {
            background: #D1FAE5;
            color: #065F46;
        }
        .quality-medium {
            background: #FEF9C3;
            color: #854D0E;
        }
        .quality-poor {
            background: #FEE2E2;
            color: #991B1B;
        }
    </style>
    """


# ─── Insight Components ──────────────────────────────────────────────────────

def render_insight_card(insight: ExecutiveInsight, key: str = "") -> None:
    """Render a single insight card with styling."""
    severity_colors = {
        "critical": ("badge-critical", "🔴"),
        "high": ("badge-high", "🟠"),
        "medium": ("badge-medium", "🟡"),
        "low": ("badge-low", "🔵"),
    }
    
    category_colors = {
        "risk": "cat-risk",
        "anomaly": "cat-anomaly",
        "trend": "cat-trend",
        "performance": "cat-performance",
        "opportunity": "cat-opportunity",
    }
    
    sev_class, sev_emoji = severity_colors.get(insight.severity, ("badge-low", "🔵"))
    cat_class = category_colors.get(insight.category, "cat-performance")
    
    confidence_pct = int(insight.confidence * 100)
    
    html = textwrap.dedent(f"""
    <div class="insight-card insight-{insight.severity}">
        <div>
            <span class="severity-badge {sev_class}">{sev_emoji} {insight.severity}</span>
            <span class="category-badge {cat_class}">{insight.category}</span>
        </div>
        <div class="insight-headline">{insight.headline}</div>
        <div class="insight-description">{insight.description}</div>
        <div class="insight-impact">💡 {insight.impact}</div>
        <div style="margin-top: 8px;">
            <span style="font-size: 0.75rem; color: #6B7280;">Confidence:</span>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence_pct}%"></div>
            </div>
            <span style="font-size: 0.75rem; color: #6B7280;">{confidence_pct}%</span>
        </div>
    </div>
    """
    ).strip()
    st.markdown(html, unsafe_allow_html=True)


def render_insights_summary(report: InsightEngineReport) -> None:
    """Render a summary of all insights."""
    # Count by severity
    severity_counts = {}
    for insight in report.executive_insights:
        severity_counts[insight.severity] = severity_counts.get(insight.severity, 0) + 1
    
    # Count by category
    category_counts = report.insight_count_by_category
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Insights",
            len(report.executive_insights),
            help="Total patterns and anomalies detected"
        )
    
    with col2:
        critical = severity_counts.get("critical", 0)
        st.metric(
            "Critical",
            critical,
            help="Issues requiring immediate attention"
        )
    
    with col3:
        high = severity_counts.get("high", 0)
        st.metric(
            "High Priority",
            high,
            help="Important issues to address soon"
        )
    
    with col4:
        st.metric(
            "Data Quality",
            f"{report.data_quality_score:.0f}/100",
            help="Overall data quality score"
        )


def render_alert_banners(report: InsightEngineReport) -> None:
    """Render alert banners for critical and high priority insights."""
    critical_alerts = [i for i in report.executive_insights if i.severity == "critical"]
    high_alerts = [i for i in report.executive_insights if i.severity == "high"]
    
    for alert in critical_alerts[:3]:
        alert_html = textwrap.dedent(f"""
        <div class="alert-banner alert-critical">
            <div style="flex: 1;">
                <div class="alert-title">🔴 CRITICAL: {alert.headline}</div>
                <div class="alert-desc">{alert.description}</div>
            </div>
        </div>
        """
        ).strip()
        st.markdown(alert_html, unsafe_allow_html=True)
    
    for alert in high_alerts[:2]:
        alert_html = textwrap.dedent(f"""
        <div class="alert-banner alert-high">
            <div style="flex: 1;">
                <div class="alert-title">🟠 HIGH PRIORITY: {alert.headline}</div>
                <div class="alert-desc">{alert.description}</div>
            </div>
        </div>
        """
        ).strip()
        st.markdown(alert_html, unsafe_allow_html=True)


def render_data_quality_score(score: float) -> None:
    """Render a visual data quality score."""
    if score >= 80:
        quality_class = "quality-good"
        label = "Good"
    elif score >= 60:
        quality_class = "quality-medium"
        label = "Fair"
    else:
        quality_class = "quality-poor"
        label = "Needs Work"
    
    quality_html = textwrap.dedent(f"""
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="quality-score {quality_class}">{int(score)}</div>
        <div>
            <div style="font-weight: 600; color: #111827;">Data Quality Score</div>
            <div style="font-size: 0.82rem; color: #6B7280;">{label} · Based on completeness, anomalies, and consistency</div>
        </div>
    </div>
    """
    ).strip()
    st.markdown(quality_html, unsafe_allow_html=True)


def render_key_findings(findings: list[str]) -> None:
    """Render key findings as a styled list."""
    if not findings:
        return
    
    findings_html = "\n".join(f"<li>{f}</li>" for f in findings[:8])
    
    findings_html_block = textwrap.dedent(f"""
    <div class="summary-box">
        <div class="summary-title">🔍 Key Findings</div>
        <ul class="findings-list">
            {findings_html}
        </ul>
    </div>
    """
    ).strip()
    st.markdown(findings_html_block, unsafe_allow_html=True)


def render_executive_summary(report: InsightEngineReport) -> None:
    """Render the executive summary section."""
    executive_html = textwrap.dedent(f"""
    <div class="summary-box">
        <div class="summary-title">📊 Executive Summary</div>
        <div class="summary-content">{report.summary_paragraph}</div>
    </div>
    """
    ).strip()
    st.markdown(executive_html, unsafe_allow_html=True)


# ─── Recommendation Components ───────────────────────────────────────────────

def render_recommendation_card(rec: Recommendation, key: str = "") -> None:
    """Render a single recommendation card."""
    effort_emoji = {"low": "⚡", "medium": "⏱️", "high": "🏋️"}
    impact_emoji = {"low": "📊", "medium": "📈", "high": "🚀"}
    
    priority_labels = {
        1: "🔴 Priority 1",
        2: "🟠 Priority 2",
        3: "🟡 Priority 3",
        4: "🔵 Priority 4",
        5: "⚪ Priority 5",
    }
    
    category_labels = {
        "immediate": "Immediate Action",
        "short_term": "Short-Term",
        "strategic": "Strategic",
        "investigation": "Investigation",
    }
    
    rec_class = f"rec-{rec.category}"
    
    success_metrics_html = ""
    if rec.success_metrics:
        metrics_list = "\n".join(f'<div class="success-metric">✓ {m}</div>' for m in rec.success_metrics)
        success_metrics_html = textwrap.dedent(f"""
        <div class="success-metrics">
            <div class="success-metrics-title">Success Metrics</div>
            {metrics_list}
        </div>
        """
        ).strip()
    
    html = textwrap.dedent(f"""
    <div class="recommendation-card {rec_class}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
            <div style="flex: 1;">
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.75rem; color: #6B7280; background: #F3F4F6; padding: 2px 8px; border-radius: 4px;">
                        {category_labels.get(rec.category, rec.category)}
                    </span>
                    <span style="font-size: 0.75rem; color: #6B7280;">
                        {priority_labels.get(rec.priority, f"Priority {rec.priority}")}
                    </span>
                </div>
                <div class="rec-title">{rec.title}</div>
                <div style="font-size: 0.85rem; color: #6B7280; line-height: 1.5;">{rec.description}</div>
            </div>
        </div>
        
        <div class="rec-meta">
            <div class="rec-meta-item">{effort_emoji.get(rec.effort, '')} Effort: {rec.effort}</div>
            <div class="rec-meta-item">{impact_emoji.get(rec.impact, '')} Impact: {rec.impact}</div>
            <div class="rec-meta-item">⏱️ {rec.estimated_timeline}</div>
            <div class="rec-meta-item">👤 {rec.owner_role}</div>
        </div>
        
        {success_metrics_html}
    </div>
    """
    ).strip()

    card_styles = textwrap.dedent("""
    <style>
        .recommendation-card {
            background: white;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .rec-immediate { border-left: 4px solid #DC2626; }
        .rec-short-term { border-left: 4px solid #EA580C; }
        .rec-strategic { border-left: 4px solid #059669; }
        .rec-investigation { border-left: 4px solid #7C3AED; }
        .rec-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 6px;
        }
        .rec-meta {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 8px 0;
        }
        .rec-meta-item {
            font-size: 0.75rem;
            color: #6B7280;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .success-metrics {
            margin-top: 8px;
            padding: 8px 12px;
            background: #F0FDF4;
            border-radius: 8px;
        }
        .success-metrics-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #166534;
            margin-bottom: 4px;
        }
        .success-metric {
            font-size: 0.78rem;
            color: #15803D;
            padding-left: 12px;
            line-height: 1.6;
        }
    </style>
    """)

    components.html(card_styles + html, height=300 + 28 * len(rec.success_metrics or []), scrolling=False)


def render_recommendations_summary(report: RecommendationReport) -> None:
    """Render a summary of recommendations."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", report.total_recommendations)
    
    with col2:
        st.metric("Immediate", len(report.immediate_actions))
    
    with col3:
        st.metric("Short-Term", len(report.short_term_actions))
    
    with col4:
        st.metric("Strategic", len(report.strategic_actions))


# ─── Main Render Functions ───────────────────────────────────────────────────

def render_full_insights_panel(
    insight_report: InsightEngineReport,
    recommendation_report: RecommendationReport | None = None,
    domain_cfg: DomainConfig | None = None,
) -> None:
    """Render the complete insights panel."""
    st.markdown(_get_insight_styles(), unsafe_allow_html=True)
    
    # Executive Summary
    render_executive_summary(insight_report)
    
    # Alert Banners for critical issues
    if insight_report.has_critical_insights:
        render_alert_banners(insight_report)
    
    # Insights Summary Metrics
    render_insights_summary(insight_report)
    
    # Key Findings
    if insight_report.key_findings:
        render_key_findings(insight_report.key_findings)
    
    # Data Quality Score
    st.markdown("### Data Quality")
    render_data_quality_score(insight_report.data_quality_score)
    
    # Detailed Insights by Category
    st.markdown("### Detailed Insights")
    
    # Group insights by severity
    critical_insights = [i for i in insight_report.executive_insights if i.severity == "critical"]
    high_insights = [i for i in insight_report.executive_insights if i.severity == "high"]
    other_insights = [i for i in insight_report.executive_insights if i.severity not in ["critical", "high"]]
    
    if critical_insights:
        st.markdown("#### 🔴 Critical Insights")
        for i, insight in enumerate(critical_insights[:5]):
            render_insight_card(insight, key=f"critical_{i}")
    
    if high_insights:
        st.markdown("#### 🟠 High Priority Insights")
        for i, insight in enumerate(high_insights[:5]):
            render_insight_card(insight, key=f"high_{i}")
    
    if other_insights:
        st.markdown("#### Other Insights")
        with st.expander(f"Show {len(other_insights)} additional insights", expanded=False):
            for i, insight in enumerate(other_insights[:10]):
                render_insight_card(insight, key=f"other_{i}")
    
    # Recommendations
    if recommendation_report:
        st.markdown("---")
        st.markdown("### 🎯 Recommendations")
        
        # Top 3 Actions
        top_actions = recommendation_report.top_3_actions
        if top_actions:
            st.markdown("#### Top 3 Priority Actions")
            for i, rec in enumerate(top_actions):
                render_recommendation_card(rec, key=f"top_{i}")
        
        # Immediate Actions
        if recommendation_report.immediate_actions:
            with st.expander(f"🔴 {len(recommendation_report.immediate_actions)} Immediate Actions Required", expanded=True):
                for i, rec in enumerate(recommendation_report.immediate_actions[:5]):
                    render_recommendation_card(rec, key=f"imm_{i}")
        
        # Short-term Actions
        if recommendation_report.short_term_actions:
            with st.expander(f"🟡 {len(recommendation_report.short_term_actions)} Short-Term Actions", expanded=False):
                for i, rec in enumerate(recommendation_report.short_term_actions[:5]):
                    render_recommendation_card(rec, key=f"st_{i}")
        
        # Strategic Actions
        if recommendation_report.strategic_actions:
            with st.expander(f"🟢 {len(recommendation_report.strategic_actions)} Strategic Initiatives", expanded=False):
                for i, rec in enumerate(recommendation_report.strategic_actions[:5]):
                    render_recommendation_card(rec, key=f"strat_{i}")
        
        # Investigation Items
        if recommendation_report.investigation_items:
            with st.expander(f"🔍 {len(recommendation_report.investigation_items)} Investigation Items", expanded=False):
                for i, rec in enumerate(recommendation_report.investigation_items[:5]):
                    render_recommendation_card(rec, key=f"inv_{i}")


def render_quick_insights(
    insight_report: InsightEngineReport,
    max_insights: int = 3,
) -> None:
    """Render a quick summary of top insights (for dashboard sidebar or compact view)."""
    st.markdown(_get_insight_styles(), unsafe_allow_html=True)
    
    # Quick metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Insights", len(insight_report.executive_insights))
    with col2:
        st.metric("Data Quality", f"{insight_report.data_quality_score:.0f}%")
    
    # Top insights
    if insight_report.executive_insights:
        st.markdown("**Top Insights:**")
        for i, insight in enumerate(insight_report.executive_insights[:max_insights]):
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
            emoji = severity_emoji.get(insight.severity, "🔵")
            st.markdown(f"{emoji} {insight.headline}")