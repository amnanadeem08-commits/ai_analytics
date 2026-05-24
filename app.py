"""
app.py — AI Analytics Assistant · Streamlit entry point.

Architecture:
    Upload → Clean → Detect Domain → KPIs + Analytics → Dashboard
    └── Chatbot (parallel, stateful)
    └── Export (Excel / PDF / PPTX)

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import logging
from pathlib import Path

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports ─────────────────────────────────────────────────────────
from config import (
    LOGS_DIR, APP_NAME, EXPORTS_DIR, SMART_CHARTS_ENABLED, SESSION_ID_LENGTH, CHART_HEIGHT,
    V3_CATEGORY_ANALYTICS_ENABLED,
)
from utils.helpers import configure_logging
from components.uploader import render_uploader
from components.sidebar import render_sidebar, apply_filters
from components.kpi_cards import render_kpi_cards
from components.chatbot import render_chatbot
from components.data_quality import render_data_quality
from components.comparison import render_comparison_upload, render_comparison_results
from components.storytelling import render_story_narrative
from components.category_charts import render_category_analytics
from services.category_analytics_service import CategoryAnalyticsService
from components.insights import render_executive_summary, render_analytics_insights, render_data_preview, render_anomaly_alerts
from services.cleaning_service import CleaningService
from services.domain_service import DomainService
from services.kpi_service import KPIService
from services.analytics_service import AnalyticsService
from services.chart_service import ChartService
from services.smart_chart_service import SmartChartService
from services.ai_summary_service import AISummaryService
from services.chatbot_service import ChatbotService
from services.export_service import ExportService
from services.data_quality_service import DataQualityService
from services.forecasting_service import ForecastingService
from services.storytelling_service import StorytellingService
from services.anomaly_narration_service import AnomalyNarrationService
from services.comparison_service import ComparisonService
from services.column_insight_service import ColumnInsightService
from services.session_service import SessionService
from services.insight_engine import InsightEngine
from services.recommendation_engine import RecommendationEngine
from components.insights_panel import render_full_insights_panel, render_quick_insights

configure_logging(LOGS_DIR)
logger = logging.getLogger(__name__)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════════ */
    /* GLOBAL RESET & BASE STYLES                                      */
    /* ═══════════════════════════════════════════════════════════════ */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #111827;
        background: #F9FAFB;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* STREAMLIT CHROME HIDING                                         */
    /* ═══════════════════════════════════════════════════════════════ */
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* TOP GRADIENT BAR - Premium SaaS indicator                       */
    /* ═══════════════════════════════════════════════════════════════ */
    
    .stApp::before {
        content: '';
        display: block;
        height: 4px;
        background: linear-gradient(90deg, #5046E4 0%, #7C3AED 50%, #0E9F6E 100%);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* SCROLLBAR STYLING                                               */
    /* ═══════════════════════════════════════════════════════════════ */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F3F4F6;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: #D1D5DB;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #9CA3AF;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* SIDEBAR STYLING                                                 */
    /* ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* SECTION HEADERS - Clear visual hierarchy                        */
    /* ═══════════════════════════════════════════════════════════════ */
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin: 2rem 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.625rem;
        letter-spacing: -0.02em;
    }
    
    .section-header .section-icon {
        font-size: 1.4rem;
    }
    
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, #E5E7EB 0%, transparent 100%);
        margin-left: 0.75rem;
    }
    
    .section-subtitle {
        font-size: 0.875rem;
        color: #6B7280;
        margin-top: -0.5rem;
        margin-bottom: 1.25rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* TAB STYLING - Modern tab navigation                             */
    /* ═══════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #F3F4F6;
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.875rem;
        color: #6B7280;
        transition: all 0.2s ease-in-out;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #FFFFFF;
        color: #5046E4;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: #374151;
        background: #E5E7EB;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* CHART CONTAINERS - Professional data visualization frames       */
    /* ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stPlotlyChart"] {
        min-height: 400px;
        border-radius: 12px;
    }
    
    [data-testid="stPlotlyChart"] > div {
        min-height: 400px;
    }
    
    .chart-wrapper {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    
    .chart-wrapper:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .chart-wrapper-title {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* BUTTONS - Consistent interactive elements                       */
    /* ═══════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.2s ease-in-out;
        border: 1px solid transparent;
        font-size: 0.875rem;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(80, 70, 228, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 16px rgba(80, 70, 228, 0.4);
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="secondary"] {
        background: #FFFFFF;
        color: #374151;
        border-color: #E5E7EB;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #F9FAFB;
        border-color: #D1D5DB;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* LOADING ANIMATIONS                                              */
    /* ═══════════════════════════════════════════════════════════════ */
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .loading {
        animation: pulse 2s ease-in-out infinite;
    }
    
    .animate-slide-up {
        animation: slideUp 0.4s ease-out;
    }
    
    /* ═══════════════════════════════════════════════════════════════ */
    /* RESPONSIVE ADJUSTMENTS                                          */
    /* ═══════════════════════════════════════════════════════════════ */
    
    @media (max-width: 768px) {
        .section-header {
            font-size: 1.1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ── Session state initialisation ─────────────────────────────────────────────
def _init_state():
    defaults = {
        "raw_df": None,
        "cleaned_df": None,
        "cleaning_report": None,
        "domain_key": "auto",
        "kpis": [],
        "analytics_report": None,
        "ai_summary": "",
        "charts": [],
        "filename": "",
        "chatbot_svc": ChatbotService(),
        "last_file_hash": None,
        "processing_done": False,
        "data_quality_report": None,
        "forecasts": [],
        "story_narrative": None,
        "anomaly_narrations": [],
        "compare_df": None,
        "compare_filename": "",
        "comparison_report": None,
        "chart_insights": {},
        "category_analytics": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


_PLOTLY_CONFIG = {"displayModeBar": True, "responsive": True}


def _render_chart(fig, key: str) -> None:
    """Render a Plotly figure with fixed height so Streamlit does not collapse it."""
    fig.update_layout(height=CHART_HEIGHT, autosize=False)
    st.plotly_chart(fig, use_container_width=True, key=key, config=_PLOTLY_CONFIG)


def _guess_chart_columns(title: str, df: pd.DataFrame) -> list[str]:
    """Infer column names referenced in a chart title for column-level insight."""
    if df is None or df.empty:
        return []
    title_lower = title.lower()
    return [c for c in df.columns if c.lower().replace("_", " ") in title_lower][:3]


# ── Service singletons ───────────────────────────────────────────────────────
cleaning_svc   = CleaningService()
domain_svc     = DomainService()
kpi_svc        = KPIService()
analytics_svc  = AnalyticsService()
chart_svc      = ChartService()
smart_chart_svc = SmartChartService()
ai_summary_svc = AISummaryService()
export_svc     = ExportService()
quality_svc    = DataQualityService()
forecast_svc   = ForecastingService()
story_svc      = StorytellingService()
anomaly_svc    = AnomalyNarrationService()
comparison_svc = ComparisonService()
column_insight_svc = ColumnInsightService()
session_svc    = SessionService()
category_svc   = CategoryAnalyticsService()
insight_engine = InsightEngine(use_llm=True)
recommendation_engine = RecommendationEngine()


# ── Header ───────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.markdown('<div style="font-size:2.8rem;padding-top:0.2rem">📊</div>', unsafe_allow_html=True)
with col_title:
    st.markdown(f"""
    <div style="padding-top:0.4rem">
        <div style="font-size:1.6rem;font-weight:800;color:#111827;letter-spacing:-0.04em">{APP_NAME}</div>
        <div style="font-size:0.82rem;color:#6B7280">
            AI-powered business analytics · Domain-aware insights · Export-ready reports
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ── Upload panel (always visible until data is loaded) ───────────────────────
if st.session_state.raw_df is None:
    df_uploaded, filename = render_uploader()
    if df_uploaded is not None:
        st.session_state.raw_df = df_uploaded
        st.session_state.filename = filename
        st.session_state.processing_done = False
        st.rerun()
    st.stop()


# ── Process pipeline (runs once per new upload) ───────────────────────────────
raw_df = st.session_state.raw_df
file_hash = hash(str(raw_df.shape) + str(raw_df.columns.tolist()))

if not st.session_state.processing_done or st.session_state.last_file_hash != file_hash:
    with st.spinner("🧹 Cleaning data…"):
        cleaned_df, cleaning_report = cleaning_svc.clean(raw_df)

    with st.spinner("🔍 Detecting domain and computing KPIs…"):
        auto_domain_key = domain_svc.auto_detect(cleaned_df)
        domain_cfg = domain_svc.get_config(auto_domain_key)
        kpis = kpi_svc.compute(cleaned_df, domain_cfg)
        analytics_report = analytics_svc.analyse(cleaned_df)

    with st.spinner("📈 Generating charts…"):
        if SMART_CHARTS_ENABLED:
            charts = smart_chart_svc.generate_charts(cleaned_df, domain_cfg)
        else:
            charts = chart_svc.auto_charts(cleaned_df, domain_cfg)

    category_analytics = None
    if V3_CATEGORY_ANALYTICS_ENABLED:
        with st.spinner("📊 Building category-wise charts…"):
            try:
                category_analytics = category_svc.generate(cleaned_df, domain_cfg)
            except Exception as e:
                logger.error("Category analytics failed: %s", e)
                category_analytics = None

    with st.spinner("✅ Scoring data quality…"):
        data_quality_report = quality_svc.score(cleaned_df)

    with st.spinner("🔮 Building forecasts…"):
        forecasts = forecast_svc.forecast(cleaned_df)

    with st.spinner("🤖 Generating AI executive summary…"):
        ai_summary = ai_summary_svc.generate_summary(
            domain_cfg, kpis, analytics_report, st.session_state.filename
        )

    with st.spinner("📖 Crafting data story…"):
        story_narrative = story_svc.generate(domain_cfg, kpis, charts, cleaned_df)

    with st.spinner("⚠️ Narrating anomalies…"):
        anomaly_narrations = anomaly_svc.narrate(analytics_report.anomalies, domain_cfg)

    st.session_state.update({
        "cleaned_df": cleaned_df,
        "cleaning_report": cleaning_report,
        "domain_key": auto_domain_key,
        "kpis": kpis,
        "analytics_report": analytics_report,
        "charts": charts,
        "ai_summary": ai_summary,
        "data_quality_report": data_quality_report,
        "forecasts": forecasts,
        "story_narrative": story_narrative,
        "anomaly_narrations": anomaly_narrations,
        "last_file_hash": file_hash,
        "processing_done": True,
        "chart_insights": {},
        "category_analytics": category_analytics,
    })
    st.session_state.chatbot_svc.reset()
    logger.info("Processing complete for '%s'", st.session_state.filename)


# ── Sidebar (filters + domain override) ──────────────────────────────────────
sidebar_cfg = render_sidebar(st.session_state.cleaned_df)
active_domain_key = sidebar_cfg["domain_key"]

# Re-compute KPIs/charts if domain changed
if active_domain_key != st.session_state.domain_key:
    domain_cfg = domain_svc.get_config(active_domain_key)
    st.session_state.kpis = kpi_svc.compute(st.session_state.cleaned_df, domain_cfg)
    if SMART_CHARTS_ENABLED:
        st.session_state.charts = smart_chart_svc.generate_charts(
            st.session_state.cleaned_df, domain_cfg
        )
    else:
        st.session_state.charts = chart_svc.auto_charts(
            st.session_state.cleaned_df, domain_cfg
        )
    st.session_state.domain_key = active_domain_key
    if V3_CATEGORY_ANALYTICS_ENABLED:
        try:
            st.session_state.category_analytics = category_svc.generate(
                st.session_state.cleaned_df, domain_cfg
            )
        except Exception as e:
            logger.warning("Category analytics refresh failed: %s", e)

domain_cfg  = domain_svc.get_config(st.session_state.domain_key)
kpis        = st.session_state.kpis
charts      = st.session_state.charts
ai_summary  = st.session_state.ai_summary
analytics_report = st.session_state.analytics_report
cleaning_report  = st.session_state.cleaning_report
data_quality_report = st.session_state.get("data_quality_report")
forecasts = st.session_state.get("forecasts") or []
story_narrative = st.session_state.get("story_narrative")
anomaly_narrations = st.session_state.get("anomaly_narrations") or []
category_analytics = st.session_state.get("category_analytics")

# Apply sidebar filters to the view
filtered_df = apply_filters(st.session_state.cleaned_df, sidebar_cfg["filters"])

active_tab = sidebar_cfg["active_tab"]


# ─────────────────────────────────────────────────────────────────────────────
# TAB: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if "Dashboard" in active_tab:
    # Upload new file button
    col_fn, col_btn = st.columns([5, 1])
    with col_fn:
        st.caption(f"📁 **{st.session_state.filename}** · {len(filtered_df):,} rows · Domain: **{domain_cfg.label}**")
    with col_btn:
        if st.button("Upload new file"):
            st.session_state.raw_df = None
            st.session_state.processing_done = False
            st.rerun()

    # Executive summary
    render_executive_summary(ai_summary, domain_cfg)

    # Anomaly alert banner
    render_anomaly_alerts(analytics_report.anomalies, anomaly_narrations)

    if data_quality_report:
        st.markdown('<div class="section-header">✅ Data Quality Score</div>', unsafe_allow_html=True)
        render_data_quality(data_quality_report)

    # KPI cards
    st.markdown('<div class="section-header">📌 Key Metrics</div>', unsafe_allow_html=True)
    render_kpi_cards(kpis, columns=4)

    # Charts grid
    if charts:
        st.markdown('<div class="section-header">📊 Visualisations</div>', unsafe_allow_html=True)
        chart_cols = st.columns(2)
        for i, (title, fig) in enumerate(charts[:6]):
            with chart_cols[i % 2]:
                st.markdown(f"**{title}**")
                _render_chart(fig, key=f"chart_{i}")
                if st.button("💡 Explain chart", key=f"explain_chart_{i}"):
                    cols_guess = _guess_chart_columns(title, filtered_df)
                    insight = column_insight_svc.explain(
                        filtered_df, domain_cfg, title, cols_guess
                    )
                    st.session_state.chart_insights[title] = insight.insight
                if title in st.session_state.get("chart_insights", {}):
                    st.info(st.session_state.chart_insights[title])

    # Insights
    st.markdown('<div class="section-header">🔎 Analytics Insights</div>', unsafe_allow_html=True)
    render_analytics_insights(
        analytics_report, domain_cfg, anomaly_narrations, forecasts
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB: CATEGORY ANALYTICS (V3)
# ─────────────────────────────────────────────────────────────────────────────
elif "Category Analytics" in active_tab:
    st.markdown("### 📊 Category Analytics")
    st.caption(
        "Complete category-wise breakdowns: totals, share, distribution, treemap, "
        "and trends over time."
    )
    if category_analytics and category_analytics.charts:
        render_category_analytics(category_analytics, _render_chart)
    else:
        st.info("Upload data with categorical and numeric columns to generate category charts.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB: DEEP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
elif "Deep Analysis" in active_tab:
    st.markdown("### 🔍 Deep Analysis")

    # Data preview
    render_data_preview(filtered_df, cleaning_report.summary())

    # Correlation heatmap
    numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) >= 3:
        st.markdown("**Correlation Matrix**")
        fig = chart_svc.correlation_heatmap(filtered_df, numeric_cols[:12])
        _render_chart(fig, key="deep_corr")

    # Custom chart builder
    st.markdown("**Custom Chart Builder**")
    chart_options = ["Bar", "Line", "Scatter", "Histogram", "Pie", "Heatmap", "Count Plot"]

    all_cols = filtered_df.columns.tolist()
    numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    category_cols = [c for c in all_cols if c not in numeric_cols]

    col_x, col_y, col_type = st.columns([3, 3, 2])
    with col_type:
        chart_type = st.selectbox("Chart type", chart_options, key="cb_type")

    if chart_type == "Histogram":
        with col_x:
            x_col = st.selectbox("Numeric column", numeric_cols if numeric_cols else all_cols, key="cb_x")
        with col_y:
            st.markdown("Histogram uses one numeric column to show distribution.")
        y_col = None
    elif chart_type == "Count Plot":
        with col_x:
            x_col = st.selectbox("Category", category_cols if category_cols else all_cols, key="cb_x")
        with col_y:
            st.markdown("Count Plot uses one categorical field to show frequency.")
        y_col = None
    elif chart_type == "Heatmap":
        with col_x:
            st.markdown("Heatmap uses all numeric columns automatically.")
            x_col = None
        with col_y:
            st.markdown("")
            y_col = None
    else:
        with col_x:
            x_col = st.selectbox("X axis", all_cols, key="cb_x")
        with col_y:
            y_col = st.selectbox(
                "Y axis (numeric)",
                numeric_cols if numeric_cols else all_cols,
                key="cb_y",
            )

    if st.button("Generate Chart", type="primary"):
        selection = chart_svc.validate_chart_selection(x_col, y_col, chart_type, filtered_df)

        for warning in selection["warnings"]:
            st.warning(warning)

        if not selection["is_valid"]:
            st.error("Selected chart combination is invalid. See recommended chart below.")
            recommended = selection.get("recommended_chart")
            if recommended:
                st.info(f"Recommended chart: {recommended.replace('_', ' ').title()}")
                fig = chart_svc.build_custom_chart(
                    recommended,
                    selection["cleaned_df"],
                    x_col,
                    y_col,
                )
                if fig is not None:
                    st.markdown(f"**{selection.get('recommended_title') or 'Recommended chart'}**")
                    _render_chart(fig, key="custom_chart")
                    insight = chart_svc.generate_chart_insight(
                        selection["cleaned_df"],
                        x_col,
                        y_col,
                        recommended,
                        selection.get("aggregation"),
                    )
                    st.info(insight)
        else:
            try:
                fig = chart_svc.build_custom_chart(
                    selection["chart_type"],
                    selection["cleaned_df"],
                    x_col,
                    y_col,
                )
                if fig is None:
                    raise ValueError("Unable to build chart for the selected combination.")
                st.markdown(f"**{selection['title']}**")
                _render_chart(fig, key="custom_chart")
                insight = chart_svc.generate_chart_insight(
                    selection["cleaned_df"],
                    x_col,
                    y_col,
                    selection["chart_type"],
                    selection.get("aggregation"),
                )
                st.info(insight)
            except Exception as e:
                st.error(f"Chart error: {e}")

    # Numeric stats table
    if numeric_cols:
        st.markdown("**Descriptive Statistics**")
        st.dataframe(
            filtered_df[numeric_cols].describe().T.style.format("{:.2f}"),
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB: DATA STORY
# ─────────────────────────────────────────────────────────────────────────────
elif "Data Story" in active_tab:
    st.markdown("### 📖 Data Story")
    if story_narrative:
        render_story_narrative(story_narrative)
        if charts:
            st.markdown('<div class="section-header">📊 Charts in this story</div>', unsafe_allow_html=True)
            for i, (title, fig) in enumerate(charts[:6]):
                st.markdown(f"**{title}**")
                _render_chart(fig, key=f"story_chart_{i}")
    else:
        st.info("Upload data to generate an AI-guided narrative.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB: BUSINESS INSIGHTS (AI-Powered)
# ─────────────────────────────────────────────────────────────────────────────
elif "Business Insights" in active_tab:
    st.markdown("### 🧠 AI-Powered Business Insights")
    st.caption("Advanced anomaly detection, pattern analysis, and actionable recommendations powered by AI.")
    
    # Initialize session state for insight reports
    if "insight_report" not in st.session_state:
        st.session_state.insight_report = None
    if "recommendation_report" not in st.session_state:
        st.session_state.recommendation_report = None
    
    # Generate insights if not already done
    if st.session_state.insight_report is None:
        with st.spinner("🧠 Analyzing data patterns and generating insights…"):
            try:
                # Generate insights
                insight_report = insight_engine.generate_insights(
                    df=filtered_df,
                    domain_cfg=domain_cfg,
                    kpis=kpis,
                    analytics_report=analytics_report,
                    dataset_name=st.session_state.filename,
                )
                st.session_state.insight_report = insight_report
                
                # Generate recommendations
                rec_report = recommendation_engine.generate_recommendations(
                    insight_report=insight_report,
                    domain_cfg=domain_cfg,
                    df=filtered_df,
                    kpis=kpis,
                )
                st.session_state.recommendation_report = rec_report
                
            except Exception as e:
                logger.error(f"Insight generation failed: {e}")
                st.error(f"Failed to generate insights: {e}")
    
    # Render insights panel
    if st.session_state.insight_report:
        render_full_insights_panel(
            insight_report=st.session_state.insight_report,
            recommendation_report=st.session_state.recommendation_report,
            domain_cfg=domain_cfg,
        )
        
        # Download insights report
        st.markdown("---")
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            if st.button("📥 Download Insights Summary", use_container_width=True):
                # Create a text summary for download
                summary_lines = [
                    f"Business Insights Report - {st.session_state.filename}",
                    f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"Domain: {domain_cfg.label}",
                    f"Records Analyzed: {len(filtered_df):,}",
                    "",
                    "EXECUTIVE SUMMARY",
                    "=" * 50,
                    st.session_state.insight_report.summary_paragraph,
                    "",
                    "KEY FINDINGS",
                    "=" * 50,
                ]
                for finding in st.session_state.insight_report.key_findings:
                    summary_lines.append(f"• {finding}")
                
                summary_lines.extend(["", "RISK ALERTS", "=" * 50])
                for alert in st.session_state.insight_report.risk_alerts:
                    summary_lines.append(f"⚠️ {alert}")
                
                summary_lines.extend(["", "OPPORTUNITIES", "=" * 50])
                for opp in st.session_state.insight_report.opportunities:
                    summary_lines.append(f"💡 {opp}")
                
                if st.session_state.recommendation_report:
                    summary_lines.extend(["", "TOP RECOMMENDATIONS", "=" * 50])
                    for rec in st.session_state.recommendation_report.top_3_actions:
                        summary_lines.append(f"• {rec.title}")
                        summary_lines.append(f"  Timeline: {rec.estimated_timeline}")
                        summary_lines.append(f"  Impact: {rec.impact}")
                        summary_lines.append("")
                
                summary_text = "\n".join(summary_lines)
                st.download_button(
                    "⬇ Download TXT",
                    summary_text,
                    file_name=f"insights_{st.session_state.filename.replace('.csv', '')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# TAB: COMPARE
# ─────────────────────────────────────────────────────────────────────────────
elif "Compare" in active_tab:
    st.markdown("### ⚖️ Dataset Comparison")
    st.caption(f"Baseline: **{st.session_state.filename}** ({len(filtered_df):,} rows)")

    compare_df, compare_name = render_comparison_upload()
    if compare_df is not None:
        st.session_state.compare_df = compare_df
        st.session_state.compare_filename = compare_name

    if st.session_state.get("compare_df") is not None:
        if st.button("Run comparison", type="primary"):
            try:
                report = comparison_svc.compare(
                    filtered_df,
                    st.session_state.compare_df,
                    domain_cfg,
                    baseline_label=st.session_state.filename,
                    compare_label=st.session_state.compare_filename or "Dataset B",
                )
                st.session_state.comparison_report = report
            except Exception as e:
                st.error(f"Comparison failed: {e}")

        if st.session_state.get("comparison_report"):
            render_comparison_results(st.session_state.comparison_report)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: DATA COPILOT
# ─────────────────────────────────────────────────────────────────────────────
elif "Copilot" in active_tab:
    render_chatbot(
        df=filtered_df,
        domain=domain_cfg,
        kpis=kpis,
        chatbot_svc=st.session_state.chatbot_svc,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB: EXPORT
# ─────────────────────────────────────────────────────────────────────────────
elif "Export" in active_tab:
    st.markdown("### 📤 Export Reports")

    st.info(
        f"**{st.session_state.filename}** · {len(filtered_df):,} rows · {len(kpis)} KPIs · Domain: {domain_cfg.label}",
        icon="📁",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 📊 Excel Report")
        st.markdown("Formatted workbook with KPIs, cleaned data, and statistics.")
        if st.button("Export Excel", type="primary", use_container_width=True):
            with st.spinner("Generating Excel…"):
                try:
                    path = export_svc.export_excel(filtered_df, kpis, domain_cfg)
                    with open(path, "rb") as f:
                        st.download_button(
                            "⬇ Download Excel",
                            f,
                            file_name=path.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"Excel export failed: {e}")

    with col2:
        st.markdown("#### 📄 PDF Report")
        st.markdown("Professional PDF with KPI summary and executive narrative.")
        if st.button("Export PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF…"):
                try:
                    path = export_svc.export_pdf(
                        domain_cfg, kpis, ai_summary, charts=charts
                    )
                    with open(path, "rb") as f:
                        st.download_button(
                            "⬇ Download PDF",
                            f,
                            file_name=path.name,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"PDF export failed: {e}")

    with col3:
        st.markdown("#### 🎞 PowerPoint Deck")
        st.markdown("Slide deck with KPI cards, charts, and executive summary.")
        include_charts = st.checkbox("Include charts in PPTX", value=True)
        if st.button("Export PPTX", type="primary", use_container_width=True):
            with st.spinner("Generating PowerPoint…"):
                try:
                    pptx_charts = charts if include_charts else []
                    path = export_svc.export_pptx(domain_cfg, kpis, ai_summary, pptx_charts)
                    with open(path, "rb") as f:
                        st.download_button(
                            "⬇ Download PPTX",
                            f,
                            file_name=path.name,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"PPTX export failed: {e}")

    st.markdown("---")
    st.markdown("#### 💾 Saved Sessions")
    sid = st.text_input(
        "Session name (optional)",
        value=st.session_state.filename.replace(".", "_")[:SESSION_ID_LENGTH],
        key="session_name_input",
    )
    if st.button("Save current session"):
        try:
            meta = {
                "filename": st.session_state.filename,
                "domain_key": st.session_state.domain_key,
                "row_count": len(st.session_state.cleaned_df),
                "ai_summary": st.session_state.ai_summary,
            }
            session_svc.save(sid or "session", meta, st.session_state.cleaned_df)
            st.success(f"Session saved as `{sid}`")
        except Exception as e:
            st.error(f"Save failed: {e}")

    saved = session_svc.list_sessions()
    if saved:
        pick = st.selectbox(
            "Restore session",
            options=[s.session_id for s in saved],
            format_func=lambda x: next(
                (f"{s.filename} ({s.saved_at[:10]})" for s in saved if s.session_id == x), x
            ),
        )
        if st.button("Load session"):
            try:
                meta, df = session_svc.load(pick)
                st.session_state.raw_df = df
                st.session_state.filename = meta.get("filename", pick)
                st.session_state.processing_done = False
                st.rerun()
            except Exception as e:
                st.error(f"Load failed: {e}")

    st.markdown("---")
    st.markdown("**Export Path:** `exports/`")
    export_files = list(EXPORTS_DIR.glob("*"))
    if export_files:
        for f in sorted(export_files, reverse=True)[:10]:
            st.caption(f"📎 {f.name} ({f.stat().st_size / 1024:.1f} KB)")
