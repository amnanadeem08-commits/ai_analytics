"""
ai_insights.py — AI Insight Engine UI (Phase 4, light RAG).
Rendered inside the Data Copilot tab; contains no analysis logic.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from services.rag_engine import RAGInsightEngine, RAGInsightResult

SUGGESTED_INSIGHT_QUESTIONS = [
    "What insights do you see?",
    "Explain this dataset",
    "What are the key trends?",
]


def render_ai_insights(df: pd.DataFrame, rag_engine: RAGInsightEngine, source_name: str = "") -> None:
    st.markdown("#### 🧩 AI Insight Engine")
    st.caption(
        "Ask open questions about your data. Answers are grounded in a knowledge base "
        "of your dataset's schema, statistics, and samples (light RAG)."
    )

    try:
        rag_engine.ensure_built(df, source_name=source_name or "dataset")
    except Exception as exc:
        st.error(f"Could not build the knowledge base: {exc}")
        return

    st.caption(f"Knowledge base: {rag_engine.chunk_count} chunks · vector store: `{rag_engine.backend}`")

    cols = st.columns(len(SUGGESTED_INSIGHT_QUESTIONS))
    for i, q in enumerate(SUGGESTED_INSIGHT_QUESTIONS):
        if cols[i].button(q, key=f"insight_suggest_{i}", use_container_width=True):
            st.session_state.insight_question_input = q
            st.rerun()

    question = st.text_input(
        "Your question",
        value=st.session_state.get("insight_question_input", ""),
        placeholder="e.g. What are the key trends and risks in this data?",
        key="insight_question_input",
    )

    col_run, col_clear = st.columns([1, 1])
    with col_run:
        run = st.button("✨ Generate insights", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear", key="insight_clear", use_container_width=True):
            st.session_state.pop("insight_result", None)
            st.session_state.insight_question_input = ""
            st.rerun()

    if run and question.strip():
        with st.spinner("Retrieving context and generating insights…"):
            st.session_state.insight_result = rag_engine.ask(question.strip())

    result: RAGInsightResult | None = st.session_state.get("insight_result")
    if result:
        _render_result(result)


def _render_result(result: RAGInsightResult) -> None:
    st.markdown("---")

    if not result.success:
        st.error(result.error or "Insight generation failed.")
        return

    st.markdown("**Summary insight**")
    st.info(result.summary or "No summary returned.")

    if result.key_findings:
        st.markdown("**Key findings**")
        for finding in result.key_findings:
            st.markdown(f"- {finding}")

    if result.suggestions:
        st.markdown("**Suggested KPIs / analysis directions**")
        for s in result.suggestions:
            st.markdown(f"- {s}")

    if result.context_titles:
        with st.expander("🔎 Context used (retrieved from knowledge base)", expanded=False):
            for title in result.context_titles:
                st.caption(f"• {title}")
