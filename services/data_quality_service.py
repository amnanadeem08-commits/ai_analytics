"""
data_quality_service.py — Rates dataset completeness, consistency, and coverage.
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ColumnQuality:
    """Per-column quality breakdown."""

    name: str
    completeness: float
    consistency: float
    issues: list[str] = field(default_factory=list)


@dataclass
class DataQualityReport:
    """Overall and dimensional data quality scores (0–100)."""

    overall_score: float
    completeness: float
    consistency: float
    coverage: float
    validity: float
    anomaly_score: float
    grade: str
    row_count: int
    column_count: int
    column_details: list[ColumnQuality] = field(default_factory=list)
    summary: str = ""


class DataQualityService:
    """Computes a weighted data quality score for a cleaned DataFrame."""

    def score(self, df: pd.DataFrame) -> DataQualityReport:
        """
        Evaluate completeness, consistency, and coverage; return a typed report.
        """
        if df is None or df.empty:
            return DataQualityReport(
                overall_score=0.0,
                completeness=0.0,
                consistency=0.0,
                coverage=0.0,
                validity=0.0,
                anomaly_score=0.0,
                grade="F",
                row_count=0,
                column_count=0,
                summary="No data available to score.",
            )

        column_details: list[ColumnQuality] = []
        completeness_scores: list[float] = []
        consistency_scores: list[float] = []
        validity_scores: list[float] = []
        anomaly_scores: list[float] = []

        for col in df.columns:
            col_comp, col_cons, col_valid, col_anom, issues = self._score_column(df[col], col)
            column_details.append(ColumnQuality(
                name=col,
                completeness=col_comp,
                consistency=col_cons,
                issues=issues,
            ))
            completeness_scores.append(col_comp)
            consistency_scores.append(col_cons)
            validity_scores.append(col_valid)
            anomaly_scores.append(col_anom)

        completeness = float(np.mean(completeness_scores)) if completeness_scores else 0.0
        consistency = float(np.mean(consistency_scores)) if consistency_scores else 0.0
        validity = float(np.mean(validity_scores)) if validity_scores else 0.0
        anomaly_score = float(np.mean(anomaly_scores)) if anomaly_scores else 0.0
        coverage = self._coverage_score(df)

        overall = (
            0.30 * completeness
            + 0.25 * consistency
            + 0.20 * validity
            + 0.15 * anomaly_score
            + 0.10 * coverage
        )
        grade = self._grade(overall)
        summary = self._build_summary(
            overall, completeness, consistency, validity, anomaly_score, coverage, grade
        )

        return DataQualityReport(
            overall_score=round(overall, 1),
            completeness=round(completeness, 1),
            consistency=round(consistency, 1),
            coverage=round(coverage, 1),
            validity=round(validity, 1),
            anomaly_score=round(anomaly_score, 1),
            grade=grade,
            row_count=len(df),
            column_count=len(df.columns),
            column_details=column_details,
            summary=summary,
        )

    def _score_column(
        self, series: pd.Series, name: str
    ) -> tuple[float, float, float, float, list[str]]:
        """Return completeness, consistency, validity, anomaly score, and issues."""
        issues: list[str] = []
        non_null = series.notna().sum()
        completeness = (non_null / len(series)) * 100 if len(series) else 0.0

        if completeness < 70:
            issues.append(f"High missing rate ({100 - completeness:.0f}% null)")

        consistency = 100.0
        validity = 100.0
        anomaly_score = 100.0
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if len(valid) > 0:
                if np.isinf(valid).any():
                    issues.append("Infinite numeric values")
                    validity -= 35
                q1, q3 = valid.quantile(0.25), valid.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    outlier_pct = (
                        ((valid < q1 - 3 * iqr) | (valid > q3 + 3 * iqr)).mean() * 100
                    )
                    if outlier_pct > 5:
                        issues.append(f"{outlier_pct:.0f}% extreme outliers")
                        consistency -= min(30, outlier_pct * 2)
                    anomaly_score -= min(45, outlier_pct * 3)
        elif pd.api.types.is_object_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            valid = series.dropna().astype(str)
            if len(valid):
                blank_pct = valid.str.strip().eq("").mean() * 100
                if blank_pct > 0:
                    issues.append(f"{blank_pct:.0f}% blank strings")
                    validity -= min(35, blank_pct * 2)
                mixed_numeric = valid.str.match(r"^-?\d+\.?\d*$", na=False).mean()
                if 0.05 < mixed_numeric < 0.95:
                    issues.append("Mixed numeric/text values")
                    consistency -= 25
                    validity -= 15
                dup_rate = (1 - valid.nunique() / len(valid)) * 100
                if dup_rate > 90 and valid.nunique() < 3:
                    issues.append("Very low cardinality (mostly one value)")
                    consistency -= 15

        consistency = max(0.0, min(100.0, consistency))
        validity = max(0.0, min(100.0, validity))
        anomaly_score = max(0.0, min(100.0, anomaly_score))
        return completeness, consistency, validity, anomaly_score, issues

    def _coverage_score(self, df: pd.DataFrame) -> float:
        """Score temporal and categorical breadth of the dataset."""
        score = 50.0
        date_cols = df.select_dtypes(include=["datetime64"]).columns
        if len(date_cols):
            span = (df[date_cols[0]].max() - df[date_cols[0]].min()).days
            if span >= 365:
                score += 30
            elif span >= 90:
                score += 20
            elif span >= 30:
                score += 10
        num_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if len(num_cols) >= 3:
            score += 10
        if len(cat_cols) >= 1:
            avg_unique = np.mean([df[c].nunique() for c in cat_cols[:5]])
            if avg_unique >= 5:
                score += 10
        return min(100.0, score)

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def _build_summary(
        self,
        overall: float,
        completeness: float,
        consistency: float,
        validity: float,
        anomaly_score: float,
        coverage: float,
        grade: str,
    ) -> str:
        parts = [f"Overall quality grade **{grade}** ({overall:.0f}/100)."]
        if completeness < 80:
            parts.append("Completeness needs attention — several columns have missing values.")
        if consistency < 80:
            parts.append("Consistency issues detected — review outliers and mixed types.")
        if validity < 85:
            parts.append("Validity issues detected - review blank strings, infinities, and type coercion.")
        if anomaly_score < 85:
            parts.append("Anomalies are materially affecting data reliability.")
        if coverage < 70:
            parts.append("Limited temporal or categorical coverage for deep trend analysis.")
        if overall >= 85:
            parts.append("Dataset is in good shape for analytics and AI insights.")
        return " ".join(parts)
