"""
story_engine_view.py — UI for the Phase 5 Storytelling Engine.
Rendering only; all narrative logic lives in services/storytelling_engine.py.
"""

from __future__ import annotations

import streamlit as st

from services.storytelling_engine import DataStory

_CATEGORY_ICON = {
    "trend": "📈",
    "anomaly": "⚠️",
    "opportunity": "💡",
    "risk": "🚨",
    "insight": "🔎",
}


def render_data_story(
    story_engine,
    df,
    domain_cfg=None,
    analytics_report=None,
    data_understanding_report=None,
    kpis=None,
    rag_result=None,
) -> None:
    st.markdown("#### 🧠 AI Storytelling Engine")
    st.caption(
        "Generates a business narrative — what is happening, why, and what to do — "
        "from your KPIs, trends, anomalies, statistics, and AI insights."
    )

    col_run, col_clear = st.columns([1, 1])
    with col_run:
        run = st.button("📖 Generate data story", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear story", key="story_clear", use_container_width=True):
            st.session_state.pop("data_story_result", None)
            st.rerun()

    if run:
        with st.spinner("Composing your data story…"):
            domain_label = getattr(domain_cfg, "label", "General")
            dataset_name = st.session_state.get("filename", "the dataset")
            ctx = story_engine.build_context(
                dataset_name=dataset_name,
                domain_label=domain_label,
                df=df,
                analytics_report=analytics_report,
                data_understanding_report=data_understanding_report,
                kpis=kpis,
                rag_result=rag_result,
            )
            st.session_state.data_story_result = story_engine.generate(ctx)

    story: DataStory | None = st.session_state.get("data_story_result")
    if story:
        _render_story(story)


def _render_story(story: DataStory) -> None:
    if not story.success:
        st.error(story.error or "Story generation failed.")
        return

    st.markdown(f"### {story.title or 'Data Story'}")
    if not story.generated_with_ai:
        st.caption("⚙️ Generated from statistics (AI unavailable — showing rule-based narrative).")

    if story.overview:
        st.markdown("**Overview**")
        st.info(story.overview)

    c1, c2 = st.columns(2)
    if story.what_is_happening:
        with c1:
            st.markdown("**What is happening?**")
            st.write(story.what_is_happening)
    if story.why_it_is_happening:
        with c2:
            st.markdown("**Why is it happening?**")
            st.write(story.why_it_is_happening)

    if story.what_should_be_done:
        st.markdown("**What should be done?**")
        for action in story.what_should_be_done:
            st.markdown(f"- {action}")

    if story.sections:
        st.markdown("---")
        st.markdown("#### Key insights")
        for sec in story.sections:
            icon = _CATEGORY_ICON.get(sec.category, "🔎")
            with st.container(border=True):
                st.markdown(f"{icon} **{sec.headline}**")
                if sec.explanation:
                    st.write(sec.explanation)
                if sec.recommendation:
                    st.markdown(f"➡️ _Recommendation:_ {sec.recommendation}")

    if story.chart_suggestions:
        st.markdown("---")
        st.markdown("#### 📊 Suggested charts")
        for ch in story.chart_suggestions:
            cols = f" ({', '.join(ch.columns)})" if ch.columns else ""
            st.markdown(f"- **{ch.title}** — `{ch.chart_type}`{cols}")
            if ch.rationale:
                st.caption(ch.rationale)
