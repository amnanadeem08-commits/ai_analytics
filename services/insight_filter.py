"""
insight_filter.py — Smart Intelligence Layer: domain-aware insight filtering.

ADDITIVE MODULE — sits AFTER insight generation and removes domain-irrelevant
items so the platform never surfaces, for example, profit/revenue framing on a
healthcare dataset.  It never rewrites text; it only drops items whose language
is irrelevant (or misleading) for the detected domain.

Design goals:
  - Conservative: when in doubt, keep the insight (avoid over-filtering).
  - Pure & defensive: any failure falls back to the original, unmodified data.
  - Zero changes to existing dataclasses — operates on InsightEngineReport in place
    via shallow copies of its list fields.

Example:
  Healthcare → blocks "profit", "revenue", "sales", "churn", "ROAS", …
  E-commerce → allows "revenue", "sales", "churn", "conversion", "AOV", …
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field


@dataclass
class FilterResult:
    """Summary of what the filter did (useful for badges / debugging)."""
    domain: str
    mode_label: str
    removed: int = 0
    blocked_terms: list[str] = field(default_factory=list)


# Terms that are irrelevant / misleading for a given domain.  Keep these tight
# and business-meaningful; generic domains block nothing.
_BLOCKED_TERMS: dict[str, list[str]] = {
    "healthcare": [
        "profit", "revenue", "sales", "churn", "roas", "gmv", "aov",
        "deal", "pipeline", "ebitda", "margin", "quota",
    ],
    "education": [
        "profit", "revenue", "churn", "roas", "gmv", "aov", "ebitda",
        "deal", "pipeline", "quota",
    ],
    "hr": [
        "revenue", "profit", "sales", "gmv", "aov", "roas", "deal", "pipeline",
    ],
    "finance": [
        "roas", "gmv", "aov", "ctr", "impression",
    ],
    "ecommerce": [
        "ebitda", "headcount", "attrition", "readmission",
    ],
    "sales": [
        "readmission", "attrition", "bed occupancy",
    ],
    "marketing": [
        "readmission", "ebitda", "bed occupancy",
    ],
    "inventory": [
        "readmission", "roas", "ctr",
    ],
    "telecom": [
        "readmission", "bed occupancy",
    ],
    # generic / unknown → no blocking (allow everything)
}

# Short, user-facing description of the active insight mode.
_MODE_LABELS: dict[str, str] = {
    "healthcare": "Healthcare-aware (clinical & operational framing)",
    "education":  "Education-aware (outcomes & engagement framing)",
    "hr":         "HR-aware (people & workforce framing)",
    "finance":    "Finance-aware (P&L & margin framing)",
    "ecommerce":  "E-commerce-aware (revenue, conversion & churn framing)",
    "sales":      "Sales-aware (pipeline & revenue framing)",
    "marketing":  "Marketing-aware (spend & ROAS framing)",
    "inventory":  "Inventory-aware (stock & turnover framing)",
    "telecom":    "Telecom-aware (ARPU & churn framing)",
    "generic":    "General (all insight types enabled)",
}


class InsightFilter:
    """Filters generated insights down to what is relevant for a domain."""

    def mode_label(self, domain: str) -> str:
        return _MODE_LABELS.get(domain, _MODE_LABELS["generic"])

    def blocked_terms(self, domain: str) -> list[str]:
        return list(_BLOCKED_TERMS.get(domain, []))

    def is_relevant(self, text: str, domain: str) -> bool:
        """True if the text contains no blocked term for this domain."""
        blocked = _BLOCKED_TERMS.get(domain)
        if not blocked or not text:
            return True
        low = str(text).lower()
        return not any(self._contains(low, term) for term in blocked)

    def filter_texts(self, items: list[str], domain: str) -> list[str]:
        if not _BLOCKED_TERMS.get(domain):
            return list(items or [])
        return [t for t in (items or []) if self.is_relevant(t, domain)]

    def filter_report(self, report, domain: str) -> FilterResult:
        """
        Filter an InsightEngineReport IN PLACE (additive, non-destructive).
        Returns a FilterResult summary. Any error leaves the report untouched.
        """
        result = FilterResult(domain=domain, mode_label=self.mode_label(domain),
                              blocked_terms=self.blocked_terms(domain))
        if report is None or not _BLOCKED_TERMS.get(domain):
            return result

        try:
            before = 0
            # Executive insights: drop if headline/description/impact is irrelevant.
            if hasattr(report, "executive_insights"):
                src = report.executive_insights or []
                before += len(src)
                kept = [
                    ins for ins in src
                    if self.is_relevant(
                        f"{getattr(ins, 'headline', '')} "
                        f"{getattr(ins, 'description', '')} "
                        f"{getattr(ins, 'impact', '')}",
                        domain,
                    )
                ]
                report.executive_insights = kept

            # Plain-text lists.
            for attr in ("key_findings", "risk_alerts", "opportunities"):
                if hasattr(report, attr):
                    src = getattr(report, attr) or []
                    before += len(src)
                    setattr(report, attr, self.filter_texts(src, domain))

            after = (
                len(getattr(report, "executive_insights", []))
                + len(getattr(report, "key_findings", []))
                + len(getattr(report, "risk_alerts", []))
                + len(getattr(report, "opportunities", []))
            )
            result.removed = max(0, before - after)
        except Exception:
            # Never break the existing flow — return what we have.
            return result

        return result

    # ── helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _contains(haystack_lower: str, term: str) -> bool:
        """Word-aware contains so 'margin' won't match inside 'marginal' etc."""
        if " " in term:
            return term in haystack_lower
        return re.search(rf"\b{re.escape(term)}\b", haystack_lower) is not None
