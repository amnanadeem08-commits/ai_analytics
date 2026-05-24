"""
export_service.py — Generates Excel, PDF, and PowerPoint reports.
All exports go to the EXPORTS_DIR and return a Path to the file.
"""

import io
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import plotly.graph_objects as go

from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from config import EXPORTS_DIR

logger = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class ExportService:

    # ── Excel ──────────────────────────────────────────────────────────────────
    def export_excel(
        self,
        df: pd.DataFrame,
        kpis: list[KPIResult],
        domain: DomainConfig,
        filename: str | None = None,
    ) -> Path:
        filename = filename or f"analytics_{domain.key}_{_timestamp()}.xlsx"
        path = EXPORTS_DIR / filename

        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            wb = writer.book

            # Formats
            header_fmt = wb.add_format({
                "bold": True, "bg_color": "#5046E4", "font_color": "#FFFFFF",
                "border": 1, "align": "center",
            })
            kpi_label_fmt = wb.add_format({"bold": True, "font_color": "#374151"})
            kpi_value_fmt = wb.add_format({"num_format": "#,##0.00", "bold": True, "font_color": "#5046E4"})
            num_fmt = wb.add_format({"num_format": "#,##0.00"})
            date_fmt = wb.add_format({"num_format": "yyyy-mm-dd"})

            # Sheet 1: KPI Summary
            ws_kpi = wb.add_worksheet("KPI Summary")
            ws_kpi.set_column("A:A", 28)
            ws_kpi.set_column("B:B", 20)
            ws_kpi.write(0, 0, f"{domain.label} — KPI Summary", wb.add_format({"bold": True, "font_size": 14}))
            ws_kpi.write(2, 0, "Metric", header_fmt)
            ws_kpi.write(2, 1, "Value", header_fmt)
            for i, kpi in enumerate(kpis):
                ws_kpi.write(3 + i, 0, kpi.name, kpi_label_fmt)
                ws_kpi.write(3 + i, 1, kpi.formatted, kpi_value_fmt)

            # Sheet 2: Cleaned Data
            df.to_excel(writer, sheet_name="Cleaned Data", index=False)
            ws_data = writer.sheets["Cleaned Data"]
            for col_num, col_name in enumerate(df.columns):
                ws_data.write(0, col_num, col_name, header_fmt)
                ws_data.set_column(col_num, col_num, 18)

            # Sheet 3: Stats Summary
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols):
                stats_df = df[numeric_cols].describe().T.round(3)
                stats_df.to_excel(writer, sheet_name="Statistics")

        logger.info("Excel exported: %s", path)
        return path

    # ── PDF ────────────────────────────────────────────────────────────────────
    def export_pdf(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        summary_text: str,
        charts: list[tuple[str, go.Figure]] | None = None,
        filename: str | None = None,
    ) -> Path:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image,
        )
        from reportlab.lib.utils import ImageReader

        filename = filename or f"report_{domain.key}_{_timestamp()}.pdf"
        path = EXPORTS_DIR / filename

        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        BRAND = colors.HexColor("#5046E4")
        DARK = colors.HexColor("#111827")

        title_style = ParagraphStyle("Title", parent=styles["Title"],
                                     textColor=BRAND, fontSize=22, spaceAfter=4)
        subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"],
                                        textColor=DARK, fontSize=11, spaceAfter=12)
        body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                    textColor=DARK, fontSize=10, leading=16)
        kpi_label = ParagraphStyle("KPILabel", parent=styles["Normal"],
                                   textColor=colors.HexColor("#6B7280"), fontSize=9)
        kpi_value = ParagraphStyle("KPIValue", parent=styles["Normal"],
                                   textColor=BRAND, fontSize=14, fontName="Helvetica-Bold")

        story = []
        story.append(Paragraph(f"{domain.label} Report", title_style))
        story.append(Paragraph(
            f"Generated {datetime.now().strftime('%B %d, %Y')} | AI Analytics Platform",
            subtitle_style,
        ))
        story.append(HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=12))

        # KPI grid (2 columns)
        story.append(Paragraph("Key Performance Indicators", styles["Heading2"]))
        story.append(Spacer(1, 6))

        kpi_data = []
        row = []
        for i, kpi in enumerate(kpis):
            cell = [Paragraph(kpi.name, kpi_label), Paragraph(kpi.formatted, kpi_value)]
            row.append(cell)
            if len(row) == 2 or i == len(kpis) - 1:
                if len(row) == 1:
                    row.append("")
                kpi_data.append(row)
                row = []

        kpi_table = Table(kpi_data, colWidths=[85*mm, 85*mm])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 16))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        story.append(Spacer(1, 6))
        for para in summary_text.replace("**", "").split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 8))

        if charts:
            story.append(Spacer(1, 12))
            story.append(Paragraph("Visualisations", styles["Heading2"]))
            story.append(Spacer(1, 6))
            for chart_title, fig in charts[:6]:
                try:
                    img_bytes = fig.to_image(format="png", width=900, height=450, scale=2)
                    img_stream = io.BytesIO(img_bytes)
                    story.append(Paragraph(chart_title, styles["Heading3"]))
                    story.append(Spacer(1, 4))
                    story.append(Image(ImageReader(img_stream), width=170*mm, height=85*mm))
                    story.append(Spacer(1, 12))
                except Exception as e:
                    logger.warning("PDF chart embed failed for '%s': %s", chart_title, e)

        doc.build(story)
        logger.info("PDF exported: %s", path)
        return path

    # ── PowerPoint ─────────────────────────────────────────────────────────────
    def export_pptx(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        summary_text: str,
        charts: list[tuple[str, go.Figure]] | None = None,
        filename: str | None = None,
    ) -> Path:
        from pptx import Presentation
        from pptx.util import Inches, Pt, Emu
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        BRAND = RGBColor(0x50, 0x46, 0xE4)
        WHITE = RGBColor(0xFF, 0xFF, 0xFF)
        DARK = RGBColor(0x11, 0x18, 0x27)
        LIGHT = RGBColor(0xF9, 0xFA, 0xFB)

        filename = filename or f"deck_{domain.key}_{_timestamp()}.pptx"
        path = EXPORTS_DIR / filename

        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)
        blank = prs.slide_layouts[6]

        def add_rect(slide, l, t, w, h, fill_rgb):
            shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
            shape.fill.solid()
            shape.fill.fore_color.rgb = fill_rgb
            shape.line.fill.background()
            return shape

        def add_text(slide, text, l, t, w, h, size=18, bold=False, color=DARK, align=PP_ALIGN.LEFT):
            tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = align
            run = p.add_run()
            run.text = text
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color

        # ── Slide 1: Cover ─────────────────────────────────────────────────────
        slide = prs.slides.add_slide(blank)
        add_rect(slide, 0, 0, 13.33, 7.5, BRAND)
        add_text(slide, domain.label, 0.8, 1.8, 11, 1.5, size=44, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
        add_text(slide, "Analytics Report", 0.8, 3.0, 11, 1, size=28, bold=False, color=RGBColor(0xC7, 0xD2, 0xFE), align=PP_ALIGN.LEFT)
        add_text(slide, datetime.now().strftime("Generated %B %d, %Y"), 0.8, 6.5, 8, 0.6,
                 size=13, color=RGBColor(0xA5, 0xB4, 0xFC))

        # ── Slide 2: KPIs ──────────────────────────────────────────────────────
        slide = prs.slides.add_slide(blank)
        add_rect(slide, 0, 0, 13.33, 1.1, BRAND)
        add_text(slide, "Key Performance Indicators", 0.4, 0.1, 12, 0.9, size=22, bold=True, color=WHITE)

        cols = 4
        card_w, card_h = 2.8, 1.5
        x_start, y_start, gap = 0.4, 1.4, 0.3

        for i, kpi in enumerate(kpis[:8]):
            row, col = divmod(i, cols)
            x = x_start + col * (card_w + gap)
            y = y_start + row * (card_h + gap)
            card = add_rect(slide, x, y, card_w, card_h, LIGHT)
            card.line.color.rgb = RGBColor(0xE5, 0xE7, 0xEB)
            add_text(slide, kpi.name, x + 0.1, y + 0.1, card_w - 0.2, 0.5, size=10, color=RGBColor(0x6B, 0x72, 0x80))
            add_text(slide, kpi.formatted, x + 0.1, y + 0.6, card_w - 0.2, 0.8, size=22, bold=True, color=BRAND)

        # ── Slide 3: Executive Summary ─────────────────────────────────────────
        slide = prs.slides.add_slide(blank)
        add_rect(slide, 0, 0, 13.33, 1.1, BRAND)
        add_text(slide, "Executive Summary", 0.4, 0.1, 12, 0.9, size=22, bold=True, color=WHITE)

        clean_summary = summary_text.replace("**", "").replace("##", "")
        add_text(slide, clean_summary[:1200], 0.4, 1.3, 12.5, 6.0, size=12, color=DARK)

        # ── Slide 4+: Charts ───────────────────────────────────────────────────
        if charts:
            for chart_title, fig in charts[:4]:
                slide = prs.slides.add_slide(blank)
                add_rect(slide, 0, 0, 13.33, 1.1, BRAND)
                add_text(slide, chart_title, 0.4, 0.1, 12, 0.9, size=22, bold=True, color=WHITE)

                # Export chart as image
                try:
                    img_bytes = fig.to_image(format="png", width=1100, height=550, scale=2)
                    img_stream = io.BytesIO(img_bytes)
                    slide.shapes.add_picture(img_stream, Inches(0.4), Inches(1.3), Inches(12.5), Inches(5.8))
                except Exception as e:
                    logger.warning("Chart image export failed for '%s': %s", chart_title, e)
                    add_text(slide, f"[Chart: {chart_title}]", 0.4, 3.5, 12, 1, size=16, color=DARK)

        prs.save(str(path))
        logger.info("PPTX exported: %s", path)
        return path
