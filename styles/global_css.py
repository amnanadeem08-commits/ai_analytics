"""
styles/global_css.py — Global CSS for AI Analytics Assistant.

Dark "command-center" design system: deep navy canvas, indigo glow accents,
glassmorphism surfaces. Call inject() once at app startup (after set_page_config).
"""

import streamlit as st

_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-0: #070A14;
        --bg-1: #0A0E1A;
        --bg-2: #111729;
        --surface: rgba(255,255,255,0.035);
        --surface-2: rgba(255,255,255,0.06);
        --border: rgba(255,255,255,0.08);
        --border-strong: rgba(255,255,255,0.14);
        --txt: #E5E7EB;
        --txt-muted: #9CA3AF;
        --txt-faint: #6B7280;
        --accent: #6366F1;
        --accent-2: #818CF8;
        --violet: #A855F7;
        --glow: rgba(99,102,241,0.35);
        --success: #34D399;
        --warning: #FBBF24;
        --error: #F87171;
        --mono: 'JetBrains Mono', ui-monospace, 'Consolas', monospace;
    }

    * { box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: var(--txt);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* ── App canvas: navy base + ambient glow ── */
    .stApp {
        background:
            radial-gradient(1100px 700px at 12% -8%, rgba(99,102,241,0.16) 0%, transparent 55%),
            radial-gradient(900px 600px at 100% 0%, rgba(168,85,247,0.12) 0%, transparent 50%),
            radial-gradient(800px 700px at 50% 120%, rgba(56,189,248,0.08) 0%, transparent 55%),
            linear-gradient(180deg, var(--bg-1) 0%, var(--bg-0) 100%);
        background-attachment: fixed;
        color: var(--txt);
    }

    /* ── Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    .block-container { padding-top: 2.2rem; }

    /* ── Top gradient bar ── */
    .stApp::before {
        content: '';
        display: block;
        height: 3px;
        background: linear-gradient(90deg, #6366F1 0%, #A855F7 50%, #38BDF8 100%);
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        box-shadow: 0 0 18px rgba(99,102,241,0.6);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar             { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track       { background: transparent; }
    ::-webkit-scrollbar-thumb       { background: rgba(255,255,255,0.12); border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }

    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6 { color: #F3F4F6 !important; letter-spacing: -0.02em; }
    p, span, label, li, .stMarkdown { color: var(--txt); }
    a { color: var(--accent-2); }
    code { color: #C7D2FE; background: rgba(99,102,241,0.12); border-radius: 6px; padding: 1px 6px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17,23,41,0.92) 0%, rgba(10,14,26,0.92) 100%);
        border-right: 1px solid var(--border);
        backdrop-filter: blur(12px);
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F3F4F6;
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
        background: linear-gradient(90deg, var(--border-strong) 0%, transparent 100%);
        margin-left: 0.75rem;
    }
    .section-subtitle {
        font-size: 0.875rem;
        color: var(--txt-muted);
        margin-top: -0.5rem;
        margin-bottom: 1.25rem;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.875rem;
        color: var(--txt-muted);
        transition: all 0.18s ease-in-out;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.9) 0%, rgba(124,58,237,0.9) 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 16px var(--glow);
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        color: #F3F4F6;
        background: var(--surface-2);
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { background: transparent; }

    /* ── Chart containers ── */
    [data-testid="stPlotlyChart"]       { min-height: 400px; border-radius: 14px; }
    [data-testid="stPlotlyChart"] > div { min-height: 400px; }

    .chart-wrapper {
        background: var(--surface);
        border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease-in-out;
        backdrop-filter: blur(10px);
    }
    .chart-wrapper:hover { border-color: var(--border-strong); box-shadow: 0 12px 40px rgba(0,0,0,0.45); }
    .chart-wrapper-title {
        font-size: 1rem;
        font-weight: 600;
        color: #E5E7EB;
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
        transition: all 0.18s ease-in-out;
        border: 1px solid var(--border);
        font-size: 0.875rem;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #7C3AED 100%);
        color: white;
        border-color: transparent;
        box-shadow: 0 4px 18px var(--glow);
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 26px rgba(99,102,241,0.55);
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: var(--surface-2);
        color: var(--txt);
        border-color: var(--border);
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(99,102,241,0.16);
        border-color: var(--accent);
        color: #FFFFFF;
    }
    .stDownloadButton > button {
        background: var(--surface-2);
        color: var(--txt);
        border: 1px solid var(--border);
        border-radius: 10px;
        font-weight: 600;
    }
    .stDownloadButton > button:hover { border-color: var(--accent); color: #FFF; }

    /* ── Inputs (text, number, select, multiselect, date) ── */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--txt) !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--glow) !important;
    }
    [data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.9), rgba(124,58,237,0.9)) !important;
        border-radius: 8px !important;
    }
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="menu"] {
        background: #131A2E !important;
        border: 1px solid var(--border) !important;
    }

    /* ── DataFrames / tables ── */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        background: var(--surface);
    }
    [data-testid="stDataFrame"] * { color: var(--txt); }

    /* ── Metric widget ── */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricValue"] { font-family: var(--mono); color: #F3F4F6; }
    [data-testid="stMetricLabel"] { color: var(--txt-muted); }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] summary { color: var(--txt); }

    /* ── Native alert banners (st.info/success/warning/error) ── */
    [data-testid="stAlert"] {
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 12px;
        color: var(--txt);
    }

    /* ── File uploader ── */
    [data-testid="stFileUploaderDropzone"] {
        background: var(--surface);
        border: 1.5px dashed var(--border-strong);
        border-radius: 14px;
        color: var(--txt-muted);
    }
    [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent); }

    /* ── Caption / small text ── */
    [data-testid="stCaptionContainer"], .stCaption { color: var(--txt-faint) !important; }

    /* ── Animations ── */
    @keyframes pulse    { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    @keyframes glowPulse{ 0%,100% { box-shadow: 0 0 8px var(--glow); } 50% { box-shadow: 0 0 18px var(--glow); } }
    @keyframes slideUp  {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0);    }
    }
    .loading          { animation: pulse 2s ease-in-out infinite; }
    .animate-slide-up { animation: slideUp 0.4s ease-out; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .section-header { font-size: 1.1rem; }
    }
</style>
"""


def inject() -> None:
    """Inject global CSS into the Streamlit page. Call once after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)
