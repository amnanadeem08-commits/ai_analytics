"""
app.py — AI Analytics Assistant · Streamlit entry point.

Architecture:
    Upload → pipeline.run_pipeline() → tabs/*

This file is intentionally minimal: page config, CSS injection,
upload gate, pipeline call, sidebar, and tab dispatch.
All business logic lives in pipeline.py and tabs/.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path (Streamlit Cloud / nested repo layouts).
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import logging

import streamlit as st

# ── Page config — MUST be the first Streamlit call ───────────────────────────
st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports ──────────────────────────────────────────────────────────
from config import APP_NAME, LOGS_DIR
from utils.helpers import configure_logging
from styles.global_css import inject as inject_css

from pipeline import get_services, init_session_state, run_pipeline, handle_domain_change

from components.uploader import render_uploader
from components.sidebar import render_sidebar, apply_filters

import tabs.dashboard        as tab_dashboard
import tabs.category         as tab_category
import tabs.deep_analysis    as tab_deep
import tabs.data_story       as tab_story
import tabs.business_insights as tab_insights
import tabs.compare          as tab_compare
import tabs.copilot          as tab_copilot
import tabs.export           as tab_export

# ── Bootstrap ─────────────────────────────────────────────────────────────────
configure_logging(LOGS_DIR)
logger = logging.getLogger(__name__)

inject_css()
init_session_state()

# ── App header ────────────────────────────────────────────────────────────────
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

# ── Upload gate ───────────────────────────────────────────────────────────────
if st.session_state.raw_df is None:
    df_uploaded, filename = render_uploader()
    if df_uploaded is not None:
        st.session_state.raw_df          = df_uploaded
        st.session_state.filename        = filename
        st.session_state.processing_done = False
        st.rerun()
    st.stop()

# ── Pipeline ──────────────────────────────────────────────────────────────────
run_pipeline(st.session_state.raw_df, st.session_state.filename)

# ── Sidebar (domain override + filters) ──────────────────────────────────────
sidebar_cfg = render_sidebar(st.session_state.cleaned_df)
handle_domain_change(sidebar_cfg["domain_key"])   # no-op if domain unchanged

# ── Resolve current state into locals ────────────────────────────────────────
svcs = get_services()

domain_cfg                = svcs["domain"].get_config(st.session_state.domain_key)
kpis                      = st.session_state.kpis
charts                    = st.session_state.charts
ai_summary                = st.session_state.ai_summary
analytics_report          = st.session_state.analytics_report
cleaning_report           = st.session_state.cleaning_report
data_quality_report       = st.session_state.get("data_quality_report")
data_understanding_report = st.session_state.get("data_understanding_report")
forecasts                 = st.session_state.get("forecasts") or []
story_narrative           = st.session_state.get("story_narrative")
anomaly_narrations        = st.session_state.get("anomaly_narrations") or []
category_analytics        = st.session_state.get("category_analytics")

filtered_df  = apply_filters(st.session_state.cleaned_df, sidebar_cfg["filters"])
active_tab   = sidebar_cfg["active_tab"]

# ── Tab dispatch ──────────────────────────────────────────────────────────────
if active_tab == "dashboard":
    tab_dashboard.render(
        filtered_df, domain_cfg, kpis, charts, ai_summary,
        analytics_report, anomaly_narrations, forecasts,
        data_quality_report, data_understanding_report,
        svcs["column_insight"],
    )

elif active_tab == "category":
    tab_category.render(category_analytics)

elif active_tab == "deep_analysis":
    tab_deep.render(
        filtered_df, domain_cfg, cleaning_report,
        data_understanding_report, svcs["chart"],
    )

elif active_tab == "data_story":
    tab_story.render(
        story_narrative, charts,
        story_engine=svcs["story_engine"],
        df=filtered_df,
        domain_cfg=domain_cfg,
        analytics_report=analytics_report,
        data_understanding_report=data_understanding_report,
        kpis=kpis,
    )

elif active_tab == "business_insights":
    tab_insights.render(
        filtered_df, domain_cfg, kpis, analytics_report,
        svcs["insight_engine"], svcs["recommendation_engine"],
    )

elif active_tab == "compare":
    tab_compare.render(filtered_df, domain_cfg, svcs["comparison"])

elif active_tab == "copilot":
    tab_copilot.render(
        filtered_df, domain_cfg, kpis,
        svcs["sql"], svcs["rag"], st.session_state.filename,
    )

elif active_tab == "export":
    tab_export.render(
        filtered_df, domain_cfg, kpis, charts, ai_summary,
        svcs["export"], svcs["session"],
    )
