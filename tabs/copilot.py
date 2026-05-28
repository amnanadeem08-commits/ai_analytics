"""tabs/copilot.py — Data Copilot (chatbot) tab."""

import streamlit as st
from components.chatbot import render_chatbot


def render(filtered_df, domain_cfg, kpis) -> None:
    render_chatbot(
        df=filtered_df,
        domain=domain_cfg,
        kpis=kpis,
        chatbot_svc=st.session_state.chatbot_svc,
    )
