"""
kpi_cards.py — Premium KPI metric cards for the AI Analytics dashboard.

Displays value, label, trend indicators, and status badges with modern styling
inspired by Power BI, Tableau, and modern SaaS analytics tools.
"""

import streamlit as st
from services.kpi_service import KPIResult


# ─── KPI Card Icons ────────────────────────────────────────────────────────────

KPI_ICONS = {
    "revenue": "💰",
    "sales": "📈",
    "customers": "👥",
    "users": "👤",
    "orders": "🛒",
    "products": "📦",
    "profit": "💎",
    "margin": "📊",
    "growth": "🚀",
    "churn": "⚠️",
    "retention": "🔄",
    "conversion": "🎯",
    "avg": "📋",
    "average": "📋",
    "total": "📝",
    "count": "🔢",
    "rate": "📉",
    "score": "⭐",
    "quality": "✅",
    "default": "📊",
}


def _get_icon_for_kpi(name: str) -> str:
    """Get an appropriate icon for a KPI based on its name."""
    name_lower = name.lower().replace("_", " ")
    for key, icon in KPI_ICONS.items():
        if key in name_lower:
            return icon
    return KPI_ICONS["default"]


def _get_trend_direction(kpi: KPIResult) -> str:
    """Determine trend direction based on delta percentage."""
    if kpi.delta_pct is None:
        return "flat"
    if kpi.delta_pct > 2:
        return "up"
    if kpi.delta_pct < -2:
        return "down"
    return "flat"


def _get_card_type(kpi: KPIResult) -> str:
    """Determine card type for color coding based on KPI nature."""
    name_lower = kpi.name.lower()
    if any(word in name_lower for word in ["error", "churn", "loss", "defect", "complaint"]):
        # Negative metrics - green is good (low values)
        return "inverse"
    return "normal"


KPI_CARD_CSS = f"""
<style>
    /* Premium KPI Card Container */
    .kpi-card-wrapper {{
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        padding: 1.25rem 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease-in-out;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    
    .kpi-card-wrapper:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: #C7D2FE;
    }}
    
    /* Accent bar on the left */
    .kpi-card-wrapper::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #5046E4 0%, #7C3AED 100%);
        border-radius: 0 2px 2px 0;
    }}
    
    .kpi-card-wrapper.success::before {{
        background: linear-gradient(180deg, #0E9F6E 0%, #059669 100%);
    }}
    
    .kpi-card-wrapper.warning::before {{
        background: linear-gradient(180deg, #EA580C 0%, #E3A008 100%);
    }}
    
    .kpi-card-wrapper.error::before {{
        background: linear-gradient(180deg, #DC2626 0%, #E74694 100%);
    }}
    
    /* Card header with label and icon */
    .kpi-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        line-height: 1.2;
    }}
    
    .kpi-icon-wrapper {{
        width: 32px;
        height: 32px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        flex-shrink: 0;
    }}
    
    .kpi-card-wrapper.success .kpi-icon-wrapper {{
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
    }}
    
    .kpi-card-wrapper.warning .kpi-icon-wrapper {{
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    }}
    
    .kpi-card-wrapper.error .kpi-icon-wrapper {{
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
    }}
    
    /* KPI Value */
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin: 0.25rem 0;
    }}
    
    /* Trend indicator */
    .kpi-trend {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: auto;
        padding-top: 0.5rem;
    }}
    
    .kpi-trend-badge {{
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        line-height: 1;
    }}
    
    .kpi-trend-badge.up {{
        background: #D1FAE5;
        color: #065F46;
    }}
    
    .kpi-trend-badge.down {{
        background: #FEE2E2;
        color: #991B1B;
    }}
    
    .kpi-trend-badge.flat {{
        background: #F3F4F6;
        color: #6B7280;
    }}
    
    .kpi-trend-label {{
        font-size: 0.7rem;
        color: #9CA3AF;
        margin-left: 4px;
    }}
    
    /* Sparkline placeholder */
    .kpi-sparkline {{
        height: 20px;
        margin-top: 0.5rem;
        opacity: 0.3;
    }}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .kpi-value {{
            font-size: 1.5rem;
        }}
        .kpi-card-wrapper {{
            padding: 1rem 1.25rem;
        }}
    }}
</style>
"""


def render_kpi_card(kpi: KPIResult, key: str = "") -> None:
    """Render a single premium KPI card."""
    icon = _get_icon_for_kpi(kpi.name)
    trend_direction = _get_trend_direction(kpi)
    card_type = _get_card_type(kpi)
    
    # Determine card class for accent color
    card_class = ""
    if trend_direction == "up" and card_type == "normal":
        card_class = "success"
    elif trend_direction == "down" and card_type == "normal":
        card_class = "error"
    elif trend_direction == "down" and card_type == "inverse":
        card_class = "success"  # Low error rate is good
    elif trend_direction == "up" and card_type == "inverse":
        card_class = "error"  # High error rate is bad
    
    # Build trend HTML
    trend_html = ""
    if kpi.delta_pct is not None:
        direction_symbol = "↑" if trend_direction == "up" else ("↓" if trend_direction == "down" else "→")
        trend_html = f"""
        <div class="kpi-trend">
            <span class="kpi-trend-badge {trend_direction}">
                {direction_symbol} {abs(kpi.delta_pct):.1f}%
            </span>
            <span class="kpi-trend-label">vs prior period</span>
        </div>
        """
    
    st.markdown(
        f"""
        <div class="kpi-card-wrapper {card_class}">
            <div class="kpi-card-header">
                <span class="kpi-label">{kpi.name}</span>
                <div class="kpi-icon-wrapper">{icon}</div>
            </div>
            <div class="kpi-value">{kpi.formatted}</div>
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(kpis: list[KPIResult], columns: int = 4) -> None:
    """Render KPI cards in a responsive grid layout."""
    st.markdown(KPI_CARD_CSS, unsafe_allow_html=True)
    
    if not kpis:
        # Empty state
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 3rem 2rem;
                background: #F9FAFB;
                border-radius: 16px;
                border: 2px dashed #E5E7EB;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
                <div style="font-size: 1rem; font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                    No Metrics Available
                </div>
                <div style="font-size: 0.875rem; color: #6B7280;">
                    Upload data with numeric columns to generate KPIs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    
    # Calculate optimal column count based on number of KPIs
    if len(kpis) <= 2:
        actual_cols = len(kpis)
    elif len(kpis) <= 4:
        actual_cols = min(columns, len(kpis))
    else:
        actual_cols = columns
    
    # Render in rows
    for i in range(0, len(kpis), actual_cols):
        batch = kpis[i : i + actual_cols]
        cols = st.columns(len(batch))
        for col, kpi_item in zip(cols, batch):
            with col:
                render_kpi_card(kpi_item, key=f"kpi_{kpi_item.name}")


def render_kpi_summary_bar(kpis: list[KPIResult]) -> None:
    """Render a compact horizontal summary bar of KPIs."""
    if not kpis:
        return
    
    st.markdown(
        """
        <style>
            .kpi-summary-bar {
                display: flex;
                gap: 1.5rem;
                padding: 1rem 1.5rem;
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                flex-wrap: wrap;
                align-items: center;
            }
            .kpi-summary-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem 1rem;
                background: #F9FAFB;
                border-radius: 10px;
                flex: 1;
                min-width: 180px;
            }
            .kpi-summary-icon {
                width: 36px;
                height: 36px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1rem;
                background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
                flex-shrink: 0;
            }
            .kpi-summary-value {
                font-size: 1.25rem;
                font-weight: 700;
                color: #111827;
                line-height: 1;
            }
            .kpi-summary-label {
                font-size: 0.7rem;
                color: #6B7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-top: 2px;
            }
        </style>
        """
    )
    
    items_html = ""
    for kpi in kpis[:6]:  # Limit to 6 for summary bar
        icon = _get_icon_for_kpi(kpi.name)
        items_html += f"""
        <div class="kpi-summary-item">
            <div class="kpi-summary-icon">{icon}</div>
            <div>
                <div class="kpi-summary-value">{kpi.formatted}</div>
                <div class="kpi-summary-label">{kpi.name}</div>
            </div>
        </div>
        """
    
    st.markdown(
        f"""
        <div class="kpi-summary-bar">
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )