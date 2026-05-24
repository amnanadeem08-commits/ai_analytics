"""
anomaly_narration_service.py — Natural-language explanations for detected anomalies.
"""

import logging
from dataclasses import dataclass

from services.analytics_service import AnomalyResult
from services.domain_service import DomainConfig
from utils.llm_client import call_llm

logger = logging.getLogger(__name__)


@dataclass
class AnomalyNarration:
    """Narrated explanation for one anomaly cluster."""

    column: str
    narration: str
    severity: str  # "high" | "medium" | "low"


class AnomalyNarrationService:
    """Turns statistical anomaly results into business-readable narratives."""

    def narrate(
        self,
        anomalies: list[AnomalyResult],
        domain: DomainConfig,
    ) -> list[AnomalyNarration]:
        """
        Generate one narration per anomaly column; LLM with statistical fallback.
        """
        if not anomalies:
            return []

        narrations: list[AnomalyNarration] = []
        for anomaly in anomalies[:8]:
            narration = self._narrate_one(anomaly, domain)
            count = len(anomaly.anomaly_indices)
            severity = "high" if count > 10 else ("medium" if count > 3 else "low")
            narrations.append(AnomalyNarration(
                column=anomaly.column,
                narration=narration,
                severity=severity,
            ))

        return narrations

    def _narrate_one(self, anomaly: AnomalyResult, domain: DomainConfig) -> str:
        """Narrate a single anomaly via LLM or template."""
        sample_vals = ", ".join(f"{v:.2g}" for v in anomaly.anomaly_values[:5])
        prompt = (
            f"Explain in 2-3 sentences for a {domain.label} audience:\n"
            f"Column '{anomaly.column}' has {len(anomaly.anomaly_indices)} outliers "
            f"outside [{anomaly.threshold_lower:.2f}, {anomaly.threshold_upper:.2f}]. "
            f"Sample values: {sample_vals}. "
            f"What might this mean and what should an analyst check?"
        )
        reply = call_llm(prompt, system_prompt=domain.analyst_persona, max_tokens=256)
        if reply:
            return reply.strip()

        return (
            f"**{anomaly.column.replace('_', ' ').title()}** shows "
            f"{len(anomaly.anomaly_indices)} value(s) outside the expected range "
            f"({anomaly.threshold_lower:.2f} to {anomaly.threshold_upper:.2f}). "
            f"This may indicate data entry errors, one-off events, or genuine extremes — "
            f"verify source records before acting on these points."
        )
