"""
chatbot.py — Data Copilot chat UI.
Renders the conversation history and input box, delegates to ChatbotService.
"""

import streamlit as st
import pandas as pd

from services.chatbot_service import ChatbotService
from services.domain_service import DomainConfig
from services.kpi_service import KPIResult


SUGGESTED_QUESTIONS = [
    "What are the top insights from this data?",
    "Which metric shows the highest growth?",
    "Are there any anomalies I should be aware of?",
    "Summarize the trend for the past period.",
    "What actions would you recommend based on this data?",
    "Which category is performing best?",
    "What is the distribution of the main numeric column?",
]


def render_chatbot(
    df: pd.DataFrame,
    domain: DomainConfig,
    kpis: list[KPIResult],
    chatbot_svc: ChatbotService,
):
    """Renders full chatbot UI. chatbot_svc is shared via st.session_state."""

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #5046E4 0%, #7C3AED 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.2rem;
        color: white;
    ">
        <div style="font-weight: 700; font-size: 1.05rem;">🤖 Data Copilot</div>
        <div style="font-size: 0.82rem; opacity: 0.85; margin-top: 2px;">
            Domain: <strong>{domain.label}</strong> · {len(df):,} rows loaded
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggested questions (only show if history is empty)
    if not chatbot_svc.history:
        st.markdown("**Quick questions:**")
        cols = st.columns(3)
        for i, q in enumerate(SUGGESTED_QUESTIONS[:6]):
            col = cols[i % 3]
            if col.button(q, key=f"suggest_{i}", use_container_width=True):
                _handle_message(q, df, domain, kpis, chatbot_svc)
                st.rerun()

    # Message history
    for msg in chatbot_svc.history:
        role = msg["role"]
        with st.chat_message(role, avatar="🤖" if role == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask about your data…"):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analysing…"):
                reply = _handle_message(prompt, df, domain, kpis, chatbot_svc)
            st.markdown(reply)

    # Reset button
    if chatbot_svc.history:
        if st.button("🗑 Clear conversation", key="clear_chat"):
            chatbot_svc.reset()
            st.rerun()


def _handle_message(
    prompt: str,
    df: pd.DataFrame,
    domain: DomainConfig,
    kpis: list[KPIResult],
    svc: ChatbotService,
) -> str:
    return svc.chat(prompt, df, domain, kpis)
