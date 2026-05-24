"""
sidebar.py — Modern sidebar navigation with enhanced styling.

Features:
- Premium gradient branding
- Icon-based navigation with hover effects
- Active state highlighting
- Domain selector with auto-detection
- Smart column filters
- Responsive design
"""

import streamlit as st
import pandas as pd
from config import DOMAINS, APP_NAME, APP_VERSION
from services.domain_service import DomainService


# ─── Navigation Configuration ──────────────────────────────────────────────────

NAVIGATION_ITEMS = [
    {"id": "📈 Dashboard", "icon": "📈", "label": "Dashboard", "description": "Overview & KPIs"},
    {"id": "📊 Category Analytics", "icon": "📊", "label": "Category Analytics", "description": "Category breakdowns"},
    {"id": "🔍 Deep Analysis", "icon": "🔍", "label": "Deep Analysis", "description": "Correlations & stats"},
    {"id": "📖 Data Story", "icon": "📖", "label": "Data Story", "description": "AI narrative"},
    {"id": "🧠 Business Insights", "icon": "🧠", "label": "Business Insights", "description": "AI-powered insights"},
    {"id": "⚖️ Compare", "icon": "⚖️", "label": "Compare", "description": "Dataset comparison"},
    {"id": "🤖 Data Copilot", "icon": "🤖", "label": "Data Copilot", "description": "AI chatbot"},
    {"id": "📤 Export", "icon": "📤", "label": "Export", "description": "Download reports"},
]

# ─── Sidebar CSS ───────────────────────────────────────────────────────────────

SIDEBAR_CSS = f"""
<style>
    /* Sidebar container styling */
    [data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }}
    
    /* Sidebar header with gradient branding */
    .sidebar-header {{
        padding: 1.5rem 1.25rem 1.25rem;
        border-bottom: 1px solid #F3F4F6;
        margin-bottom: 0.5rem;
    }}
    
    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    .sidebar-logo-icon {{
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(80, 70, 228, 0.3);
        flex-shrink: 0;
    }}
    
    .sidebar-title {{
        font-size: 1.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }}
    
    .sidebar-version {{
        font-size: 0.65rem;
        color: #9CA3AF;
        margin-top: 2px;
        font-weight: 500;
    }}
    
    /* Navigation section */
    .sidebar-nav-section {{
        padding: 0.75rem 0;
    }}
    
    .sidebar-section-label {{
        font-size: 0.65rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.5rem 1rem 0.375rem;
    }}
    
    /* Navigation items */
    .nav-item {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.7rem 1rem;
        margin: 0.125rem 0.5rem;
        border-radius: 10px;
        color: #4B5563;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
        border: none;
        background: transparent;
        width: calc(100% - 1rem);
        text-align: left;
        text-decoration: none;
    }}
    
    .nav-item:hover {{
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        color: #5046E4;
    }}
    
    .nav-item.active {{
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(80, 70, 228, 0.35);
    }}
    
    .nav-item-icon {{
        font-size: 1.1rem;
        width: 22px;
        text-align: center;
        flex-shrink: 0;
    }}
    
    .nav-item-label {{
        flex: 1;
        font-weight: 600;
    }}
    
    /* Hide default Streamlit sidebar navigation */
    [data-testid="stSidebar"] .stRadio {{
        display: none;
    }}
    
    /* Domain selector styling */
    .sidebar-domain-section {{
        padding: 0.75rem 0;
        border-top: 1px solid #F3F4F6;
        margin-top: 0.5rem;
    }}
    
    .sidebar-domain-label {{
        font-size: 0.65rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.5rem 1rem 0.375rem;
    }}
    
    /* Filter section */
    .sidebar-filter-section {{
        padding: 0.75rem 0;
        border-top: 1px solid #F3F4F6;
    }}
    
    .sidebar-filter-label {{
        font-size: 0.65rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.5rem 1rem 0.375rem;
    }}
    
    /* Sidebar footer */
    .sidebar-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem 1.25rem;
        border-top: 1px solid #F3F4F6;
        background: #FFFFFF;
    }}
    
    .sidebar-footer-text {{
        font-size: 0.7rem;
        color: #9CA3AF;
        text-align: center;
        line-height: 1.5;
    }}
    
    .sidebar-footer-text strong {{
        color: #6B7280;
    }}
    
    /* Override Streamlit selectbox in sidebar */
    [data-testid="stSidebar"] .stSelectbox {{
        margin: 0.5rem 0;
    }}
    
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }}
    
    [data-testid="stSidebar"] .stSelectbox > div > div:hover {{
        border-color: #C7D2FE;
    }}
    
    /* Override Streamlit multiselect in sidebar */
    [data-testid="stSidebar"] .stMultiSelect > div > div {{
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }}
    
    /* Override Streamlit date input in sidebar */
    [data-testid="stSidebar"] .stDateInput > div > div {{
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }}
    
    /* Auto-detect badge */
    .auto-detect-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        border-radius: 6px;
        font-size: 0.65rem;
        font-weight: 600;
        color: #065F46;
        margin: 0.5rem 1rem;
    }}
    
    /* Responsive sidebar adjustments */
    @media (max-width: 768px) {{
        .sidebar-header {{
            padding: 1rem;
        }}
        .sidebar-title {{
            font-size: 0.95rem;
        }}
    }}
</style>
"""


def render_sidebar(df: pd.DataFrame | None = None) -> dict:
    """
    Renders the modern sidebar and returns a config dict:
    {{
        domain_key: str,
        filters: dict,
        active_tab: str,
    }}
    """
    domain_svc = DomainService()
    
    # Inject CSS
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    
    with st.sidebar:
        # ── Brand Header ───────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    <div class="sidebar-logo-icon">📊</div>
                    <div>
                        <div class="sidebar-title">AI Analytics<br>Assistant</div>
                        <div class="sidebar-version">v{APP_VERSION}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # ── Domain Selector ────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-domain-section"><div class="sidebar-domain-label">Business Domain</div></div>', unsafe_allow_html=True)
        
        domain_options = list(DOMAINS.keys())
        domain_labels = list(DOMAINS.values())
        
        # Auto-detect suggestion
        auto_key = "generic"
        if df is not None:
            auto_key = domain_svc.auto_detect(df)
            detected_label = DOMAINS.get(auto_key, "Generic")
            st.markdown(
                f'<div class="auto-detect-badge">💡 Auto-detected: {detected_label}</div>',
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
        
        # ── Navigation ─────────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-nav-section"><div class="sidebar-section-label">Navigation</div></div>', unsafe_allow_html=True)
        
        # Use a hidden radio button for state management
        tab_options = [item["id"] for item in NAVIGATION_ITEMS]
        active_tab = st.radio(
            "Navigation",
            tab_options,
            label_visibility="collapsed",
            index=0,
            key="nav_radio",
        )
        
        # Render custom navigation items
        for item in NAVIGATION_ITEMS:
            is_active = item["id"] == active_tab
            active_class = "active" if is_active else ""
            
            # Create a clickable element that sets the radio value
            st.markdown(
                f"""
                <div class="nav-item {active_class}" 
                     onclick="document.querySelector('input[value="{item['id']}"]').click();">
                    <span class="nav-item-icon">{item["icon"]}</span>
                    <span class="nav-item-label">{item["label"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        # ── Column Filters ─────────────────────────────────────────────────────
        filters = {}
        if df is not None:
            st.markdown('<div class="sidebar-filter-section"><div class="sidebar-filter-label">Filters</div></div>', unsafe_allow_html=True)
            
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
            
            for col in cat_cols[:3]:
                unique_vals = df[col].dropna().unique().tolist()
                if 2 <= len(unique_vals) <= 40:
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
        
        # ── Footer ─────────────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer-text">
                    Powered by <strong>AI Analytics</strong><br>
                    Built with Streamlit & Plotly
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    return {
        "domain_key": domain_key,
        "filters": filters,
        "active_tab": active_tab,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply sidebar filters to the DataFrame."""
    df = df.copy()
    for key, val in filters.items():
        if key == "__date__":
            start, end, col = val
            df = df[
                (df[col] >= pd.Timestamp(start)) &
                (df[col] <= pd.Timestamp(end))
            ]
        elif key in df.columns and val:
            df = df[df[key].isin(val)]
    return df