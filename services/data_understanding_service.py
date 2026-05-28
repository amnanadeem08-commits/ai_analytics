"""
data_understanding_service.py - Business-oriented dataset profiling.

This service translates raw dataframe structure into BI concepts: measures,
dimensions, dates, identifier fields, KPI candidates, and chartable columns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


KPI_HINTS = {
    "revenue", "sales", "amount", "profit", "margin", "cost", "expense", "order",
    "customer", "churn", "fraud", "conversion", "quantity", "price", "salary",
    "score", "rate", "lead", "pipeline", "budget", "spend", "arpu",
}

ID_HINTS = {"id", "uuid", "guid", "code", "number", "serial"}


@dataclass(frozen=True)
class ColumnUnderstanding:
    name: str
    role: str
    dtype: str
    unique_count: int
    missing_pct: float
    business_score: float
    notes: tuple[str, ...] = ()


@dataclass
class DataUnderstandingReport:
    row_count: int
    column_count: int
    measures: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    date_columns: list[str] = field(default_factory=list)
    kpi_candidates: list[str] = field(default_factory=list)
    id_columns: list[str] = field(default_factory=list)
    high_cardinality_dimensions: list[str] = field(default_factory=list)
    empty_columns: list[str] = field(default_factory=list)
    column_details: list[ColumnUnderstanding] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"{self.row_count:,} rows, {self.column_count:,} columns, "
            f"{len(self.measures)} measures, {len(self.dimensions)} dimensions, "
            f"{len(self.date_columns)} date fields."
        )


class DataUnderstandingService:
    """Infer BI semantics from a pandas DataFrame."""

    def profile(self, df: pd.DataFrame) -> DataUnderstandingReport:
        if df is None or df.empty:
            return DataUnderstandingReport(row_count=0, column_count=0)

        report = DataUnderstandingReport(row_count=len(df), column_count=len(df.columns))

        for col in df.columns:
            series = df[col]
            lower = col.lower()
            unique_count = int(series.nunique(dropna=True))
            missing_pct = float(series.isna().mean() * 100)
            dtype = self._semantic_dtype(series)
            role = self._role(col, series, dtype, unique_count, len(df))
            score = self._business_score(col, role, series)
            notes = self._notes(series, role, unique_count, missing_pct, len(df))

            detail = ColumnUnderstanding(
                name=col,
                role=role,
                dtype=dtype,
                unique_count=unique_count,
                missing_pct=round(missing_pct, 1),
                business_score=round(score, 1),
                notes=tuple(notes),
            )
            report.column_details.append(detail)

            if role == "measure":
                report.measures.append(col)
            elif role == "dimension":
                report.dimensions.append(col)
            elif role == "date":
                report.date_columns.append(col)
            elif role == "identifier":
                report.id_columns.append(col)

            if unique_count == 0:
                report.empty_columns.append(col)
            if role == "dimension" and unique_count > 50:
                report.high_cardinality_dimensions.append(col)
            if score >= 6:
                report.kpi_candidates.append(col)

        report.kpi_candidates = sorted(
            report.kpi_candidates,
            key=lambda c: next(d.business_score for d in report.column_details if d.name == c),
            reverse=True,
        )[:8]
        return report

    def _semantic_dtype(self, series: pd.Series) -> str:
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        sample = series.dropna().astype(str).head(300)
        if not sample.empty:
            parsed_dates = pd.to_datetime(sample, errors="coerce")
            if parsed_dates.notna().mean() >= 0.8:
                return "datetime"
            parsed_numbers = pd.to_numeric(sample.str.replace(",", "", regex=False), errors="coerce")
            if parsed_numbers.notna().mean() >= 0.85:
                return "numeric_text"
        return "categorical"

    def _role(self, col: str, series: pd.Series, dtype: str, unique_count: int, row_count: int) -> str:
        lower = col.lower()
        if dtype == "datetime":
            return "date"
        if any(h == lower or lower.endswith(f"_{h}") or lower.startswith(f"{h}_") for h in ID_HINTS):
            if unique_count >= max(10, row_count * 0.8):
                return "identifier"
        if dtype in {"numeric", "numeric_text"}:
            if unique_count <= 20 and not any(h in lower for h in KPI_HINTS):
                return "dimension"
            return "measure"
        if unique_count >= max(10, row_count * 0.8):
            return "identifier"
        return "dimension"

    def _business_score(self, col: str, role: str, series: pd.Series) -> float:
        lower = col.lower()
        score = 0.0
        if role == "measure":
            score += 4.0
        if any(h in lower for h in KPI_HINTS):
            score += 5.0
        if any(h in lower for h in ("total", "avg", "average", "rate", "pct", "amount")):
            score += 1.5
        if pd.api.types.is_numeric_dtype(series):
            std = float(series.dropna().std() or 0)
            if std > 0:
                score += min(2.0, np.log1p(std) / 4)
        return score

    def _notes(
        self,
        series: pd.Series,
        role: str,
        unique_count: int,
        missing_pct: float,
        row_count: int,
    ) -> list[str]:
        notes: list[str] = []
        if missing_pct > 20:
            notes.append("missing values need review")
        if unique_count == 0:
            notes.append("empty column")
        if role == "identifier":
            notes.append("excluded from metric charts")
        if role == "dimension" and unique_count > 50:
            notes.append("high-cardinality dimension; use top-N filters")
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if len(valid) > 10:
                q1, q3 = valid.quantile(0.25), valid.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    outlier_pct = ((valid < q1 - 3 * iqr) | (valid > q3 + 3 * iqr)).mean() * 100
                    if outlier_pct > 2:
                        notes.append(f"{outlier_pct:.1f}% possible anomalies")
        if row_count > 10000 and role == "measure":
            notes.append("aggregate before visualization")
        return notes
