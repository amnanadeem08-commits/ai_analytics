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


KPI_CARD_CSS = """
<style>
    /* Dark glass KPI card */
    .kpi-card-wrapper {
        background: rgba(255,255,255,0.04);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        backdrop-filter: blur(10px);
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease-in-out;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .kpi-card-wrapper::after {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(420px 120px at 0% 0%, rgba(99,102,241,0.14) 0%, transparent 70%);
        pointer-events: none;
    }

    .kpi-card-wrapper:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 40px rgba(0,0,0,0.5);
        border-color: rgba(99,102,241,0.5);
    }

    /* Accent bar on the left */
    .kpi-card-wrapper::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #6366F1 0%, #A855F7 100%);
        box-shadow: 0 0 14px rgba(99,102,241,0.6);
    }
    .kpi-card-wrapper.success::before { background: linear-gradient(180deg, #34D399 0%, #059669 100%); }
    .kpi-card-wrapper.warning::before { background: linear-gradient(180deg, #FBBF24 0%, #EA580C 100%); }
    .kpi-card-wrapper.error::before   { background: linear-gradient(180deg, #F87171 0%, #DC2626 100%); }

    .kpi-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        line-height: 1.2;
    }

    .kpi-icon-wrapper {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        background: rgba(99,102,241,0.16);
        border: 1px solid rgba(99,102,241,0.3);
        flex-shrink: 0;
    }
    .kpi-card-wrapper.success .kpi-icon-wrapper { background: rgba(52,211,153,0.16); border-color: rgba(52,211,153,0.3); }
    .kpi-card-wrapper.warning .kpi-icon-wrapper { background: rgba(251,191,36,0.16); border-color: rgba(251,191,36,0.3); }
    .kpi-card-wrapper.error .kpi-icon-wrapper   { background: rgba(248,113,113,0.16); border-color: rgba(248,113,113,0.3); }

    /* KPI Value — monospace, like the reference */
    .kpi-value {
        font-family: 'JetBrains Mono', ui-monospace, 'Consolas', monospace;
        font-size: 1.9rem;
        font-weight: 700;
        color: #F3F4F6;
        line-height: 1.1;
        letter-spacing: -0.02em;
        margin: 0.25rem 0;
        position: relative;
        z-index: 1;
    }

    .kpi-trend {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: auto;
        padding-top: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .kpi-trend-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        line-height: 1;
    }
    .kpi-trend-badge.up   { background: rgba(52,211,153,0.16); color: #34D399; }
    .kpi-trend-badge.down { background: rgba(248,113,113,0.16); color: #F87171; }
    .kpi-trend-badge.flat { background: rgba(255,255,255,0.08); color: #9CA3AF; }

    .kpi-trend-label {
        font-size: 0.7rem;
        color: #6B7280;
        margin-left: 4px;
    }

    @media (max-width: 768px) {
        .kpi-value { font-size: 1.5rem; }
        .kpi-card-wrapper { padding: 1rem 1.1rem; }
    }
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
                background: rgba(255,255,255,0.03);
                border-radius: 16px;
                border: 2px dashed rgba(255,255,255,0.12);
            ">
                <div style="font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.6;">📊</div>
                <div style="font-size: 1rem; font-weight: 600; color: #E5E7EB; margin-bottom: 0.5rem;">
                    No Metrics Available
                </div>
                <div style="font-size: 0.875rem; color: #9CA3AF;">
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
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.08);
                box-shadow: 0 8px 28px rgba(0,0,0,0.35);
                backdrop-filter: blur(10px);
                flex-wrap: wrap;
                align-items: center;
            }
            .kpi-summary-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem 1rem;
                background: rgba(255,255,255,0.04);
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
                background: rgba(99,102,241,0.16);
                border: 1px solid rgba(99,102,241,0.3);
                flex-shrink: 0;
            }
            .kpi-summary-value {
                font-family: 'JetBrains Mono', ui-monospace, 'Consolas', monospace;
                font-size: 1.25rem;
                font-weight: 700;
                color: #F3F4F6;
                line-height: 1;
            }
            .kpi-summary-label {
                font-size: 0.7rem;
                color: #9CA3AF;
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