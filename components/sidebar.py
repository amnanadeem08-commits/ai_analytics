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
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    .sidebar-header {
        padding: 1.25rem 1rem 1rem;
        border-bottom: 1px solid #F3F4F6;
        margin-bottom: 0.5rem;
    }

    .sidebar-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #5046E4;
        letter-spacing: 0;
        line-height: 1.2;
    }

    .sidebar-version {
        font-size: 0.68rem;
        color: #9CA3AF;
        margin-top: 0.25rem;
    }

    .sidebar-section-label {
        font-size: 0.68rem;
        font-weight: 800;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.65rem 0 0.3rem;
    }

    .auto-detect-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        background: #D1FAE5;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 650;
        color: #065F46;
        margin: 0.25rem 0 0.4rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        justify-content: flex-start;
        border-radius: 10px;
        padding: 0.72rem 0.9rem;
        margin: 0.08rem 0;
        font-size: 0.86rem;
        font-weight: 650;
        border: 1px solid transparent;
        box-shadow: none;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: #FFFFFF;
        color: #4B5563;
        border-color: transparent;
    }

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: #F5F3FF;
        color: #5046E4;
        border-color: #EDE9FE;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        color: #FFFFFF;
        border-color: transparent;
        box-shadow: 0 4px 12px rgba(80, 70, 228, 0.35);
    }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div,
    [data-testid="stSidebar"] .stDateInput > div > div {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
</style>
"""


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
            f"""
            <div class="sidebar-header">
                <div class="sidebar-title">AI Analytics<br>Platform</div>
                <div class="sidebar-version">v{APP_VERSION} | Streamlit + Plotly</div>
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
                f'<div class="auto-detect-badge">Auto-detected: {detected_label}</div>',
                unsafe_allow_html=True,
            )

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

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        active_route = _valid_route()

        for item in NAVIGATION_ITEMS:
            is_active = item["route"] == active_route
            label = f'{item["icon"]}  {item["label"]}'
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