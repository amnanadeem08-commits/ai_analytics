"""tabs/export.py — Export Reports tab."""

from __future__ import annotations

import logging

import streamlit as st

from config import EXPORTS_DIR, SESSION_ID_LENGTH
from services.export_service import ExportService
from utils.branding import BrandTheme, build_brand_theme, extract_palette_from_logo

logger = logging.getLogger(__name__)


def _render_branding_panel() -> BrandTheme:
    """Logo upload + brand color pickers; returns a BrandTheme for exports."""
    st.markdown("#### 🎨 Brand & Logo")
    st.caption("Upload your logo to apply your official colors across PDF, PowerPoint, and Excel exports.")

    col_logo, col_meta = st.columns([1, 2])

    with col_logo:
        logo_file = st.file_uploader(
            "Company logo",
            type=["png", "jpg", "jpeg", "webp"],
            key="export_logo_uploader",
            help="PNG or JPG recommended. Colors are auto-detected from the logo.",
        )
        if logo_file is not None:
            st.image(logo_file, width=120)
            st.session_state.export_logo_bytes = logo_file.getvalue()
        elif st.session_state.get("export_logo_bytes"):
            st.image(st.session_state.export_logo_bytes, width=120)

    detected_palette: list[str] = []
    if st.session_state.get("export_logo_bytes"):
        detected_palette = extract_palette_from_logo(st.session_state.export_logo_bytes)
        with col_meta:
            st.markdown("**Detected palette from logo**")
            swatches = " ".join(
                f'<span style="display:inline-block;width:28px;height:28px;border-radius:6px;'
                f'background:{color};border:1px solid #E5E7EB;margin-right:6px;" title="{color}"></span>'
                for color in detected_palette[:6]
            )
            st.markdown(swatches, unsafe_allow_html=True)

    default_primary = detected_palette[0] if detected_palette else st.session_state.get("export_brand_primary", "#5046E4")
    default_secondary = detected_palette[1] if len(detected_palette) > 1 else st.session_state.get("export_brand_secondary", "#7C3AED")
    default_accent = detected_palette[2] if len(detected_palette) > 2 else st.session_state.get("export_brand_accent", "#0E9F6E")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        primary = st.color_picker("Primary", value=default_primary, key="export_brand_primary_picker")
    with c2:
        secondary = st.color_picker("Secondary", value=default_secondary, key="export_brand_secondary_picker")
    with c3:
        accent = st.color_picker("Accent", value=default_accent, key="export_brand_accent_picker")
    with c4:
        company_name = st.text_input(
            "Company / report name",
            value=st.session_state.get("export_company_name", ""),
            placeholder="Acme Corp",
            key="export_company_name_input",
        )

    st.session_state.export_brand_primary = primary
    st.session_state.export_brand_secondary = secondary
    st.session_state.export_brand_accent = accent
    st.session_state.export_company_name = company_name

    if st.button("Clear logo & brand", key="clear_export_brand"):
        for key in (
            "export_logo_bytes", "export_brand_primary", "export_brand_secondary",
            "export_brand_accent", "export_company_name",
        ):
            st.session_state.pop(key, None)
        st.rerun()

    return build_brand_theme(
        logo_bytes=st.session_state.get("export_logo_bytes"),
        primary=primary,
        secondary=secondary,
        accent=accent,
        company_name=company_name,
    )


def render(filtered_df, domain_cfg, kpis, charts, ai_summary, export_svc, session_svc) -> None:
    # Stateless — always instantiate fresh so export API updates apply without stale cache.
    export_svc = ExportService()

    st.markdown("### 📤 Export Reports")
    st.info(
        f"**{st.session_state.filename}** · {len(filtered_df):,} rows · "
        f"{len(kpis)} KPIs · Domain: {domain_cfg.label}",
        icon="📁",
    )

    brand = _render_branding_panel()
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("#### 📊 Excel Report")
        st.markdown("Formatted workbook with KPIs, cleaned data, and statistics.")
        if st.button("Export Excel", type="primary", use_container_width=True):
            with st.spinner("Generating Excel…"):
                try:
                    path = export_svc.export_excel(filtered_df, kpis, domain_cfg, brand=brand)
                    with open(path, "rb") as fh:
                        st.download_button(
                            "⬇ Download Excel", fh, file_name=path.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                        )
                except Exception as exc:
                    st.error(f"Excel export failed: {exc}")

    with col2:
        st.markdown("#### 📄 PDF Report")
        st.markdown("Branded PDF with KPIs, executive summary, and chart visuals.")
        if st.button("Export PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF…"):
                try:
                    path = export_svc.export_pdf(
                        domain_cfg, kpis, ai_summary, charts=charts, brand=brand,
                    )
                    with open(path, "rb") as fh:
                        st.download_button(
                            "⬇ Download PDF", fh, file_name=path.name,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception as exc:
                    st.error(f"PDF export failed: {exc}")

    with col3:
        st.markdown("#### 🎞 PowerPoint Deck")
        st.markdown("Colorful slide deck with KPI cards, insights, and charts.")
        include_charts = st.checkbox("Include charts in PPTX", value=True)
        if st.button("Export PPTX", type="primary", use_container_width=True):
            with st.spinner("Generating PowerPoint…"):
                try:
                    path = export_svc.export_pptx(
                        domain_cfg, kpis, ai_summary,
                        charts if include_charts else [],
                        brand=brand,
                    )
                    with open(path, "rb") as fh:
                        st.download_button(
                            "⬇ Download PPTX", fh, file_name=path.name,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True,
                        )
                except Exception as exc:
                    st.error(f"PPTX export failed: {exc}")

    with col4:
        st.markdown("#### CSV Export")
        st.markdown("Cleaned dataset for BI tools, notebooks, and warehouses.")
        if st.button("Export CSV", type="primary", use_container_width=True):
            with st.spinner("Generating CSV…"):
                try:
                    path = export_svc.export_csv(filtered_df, domain_cfg)
                    with open(path, "rb") as fh:
                        st.download_button(
                            "⬇ Download CSV", fh, file_name=path.name,
                            mime="text/csv",
                            use_container_width=True,
                        )
                except Exception as exc:
                    st.error(f"CSV export failed: {exc}")

    # Session management
    st.markdown("---")
    st.markdown("#### 💾 Saved Sessions")
    sid = st.text_input(
        "Session name (optional)",
        value=st.session_state.filename.replace(".", "_")[:SESSION_ID_LENGTH],
        key="session_name_input",
    )
    if st.button("Save current session"):
        try:
            session_svc.save(
                sid or "session",
                {
                    "filename":   st.session_state.filename,
                    "domain_key": st.session_state.domain_key,
                    "row_count":  len(st.session_state.cleaned_df),
                    "ai_summary": st.session_state.ai_summary,
                },
                st.session_state.cleaned_df,
            )
            st.success(f"Session saved as `{sid}`")
        except Exception as exc:
            st.error(f"Save failed: {exc}")

    saved = session_svc.list_sessions()
    if saved:
        pick = st.selectbox(
            "Restore session",
            options=[s.session_id for s in saved],
            format_func=lambda x: next(
                (f"{s.filename} ({s.saved_at[:10]})" for s in saved if s.session_id == x), x
            ),
        )
        if st.button("Load session"):
            try:
                meta, df = session_svc.load(pick)
                st.session_state.raw_df          = df
                st.session_state.filename        = meta.get("filename", pick)
                st.session_state.processing_done = False
                st.rerun()
            except Exception as exc:
                st.error(f"Load failed: {exc}")

    st.markdown("---")
    st.markdown("**Export Path:** `exports/`")
    export_files = list(EXPORTS_DIR.glob("*"))
    if export_files:
        for f in sorted(export_files, reverse=True)[:10]:
            st.caption(f"📎 {f.name} ({f.stat().st_size / 1024:.1f} KB)")
