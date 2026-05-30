"""
domain_detector.py — Smart Intelligence Layer: automatic domain detection.

ADDITIVE MODULE — does not replace the existing `DomainService.auto_detect`.
It wraps the same keyword knowledge (DOMAIN_CONFIGS) and adds:
  - a confidence score (0–100)
  - the keywords that matched
  - a human-readable label

Returns a `DomainSignal` so callers (pipeline, sidebar badges) can show
"Detected Domain / Confidence" without changing any existing logic.

Detection strategy (rules + simple heuristics):
  1. Keyword scoring — substring + whole-token matches of column names against
     each domain's `kpi_columns` vocabulary.
  2. Margin/share heuristics — confidence rises with the number of matches and
     how clearly the top domain beats the runner-up.
  3. Graceful fallback — no strong signal → "generic" (General) at low confidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from services.domain_service import DOMAIN_CONFIGS


@dataclass
class DomainSignal:
    """Result of automatic domain detection."""
    domain: str                              # domain key, e.g. "ecommerce"
    label: str                               # human label, e.g. "E-commerce Analytics"
    confidence: float                        # 0–100
    matched_keywords: list[str] = field(default_factory=list)
    scores: dict[str, int] = field(default_factory=dict)
    is_confident: bool = False               # True when confidence >= threshold

    @property
    def confidence_pct(self) -> str:
        return f"{self.confidence:.0f}%"


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_CONFIDENT_THRESHOLD = 60.0


class DomainDetector:
    """Rule + heuristic domain detector returning a DomainSignal."""

    def __init__(self, confident_threshold: float = _CONFIDENT_THRESHOLD):
        self.confident_threshold = confident_threshold

    # ── public API ───────────────────────────────────────────────────────────
    def detect(self, df: pd.DataFrame | None) -> DomainSignal:
        if df is None or getattr(df, "empty", True) or len(df.columns) == 0:
            return DomainSignal(domain="generic", label=self._label("generic"),
                                confidence=0.0, is_confident=False)

        columns = [str(c).lower() for c in df.columns]
        col_text = " ".join(columns)
        col_tokens = set(_TOKEN_RE.findall(col_text))

        scores: dict[str, int] = {}
        matched: dict[str, list[str]] = {}

        for key, cfg in DOMAIN_CONFIGS.items():
            if key == "generic" or not cfg.kpi_columns:
                continue
            hits: list[str] = []
            for kw in cfg.kpi_columns:
                kw_l = kw.lower()
                # substring match (matches existing auto_detect behaviour) …
                if kw_l in col_text:
                    hits.append(kw_l)
                # … plus whole-token match for robustness (e.g. "win" token)
                elif kw_l in col_tokens:
                    hits.append(kw_l)
            if hits:
                scores[key] = len(hits)
                matched[key] = sorted(set(hits))

        if not scores:
            return DomainSignal(domain="generic", label=self._label("generic"),
                                confidence=30.0, scores={}, is_confident=False)

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        best_key, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0

        confidence = self._confidence(best_score, second_score)

        return DomainSignal(
            domain=best_key,
            label=self._label(best_key),
            confidence=confidence,
            matched_keywords=matched.get(best_key, []),
            scores=scores,
            is_confident=confidence >= self.confident_threshold,
        )

    # ── helpers ────────────────────────────────────────────────────────────────
    def _confidence(self, best: int, second: int) -> float:
        """Map match counts + lead margin to a 0–100 confidence score."""
        base = 50.0 + best * 9.0           # more matched keywords → higher base
        margin_bonus = 15.0 if best > second else 4.0
        score = base + margin_bonus
        return float(max(50.0, min(95.0, round(score))))

    def _label(self, key: str) -> str:
        cfg = DOMAIN_CONFIGS.get(key)
        return cfg.label if cfg else "General Analytics"
