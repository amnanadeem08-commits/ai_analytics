"""
theme.py — Central theme and styling system for AI Analytics Assistant.

Provides a unified design system with:
- Color palette (primary, secondary, accents, semantic colors)
- Typography scale
- Spacing system
- Shadow definitions
- Border radius system
- Animation definitions
- Pre-built CSS for components
"""

# ─── Color Palette ──────────────────────────────────────────────────────────────

COLORS = {
    # Primary brand colors
    "primary": "#5046E4",
    "primary_light": "#7C6FFF",
    "primary_dark": "#3B31C4",
    "primary_bg": "#F5F3FF",
    
    # Secondary colors
    "secondary": "#7C3AED",
    "secondary_light": "#A78BFA",
    "secondary_dark": "#5B21B6",
    
    # Accent colors
    "accent_green": "#0E9F6E",
    "accent_green_light": "#D1FAE5",
    "accent_yellow": "#E3A008",
    "accent_yellow_light": "#FEF9C3",
    "accent_pink": "#E74694",
    "accent_blue": "#3F83F8",
    "accent_blue_light": "#DBEAFE",
    
    # Semantic colors
    "success": "#059669",
    "success_bg": "#F0FDF4",
    "warning": "#EA580C",
    "warning_bg": "#FFF7ED",
    "error": "#DC2626",
    "error_bg": "#FEF2F2",
    "info": "#2563EB",
    "info_bg": "#DBEAFE",
    
    # Neutral colors
    "gray_50": "#F9FAFB",
    "gray_100": "#F3F4F6",
    "gray_200": "#E5E7EB",
    "gray_300": "#D1D5DB",
    "gray_400": "#9CA3AF",
    "gray_500": "#6B7280",
    "gray_600": "#4B5563",
    "gray_700": "#374151",
    "gray_800": "#1F2937",
    "gray_900": "#111827",
    
    # Backgrounds
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F9FAFB",
    "bg_tertiary": "#F3F4F6",
    
    # Chart colors
    "chart_colors": [
        "#5046E4", "#0E9F6E", "#E3A008", "#E74694",
        "#3F83F8", "#F98080", "#9061F9", "#31C48D",
        "#EA580C", "#06B6D4", "#8B5CF6", "#EC4899",
    ],
}

# ─── Typography ─────────────────────────────────────────────────────────────────

TYPOGRAPHY = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_mono": "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
    
    # Font sizes (in rem)
    "xs": "0.75rem",     # 12px
    "sm": "0.875rem",    # 14px
    "base": "1rem",      # 16px
    "lg": "1.125rem",    # 18px
    "xl": "1.25rem",     # 20px
    "2xl": "1.5rem",     # 24px
    "3xl": "1.875rem",   # 30px
    "4xl": "2.25rem",    # 36px
    "5xl": "3rem",       # 48px
}

# ─── Spacing ────────────────────────────────────────────────────────────────────

SPACING = {
    "xs": "0.25rem",   # 4px
    "sm": "0.5rem",    # 8px
    "md": "1rem",      # 16px
    "lg": "1.5rem",    # 24px
    "xl": "2rem",      # 32px
    "2xl": "3rem",     # 48px
    "3xl": "4rem",     # 64px
}

# ─── Border Radius ──────────────────────────────────────────────────────────────

BORDER_RADIUS = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "2xl": "20px",
    "full": "9999px",
}

# ─── Shadows ────────────────────────────────────────────────────────────────────

SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
    "glow_primary": "0 0 20px rgba(80, 70, 228, 0.3)",
    "glow_success": "0 0 20px rgba(14, 159, 110, 0.3)",
}

# ─── Transitions ────────────────────────────────────────────────────────────────

TRANSITIONS = {
    "fast": "all 0.15s ease-in-out",
    "normal": "all 0.2s ease-in-out",
    "slow": "all 0.3s ease-in-out",
    "bounce": "all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)",
}

# ─── Gradient Definitions ───────────────────────────────────────────────────────

GRADIENTS = {
    "primary": "linear-gradient(135deg, #5046E4 0%, #7C3AED 100%)",
    "primary_horizontal": "linear-gradient(90deg, #5046E4 0%, #7C3AED 50%, #0E9F6E 100%)",
    "success": "linear-gradient(135deg, #0E9F6E 0%, #059669 100%)",
    "warning": "linear-gradient(135deg, #EA580C 0%, #E3A008 100%)",
    "error": "linear-gradient(135deg, #DC2626 0%, #E74694 100%)",
    "card_bg": "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)",
    "card_hover": "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)",
}


def get_global_css() -> str:
    """Return the complete global CSS styling for the application."""
    return f"""
    <style>
        /* ═══════════════════════════════════════════════════════════════ */
        /* GLOBAL RESET & BASE STYLES                                      */
        /* ═══════════════════════════════════════════════════════════════ */
        
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body, [class*="css"] {{
            font-family: {TYPOGRAPHY["font_family"]};
            font-size: 16px;
            line-height: 1.6;
            color: {COLORS["gray_900"]};
            background: {COLORS["bg_secondary"]};
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* STREAMLIT CHROME HIDING                                         */
        /* ═══════════════════════════════════════════════════════════════ */
        
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* TOP GRADIENT BAR - Premium SaaS indicator                       */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .stApp::before {{
            content: '';
            display: block;
            height: 4px;
            background: {GRADIENTS["primary_horizontal"]};
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* SCROLLBAR STYLING                                               */
        /* ═══════════════════════════════════════════════════════════════ */
        
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {COLORS["gray_100"]};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {COLORS["gray_300"]};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS["gray_400"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* SIDEBAR STYLING - Modern navigation panel                       */
        /* ═══════════════════════════════════════════════════════════════ */
        
        [data-testid="stSidebar"] {{
            background: {COLORS["bg_primary"]};
            border-right: 1px solid {COLORS["gray_200"]};
        }}
        
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label {{
            font-weight: 600;
            color: {COLORS["gray_700"]};
        }}
        
        /* Sidebar navigation items */
        .sidebar-nav-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            margin: 4px 8px;
            border-radius: {BORDER_RADIUS["lg"]};
            color: {COLORS["gray_600"]};
            font-weight: 500;
            font-size: {TYPOGRAPHY["sm"]};
            transition: {TRANSITIONS["normal"]};
            cursor: pointer;
            border: none;
            background: transparent;
            width: 100%;
            text-align: left;
        }}
        
        .sidebar-nav-item:hover {{
            background: {COLORS["primary_bg"]};
            color: {COLORS["primary"]};
        }}
        
        .sidebar-nav-item.active {{
            background: {GRADIENTS["primary"]};
            color: white;
            box-shadow: {SHADOWS["md"]};
        }}
        
        .sidebar-nav-item .nav-icon {{
            font-size: 1.2rem;
            width: 24px;
            text-align: center;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* SECTION HEADERS - Clear visual hierarchy                        */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .section-header {{
            font-size: {TYPOGRAPHY["xl"]};
            font-weight: 700;
            color: {COLORS["gray_900"]};
            margin: {SPACING["xl"]} 0 {SPACING["md"]};
            display: flex;
            align-items: center;
            gap: {SPACING["sm"]};
            letter-spacing: -0.02em;
        }}
        
        .section-header .section-icon {{
            font-size: 1.4rem;
        }}
        
        .section-header::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, {COLORS["gray_200"]} 0%, transparent 100%);
            margin-left: {SPACING["md"]};
        }}
        
        .section-subtitle {{
            font-size: {TYPOGRAPHY["sm"]};
            color: {COLORS["gray_500"]};
            margin-top: -{SPACING["sm"]};
            margin-bottom: {SPACING["lg"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* KPI CARDS - Premium metric display                              */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .kpi-card {{
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["xl"]};
            padding: {SPACING["lg"]};
            border: 1px solid {COLORS["gray_200"]};
            box-shadow: {SHADOWS["sm"]};
            transition: {TRANSITIONS["normal"]};
            position: relative;
            overflow: hidden;
        }}
        
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: {GRADIENTS["primary"]};
            border-radius: {BORDER_RADIUS["xl"]} 0 0 {BORDER_RADIUS["xl"]};
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: {SHADOWS["lg"]};
            border-color: {COLORS["primary_light"]};
        }}
        
        .kpi-card.success::before {{ background: {GRADIENTS["success"]}; }}
        .kpi-card.warning::before {{ background: {GRADIENTS["warning"]}; }}
        .kpi-card.error::before {{ background: {GRADIENTS["error"]}; }}
        
        .kpi-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: {SPACING["sm"]};
        }}
        
        .kpi-label {{
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 600;
            color: {COLORS["gray_500"]};
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        
        .kpi-icon {{
            width: 36px;
            height: 36px;
            border-radius: {BORDER_RADIUS["md"]};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            background: {COLORS["primary_bg"]};
        }}
        
        .kpi-card.success .kpi-icon {{ background: {COLORS["accent_green_light"]}; }}
        .kpi-card.warning .kpi-icon {{ background: {COLORS["accent_yellow_light"]}; }}
        .kpi-card.error .kpi-icon {{ background: {COLORS["error_bg"]}; }}
        
        .kpi-value {{
            font-size: {TYPOGRAPHY["3xl"]};
            font-weight: 800;
            color: {COLORS["gray_900"]};
            line-height: 1.2;
            letter-spacing: -0.03em;
        }}
        
        .kpi-delta {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-top: {SPACING["sm"]};
            padding: 4px 10px;
            border-radius: {BORDER_RADIUS["full"]};
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 600;
        }}
        
        .kpi-delta.up {{
            background: {COLORS["accent_green_light"]};
            color: {COLORS["success"]};
        }}
        
        .kpi-delta.down {{
            background: {COLORS["error_bg"]};
            color: {COLORS["error"]};
        }}
        
        .kpi-delta.flat {{
            background: {COLORS["gray_100"]};
            color: {COLORS["gray_500"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* CHART CONTAINERS - Professional data visualization frames       */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .chart-container {{
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["xl"]};
            border: 1px solid {COLORS["gray_200"]};
            box-shadow: {SHADOWS["sm"]};
            padding: {SPACING["lg"]};
            margin-bottom: {SPACING["lg"]};
            transition: {TRANSITIONS["normal"]};
        }}
        
        .chart-container:hover {{
            box-shadow: {SHADOWS["md"]};
        }}
        
        .chart-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: {SPACING["md"]};
        }}
        
        .chart-title {{
            font-size: {TYPOGRAPHY["lg"]};
            font-weight: 700;
            color: {COLORS["gray_900"]};
            display: flex;
            align-items: center;
            gap: {SPACING["sm"]};
        }}
        
        .chart-actions {{
            display: flex;
            gap: {SPACING["sm"]};
        }}
        
        .chart-action-btn {{
            padding: 6px 12px;
            border-radius: {BORDER_RADIUS["md"]};
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 500;
            background: {COLORS["gray_100"]};
            color: {COLORS["gray_600"]};
            border: none;
            cursor: pointer;
            transition: {TRANSITIONS["fast"]};
        }}
        
        .chart-action-btn:hover {{
            background: {COLORS["primary_bg"]};
            color: {COLORS["primary"]};
        }}
        
        [data-testid="stPlotlyChart"] {{
            min-height: 380px;
            border-radius: {BORDER_RADIUS["md"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* INSIGHT CARDS - AI-powered insight display                      */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .insight-card {{
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["lg"]};
            padding: {SPACING["md"]} {SPACING["lg"]};
            margin-bottom: {SPACING["md"]};
            border-left: 4px solid {COLORS["gray_300"]};
            box-shadow: {SHADOWS["sm"]};
            transition: {TRANSITIONS["normal"]};
        }}
        
        .insight-card:hover {{
            box-shadow: {SHADOWS["md"]};
            transform: translateX(4px);
        }}
        
        .insight-card.critical {{ border-left-color: {COLORS["error"]}; }}
        .insight-card.high {{ border-left-color: {COLORS["warning"]}; }}
        .insight-card.medium {{ border-left-color: {COLORS["accent_yellow"]}; }}
        .insight-card.low {{ border-left-color: {COLORS["info"]}; }}
        
        .insight-header {{
            display: flex;
            align-items: center;
            gap: {SPACING["sm"]};
            margin-bottom: {SPACING["sm"]};
        }}
        
        .severity-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: {BORDER_RADIUS["full"]};
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .severity-badge.critical {{
            background: {COLORS["error_bg"]};
            color: {COLORS["error"]};
        }}
        
        .severity-badge.high {{
            background: {COLORS["warning_bg"]};
            color: {COLORS["warning"]};
        }}
        
        .severity-badge.medium {{
            background: {COLORS["accent_yellow_light"]};
            color: {COLORS["accent_yellow"]};
        }}
        
        .severity-badge.low {{
            background: {COLORS["accent_blue_light"]};
            color: {COLORS["info"]};
        }}
        
        .insight-title {{
            font-size: {TYPOGRAPHY["sm"]};
            font-weight: 600;
            color: {COLORS["gray_900"]};
            line-height: 1.4;
        }}
        
        .insight-description {{
            font-size: {TYPOGRAPHY["sm"]};
            color: {COLORS["gray_600"]};
            line-height: 1.5;
            margin-bottom: {SPACING["sm"]};
        }}
        
        .insight-impact {{
            background: {COLORS["gray_50"]};
            padding: {SPACING["sm"]} {SPACING["md"]};
            border-radius: {BORDER_RADIUS["md"]};
            font-size: {TYPOGRAPHY["xs"]};
            color: {COLORS["gray_700"]};
            line-height: 1.5;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* ALERT BANNERS - Critical notifications                          */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .alert-banner {{
            padding: {SPACING["md"]} {SPACING["lg"]};
            border-radius: {BORDER_RADIUS["lg"]};
            margin-bottom: {SPACING["md"]};
            display: flex;
            align-items: flex-start;
            gap: {SPACING["md"]};
            border: 1px solid transparent;
        }}
        
        .alert-banner.critical {{
            background: {COLORS["error_bg"]};
            border-color: #FECACA;
        }}
        
        .alert-banner.high {{
            background: {COLORS["warning_bg"]};
            border-color: #FED7AA;
        }}
        
        .alert-banner.medium {{
            background: {COLORS["accent_yellow_light"]};
            border-color: #FDE68A;
        }}
        
        .alert-banner.info {{
            background: {COLORS["accent_blue_light"]};
            border-color: #BFDBFE;
        }}
        
        .alert-icon {{
            font-size: 1.4rem;
            flex-shrink: 0;
        }}
        
        .alert-content {{
            flex: 1;
        }}
        
        .alert-title {{
            font-weight: 700;
            font-size: {TYPOGRAPHY["sm"]};
            margin-bottom: 4px;
        }}
        
        .alert-banner.critical .alert-title {{ color: {COLORS["error"]}; }}
        .alert-banner.high .alert-title {{ color: {COLORS["warning"]}; }}
        .alert-banner.medium .alert-title {{ color: {COLORS["accent_yellow"]}; }}
        .alert-banner.info .alert-title {{ color: {COLORS["info"]}; }}
        
        .alert-message {{
            font-size: {TYPOGRAPHY["sm"]};
            line-height: 1.5;
        }}
        
        .alert-banner.critical .alert-message {{ color: #7F1D1D; }}
        .alert-banner.high .alert-message {{ color: #7C2D12; }}
        .alert-banner.medium .alert-message {{ color: #78350F; }}
        .alert-banner.info .alert-message {{ color: #1E40AF; }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* EXECUTIVE SUMMARY BOX - Featured content area                   */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .executive-summary {{
            background: {GRADIENTS["card_bg"]};
            border-radius: {BORDER_RADIUS["xl"]};
            padding: {SPACING["xl"]};
            margin-bottom: {SPACING["lg"]};
            border: 1px solid {COLORS["gray_200"]};
            position: relative;
            overflow: hidden;
        }}
        
        .executive-summary::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: {GRADIENTS["primary"]};
        }}
        
        .executive-summary-title {{
            font-size: {TYPOGRAPHY["lg"]};
            font-weight: 700;
            color: {COLORS["gray_900"]};
            margin-bottom: {SPACING["md"]};
            display: flex;
            align-items: center;
            gap: {SPACING["sm"]};
        }}
        
        .executive-summary-content {{
            font-size: {TYPOGRAPHY["base"]};
            color: {COLORS["gray_700"]};
            line-height: 1.7;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* DATA QUALITY SCORE - Visual quality indicator                   */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .quality-score-card {{
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["xl"]};
            padding: {SPACING["lg"]};
            border: 1px solid {COLORS["gray_200"]};
            box-shadow: {SHADOWS["sm"]};
            display: flex;
            align-items: center;
            gap: {SPACING["lg"]};
        }}
        
        .quality-grade {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: 800;
        }}
        
        .quality-grade.A {{
            background: {COLORS["accent_green_light"]};
            color: {COLORS["accent_green"]};
        }}
        
        .quality-grade.B {{
            background: #D1FAE5;
            color: #047857;
        }}
        
        .quality-grade.C {{
            background: {COLORS["accent_yellow_light"]};
            color: #B45309;
        }}
        
        .quality-grade.D {{
            background: #FEE2E2;
            color: #B91C1C;
        }}
        
        .quality-grade.F {{
            background: {COLORS["error_bg"]};
            color: {COLORS["error"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* LOADING ANIMATIONS                                              */
        /* ═══════════════════════════════════════════════════════════════ */
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .loading {{
            animation: pulse 2s ease-in-out infinite;
        }}
        
        .loading-shimmer {{
            background: linear-gradient(90deg, {COLORS["gray_100"]} 25%, {COLORS["gray_200"]} 50%, {COLORS["gray_100"]} 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }}
        
        .animate-slide-up {{
            animation: slideUp 0.4s ease-out;
        }}
        
        .animate-fade-in {{
            animation: fadeIn 0.3s ease-out;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* EMPTY STATE - No data placeholder                               */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .empty-state {{
            text-align: center;
            padding: {SPACING["3xl"]} {SPACING["xl"]};
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["xl"]};
            border: 2px dashed {COLORS["gray_200"]};
        }}
        
        .empty-state-icon {{
            font-size: 3rem;
            margin-bottom: {SPACING["md"]};
            opacity: 0.5;
        }}
        
        .empty-state-title {{
            font-size: {TYPOGRAPHY["lg"]};
            font-weight: 600;
            color: {COLORS["gray_700"]};
            margin-bottom: {SPACING["sm"]};
        }}
        
        .empty-state-description {{
            font-size: {TYPOGRAPHY["sm"]};
            color: {COLORS["gray_500"]};
            max-width: 400px;
            margin: 0 auto;
            line-height: 1.6;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* BUTTONS - Consistent interactive elements                       */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .stButton > button {{
            border-radius: {BORDER_RADIUS["md"]};
            font-weight: 600;
            padding: 8px 20px;
            transition: {TRANSITIONS["normal"]};
            border: 1px solid transparent;
        }}
        
        .stButton > button[kind="primary"] {{
            background: {GRADIENTS["primary"]};
            color: white;
            box-shadow: {SHADOWS["sm"]};
        }}
        
        .stButton > button[kind="primary"]:hover {{
            box-shadow: {SHADOWS["md"]};
            transform: translateY(-1px);
        }}
        
        .stButton > button[kind="secondary"] {{
            background: {COLORS["bg_primary"]};
            color: {COLORS["gray_700"]};
            border-color: {COLORS["gray_300"]};
        }}
        
        .stButton > button[kind="secondary"]:hover {{
            background: {COLORS["gray_50"]};
            border-color: {COLORS["gray_400"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* TABS - Modern tab navigation                                    */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {COLORS["gray_100"]};
            border-radius: {BORDER_RADIUS["lg"]};
            padding: 4px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: {BORDER_RADIUS["md"]};
            padding: 8px 20px;
            font-weight: 600;
            font-size: {TYPOGRAPHY["sm"]};
            color: {COLORS["gray_600"]};
            transition: {TRANSITIONS["normal"]};
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {COLORS["bg_primary"]};
            color: {COLORS["primary"]};
            box-shadow: {SHADOWS["sm"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* METRIC CARDS - Summary statistics                               */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .metric-card {{
            background: {COLORS["bg_primary"]};
            border-radius: {BORDER_RADIUS["lg"]};
            padding: {SPACING["md"]};
            text-align: center;
            border: 1px solid {COLORS["gray_200"]};
        }}
        
        .metric-value {{
            font-size: {TYPOGRAPHY["2xl"]};
            font-weight: 800;
            color: {COLORS["gray_900"]};
        }}
        
        .metric-label {{
            font-size: {TYPOGRAPHY["xs"]};
            color: {COLORS["gray_500"]};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* STATUS BADGES                                                   */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: {BORDER_RADIUS["full"]};
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 600;
        }}
        
        .status-badge.success {{
            background: {COLORS["accent_green_light"]};
            color: {COLORS["accent_green"]};
        }}
        
        .status-badge.warning {{
            background: {COLORS["accent_yellow_light"]};
            color: {COLORS["accent_yellow"]};
        }}
        
        .status-badge.error {{
            background: {COLORS["error_bg"]};
            color: {COLORS["error"]};
        }}
        
        .status-badge.info {{
            background: {COLORS["accent_blue_light"]};
            color: {COLORS["info"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* PROGRESS BARS                                                   */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .progress-bar {{
            height: 8px;
            background: {COLORS["gray_200"]};
            border-radius: {BORDER_RADIUS["full"]};
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: {BORDER_RADIUS["full"]};
            background: {GRADIENTS["primary"]};
            transition: width 0.5s ease-out;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* CARD GRID LAYOUT                                                */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: {SPACING["lg"]};
            margin-bottom: {SPACING["lg"]};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* TOOLTIP STYLES                                                  */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .tooltip {{
            position: relative;
        }}
        
        .tooltip::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 6px 12px;
            background: {COLORS["gray_900"]};
            color: white;
            font-size: {TYPOGRAPHY["xs"]};
            border-radius: {BORDER_RADIUS["sm"]};
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: {TRANSITIONS["fast"]};
            z-index: 1000;
        }}
        
        .tooltip:hover::after {{
            opacity: 1;
            visibility: visible;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* RESPONSIVE ADJUSTMENTS                                          */
        /* ═══════════════════════════════════════════════════════════════ */
        
        @media (max-width: 768px) {{
            .kpi-value {{
                font-size: {TYPOGRAPHY["2xl"]};
            }}
            
            .section-header {{
                font-size: {TYPOGRAPHY["lg"]};
            }}
            
            .executive-summary {{
                padding: {SPACING["lg"]};
            }}
        }}
    </style>
    """


def get_sidebar_css() -> str:
    """Return CSS specifically for sidebar styling."""
    return f"""
    <style>
        /* Sidebar container */
        [data-testid="stSidebar"] {{
            background: {COLORS["bg_primary"]};
            border-right: 1px solid {COLORS["gray_200"]};
        }}
        
        /* Sidebar header */
        .sidebar-header {{
            padding: {SPACING["lg"]};
            border-bottom: 1px solid {COLORS["gray_200"]};
            margin-bottom: {SPACING["md"]};
        }}
        
        .sidebar-logo {{
            font-size: 1.8rem;
            font-weight: 800;
            background: {GRADIENTS["primary"]};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.03em;
        }}
        
        .sidebar-version {{
            font-size: {TYPOGRAPHY["xs"]};
            color: {COLORS["gray_400"]};
            margin-top: 2px;
        }}
        
        /* Sidebar sections */
        .sidebar-section {{
            padding: {SPACING["md"]} {SPACING["lg"]};
            margin-bottom: {SPACING["sm"]};
        }}
        
        .sidebar-section-title {{
            font-size: {TYPOGRAPHY["xs"]};
            font-weight: 700;
            color: {COLORS["gray_400"]};
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: {SPACING["sm"]};
        }}
        
        /* Streamlit sidebar overrides */
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background: {COLORS["gray_50"]};
            border: 1px solid {COLORS["gray_200"]};
            border-radius: {BORDER_RADIUS["md"]};
        }}
        
        [data-testid="stSidebar"] .stRadio > label {{
            padding: 10px 14px;
            border-radius: {BORDER_RADIUS["md"]};
            margin-bottom: 4px;
            transition: {TRANSITIONS["fast"]};
        }}
        
        [data-testid="stSidebar"] .stRadio > label:hover {{
            background: {COLORS["gray_50"]};
        }}
        
        [data-testid="stSidebar"] .stRadio input:checked + span + div {{
            background: {COLORS["primary_bg"]};
            border-color: {COLORS["primary"]};
        }}
        
        /* Sidebar footer */
        .sidebar-footer {{
            position: absolute;
            bottom: {SPACING["lg"]};
            left: 0;
            right: 0;
            padding: {SPACING["md"]} {SPACING["lg"]};
            border-top: 1px solid {COLORS["gray_200"]};
            text-align: center;
        }}
        
        .sidebar-footer-text {{
            font-size: {TYPOGRAPHY["xs"]};
            color: {COLORS["gray_400"]};
        }}
    </style>
    """


def get_loading_overlay() -> str:
    """Return HTML/CSS for a loading overlay."""
    return f"""
    <style>
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 99999;
        }}
        
        .loading-spinner {{
            width: 48px;
            height: 48px;
            border: 4px solid {COLORS["gray_200"]};
            border-top-color: {COLORS["primary"]};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .loading-text {{
            margin-top: {SPACING["lg"]};
            font-size: {TYPOGRAPHY["base"]};
            font-weight: 600;
            color: {COLORS["gray_600"]};
        }}
        
        .loading-subtext {{
            margin-top: {SPACING["sm"]};
            font-size: {TYPOGRAPHY["sm"]};
            color: {COLORS["gray_400"]};
        }}
    </style>
    
    <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Processing your data...</div>
        <div class="loading-subtext">This may take a moment</div>
    </div>
    """