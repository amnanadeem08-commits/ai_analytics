"""
pipeline.py — Processing orchestration for AI Analytics Assistant.

Responsibilities:
  - Service registry via @st.cache_resource (one instance per server process)
  - Session state initialisation
  - Full data processing pipeline
  - Domain-change handler

Bug fixes applied:
  1. hash() replaced with MD5 — deterministic across Python processes.
  2. Domain change now invalidates insight_report + recommendation_report.
  3. All services use @st.cache_resource — never re-instantiated on reruns.
"""

from __future__ import annotations

import hashlib
import json
import logging

import streamlit as st

from config import SMART_CHARTS_ENABLED, V3_CATEGORY_ANALYTICS_ENABLED

logger = logging.getLogger(__name__)


def _file_hash(df) -> str:
    """MD5 over shape + column list — deterministic across Python processes."""
    payload = json.dumps([list(df.shape), df.columns.tolist()]).encode()
    return hashlib.md5(payload).hexdigest()


_SERVICES_CACHE_VERSION = 2  # bump when service APIs change (e.g. export branding)


@st.cache_resource
def get_services(_cache_version: int = _SERVICES_CACHE_VERSION) -> dict:
    """
    Instantiate every heavy service exactly ONCE per server process.
    ChatbotService excluded — it is stateful per-session, lives in st.session_state.
    """
    _ = _cache_version  # cache-bust token only
    from services.cleaning_service import CleaningService
    from services.domain_service import DomainService
    from services.kpi_service import KPIService
    from services.analytics_service import AnalyticsService
    from services.chart_service import ChartService
    from services.smart_chart_service import SmartChartService
    from services.ai_summary_service import AISummaryService
    from services.export_service import ExportService
    from services.data_quality_service import DataQualityService
    from services.forecasting_service import ForecastingService
    from services.storytelling_service import StorytellingService
    from services.anomaly_narration_service import AnomalyNarrationService
    from services.comparison_service import ComparisonService
    from services.column_insight_service import ColumnInsightService
    from services.session_service import SessionService
    from services.category_analytics_service import CategoryAnalyticsService
    from services.insight_engine import InsightEngine
    from services.recommendation_engine import RecommendationEngine
    from services.data_understanding_service import DataUnderstandingService

    return {
        "cleaning":              CleaningService(),
        "domain":                DomainService(),
        "kpi":                   KPIService(),
        "analytics":             AnalyticsService(),
        "chart":                 ChartService(),
        "smart_chart":           SmartChartService(),
        "ai_summary":            AISummaryService(),
        "export":                ExportService(),
        "quality":               DataQualityService(),
        "understanding":         DataUnderstandingService(),
        "forecasting":           ForecastingService(),
        "storytelling":          StorytellingService(),
        "anomaly":               AnomalyNarrationService(),
        "comparison":            ComparisonService(),
        "column_insight":        ColumnInsightService(),
        "session":               SessionService(),
        "category":              CategoryAnalyticsService(),
        "insight_engine":        InsightEngine(use_llm=True),
        "recommendation_engine": RecommendationEngine(),
    }


def init_session_state() -> None:
    """Set defaults for every session key. Called once per browser session."""
    from services.chatbot_service import ChatbotService

    defaults = {
        "raw_df":                    None,
        "cleaned_df":                None,
        "cleaning_report":           None,
        "domain_key":                "auto",
        "kpis":                      [],
        "analytics_report":          None,
        "ai_summary":                "",
        "charts":                    [],
        "filename":                  "",
        "chatbot_svc":               ChatbotService(),
        "last_file_hash":            None,
        "processing_done":           False,
        "data_quality_report":       None,
        "forecasts":                 [],
        "story_narrative":           None,
        "anomaly_narrations":        [],
        "compare_df":                None,
        "compare_filename":          "",
        "comparison_report":         None,
        "chart_insights":            {},
        "category_analytics":        None,
        "data_understanding_report": None,
        "insight_report":            None,
        "recommendation_report":     None,
        "export_logo_bytes":         None,
        "export_brand_primary":      "#5046E4",
        "export_brand_secondary":    "#7C3AED",
        "export_brand_accent":       "#0E9F6E",
        "export_company_name":       "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def run_pipeline(raw_df, filename: str) -> None:
    """Full processing pipeline — skips if file hash unchanged."""
    svcs  = get_services()
    fhash = _file_hash(raw_df)

    if st.session_state.processing_done and st.session_state.last_file_hash == fhash:
        return

    with st.spinner("🧹 Cleaning data…"):
        cleaned_df, cleaning_report = svcs["cleaning"].clean(raw_df)

    with st.spinner("🔍 Detecting domain and computing KPIs…"):
        auto_domain_key           = svcs["domain"].auto_detect(cleaned_df)
        domain_cfg                = svcs["domain"].get_config(auto_domain_key)
        data_understanding_report = svcs["understanding"].profile(cleaned_df)
        kpis                      = svcs["kpi"].compute(cleaned_df, domain_cfg)
        analytics_report          = svcs["analytics"].analyse(cleaned_df)

    with st.spinner("📈 Generating visualisations…"):
        charts = (
            svcs["smart_chart"].generate_charts(cleaned_df, domain_cfg)
            if SMART_CHARTS_ENABLED
            else svcs["chart"].auto_charts(cleaned_df, domain_cfg)
        )

    category_analytics = None
    if V3_CATEGORY_ANALYTICS_ENABLED:
        with st.spinner("📊 Building category-wise charts…"):
            try:
                category_analytics = svcs["category"].generate(cleaned_df, domain_cfg)
            except Exception as exc:
                logger.error("Category analytics failed: %s", exc)

    with st.spinner("✅ Scoring data quality…"):
        data_quality_report = svcs["quality"].score(cleaned_df)

    with st.spinner("🔮 Building forecasts…"):
        forecasts = svcs["forecasting"].forecast(cleaned_df)

    with st.spinner("🤖 Generating AI executive summary…"):
        ai_summary = svcs["ai_summary"].generate_summary(
            domain_cfg, kpis, analytics_report, filename
        )

    with st.spinner("📖 Crafting data story…"):
        story_narrative = svcs["storytelling"].generate(domain_cfg, kpis, charts, cleaned_df)

    with st.spinner("⚠️ Narrating anomalies…"):
        anomaly_narrations = svcs["anomaly"].narrate(analytics_report.anomalies, domain_cfg)

    st.session_state.update({
        "cleaned_df":                cleaned_df,
        "cleaning_report":           cleaning_report,
        "domain_key":                auto_domain_key,
        "kpis":                      kpis,
        "analytics_report":          analytics_report,
        "charts":                    charts,
        "ai_summary":                ai_summary,
        "data_quality_report":       data_quality_report,
        "data_understanding_report": data_understanding_report,
        "forecasts":                 forecasts,
        "story_narrative":           story_narrative,
        "anomaly_narrations":        anomaly_narrations,
        "last_file_hash":            fhash,
        "processing_done":           True,
        "chart_insights":            {},
        "category_analytics":        category_analytics,
        "insight_report":            None,   # force regeneration for new data
        "recommendation_report":     None,
    })
    st.session_state.chatbot_svc.reset()
    logger.info("Pipeline complete for '%s' (%d rows)", filename, len(cleaned_df))


def handle_domain_change(new_domain_key: str) -> None:
    """
    Re-compute domain-dependent outputs on sidebar domain override.
    BUG FIX: insight_report + recommendation_report are invalidated here.
    Previously switching domain kept stale AI insights from the prior domain.
    """
    if new_domain_key == st.session_state.domain_key:
        return

    svcs       = get_services()
    cleaned_df = st.session_state.cleaned_df
    domain_cfg = svcs["domain"].get_config(new_domain_key)

    st.session_state.kpis = svcs["kpi"].compute(cleaned_df, domain_cfg)
    st.session_state.charts = (
        svcs["smart_chart"].generate_charts(cleaned_df, domain_cfg)
        if SMART_CHARTS_ENABLED
        else svcs["chart"].auto_charts(cleaned_df, domain_cfg)
    )

    if V3_CATEGORY_ANALYTICS_ENABLED:
        try:
            st.session_state.category_analytics = svcs["category"].generate(
                cleaned_df, domain_cfg
            )
        except Exception as exc:
            logger.warning("Category analytics refresh failed: %s", exc)

    # BUG FIX: stale insight reports from old domain must be cleared
    st.session_state.domain_key            = new_domain_key
    st.session_state.insight_report        = None
    st.session_state.recommendation_report = None
    logger.info("Domain changed to '%s' — insight cache cleared", new_domain_key)
