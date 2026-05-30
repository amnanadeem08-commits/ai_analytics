"""
sidebar.py - Streamlit-native sidebar navigation and filters.

The previous sidebar rendered custom HTML with JavaScript click handlers. Streamlit
does not wire those handlers as widget events, which made the menu look clickable
while the active route stayed stuck. This version uses native buttons for reliable
routing and keeps the same render_sidebar/apply_filters API used by app.py.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import APP_VERSION, DOMAINS
from services.domain_service import DomainService


NAVIGATION_ITEMS = [
    {"route": "dashboard", "icon": "📈", "label": "Visual Graphs", "description": "Overview, KPIs, and smart charts"},
    {"route": "category", "icon": "📊", "label": "Categorical Visuals", "description": "Category-wise business breakdowns"},
    {"route": "deep_analysis", "icon": "🔍", "label": "Deep Analysis", "description": "Statistics, correlations, and custom charts"},
    {"route": "data_story", "icon": "📖", "label": "Data Story", "description": "AI narrative and chart story"},
    {"route": "business_insights", "icon": "🧠", "label": "Business Insights", "description": "Automated findings and recommendations"},
    {"route": "compare", "icon": "⚖️", "label": "Compare", "description": "Compare two datasets"},
    {"route": "copilot", "icon": "🤖", "label": "Data Copilot", "description": "Ask questions about your data"},
    {"route": "export", "icon": "📤", "label": "Export", "description": "Download reports and cleaned data"},
]


SIDEBAR_CSS = """
<style>
    .sidebar-header {
        padding: 0.5rem 0.25rem 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .sidebar-logo-mark {
        width: 38px; height: 38px;
        border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #6C63FF 0%, #A855F7 100%);
        box-shadow: 0 0 18px rgba(108,99,255,0.55);
        flex-shrink: 0;
    }

    .sidebar-title {
        font-size: 1.02rem;
        font-weight: 800;
        color: #F3F4F6;
        letter-spacing: -0.01em;
        line-height: 1.15;
    }

    .sidebar-version {
        font-size: 0.66rem;
        color: #6B7280;
        margin-top: 0.15rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .sidebar-section-label {
        font-size: 0.66rem;
        font-weight: 800;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        padding: 0.7rem 0 0.35rem;
    }

    .auto-detect-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        background: rgba(52,211,153,0.14);
        border: 1px solid rgba(52,211,153,0.3);
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 650;
        color: #34D399;
        margin: 0.25rem 0 0.4rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        justify-content: flex-start;
        border-radius: 10px;
        padding: 0.66rem 0.85rem;
        margin: 0.1rem 0;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid transparent;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: transparent;
        color: #9CA3AF;
        border-color: transparent;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.05);
        color: #E5E7EB;
        border-color: rgba(255,255,255,0.1);
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.95) 0%, rgba(124,58,237,0.95) 100%);
        color: #FFFFFF;
        border-color: transparent;
        box-shadow: 0 4px 16px rgba(99,102,241,0.4);
    }

    /* AI copilot status card */
    .copilot-status {
        margin-top: 0.9rem;
        padding: 0.85rem 0.9rem;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.28);
        border-radius: 12px;
    }
    .copilot-status-title {
        display: flex; align-items: center; gap: 6px;
        font-size: 0.74rem; font-weight: 800;
        color: #C7D2FE; text-transform: uppercase; letter-spacing: 0.08em;
    }
    .copilot-status-title .dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: #34D399; box-shadow: 0 0 8px #34D399;
        animation: pulse 2s ease-in-out infinite;
    }
    .copilot-status-desc {
        font-size: 0.72rem; color: #9CA3AF; margin-top: 0.35rem; line-height: 1.45;
    }

    /* Smart Intelligence Layer badges */
    .intel-panel {
        margin: 0.45rem 0 0.2rem;
        padding: 0.6rem 0.75rem;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
    }
    .intel-row {
        display: flex; align-items: center; justify-content: space-between;
        gap: 0.5rem; padding: 0.12rem 0;
    }
    .intel-key {
        font-size: 0.66rem; font-weight: 700; color: #6B7280;
        text-transform: uppercase; letter-spacing: 0.06em;
    }
    .intel-val {
        font-size: 0.74rem; font-weight: 700; color: #C7D2FE; text-align: right;
    }
    .intel-conf { font-family: 'JetBrains Mono', monospace; }
    .intel-bar-track {
        height: 5px; background: rgba(255,255,255,0.1); border-radius: 3px;
        overflow: hidden; margin-top: 0.35rem;
    }
    .intel-bar-fill {
        height: 100%; border-radius: 3px;
        background: linear-gradient(90deg, #6366F1, #A855F7);
    }
</style>
"""


def _render_intelligence_badges() -> None:
    """
    Smart Intelligence Layer badges (additive, read-only).
    Shows Detected Domain, Confidence, and active Insight Mode from session
    state (populated by the pipeline). Falls back gracefully if absent.
    """
    label = st.session_state.get("detected_domain_label", "General Analytics")
    confidence = float(st.session_state.get("detected_confidence", 0.0) or 0.0)
    mode = st.session_state.get("insight_mode", "General (all insight types enabled)")
    pct = max(0, min(100, int(round(confidence))))

    st.markdown(
        f"""
        <div class="intel-panel">
            <div class="intel-row">
                <span class="intel-key">Detected Domain</span>
                <span class="intel-val">{label}</span>
            </div>
            <div class="intel-row">
                <span class="intel-key">Confidence</span>
                <span class="intel-val intel-conf">{pct}%</span>
            </div>
            <div class="intel-bar-track"><div class="intel-bar-fill" style="width:{pct}%"></div></div>
            <div class="intel-row" style="margin-top:0.4rem">
                <span class="intel-key">Insight Mode Active</span>
            </div>
            <div class="intel-val" style="text-align:left;color:#9AA4BC;font-weight:600;font-size:0.72rem;line-height:1.35">
                {mode}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _valid_route() -> str:
    valid_routes = {item["route"] for item in NAVIGATION_ITEMS}
    if "active_route" not in st.session_state or st.session_state.active_route not in valid_routes:
        st.session_state.active_route = NAVIGATION_ITEMS[0]["route"]
    return st.session_state.active_route


def render_sidebar(df: pd.DataFrame | None = None) -> dict:
    """
    Render sidebar controls and return domain, filter, and route config.
    """
    domain_svc = DomainService()
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] .stButton > button[kind="primary"],
            [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
            [data-testid="stSidebar"] .stButton > button[kind="primary"]:focus,
            [data-testid="stSidebar"] .stButton > button[kind="primary"]:active {
                background: linear-gradient(135deg, #6C63FF 0%, #7C3AED 100%) !important;
                color: #FFFFFF !important;
                border: 1px solid rgba(108,99,255,0.55) !important;
                box-shadow: 0 4px 16px rgba(108,99,255,0.40) !important;
            }
            [data-testid="stSidebar"] .stButton > button:focus,
            [data-testid="stSidebar"] .stButton > button:focus:not(:active) {
                outline: none !important;
                border-color: rgba(108,99,255,0.45) !important;
                box-shadow: 0 4px 16px rgba(108,99,255,0.30) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-header">
                <div class="sidebar-logo-mark">📊</div>
                <div>
                    <div class="sidebar-title">AI Analytics</div>
                    <div class="sidebar-version">v{APP_VERSION} · Streamlit + Plotly</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Business Domain</div>', unsafe_allow_html=True)
        domain_options = list(DOMAINS.keys())
        domain_labels = list(DOMAINS.values())

        auto_key = "generic"
        if df is not None:
            auto_key = domain_svc.auto_detect(df)
            detected_label = DOMAINS.get(auto_key, "General / Other")
            st.markdown(
                f'<div class="auto-detect-badge">⬡ Auto-detected: {detected_label}</div>',
                unsafe_allow_html=True,
            )
            _render_intelligence_badges()

        default_idx = domain_options.index(auto_key) if auto_key in domain_options else 0
        selected_label = st.selectbox(
            "Select domain",
            options=domain_labels,
            index=default_idx,
            label_visibility="collapsed",
            key="domain_selector",
        )
        domain_key = domain_options[domain_labels.index(selected_label)]
        if domain_key == "auto":
            domain_key = auto_key

        if df is not None and not df.empty:
            fname = st.session_state.get("filename", "Uploaded file")
            fname_short = fname[:22] + "…" if len(fname) > 22 else fname
            nrows, ncols = df.shape
            st.markdown(
                f"""
                <div style="margin:0.55rem 0 0.2rem; padding:0.7rem 0.8rem;
                            background:rgba(255,255,255,0.04);
                            border:1px solid rgba(255,255,255,0.08); border-radius:10px;">
                    <div style="display:flex; align-items:center; gap:6px; font-size:0.8rem;
                                font-weight:700; color:#E5E7EB; margin-bottom:0.45rem;
                                overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                        <span>📄</span><span>{fname_short}</span>
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
                        <span style="font-size:0.68rem; color:#9CA3AF;
                                     background:rgba(255,255,255,0.05); padding:2px 8px;
                                     border-radius:6px;">🗂 {nrows:,} rows</span>
                        <span style="font-size:0.68rem; color:#9CA3AF;
                                     background:rgba(255,255,255,0.05); padding:2px 8px;
                                     border-radius:6px;">📐 {ncols} cols</span>
                        <span style="font-size:0.68rem; color:#34D399;
                                     background:rgba(52,211,153,0.12); padding:2px 8px;
                                     border-radius:6px;">● Ready</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        active_route = _valid_route()

        for idx, item in enumerate(NAVIGATION_ITEMS, start=1):
            is_active = item["route"] == active_route
            label = f'{idx:02d}   {item["icon"]}  {item["label"]}'
            clicked = st.button(
                label,
                key=f"nav_{item['route']}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
                help=item["description"],
            )
            if clicked and not is_active:
                st.session_state.active_route = item["route"]
                st.rerun()

        st.markdown(
            """
            <div class="copilot-status">
                <div class="copilot-status-title"><span class="dot"></span>AI Copilot Active</div>
                <div class="copilot-status-desc">
                    Ask questions, run SQL, or generate insights in the Data Copilot tab.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        filters = {}
        if df is not None and not df.empty:
            st.markdown('<div class="sidebar-section-label">Filters</div>', unsafe_allow_html=True)

            cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
            date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

            for col in cat_cols[:4]:
                unique_vals = df[col].dropna().unique().tolist()
                if 2 <= len(unique_vals) <= 50:
                    selected = st.multiselect(
                        col.replace("_", " ").title(),
                        options=unique_vals,
                        default=[],
                        key=f"filter_{col}",
                    )
                    if selected:
                        filters[col] = selected

            if date_cols:
                dcol = date_cols[0]
                min_d = df[dcol].min().date()
                max_d = df[dcol].max().date()
                if min_d < max_d:
                    date_range = st.date_input(
                        "Date Range",
                        value=(min_d, max_d),
                        min_value=min_d,
                        max_value=max_d,
                        key="date_filter",
                    )
                    if isinstance(date_range, tuple) and len(date_range) == 2:
                        filters["__date__"] = (date_range[0], date_range[1], dcol)

        active_item = next(item for item in NAVIGATION_ITEMS if item["route"] == st.session_state.active_route)

    return {
        "domain_key": domain_key,
        "filters": filters,
        "active_tab": active_item["route"],
        "active_label": active_item["label"],
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filters to the DataFrame."""
    df = df.copy()
    for key, val in filters.items():
        if key == "__date__":
            start, end, col = val
            df = df[(df[col] >= pd.Timestamp(start)) & (df[col] <= pd.Timestamp(end))]
        elif key in df.columns and val:
            df = df[df[key].isin(val)]
    return df