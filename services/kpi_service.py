"""
kpi_service.py — Domain-aware KPI detection and computation.
Identifies and calculates the most relevant metrics for the active domain.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from services.domain_service import DomainConfig


@dataclass
class KPIResult:
    name: str
    value: float | int | str
    formatted: str
    delta: float | None = None        # period-over-period change
    delta_pct: float | None = None
    is_currency: bool = False
    is_pct: bool = False
    column: str | None = None


class KPIService:
    """Computes KPIs from the cleaned DataFrame, guided by DomainConfig."""

    def compute(self, df: pd.DataFrame, domain: DomainConfig) -> list[KPIResult]:
        kpis: list[KPIResult] = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        # ── Always-available base KPIs ─────────────────────────────────────────
        kpis.append(KPIResult(
            name="Total Records",
            value=len(df),
            formatted=f"{len(df):,}",
        ))

        # ── Domain keyword matching ────────────────────────────────────────────
        matched = self._match_domain_columns(df, domain)

        for kpi_name, col in matched.items():
            if col not in df.columns:
                continue

            series = df[col].dropna()
            if not pd.api.types.is_numeric_dtype(series):
                continue

            total = series.sum()
            is_currency = any(k in kpi_name.lower() for k in ["revenue", "profit", "cost", "expense", "value", "spend", "salary", "arpu"])
            is_pct = any(k in kpi_name.lower() for k in ["rate", "ratio", "pct", "%", "margin"])

            if is_pct:
                val = series.mean() * (100 if series.max() <= 1.0 else 1)
                fmt = f"{val:.1f}%"
            elif is_currency:
                fmt = self._fmt_currency(total)
            else:
                fmt = f"{total:,.0f}"

            kpis.append(KPIResult(
                name=kpi_name,
                value=total,
                formatted=fmt,
                is_currency=is_currency,
                is_pct=is_pct,
                column=col,
            ))

        # ── Numeric summary KPIs ───────────────────────────────────────────────
        for col in numeric_cols[:8]:  # cap at 8 extra numeric KPIs
            if any(k.column == col for k in kpis):
                continue
            series = df[col].dropna()
            kpis.append(KPIResult(
                name=f"Avg {col.replace('_', ' ').title()}",
                value=series.mean(),
                formatted=f"{series.mean():,.2f}",
                column=col,
            ))

        # ── Time range KPI ─────────────────────────────────────────────────────
        if date_cols:
            dcol = date_cols[0]
            min_d = df[dcol].min()
            max_d = df[dcol].max()
            kpis.append(KPIResult(
                name="Date Range",
                value=str(min_d.date()),
                formatted=f"{min_d.strftime('%b %Y')} – {max_d.strftime('%b %Y')}",
            ))

        return kpis[:12]  # UI cap

    def _match_domain_columns(self, df: pd.DataFrame, domain: DomainConfig) -> dict[str, str]:
        """Return {kpi_display_name: column_name} for domain keyword matches."""
        mapping: dict[str, str] = {}
        for kw in domain.kpi_columns:
            for col in df.columns:
                if kw in col and col not in mapping.values():
                    display = col.replace("_", " ").title()
                    mapping[display] = col
                    break
        return mapping

    @staticmethod
    def _fmt_currency(value: float) -> str:
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        return f"${value:.2f}"
