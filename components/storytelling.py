"""
storytelling.py — AI narrative walkthrough of charts.
"""

import streamlit as st
from services.storytelling_service import StoryNarrative


def render_story_narrative(story: StoryNarrative) -> None:
    """Render introduction, per-chart beats, and conclusion."""
    st.markdown(f"### 📖 {story.title}")
    st.markdown(story.introduction)

    for beat in story.beats:
        st.markdown(f"""
        <div style="
            border-left: 3px solid #7C3AED; padding: 0.6rem 1rem;
            margin: 0.8rem 0; background: #FAF5FF; border-radius: 0 8px 8px 0;
        ">
            <div style="font-weight:600;color:#5B21B6;">Step {beat.order}: {beat.chart_title}</div>
            <div style="margin-top:4px;color:#374151;font-size:0.92rem;">{beat.narrative}</div>
        </div>
        """, unsafe_allow_html=True)

    if story.conclusion:
        st.markdown("**Conclusion**")
        st.markdown(story.conclusion)
