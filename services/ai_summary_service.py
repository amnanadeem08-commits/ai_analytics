"""
services/ai_summary_service.py — AI Executive Summary Service.

Generates a domain-specific business narrative using the configured LLM.
Falls back to a rich statistical summary if no API key is configured,
so PPTX/PDF exports always contain meaningful content.

Fix applied:
  - Fallback now produces a full structured narrative (not an empty string)
    so export_service.py always has real text to embed in slides/PDF.
  - Added explicit API key validation with a clear error message.
  - Model pulled from config so it can be overridden via .env.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from config import AI_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY, AI_MODEL, AI_MAX_TOKENS

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AISummaryService:
    """Generates an executive summary narrative for the uploaded dataset."""

    def generate_summary(self, domain_cfg, kpis: list, analytics_report, filename: str) -> str:
        """
        Returns a rich narrative string.
        Tries LLM first; falls back to statistical summary on any failure.
        The fallback is intentionally detailed so exports are never empty.
        """
        try:
            summary = self._llm_summary(domain_cfg, kpis, analytics_report, filename)
            if summary and len(summary.strip()) > 50:
                return summary
        except Exception as exc:
            logger.warning("LLM summary failed, using statistical fallback: %s", exc)

        return self._statistical_summary(domain_cfg, kpis, analytics_report, filename)

    # ── LLM path ──────────────────────────────────────────────────────────────
    def _llm_summary(self, domain_cfg, kpis, analytics_report, filename: str) -> str:
        provider = AI_PROVIDER.lower().strip()

        if provider == "anthropic":
            if not ANTHROPIC_API_KEY:
                raise ValueError(
                    "ANTHROPIC_API_KEY is not set. "
                    "Add it to your .env file and restart the app."
                )
            return self._anthropic_summary(domain_cfg, kpis, analytics_report, filename)

        elif provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is not set. "
                    "Add it to your .env file and restart the app."
                )
            return self._openai_summary(domain_cfg, kpis, analytics_report, filename)

        else:
            raise ValueError(f"Unknown AI_PROVIDER: '{provider}'. Use 'anthropic' or 'openai'.")

    def _build_prompt(self, domain_cfg, kpis, analytics_report, filename: str) -> str:
        kpi_lines = "\n".join(
            f"  - {k.name}: {k.formatted}" for k in kpis[:12]
        )
        trend_lines = "\n".join(
            f"  - {t}" for t in (getattr(analytics_report, "trend_summary", []) or [])[:5]
        )
        anomaly_lines = "\n".join(
            f"  - {a}" for a in (getattr(analytics_report, "anomalies", []) or [])[:3]
        )
        return f"""You are a senior {domain_cfg.label} analyst writing an executive summary report.

Dataset: {filename}
Domain: {domain_cfg.label}
Records analysed: {getattr(analytics_report, 'row_count', 'N/A'):,}

KEY PERFORMANCE INDICATORS:
{kpi_lines or '  (none computed)'}

TREND SIGNALS:
{trend_lines or '  (none detected)'}

ANOMALIES:
{anomaly_lines or '  (none detected)'}

Write a 3–4 paragraph executive summary covering:
1. Overall business performance and what the data reveals
2. Key trends and their business implications
3. Risk areas or anomalies requiring attention
4. Top 2–3 actionable recommendations

Write in professional business English. Be specific, data-driven, and concise.
Do NOT use bullet points — write in flowing paragraphs only."""

    def _anthropic_summary(self, domain_cfg, kpis, analytics_report, filename: str) -> str:
        import anthropic
        client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            messages=[{"role": "user", "content": self._build_prompt(domain_cfg, kpis, analytics_report, filename)}],
        )
        return message.content[0].text.strip()

    def _openai_summary(self, domain_cfg, kpis, analytics_report, filename: str) -> str:
        from openai import OpenAI
        client   = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=AI_MAX_TOKENS,
            messages=[{"role": "user", "content": self._build_prompt(domain_cfg, kpis, analytics_report, filename)}],
        )
        return response.choices[0].message.content.strip()

    # ── Statistical fallback — always produces real content ───────────────────
    def _statistical_summary(self, domain_cfg, kpis, analytics_report, filename: str) -> str:
        """
        Rich structured fallback used when no API key is configured.
        Produces enough content for PPTX/PDF exports to be meaningful.
        """
        row_count   = getattr(analytics_report, "row_count", 0)
        col_count   = getattr(analytics_report, "col_count", 0)
        anomalies   = getattr(analytics_report, "anomalies", []) or []
        trends      = getattr(analytics_report, "trend_summary", []) or []

        # Build KPI narrative
        kpi_text = ""
        if kpis:
            top_kpis = kpis[:4]
            kpi_text = "Key performance indicators show: " + ", ".join(
                f"{k.name} at {k.formatted}" for k in top_kpis
            ) + "."

        # Build trend narrative
        trend_text = ""
        if trends:
            trend_text = f"Trend analysis identifies {len(trends)} significant signal(s), including: " + \
                         "; ".join(str(t) for t in trends[:3]) + "."
        else:
            trend_text = "No strong directional trends were detected in the current dataset."

        # Build anomaly narrative
        if anomalies:
            anomaly_text = (
                f"Anomaly detection flagged {len(anomalies)} area(s) requiring attention. "
                f"These may indicate data quality issues, outlier events, or genuine business extremes "
                f"that warrant further investigation before operational decisions are made."
            )
        else:
            anomaly_text = "No statistical anomalies were detected. Data distribution appears consistent across all measured dimensions."

        summary = f"""This {domain_cfg.label} report analyses {filename}, covering {row_count:,} records across {col_count} dimensions. The dataset has been automatically cleaned, validated, and scored for quality prior to analysis.

{kpi_text} {trend_text} The domain-specific KPI framework applied is aligned to {domain_cfg.label} best practices, ensuring that the metrics presented reflect operationally relevant performance indicators rather than generic statistical averages.

{anomaly_text} Particular attention should be given to columns flagged during quality scoring, as these may affect the reliability of aggregated KPI figures.

To unlock AI-generated narrative insights, executive commentary, and natural language recommendations, configure your API key: set ANTHROPIC_API_KEY (Anthropic Claude) or OPENAI_API_KEY (OpenAI GPT-4o) in the .env file and restart the application. The AI layer will then provide domain-specific strategic analysis, anomaly explanations, and prioritised action plans tailored to your {domain_cfg.label} context."""

        return summary
