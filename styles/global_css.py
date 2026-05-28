"""
styles/global_css.py — Global CSS for AI Analytics Assistant.

Extracted from app.py to keep the entry point clean.
Call inject() once at app startup (after st.set_page_config).
"""

import streamlit as st

_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    * { margin: 0; padding: 0; box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #111827;
        background: #F9FAFB;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ── Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    /* ── Top gradient bar ── */
    .stApp::before {
        content: '';
        display: block;
        height: 4px;
        background: linear-gradient(90deg, #5046E4 0%, #7C3AED 50%, #0E9F6E 100%);
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar              { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track        { background: #F3F4F6; border-radius: 4px; }
    ::-webkit-scrollbar-thumb        { background: #D1D5DB; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover  { background: #9CA3AF; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    /* ── Section headers ── */
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
    .section-header .section-icon { font-size: 1.4rem; }
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

    /* ── Tabs ── */
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
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: #374151;
        background: #E5E7EB;
    }

    /* ── Chart containers ── */
    [data-testid="stPlotlyChart"]       { min-height: 400px; border-radius: 12px; }
    [data-testid="stPlotlyChart"] > div { min-height: 400px; }

    .chart-wrapper {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    .chart-wrapper:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .chart-wrapper-title {
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── Buttons ── */
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
        box-shadow: 0 2px 8px rgba(80,70,228,0.3);
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 16px rgba(80,70,228,0.4);
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

    /* ── Animations ── */
    @keyframes pulse    { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    @keyframes shimmer  { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    @keyframes slideUp  {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    .loading           { animation: pulse 2s ease-in-out infinite; }
    .animate-slide-up  { animation: slideUp 0.4s ease-out; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .section-header { font-size: 1.1rem; }
    }
</style>
"""


def inject() -> None:
    """Inject global CSS into the Streamlit page. Call once after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)