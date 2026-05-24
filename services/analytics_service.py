"""
analytics_service.py — Statistical analysis, trend detection, anomaly flagging.
Returns structured insight objects consumed by the AI summary and charts.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from scipy import stats
from config import OUTLIER_STD_MULTIPLIER


@dataclass
class TrendResult:
    column: str
    date_column: str
    direction: str       # "up" | "down" | "flat"
    slope: float
    r_squared: float
    summary: str


@dataclass
class AnomalyResult:
    column: str
    anomaly_indices: list[int]
    anomaly_values: list[float]
    threshold_upper: float
    threshold_lower: float
    severity: str = "medium"  # "critical" | "high" | "medium" | "low"
    anomaly_type: str = "outlier"  # "outlier" | "sudden_change" | "deviation"


@dataclass
class AnalyticsReport:
    numeric_summary: pd.DataFrame | None = None
    correlations: pd.DataFrame | None = None
    trends: list[TrendResult] = field(default_factory=list)
    anomalies: list[AnomalyResult] = field(default_factory=list)
    top_categories: dict[str, pd.Series] = field(default_factory=dict)
    distribution_skew: dict[str, str] = field(default_factory=dict)


class AnalyticsService:
    """Runs the full analytical pipeline on a cleaned DataFrame."""

    def analyse(self, df: pd.DataFrame) -> AnalyticsReport:
        report = AnalyticsReport()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        if numeric_cols:
            report.numeric_summary = df[numeric_cols].describe().T
            report.correlations = (
                df[numeric_cols].corr() if len(numeric_cols) > 1 else None
            )
            report.anomalies = self._detect_anomalies(df, numeric_cols)
            report.distribution_skew = self._classify_skew(df, numeric_cols)

        if date_cols and numeric_cols:
            report.trends = self._detect_trends(df, date_cols[0], numeric_cols[:5])

        for col in cat_cols[:6]:
            report.top_categories[col] = df[col].value_counts().head(10)

        return report

    def _detect_anomalies(
        self, df: pd.DataFrame, cols: list[str]
    ) -> list[AnomalyResult]:
        results = []
        for col in cols:
            series = df[col].dropna()
            mean, std = series.mean(), series.std()
            if std == 0:
                continue
            upper = mean + OUTLIER_STD_MULTIPLIER * std
            lower = mean - OUTLIER_STD_MULTIPLIER * std
            mask = (df[col] > upper) | (df[col] < lower)
            idxs = df.index[mask].tolist()
            if idxs:
                # Calculate severity based on count and magnitude
                count = len(idxs)
                max_val = max(abs(v - mean) for v in df.loc[idxs, col])
                magnitude = max_val / (std + 1e-9)
                
                if count >= len(series) * 0.1 or magnitude > 5 * std:
                    severity = "critical"
                elif count >= len(series) * 0.05 or magnitude > 4 * std:
                    severity = "high"
                elif count >= len(series) * 0.02 or magnitude > 3 * std:
                    severity = "medium"
                else:
                    severity = "low"
                
                results.append(AnomalyResult(
                    column=col,
                    anomaly_indices=idxs[:20],
                    anomaly_values=df.loc[idxs[:20], col].tolist(),
                    threshold_upper=upper,
                    threshold_lower=lower,
                    severity=severity,
                    anomaly_type="outlier",
                ))
        return results

    def _detect_trends(
        self, df: pd.DataFrame, date_col: str, num_cols: list[str]
    ) -> list[TrendResult]:
        results = []
        df_sorted = df.sort_values(date_col).copy()
        x = np.arange(len(df_sorted))

        for col in num_cols:
            y = df_sorted[col].ffill().values
            if len(y) < 3:
                continue
            slope, intercept, r, p, se = stats.linregress(x, y)
            r_sq = r ** 2
            direction = "up" if slope > 0 else ("down" if slope < 0 else "flat")
            pct_change = (slope * len(x)) / (abs(y.mean()) + 1e-9) * 100
            results.append(TrendResult(
                column=col,
                date_column=date_col,
                direction=direction,
                slope=slope,
                r_squared=r_sq,
                summary=(
                    f"{col.replace('_', ' ').title()} is trending {direction} "
                    f"({pct_change:+.1f}% over period, R²={r_sq:.2f})"
                ),
            ))
        return results

    def _classify_skew(
        self, df: pd.DataFrame, cols: list[str]
    ) -> dict[str, str]:
        result = {}
        for col in cols:
            sk = df[col].skew()
            if sk > 1:
                result[col] = "right-skewed (long tail above median)"
            elif sk < -1:
                result[col] = "left-skewed (long tail below median)"
            else:
                result[col] = "approximately symmetric"
        return result
