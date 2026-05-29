"""tabs/copilot.py — Data Copilot tab (AI insights + SQL engine + chatbot)."""

import streamlit as st

from components.chatbot import render_chatbot
from components.sql_query import render_sql_query
from components.ai_insights import render_ai_insights


def render(filtered_df, domain_cfg, kpis, sql_engine, rag_engine, filename: str = "") -> None:
    tab_insights, tab_sql, tab_chat = st.tabs(
        ["🧩 AI Insights", "🗄️ SQL Query", "🤖 Chat Copilot"]
    )

    with tab_insights:
        render_ai_insights(filtered_df, rag_engine, source_name=filename)

    with tab_sql:
        render_sql_query(filtered_df, sql_engine, source_name=filename)

    with tab_chat:
        render_chatbot(
            df=filtered_df,
            domain=domain_cfg,
            kpis=kpis,
            chatbot_svc=st.session_state.chatbot_svc,
        )
