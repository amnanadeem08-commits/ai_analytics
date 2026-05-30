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
            border-left: 3px solid #818CF8; padding: 0.6rem 1rem;
            margin: 0.8rem 0; background: rgba(99,102,241,0.1); border-radius: 0 8px 8px 0;
            border: 1px solid rgba(99,102,241,0.18); border-left-width: 3px;
        ">
            <div style="font-weight:600;color:#C7D2FE;">Step {beat.order}: {beat.chart_title}</div>
            <div style="margin-top:4px;color:#CBD5E1;font-size:0.92rem;">{beat.narrative}</div>
        </div>
        """, unsafe_allow_html=True)

    if story.conclusion:
        st.markdown("**Conclusion**")
        st.markdown(story.conclusion)
