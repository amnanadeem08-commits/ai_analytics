"""
chatbot_service.py — Domain-aware Data Copilot.
Maintains conversation history, builds context from active dataset, and streams answers.
"""

import json
import logging
import pandas as pd
import numpy as np
from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from utils.llm_client import call_llm
from config import AI_MAX_TOKENS

logger = logging.getLogger(__name__)

MAX_HISTORY = 20   # message pairs kept in context


class ChatbotService:
    """Stateful Data Copilot powered by an LLM."""

    def __init__(self):
        self.history: list[dict] = []

    def reset(self):
        self.history = []

    def chat(
        self,
        user_message: str,
        df: pd.DataFrame,
        domain: DomainConfig,
        kpis: list[KPIResult],
    ) -> str:
        system_prompt = self._build_system(df, domain, kpis)
        self.history.append({"role": "user", "content": user_message})

        try:
            reply = self._call_llm(system_prompt)
        except Exception as e:
            logger.error("Chatbot LLM error: %s", e)
            reply = f"I encountered an error: {e}. Please check your API configuration."

        self.history.append({"role": "assistant", "content": reply})
        # trim history
        if len(self.history) > MAX_HISTORY * 2:
            self.history = self.history[-(MAX_HISTORY * 2):]

        return reply

    def _build_system(
        self,
        df: pd.DataFrame,
        domain: DomainConfig,
        kpis: list[KPIResult],
    ) -> str:
        schema = self._schema_summary(df)
        kpi_text = "\n".join(f"- {k.name}: {k.formatted}" for k in kpis[:8])
        sample = df.head(5).to_string(max_cols=12, max_colwidth=30)

        return (
            f"{domain.analyst_persona}\n\n"
            f"You are answering questions about a {domain.label} dataset.\n\n"
            f"Dataset schema:\n{schema}\n\n"
            f"Current KPIs:\n{kpi_text}\n\n"
            f"Sample rows (first 5):\n{sample}\n\n"
            f"Rules:\n"
            f"- Answer concisely and precisely.\n"
            f"- Cite specific numbers when available.\n"
            f"- If asked to create a chart, describe what chart type and columns to use.\n"
            f"- If asked for data you don't have, say so clearly.\n"
            f"- Stay in character as a {domain.label} expert.\n"
        )

    def _schema_summary(self, df: pd.DataFrame) -> str:
        lines = [f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns"]
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = df[col].isnull().mean() * 100
            if pd.api.types.is_numeric_dtype(df[col]):
                extra = f"min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}"
            else:
                top = df[col].value_counts().index[0] if not df[col].empty else "N/A"
                extra = f"top value: {top!r}, unique: {df[col].nunique()}"
            lines.append(f"  {col} [{dtype}] null={null_pct:.1f}% | {extra}")
        return "\n".join(lines)

    def _call_llm(self, system_prompt: str) -> str:
        if not self.history:
            return "No prompt available for the chatbot."

        result = call_llm(
            user_prompt=self.history[-1]["content"],
            system_prompt=system_prompt,
            max_tokens=AI_MAX_TOKENS,
            history=self.history[:-1],
        )
        if not result:
            return (
                "AI is not configured or the LLM request failed. Please add your ANTHROPIC_API_KEY "
                "or OPENAI_API_KEY to the .env file and restart the app."
            )
        return result
