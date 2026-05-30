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


_SERVICES_CACHE_VERSION = 6  # bump when service APIs change (e.g. smart intelligence layer)


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
    from services.sql_engine import SQLEngine
    from services.rag_engine import RAGInsightEngine
    from services.storytelling_engine import StorytellingEngine
    from services.domain_detector import DomainDetector
    from services.insight_filter import InsightFilter

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
        "sql":                   SQLEngine(),
        "rag":                   RAGInsightEngine(),
        "story_engine":          StorytellingEngine(),
        "domain_detector":       DomainDetector(),
        "insight_filter":        InsightFilter(),
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
        # ── Smart Intelligence Layer (additive) ──
        "detected_domain":           "generic",
        "detected_domain_label":     "General Analytics",
        "detected_confidence":       0.0,
        "insight_mode":              "General (all insight types enabled)",
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

    # ── Eager: fast, deterministic work needed for the default Dashboard ──────
    with st.spinner("🧹 Cleaning data…"):
        cleaned_df, cleaning_report = svcs["cleaning"].clean(raw_df)

    with st.spinner("🔍 Detecting domain and computing KPIs…"):
        auto_domain_key           = svcs["domain"].auto_detect(cleaned_df)
        domain_cfg                = svcs["domain"].get_config(auto_domain_key)
        data_understanding_report = svcs["understanding"].profile(cleaned_df)
        kpis                      = svcs["kpi"].compute(cleaned_df, domain_cfg)
        analytics_report          = svcs["analytics"].analyse(cleaned_df)

    # ── Smart Intelligence Layer: confidence + insight mode (additive) ────────
    try:
        signal      = svcs["domain_detector"].detect(cleaned_df)
        insight_mode = svcs["insight_filter"].mode_label(auto_domain_key)
        st.session_state.update({
            "detected_domain":       auto_domain_key,
            "detected_domain_label": domain_cfg.label,
            "detected_confidence":   signal.confidence,
            "insight_mode":          insight_mode,
        })
    except Exception as exc:
        logger.warning("Domain detector failed: %s", exc)

    with st.spinner("📈 Generating visualisations…"):
        # use_ai=False: skip the optional LLM chart-refine call at upload time.
        charts = (
            svcs["smart_chart"].generate_charts(cleaned_df, domain_cfg, use_ai=False)
            if SMART_CHARTS_ENABLED
            else svcs["chart"].auto_charts(cleaned_df, domain_cfg)
        )

    with st.spinner("✅ Scoring data quality…"):
        data_quality_report = svcs["quality"].score(cleaned_df)

    # ── Deferred: expensive / LLM work runs only when its tab is opened ───────
    # (ai_summary, story_narrative, anomaly_narrations, forecasts, category)
    st.session_state.update({
        "cleaned_df":                cleaned_df,
        "cleaning_report":           cleaning_report,
        "domain_key":                auto_domain_key,
        "kpis":                      kpis,
        "analytics_report":          analytics_report,
        "charts":                    charts,
        "ai_summary":                "",
        "data_quality_report":       data_quality_report,
        "data_understanding_report": data_understanding_report,
        "forecasts":                 None,
        "story_narrative":           None,
        "anomaly_narrations":        None,
        "last_file_hash":            fhash,
        "processing_done":           True,
        "chart_insights":            {},
        "category_analytics":        None,
        "insight_report":            None,   # force regeneration for new data
        "recommendation_report":     None,
    })
    st.session_state.chatbot_svc.reset()
    try:
        svcs["sql"].load_dataframe(cleaned_df, source_name=filename)
        st.session_state.pop("sql_query_result", None)
    except Exception as exc:
        logger.warning("SQL engine init failed: %s", exc)
    try:
        svcs["rag"].build_knowledge_base(cleaned_df, source_name=filename)
        st.session_state.pop("insight_result", None)
    except Exception as exc:
        logger.warning("RAG knowledge base init failed: %s", exc)
    logger.info("Pipeline complete for '%s' (%d rows)", filename, len(cleaned_df))


def compute_filtered_outputs(filtered_df, domain_cfg, signature: str) -> dict:
    """
    Recompute filter-sensitive, deterministic outputs (KPIs, analytics, charts,
    category analytics) from the filtered DataFrame.

    Cached in session_state by `signature` so it only recomputes when the filter
    selection (or domain) changes — not on every rerun or tab switch. Charts are
    built without the optional LLM refinement to keep filtering fast and avoid
    rate limits.
    """
    cache = st.session_state.get("_filtered_cache")
    if cache and cache.get("sig") == signature:
        return cache["data"]

    svcs = get_services()
    kpis = svcs["kpi"].compute(filtered_df, domain_cfg)
    analytics_report = svcs["analytics"].analyse(filtered_df)

    if SMART_CHARTS_ENABLED:
        charts = svcs["smart_chart"].generate_charts(filtered_df, domain_cfg, use_ai=False)
    else:
        charts = svcs["chart"].auto_charts(filtered_df, domain_cfg)

    category_analytics = None
    if V3_CATEGORY_ANALYTICS_ENABLED:
        try:
            category_analytics = svcs["category"].generate(filtered_df, domain_cfg)
        except Exception as exc:
            logger.warning("Filtered category analytics failed: %s", exc)

    data = {
        "kpis": kpis,
        "analytics_report": analytics_report,
        "charts": charts,
        "category_analytics": category_analytics,
    }
    st.session_state["_filtered_cache"] = {"sig": signature, "data": data}
    return data


def _current_domain_cfg():
    svcs = get_services()
    return svcs["domain"].get_config(st.session_state.domain_key)


def ensure_ai_summary() -> str:
    """Generate the AI executive summary on first request, then cache it."""
    if st.session_state.get("ai_summary"):
        return st.session_state.ai_summary
    svcs = get_services()
    with st.spinner("🤖 Generating AI executive summary…"):
        summary = svcs["ai_summary"].generate_summary(
            _current_domain_cfg(),
            st.session_state.kpis,
            st.session_state.analytics_report,
            st.session_state.filename,
        )
    st.session_state.ai_summary = summary or ""
    return st.session_state.ai_summary


def ensure_forecasts() -> list:
    """Compute forecasts on first request, then cache them."""
    if st.session_state.get("forecasts") is not None:
        return st.session_state.forecasts
    with st.spinner("🔮 Building forecasts…"):
        forecasts = _cached_forecasts(st.session_state.last_file_hash, st.session_state.cleaned_df)
    st.session_state.forecasts = forecasts
    return forecasts


def ensure_anomaly_narrations() -> list:
    """Narrate anomalies (LLM) on first request, then cache."""
    if st.session_state.get("anomaly_narrations") is not None:
        return st.session_state.anomaly_narrations
    svcs = get_services()
    report = st.session_state.analytics_report
    anomalies = getattr(report, "anomalies", []) if report else []
    with st.spinner("⚠️ Narrating anomalies…"):
        narrations = svcs["anomaly"].narrate(anomalies, _current_domain_cfg())
    st.session_state.anomaly_narrations = narrations or []
    return st.session_state.anomaly_narrations


def ensure_story_narrative():
    """Build the chart-walkthrough story (LLM) on first request, then cache."""
    if st.session_state.get("story_narrative") is not None:
        return st.session_state.story_narrative
    svcs = get_services()
    with st.spinner("📖 Crafting data story…"):
        story = svcs["storytelling"].generate(
            _current_domain_cfg(),
            st.session_state.kpis,
            st.session_state.charts,
            st.session_state.cleaned_df,
        )
    st.session_state.story_narrative = story
    return story


def ensure_category_analytics():
    """Build category-wise analytics on first request, then cache."""
    if st.session_state.get("category_analytics") is not None:
        return st.session_state.category_analytics
    if not V3_CATEGORY_ANALYTICS_ENABLED:
        return None
    svcs = get_services()
    with st.spinner("📊 Building category-wise charts…"):
        try:
            result = svcs["category"].generate(
                st.session_state.cleaned_df, _current_domain_cfg()
            )
        except Exception as exc:
            logger.error("Category analytics failed: %s", exc)
            result = None
    st.session_state.category_analytics = result
    return result


@st.cache_data(show_spinner=False)
def _cached_forecasts(file_hash: str, _df):
    """
    Deterministic forecast computation cached by dataset fingerprint.
    `_df` is prefixed with underscore so Streamlit keys the cache on `file_hash`
    only (avoids re-hashing the whole DataFrame on every call).
    """
    from services.forecasting_service import ForecastingService
    return ForecastingService().forecast(_df)


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
        svcs["smart_chart"].generate_charts(cleaned_df, domain_cfg, use_ai=False)
        if SMART_CHARTS_ENABLED
        else svcs["chart"].auto_charts(cleaned_df, domain_cfg)
    )

    # Smart Intelligence Layer: keep badges in sync on manual override (additive).
    try:
        st.session_state.detected_domain       = new_domain_key
        st.session_state.detected_domain_label = domain_cfg.label
        st.session_state.detected_confidence   = 100.0  # user-selected → certain
        st.session_state.insight_mode          = svcs["insight_filter"].mode_label(new_domain_key)
    except Exception:
        pass

    # Invalidate domain-dependent lazy outputs so they regenerate on next view.
    st.session_state.domain_key            = new_domain_key
    st.session_state.category_analytics    = None
    st.session_state.ai_summary            = ""
    st.session_state.story_narrative       = None
    st.session_state.anomaly_narrations    = None
    st.session_state.insight_report        = None
    st.session_state.recommendation_report = None
    st.session_state.pop("_filtered_cache", None)
    logger.info("Domain changed to '%s' — dependent caches cleared", new_domain_key)
