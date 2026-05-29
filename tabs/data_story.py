"""tabs/data_story.py — Data Story tab (chart walkthrough + AI Storytelling Engine)."""

import streamlit as st

from components.storytelling import render_story_narrative
from components.story_engine_view import render_data_story
from tabs.dashboard import render_chart


def render(
    story_narrative,
    charts,
    story_engine=None,
    df=None,
    domain_cfg=None,
    analytics_report=None,
    data_understanding_report=None,
    kpis=None,
) -> None:
    st.markdown("### 📖 Data Story")

    # ── Phase 5: AI Storytelling Engine (narrative) ───────────────────────────
    if story_engine is not None and df is not None:
        render_data_story(
            story_engine=story_engine,
            df=df,
            domain_cfg=domain_cfg,
            analytics_report=analytics_report,
            data_understanding_report=data_understanding_report,
            kpis=kpis,
            rag_result=st.session_state.get("insight_result"),
        )
        st.markdown("---")

    # ── Existing chart-by-chart narrative ────────────────────────────────────
    if story_narrative:
        render_story_narrative(story_narrative)
        if charts:
            st.markdown(
                '<div class="section-header">📊 Charts in this story</div>',
                unsafe_allow_html=True,
            )
            for i, (title, fig) in enumerate(charts[:6]):
                st.markdown(f"**{title}**")
                render_chart(fig, key=f"story_chart_{i}")
    else:
        st.info("Upload data to generate an AI-guided narrative.")
