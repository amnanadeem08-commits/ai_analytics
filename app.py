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

import json

from pipeline import (
    get_services, init_session_state, run_pipeline, handle_domain_change,
    compute_filtered_outputs,
    ensure_ai_summary, ensure_forecasts, ensure_anomaly_narrations,
    ensure_story_narrative, ensure_category_analytics,
)

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

# ── App header (glass command bar) ───────────────────────────────────────────
st.markdown(f"""
<div style="
    display:flex; align-items:center; gap:1rem;
    padding:1rem 1.25rem; margin-bottom:1.4rem;
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:16px;
    border-bottom:1px solid rgba(255,255,255,0.06);
">
    <div style="
        width:52px;height:52px;border-radius:14px;display:flex;align-items:center;
        justify-content:center;font-size:1.7rem;flex-shrink:0;
        background:linear-gradient(135deg,#6366F1 0%,#A855F7 100%);
        box-shadow:0 0 22px rgba(99,102,241,0.55);
    ">📊</div>
    <div style="flex:1">
        <div style="font-size:1.55rem;font-weight:800;color:#F3F4F6;letter-spacing:-0.03em;line-height:1.1">
            {APP_NAME}
        </div>
        <div style="font-size:0.82rem;color:#9CA3AF;margin-top:0.15rem">
            AI-powered business analytics · Domain-aware insights · Export-ready reports
        </div>
    </div>
    <div style="
        display:flex;align-items:center;gap:6px;padding:6px 12px;
        background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.3);
        border-radius:20px;font-size:0.72rem;font-weight:700;color:#34D399;
    ">
        <span style="width:7px;height:7px;border-radius:50%;background:#34D399;box-shadow:0 0 8px #34D399"></span>
        LIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload gate ───────────────────────────────────────────────────────────────
if st.session_state.raw_df is None:
    # ── Hero landing ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; max-width:760px; margin:2.5rem auto 1.25rem auto;">
          <div style="font-size:2.6rem; line-height:1; margin:0 auto 1.1rem auto;
                      display:flex; align-items:center; justify-content:center;
                      width:84px; height:84px; border-radius:22px;
                      background:linear-gradient(135deg, rgba(99,102,241,0.28), rgba(99,102,241,0.04));
                      border:1px solid rgba(99,102,241,0.38);
                      box-shadow:0 0 44px rgba(99,102,241,0.25);">📊</div>
          <h1 style="font-size:2.4rem; font-weight:800; color:#F9FAFB;
                     margin:0.25rem 0 0.85rem 0; letter-spacing:-0.02em; line-height:1.15;">
            Drop your data. Get instant AI insights.
          </h1>
          <p style="font-size:1.02rem; color:#9CA3AF; margin:0 auto; max-width:600px; line-height:1.6;">
            Upload any CSV or Excel file — your data is auto-cleaned, domain-detected,
            and turned into KPIs, charts, and a branded report in seconds.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Feature pills ────────────────────────────────────────────────────────
    _pill = (
        "display:inline-flex; align-items:center; background:rgba(255,255,255,0.04); "
        "border:1px solid rgba(255,255,255,0.08); border-radius:999px; "
        "padding:0.4rem 0.85rem; color:#C7CBD4; font-size:0.8rem; font-weight:500;"
    )
    st.markdown(
        f"""
        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center;
                    max-width:720px; margin:0 auto 1.75rem auto;">
          <span style="{_pill}">✦ Auto Data Cleaning</span>
          <span style="{_pill}">✦ 10 Business Domains</span>
          <span style="{_pill}">✦ AI Executive Summary</span>
          <span style="{_pill}">✦ NL→SQL Copilot</span>
          <span style="{_pill}">✦ PDF · PPTX · Excel Export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_uploaded, filename = render_uploader()
    if df_uploaded is not None:
        st.session_state.raw_df          = df_uploaded
        st.session_state.filename        = filename
        st.session_state.processing_done = False
        st.rerun()
    else:
        # ── Domain support grid (only while waiting for upload) ───────────────
        st.markdown(
            """
            <p style="text-align:center; color:#9CA3AF; font-size:0.78rem; margin:1.75rem 0 0.75rem 0;">
              Supports 10 business domains — auto-detected on upload
            </p>
            """,
            unsafe_allow_html=True,
        )

        DOMAIN_GRID = [
            ("📈", "Sales", "Revenue · Orders · AOV"),
            ("🏥", "Healthcare", "LOS · Readmission · Recovery"),
            ("💰", "Finance", "P&L · Cashflow · Variance"),
            ("👥", "HR", "Headcount · Attrition · Tenure"),
            ("🚚", "Logistics", "On-time · Routes · Cost/km"),
            ("🛒", "E-commerce", "GMV · Returns · Top SKUs"),
            ("📣", "Marketing", "CAC · ROAS · Conversion"),
            ("🏪", "Retail", "Foot traffic · Basket · Margin"),
            ("⚙️", "Operations", "Throughput · Downtime · OEE"),
            ("📋", "General", "Auto KPIs · Any dataset"),
        ]

        def _domain_cell(icon: str, name: str, metrics: str) -> str:
            return (
                "<div style='background:#1A1D2E; border:1px solid rgba(255,255,255,0.06); "
                "border-radius:10px; padding:0.75rem 0.5rem; height:100%;'>"
                f"<div style='font-size:1.5rem; text-align:center;'>{icon}</div>"
                f"<div style='color:#FFFFFF; font-size:0.8rem; font-weight:700; "
                f"text-align:center; margin-top:0.25rem;'>{name}</div>"
                f"<div style='color:#9CA3AF; font-size:0.65rem; text-align:center; "
                f"margin-top:0.2rem;'>{metrics}</div></div>"
            )

        for start in (0, 5):
            cols = st.columns(5)
            for col, (icon, name, metrics) in zip(cols, DOMAIN_GRID[start:start + 5]):
                with col:
                    st.markdown(_domain_cell(icon, name, metrics), unsafe_allow_html=True)
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

# When filters are active, recompute the filter-sensitive (deterministic) outputs
# so KPIs, charts, analytics, and category visuals reflect the filtered data
# across every tab. AI narratives (summary/story) remain dataset-level.
if sidebar_cfg["filters"]:
    _filter_sig = json.dumps(
        {"f": {k: str(v) for k, v in sidebar_cfg["filters"].items()},
         "d": st.session_state.domain_key,
         "n": int(len(filtered_df))},
        sort_keys=True,
    )
    _filtered = compute_filtered_outputs(filtered_df, domain_cfg, _filter_sig)
    kpis               = _filtered["kpis"]
    charts             = _filtered["charts"]
    analytics_report   = _filtered["analytics_report"]
    category_analytics = _filtered["category_analytics"]
    st.sidebar.caption(f"🔎 Filters active · {len(filtered_df):,} of {len(st.session_state.cleaned_df):,} rows")

# ── Tab dispatch ──────────────────────────────────────────────────────────────
if active_tab == "dashboard":
    # Expensive outputs are generated lazily, only when the Dashboard is viewed.
    ai_summary         = ensure_ai_summary()
    anomaly_narrations = ensure_anomaly_narrations()
    forecasts          = ensure_forecasts()
    tab_dashboard.render(
        filtered_df, domain_cfg, kpis, charts, ai_summary,
        analytics_report, anomaly_narrations, forecasts,
        data_quality_report, data_understanding_report,
        svcs["column_insight"],
    )

elif active_tab == "category":
    if not sidebar_cfg["filters"]:
        category_analytics = ensure_category_analytics()
    tab_category.render(category_analytics)

elif active_tab == "deep_analysis":
    tab_deep.render(
        filtered_df, domain_cfg, cleaning_report,
        data_understanding_report, svcs["chart"],
    )

elif active_tab == "data_story":
    story_narrative = ensure_story_narrative()
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
    ai_summary = ensure_ai_summary()
    tab_export.render(
        filtered_df, domain_cfg, kpis, charts, ai_summary,
        svcs["export"], svcs["session"],
    )
