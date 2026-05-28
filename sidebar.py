"""
services/sidebar.py → components/sidebar.py — Sidebar renderer.

Fix applied:
  - Navigation labels were doubled ("Chart Visual Graphs", "Compare Compare",
    "Export Export") because the tab key was being appended to the display label.
  - Labels are now defined once in _TABS and used cleanly.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from config import DOMAINS

# ── Tab registry — single source of truth for labels ─────────────────────────
_TABS: list[dict] = [
    {"key": "dashboard",          "icon": "📈", "label": "Dashboard"},
    {"key": "category",           "icon": "📊", "label": "Category Analytics"},
    {"key": "deep_analysis",      "icon": "🔍", "label": "Deep Analysis"},
    {"key": "data_story",         "icon": "📖", "label": "Data Story"},
    {"key": "business_insights",  "icon": "🧠", "label": "Business Insights"},
    {"key": "compare",            "icon": "⚖️", "label": "Compare"},
    {"key": "copilot",            "icon": "🤖", "label": "AI Data Copilot"},
    {"key": "export",             "icon": "📤", "label": "Export"},
]


def render_sidebar(df: pd.DataFrame | None) -> dict:
    """
    Render the sidebar and return a dict with:
      active_tab  — key of the selected tab
      domain_key  — selected domain key
      filters     — dict of active filter values
    """
    with st.sidebar:
        # App branding
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem">
                <div style="font-size:1.1rem;font-weight:800;color:#5046E4">AI Analytics Platform</div>
                <div style="font-size:0.75rem;color:#9CA3AF">v3.0.0 | Streamlit + Plotly</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Domain selector ───────────────────────────────────────────────────
        st.markdown("**BUSINESS DOMAIN**")
        current_domain = st.session_state.get("domain_key", "auto")

        # Auto-detected badge
        if current_domain and current_domain != "auto":
            domain_label = DOMAINS.get(current_domain, current_domain)
            st.markdown(
                f'<div style="background:#D1FAE5;color:#065F46;padding:4px 10px;'
                f'border-radius:20px;font-size:0.75rem;font-weight:600;display:inline-block;'
                f'margin-bottom:0.5rem">Auto-detected: {domain_label}</div>',
                unsafe_allow_html=True,
            )

        domain_options = list(DOMAINS.keys())
        domain_labels  = list(DOMAINS.values())
        current_idx    = domain_options.index(current_domain) if current_domain in domain_options else 0

        selected_idx = st.selectbox(
            "domain_selector",
            options=range(len(domain_options)),
            format_func=lambda i: domain_labels[i],
            index=current_idx,
            label_visibility="collapsed",
        )
        selected_domain_key = domain_options[selected_idx]

        st.divider()

        # ── Navigation ────────────────────────────────────────────────────────
        st.markdown("**NAVIGATION**")

        # Persist active tab in session state
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "dashboard"

        for tab in _TABS:
            is_active = st.session_state.active_tab == tab["key"]
            # Use primary style for active tab
            if st.button(
                f"{tab['icon']}  {tab['label']}",
                key=f"nav_{tab['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_tab = tab["key"]
                st.rerun()

        st.divider()

        # ── Filters (only shown when data is loaded) ──────────────────────────
        filters: dict = {}
        if df is not None and not df.empty:
            st.markdown("**FILTERS**")

            # Date range filter
            date_cols = df.select_dtypes(include=["datetime64", "datetime"]).columns.tolist()
            if not date_cols:
                # Try to find columns that look like dates
                for col in df.columns:
                    if "date" in col.lower() or "time" in col.lower():
                        try:
                            pd.to_datetime(df[col], errors="raise")
                            date_cols.append(col)
                        except Exception:
                            pass

            if date_cols:
                date_col = date_cols[0]
                try:
                    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
                    if len(dates):
                        min_date = dates.min().date()
                        max_date = dates.max().date()
                        date_range = st.date_input(
                            "Date Range",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date,
                            key="filter_date_range",
                        )
                        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                            filters["date_range"] = {"col": date_col, "range": date_range}
                except Exception:
                    pass

            # Categorical filters (top 2 low-cardinality columns)
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            cat_cols = [c for c in cat_cols if 2 <= df[c].nunique() <= 30][:2]
            for col in cat_cols:
                options = sorted(df[col].dropna().unique().tolist())
                selected = st.multiselect(
                    col.replace("_", " ").title(),
                    options=options,
                    default=[],
                    key=f"filter_{col}",
                )
                if selected:
                    filters[col] = selected

        st.divider()
        st.markdown(
            '<div style="font-size:0.7rem;color:#9CA3AF;text-align:center">'
            'AI Analytics Platform · Built with Streamlit</div>',
            unsafe_allow_html=True,
        )

    return {
        "active_tab": st.session_state.active_tab,
        "domain_key": selected_domain_key,
        "filters":    filters,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filters to the cleaned DataFrame."""
    if df is None or df.empty or not filters:
        return df

    result = df.copy()

    # Date range
    if "date_range" in filters:
        info    = filters["date_range"]
        col     = info["col"]
        start, end = info["range"]
        try:
            result[col] = pd.to_datetime(result[col], errors="coerce")
            result = result[
                (result[col].dt.date >= start) &
                (result[col].dt.date <= end)
            ]
        except Exception as exc:
            logger.warning("Date filter failed: %s", exc)

    # Categorical multiselect filters
    for col, values in filters.items():
        if col == "date_range":
            continue
        if col in result.columns and values:
            result = result[result[col].isin(values)]

    return result if not result.empty else df
