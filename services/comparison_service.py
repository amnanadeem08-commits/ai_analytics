"""
comparison_service.py — Side-by-side KPI comparison for two datasets.
"""

import logging
from dataclasses import dataclass, field

import pandas as pd

from services.domain_service import DomainConfig
from services.kpi_service import KPIService, KPIResult

logger = logging.getLogger(__name__)


@dataclass
class KPIComparison:
    """Single KPI delta between baseline and comparison dataset."""

    name: str
    baseline_value: str
    compare_value: str
    delta_pct: float | None
    direction: str  # "better" | "worse" | "neutral"


@dataclass
class ComparisonReport:
    """Full comparison result between two datasets."""

    baseline_label: str
    compare_label: str
    baseline_rows: int
    compare_rows: int
    kpi_comparisons: list[KPIComparison] = field(default_factory=list)
    summary: str = ""


class ComparisonService:
    """Compares KPIs from two DataFrames under the same domain config."""

    def __init__(self):
        self._kpi_svc = KPIService()

    def compare(
        self,
        df_baseline: pd.DataFrame,
        df_compare: pd.DataFrame,
        domain: DomainConfig,
        baseline_label: str = "Dataset A",
        compare_label: str = "Dataset B",
    ) -> ComparisonReport:
        """
        Compute KPIs for both datasets and align by metric name.
        """
        if df_baseline is None or df_baseline.empty or df_compare is None or df_compare.empty:
            return ComparisonReport(
                baseline_label=baseline_label,
                compare_label=compare_label,
                baseline_rows=0,
                compare_rows=0,
                summary="Both datasets must be non-empty for comparison.",
            )

        kpis_a = {k.name: k for k in self._kpi_svc.compute(df_baseline, domain)}
        kpis_b = {k.name: k for k in self._kpi_svc.compute(df_compare, domain)}

        comparisons: list[KPIComparison] = []
        shared_names = sorted(set(kpis_a) & set(kpis_b))

        for name in shared_names:
            ka, kb = kpis_a[name], kpis_b[name]
            delta_pct, direction = self._delta(ka, kb)
            comparisons.append(KPIComparison(
                name=name,
                baseline_value=ka.formatted,
                compare_value=kb.formatted,
                delta_pct=delta_pct,
                direction=direction,
            ))

        summary = (
            f"Compared **{len(comparisons)}** shared KPIs across "
            f"{baseline_label} ({len(df_baseline):,} rows) vs "
            f"{compare_label} ({len(df_compare):,} rows)."
        )

        return ComparisonReport(
            baseline_label=baseline_label,
            compare_label=compare_label,
            baseline_rows=len(df_baseline),
            compare_rows=len(df_compare),
            kpi_comparisons=comparisons,
            summary=summary,
        )

    def _delta(self, a: KPIResult, b: KPIResult) -> tuple[float | None, str]:
        """Compute percent change and direction when both values are numeric."""
        try:
            va = float(a.value) if isinstance(a.value, (int, float)) else float(str(a.value).replace(",", ""))
            vb = float(b.value) if isinstance(b.value, (int, float)) else float(str(b.value).replace(",", ""))
        except (TypeError, ValueError):
            return None, "neutral"

        if va == 0:
            return None, "neutral"

        pct = ((vb - va) / abs(va)) * 100
        direction = "better" if pct > 0 else ("worse" if pct < 0 else "neutral")
        return round(pct, 1), direction
