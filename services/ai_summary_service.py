"""
ai_summary_service.py — Generates domain-aware executive summaries via LLM.
Composes a rich prompt from KPIs, analytics, and domain config.
"""

import logging
from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from services.analytics_service import AnalyticsReport
from utils.llm_client import call_llm
from config import AI_MAX_TOKENS

logger = logging.getLogger(__name__)


class AISummaryService:
    """Calls the configured LLM to produce a business executive summary."""

    def generate_summary(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        analytics: AnalyticsReport,
        dataset_name: str = "the dataset",
    ) -> str:
        prompt = self._build_prompt(domain, kpis, analytics, dataset_name)
        try:
            return self._call_llm(prompt)
        except Exception as e:
            logger.warning("LLM summary unavailable, using fallback summary: %s", e)
            return self._fallback_summary(kpis, analytics)

    def _build_prompt(
        self,
        domain: DomainConfig,
        kpis: list[KPIResult],
        analytics: AnalyticsReport,
        dataset_name: str,
    ) -> str:
        kpi_block = "\n".join(f"- {k.name}: {k.formatted}" for k in kpis)

        trend_block = ""
        if analytics.trends:
            trend_block = "\nKey trends:\n" + "\n".join(
                f"- {t.summary}" for t in analytics.trends[:5]
            )

        anomaly_block = ""
        if analytics.anomalies:
            anomaly_block = "\nAnomalies detected:\n" + "\n".join(
                f"- {a.column}: {len(a.anomaly_indices)} outlier(s)" for a in analytics.anomalies[:4]
            )

        top_cats_block = ""
        if analytics.top_categories:
            lines = []
            for col, series in list(analytics.top_categories.items())[:3]:
                top = series.head(3)
                lines.append(f"- {col}: top values are {', '.join(str(v) for v in top.index)}")
            top_cats_block = "\nTop categories:\n" + "\n".join(lines)

        return (
            f"You are acting as: {domain.analyst_persona}\n\n"
            f"Analyse this {domain.label} dataset named '{dataset_name}' and write a "
            f"concise executive summary (3–5 paragraphs). Use bullet points for key findings. "
            f"Focus on: {', '.join(domain.insights_focus)}.\n\n"
            f"KPIs:\n{kpi_block}"
            f"{trend_block}"
            f"{anomaly_block}"
            f"{top_cats_block}\n\n"
            f"Write in a professional business tone. Be specific, use the numbers provided. "
            f"End with 2–3 actionable recommendations."
        )

    def _call_llm(self, prompt: str) -> str:
        result = call_llm(prompt, max_tokens=AI_MAX_TOKENS)
        if not result:
            raise ValueError("LLM request failed or AI provider not configured.")
        return result

    def _fallback_summary(self, kpis: list[KPIResult], analytics: AnalyticsReport) -> str:
        lines = ["**Executive Summary** (AI offline — statistical summary)\n"]
        for k in kpis[:6]:
            lines.append(f"- **{k.name}**: {k.formatted}")
        if analytics.trends:
            lines.append("\n**Trends:**")
            for t in analytics.trends[:3]:
                lines.append(f"- {t.summary}")
        return "\n".join(lines)
