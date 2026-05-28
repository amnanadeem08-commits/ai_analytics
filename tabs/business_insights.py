"""
tabs/business_insights.py — AI-Powered Business Insights tab.

Lazy-generates InsightEngine + RecommendationEngine reports on first visit,
then caches them in session_state.  They are invalidated by pipeline.py on
new upload or domain change.
"""

from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from components.insights_panel import render_full_insights_panel

logger = logging.getLogger(__name__)


def render(filtered_df, domain_cfg, kpis, analytics_report, insight_engine, recommendation_engine) -> None:
    st.markdown("### 🧠 AI-Powered Business Insights")
    st.caption(
        "Advanced anomaly detection, pattern analysis, and actionable "
        "recommendations powered by AI."
    )

    # Lazy generation — only runs once per data+domain combination
    if st.session_state.insight_report is None:
        with st.spinner("🧠 Analysing data patterns and generating insights…"):
            try:
                insight_report = insight_engine.generate_insights(
                    df=filtered_df,
                    domain_cfg=domain_cfg,
                    kpis=kpis,
                    analytics_report=analytics_report,
                    dataset_name=st.session_state.filename,
                )
                st.session_state.insight_report = insight_report

                rec_report = recommendation_engine.generate_recommendations(
                    insight_report=insight_report,
                    domain_cfg=domain_cfg,
                    df=filtered_df,
                    kpis=kpis,
                )
                st.session_state.recommendation_report = rec_report

            except Exception as exc:
                logger.error("Insight generation failed: %s", exc)
                st.error(f"Failed to generate insights: {exc}")
                return

    if not st.session_state.insight_report:
        return

    render_full_insights_panel(
        insight_report=st.session_state.insight_report,
        recommendation_report=st.session_state.recommendation_report,
        domain_cfg=domain_cfg,
    )

    # Download
    st.markdown("---")
    col_dl1, _, _ = st.columns(3)
    with col_dl1:
        if st.button("📥 Download Insights Summary", use_container_width=True):
            report = st.session_state.insight_report
            rec    = st.session_state.recommendation_report
            lines  = [
                f"Business Insights Report — {st.session_state.filename}",
                f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Domain: {domain_cfg.label}",
                f"Records Analysed: {len(filtered_df):,}",
                "",
                "EXECUTIVE SUMMARY", "=" * 50,
                report.summary_paragraph, "",
                "KEY FINDINGS", "=" * 50,
                *[f"• {f}" for f in report.key_findings],
                "", "RISK ALERTS", "=" * 50,
                *[f"⚠️ {a}" for a in report.risk_alerts],
                "", "OPPORTUNITIES", "=" * 50,
                *[f"💡 {o}" for o in report.opportunities],
            ]
            if rec:
                lines += ["", "TOP RECOMMENDATIONS", "=" * 50]
                for r in rec.top_3_actions:
                    lines += [
                        f"• {r.title}",
                        f"  Timeline: {r.estimated_timeline}",
                        f"  Impact: {r.impact}",
                        "",
                    ]
            st.download_button(
                "⬇ Download TXT",
                "\n".join(lines),
                file_name=f"insights_{st.session_state.filename.replace('.csv', '')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
