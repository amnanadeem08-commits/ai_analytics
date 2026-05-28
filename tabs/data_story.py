"""tabs/data_story.py — Data Story tab."""

import streamlit as st
from components.storytelling import render_story_narrative
from tabs.dashboard import render_chart


def render(story_narrative, charts) -> None:
    st.markdown("### 📖 Data Story")
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
