"""
insight_detector.py — Advanced anomaly and pattern detection engine.

Detects outliers, sudden changes, fraud patterns, missing value anomalies,
and abnormal churn with severity scoring and confidence levels.
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass, field
from typing import Literal
from config import OUTLIER_STD_MULTIPLIER


@dataclass
class Insight:
    """A single business insight with confidence and severity."""
    insight_type: Literal["anomaly", "trend", "pattern", "fraud", "churn", "missing"]
    title: str
    description: str
    column: str
    severity: Literal["critical", "high", "medium", "low"]
    confidence: float  # 0.0 to 1.0
    affected_rows: list[int] = field(default_factory=list)
    affected_count: int = 0
    metric_value: float | None = None
    baseline_value: float | None = None
    change_pct: float | None = None
    recommendation: str = ""
    domain_relevance: list[str] = field(default_factory=list)


@dataclass
class InsightReport:
    """Complete insight report for a dataset."""
    insights: list[Insight] = field(default_factory=list)
    total_anomalies: int = 0
    critical_count: int = 0
    high_count: int = 0
    data_quality_issues: int = 0
    fraud_indicators: int = 0
    churn_alerts: int = 0

    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0

    @property
    def summary(self) -> str:
        if not self.insights:
            return "No significant patterns detected in the data."
        
        parts = [f"Detected {len(self.insights)} insights:"]
        if self.critical_count:
            parts.append(f"🔴 {self.critical_count} critical")
        if self.high_count:
            parts.append(f"🟠 {self.high_count} high priority")
        if self.fraud_indicators:
            parts.append(f"⚠️ {self.fraud_indicators} fraud indicators")
        if self.churn_alerts:
            parts.append(f"📉 {self.churn_alerts} churn alerts")
        return " ".join(parts)


class InsightDetector:
    """Advanced pattern and anomaly detection with business context."""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination

    def detect_all(
        self,
        df: pd.DataFrame,
        domain_key: str = "generic",
        date_column: str | None = None,
        churn_column: str | None = None,
    ) -> InsightReport:
        """Run all detection algorithms and return comprehensive insights."""
        report = InsightReport()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        if not date_column and date_cols:
            date_column = date_cols[0]

        # Run detection algorithms
        report.insights.extend(self._detect_zscore_outliers(df, numeric_cols))
        report.insights.extend(self._detect_iqr_outliers(df, numeric_cols))
        report.insights.extend(self._detect_sudden_changes(df, numeric_cols, date_column))
        report.insights.extend(self._detect_missing_patterns(df))
        report.insights.extend(self._detect_distribution_shifts(df, numeric_cols))

        # Domain-specific detections
        if churn_column or self._find_churn_column(df):
            churn_col = churn_column or self._find_churn_column(df)
            report.insights.extend(self._detect_abnormal_churn(df, churn_col, date_column))

        report.insights.extend(self._detect_fraud_patterns(df, numeric_cols, domain_key))

        # Use ML-based detection for larger datasets
        if len(df) > 50 and len(numeric_cols) >= 3:
            report.insights.extend(self._detect_isolation_forest(df, numeric_cols))

        # Aggregate statistics
        report.total_anomalies = sum(1 for i in report.insights if i.insight_type == "anomaly")
        report.critical_count = sum(1 for i in report.insights if i.severity == "critical")
        report.high_count = sum(1 for i in report.insights if i.severity == "high")
        report.data_quality_issues = sum(1 for i in report.insights if i.insight_type == "missing")
        report.fraud_indicators = sum(1 for i in report.insights if i.insight_type == "fraud")
        report.churn_alerts = sum(1 for i in report.insights if i.insight_type == "churn")

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        report.insights.sort(key=lambda x: (severity_order.get(x.severity, 4), -x.confidence))

        return report

    def _detect_zscore_outliers(self, df: pd.DataFrame, cols: list[str]) -> list[Insight]:
        """Detect outliers using Z-score method."""
        insights = []
        for col in cols:
            series = df[col].dropna()
            if len(series) < 10 or series.std() == 0:
                continue

            mean, std = series.mean(), series.std()
            z_scores = np.abs((series - mean) / std)
            outlier_mask = z_scores > OUTLIER_STD_MULTIPLIER

            if outlier_mask.any():
                outlier_indices = df.index[outlier_mask].tolist()
                outlier_values = series[outlier_mask]
                max_z = z_scores.max()

                # Calculate severity
                outlier_pct = outlier_mask.sum() / len(series)
                if outlier_pct > 0.1 or max_z > 5:
                    severity = "critical"
                elif outlier_pct > 0.05 or max_z > 4:
                    severity = "high"
                elif outlier_pct > 0.02 or max_z > 3.5:
                    severity = "medium"
                else:
                    severity = "low"

                insights.append(Insight(
                    insight_type="anomaly",
                    title=f"Z-Score Outliers in {col.replace('_', ' ').title()}",
                    description=(
                        f"Found {len(outlier_indices)} values (±{OUTLIER_STD_MULTIPLIER}σ from mean). "
                        f"Range: [{outlier_values.min():.2f}, {outlier_values.max():.2f}] vs "
                        f"normal range: [{mean - OUTLIER_STD_MULTIPLIER * std:.2f}, "
                        f"{mean + OUTLIER_STD_MULTIPLIER * std:.2f}]."
                    ),
                    column=col,
                    severity=severity,
                    confidence=min(0.95, 0.7 + (max_z - OUTLIER_STD_MULTIPLIER) * 0.1),
                    affected_rows=outlier_indices[:20],
                    affected_count=len(outlier_indices),
                    metric_value=float(outlier_values.max()),
                    baseline_value=float(mean),
                    change_pct=float((outlier_values.max() - mean) / mean * 100) if mean != 0 else None,
                    recommendation=f"Review {len(outlier_indices)} outlier records for data quality issues or exceptional cases.",
                    domain_relevance=["finance", "sales", "ecommerce", "healthcare", "hr"],
                ))
        return insights

    def _detect_iqr_outliers(self, df: pd.DataFrame, cols: list[str]) -> list[Insight]:
        """Detect outliers using IQR method (more robust for skewed distributions)."""
        insights = []
        for col in cols:
            series = df[col].dropna()
            if len(series) < 10:
                continue

            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr == 0:
                continue

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_mask = (series < lower_bound) | (series > upper_bound)

            if outlier_mask.any():
                outlier_indices = df.index[outlier_mask].tolist()
                outlier_pct = outlier_mask.sum() / len(series)

                # Only report if not already caught by Z-score (avoid duplicates)
                if outlier_pct < 0.15:  # Skip if too many (likely caught by Z-score)
                    severity = "high" if outlier_pct > 0.05 else "medium"
                    insights.append(Insight(
                        insight_type="anomaly",
                        title=f"IQR Outliers in {col.replace('_', ' ').title()}",
                        description=(
                            f"Found {len(outlier_indices)} values outside IQR bounds "
                            f"[{lower_bound:.2f}, {upper_bound:.2f}]."
                        ),
                        column=col,
                        severity=severity,
                        confidence=0.75,
                        affected_rows=outlier_indices[:20],
                        affected_count=len(outlier_indices),
                        recommendation=f"Investigate {len(outlier_indices)} records with unusual {col} values.",
                        domain_relevance=["finance", "inventory", "sales"],
                    ))
        return insights

    def _detect_sudden_changes(
        self, df: pd.DataFrame, cols: list[str], date_column: str | None
    ) -> list[Insight]:
        """Detect sudden drops or spikes in time-series data."""
        insights = []
        if not date_column or date_column not in df.columns:
            return insights

        df_sorted = df.sort_values(date_column).copy()

        for col in cols:
            series = df_sorted[col].dropna()
            if len(series) < 5:
                continue

            # Calculate period-over-period changes
            pct_changes = series.pct_change().dropna()
            if pct_changes.empty:
                continue

            # Detect sudden changes (>50% change)
            sudden_mask = pct_changes.abs() > 0.5
            if sudden_mask.any():
                sudden_indices = pct_changes[sudden_mask].index.tolist()
                max_change = pct_changes.abs().max()

                severity = "critical" if max_change > 1.0 else "high" if max_change > 0.7 else "medium"
                direction = "spike" if pct_changes[sudden_mask].mean() > 0 else "drop"

                insights.append(Insight(
                    insight_type="trend",
                    title=f"Sudden {direction.title()} detected in {col.replace('_', ' ').title()}",
                    description=(
                        f"Detected {len(sudden_indices)} sudden {direction}s. "
                        f"Maximum change: {max_change*100:.1f}%. "
                        f"This may indicate data quality issues or significant business events."
                    ),
                    column=col,
                    severity=severity,
                    confidence=min(0.9, 0.6 + max_change * 0.2),
                    affected_rows=[df_sorted.index.get_loc(idx) for idx in sudden_indices[:10]],
                    affected_count=len(sudden_indices),
                    change_pct=float(max_change * 100),
                    recommendation=f"Investigate the cause of {direction} in {col}. Check for data entry errors or significant business events.",
                    domain_relevance=["sales", "finance", "ecommerce", "marketing"],
                ))
        return insights

    def _detect_missing_patterns(self, df: pd.DataFrame) -> list[Insight]:
        """Detect anomalous missing value patterns."""
        insights = []
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_pct = null_count / len(df)

            if null_pct > 0.3:
                severity = "critical" if null_pct > 0.6 else "high" if null_pct > 0.4 else "medium"
                insights.append(Insight(
                    insight_type="missing",
                    title=f"High missing rate in {col.replace('_', ' ').title()}",
                    description=(
                        f"{null_count} values ({null_pct*100:.1f}%) are missing in '{col}'. "
                        f"This may impact analysis quality."
                    ),
                    column=col,
                    severity=severity,
                    confidence=0.95,
                    affected_count=int(null_count),
                    recommendation=f"Consider imputation strategies or exclude column if missing rate exceeds 60%.",
                    domain_relevance=["generic"],
                ))

            # Detect patterns in missingness (e.g., all missing in a date range)
            if null_pct > 0.05 and null_pct < 0.5:
                # Check if missing values are clustered
                null_mask = df[col].isnull()
                if null_mask.any():
                    # Simple clustering check: are nulls consecutive?
                    null_indices = df[null_mask].index.tolist()
                    if len(null_indices) > 1:
                        consecutive = sum(1 for i in range(len(null_indices)-1)
                                         if null_indices[i+1] - null_indices[i] == 1)
                        if consecutive > len(null_indices) * 0.5:
                            insights.append(Insight(
                                insight_type="missing",
                                title=f"Clustered missing values in {col.replace('_', ' ').title()}",
                                description=(
                                    f"Missing values in '{col}' appear to be clustered, "
                                    f"suggesting systematic data collection issues."
                                ),
                                column=col,
                                severity="medium",
                                confidence=0.7,
                                affected_count=int(null_count),
                                recommendation="Investigate why data is missing in clusters - may indicate system or process issues.",
                                domain_relevance=["healthcare", "finance", "hr"],
                            ))
        return insights

    def _detect_distribution_shifts(self, df: pd.DataFrame, cols: list[str]) -> list[Insight]:
        """Detect unusual distribution shapes (skewness, kurtosis)."""
        insights = []
        for col in cols:
            series = df[col].dropna()
            if len(series) < 20:
                continue

            skewness = series.skew()
            kurtosis = series.kurtosis()

            if abs(skewness) > 2:
                direction = "right" if skewness > 0 else "left"
                insights.append(Insight(
                    insight_type="pattern",
                    title=f"Extreme {direction}-skew in {col.replace('_', ' ').title()}",
                    description=(
                        f"Distribution has skewness of {skewness:.2f} (threshold: ±2.0). "
                        f"This indicates a long tail of {'high' if skewness > 0 else 'low'} values."
                    ),
                    column=col,
                    severity="medium",
                    confidence=0.8,
                    metric_value=float(skewness),
                    recommendation="Consider log transformation or investigate the tail values for outliers.",
                    domain_relevance=["finance", "sales", "healthcare"],
                ))

            if abs(kurtosis) > 10:
                insights.append(Insight(
                    insight_type="pattern",
                    title=f"Extreme kurtosis in {col.replace('_', ' ').title()}",
                    description=(
                        f"Distribution has kurtosis of {kurtosis:.2f}, indicating "
                        f"{'heavy tails and outliers' if kurtosis > 0 else 'light tails'}."
                    ),
                    column=col,
                    severity="medium",
                    confidence=0.75,
                    metric_value=float(kurtosis),
                    recommendation="Review data for outliers or consider robust statistical methods.",
                    domain_relevance=["finance", "sales"],
                ))
        return insights

    def _detect_abnormal_churn(
        self, df: pd.DataFrame, churn_col: str, date_column: str | None
    ) -> list[Insight]:
        """Detect abnormal churn patterns."""
        insights = []
        if churn_col not in df.columns:
            return insights

        churn_series = df[churn_col]
        # Handle different churn encoding (Yes/No, 1/0, True/False)
        if churn_series.dtype == 'object':
            churn_flag = churn_series.str.lower().isin(['yes', 'true', 'churned', '1'])
        else:
            churn_flag = churn_series.astype(bool)

        churn_rate = churn_flag.mean()

        # Check for high churn rate
        if churn_rate > 0.3:
            severity = "critical" if churn_rate > 0.5 else "high" if churn_rate > 0.4 else "medium"
            insights.append(Insight(
                insight_type="churn",
                title="Abnormally high churn rate detected",
                description=(
                    f"Overall churn rate is {churn_rate*100:.1f}%, which is critically high. "
                    f"Total churned: {churn_flag.sum()} out of {len(churn_flag)} records."
                ),
                column=churn_col,
                severity=severity,
                confidence=0.9,
                affected_count=int(churn_flag.sum()),
                metric_value=float(churn_rate * 100),
                recommendation="Implement immediate retention campaigns. Analyze churned customer segments for common patterns.",
                domain_relevance=["ecommerce", "telecom", "hr", "finance"],
            ))

        # Check churn trends over time if date column exists
        if date_column and date_column in df.columns:
            df_temp = pd.DataFrame({date_column: df[date_column], 'churn': churn_flag})
            df_temp = df_temp.sort_values(date_column)

            # Group by month if enough data
            if len(df_temp) > 30:
                df_temp['month'] = df_temp[date_column].dt.to_period('M')
                monthly_churn = df_temp.groupby('month')['churn'].mean()

                if len(monthly_churn) >= 3:
                    # Check for increasing trend
                    recent_trend = monthly_churn.tail(3).diff().dropna()
                    if (recent_trend > 0.05).all():
                        insights.append(Insight(
                            insight_type="churn",
                            title="Churn rate is increasing month-over-month",
                            description=(
                                f"Churn rate has increased for {len(recent_trend)} consecutive months. "
                                f"Current rate: {monthly_churn.iloc[-1]*100:.1f}% vs "
                                f"3 months ago: {monthly_churn.iloc[-3]*100:.1f}%."
                            ),
                            column=churn_col,
                            severity="high",
                            confidence=0.85,
                            metric_value=float(monthly_churn.iloc[-1] * 100),
                            baseline_value=float(monthly_churn.iloc[-3] * 100),
                            change_pct=float((monthly_churn.iloc[-1] - monthly_churn.iloc[-3]) / monthly_churn.iloc[-3] * 100),
                            recommendation="Urgent: Investigate recent changes that may be driving churn increase.",
                            domain_relevance=["ecommerce", "telecom", "hr"],
                        ))
        return insights

    def _detect_fraud_patterns(
        self, df: pd.DataFrame, cols: list[str], domain_key: str
    ) -> list[Insight]:
        """Detect potential fraud patterns (Benford's law, unusual round numbers, etc.)."""
        insights = []

        # Focus on columns that might contain transaction amounts
        fraud_keywords = ['amount', 'transaction', 'payment', 'price', 'total', 'cost', 'revenue', 'expense']
        amount_cols = [c for c in cols if any(kw in c.lower() for kw in fraud_keywords)]

        if not amount_cols:
            amount_cols = cols[:3]  # Use first few numeric columns

        for col in amount_cols:
            series = df[col].dropna()
            if len(series) < 30:
                continue

            # Detect unusual round numbers (potential manual entry)
            round_numbers = series[series % 100 == 0]
            round_pct = len(round_numbers) / len(series)

            if round_pct > 0.3:
                severity = "high" if round_pct > 0.5 else "medium"
                insights.append(Insight(
                    insight_type="fraud",
                    title=f"Unusual round numbers in {col.replace('_', ' ').title()}",
                    description=(
                        f"{round_pct*100:.1f}% of values are perfectly round (multiples of 100). "
                        f"This pattern may indicate manual data entry or fabricated values."
                    ),
                    column=col,
                    severity=severity,
                    confidence=0.65,
                    affected_count=len(round_numbers),
                    metric_value=float(round_pct * 100),
                    recommendation="Review round-number transactions for potential data quality issues or fraud indicators.",
                    domain_relevance=["finance", "sales", "ecommerce"],
                ))

            # Detect duplicate amounts (potential duplicate transactions)
            dup_counts = series.value_counts()
            top_dup_count = dup_counts.iloc[0] if len(dup_counts) > 0 else 0
            top_dup_value = dup_counts.index[0] if len(dup_counts) > 0 else None

            if top_dup_count > len(series) * 0.1 and top_dup_value is not None:
                severity = "high" if top_dup_count > len(series) * 0.2 else "medium"
                insights.append(Insight(
                    insight_type="fraud",
                    title=f"Repeated value in {col.replace('_', ' ').title()}",
                    description=(
                        f"Value {top_dup_value} appears {top_dup_count} times ({top_dup_count/len(series)*100:.1f}% of records). "
                        f"This may indicate duplicate entries or systematic errors."
                    ),
                    column=col,
                    severity=severity,
                    confidence=0.7,
                    affected_count=int(top_dup_count),
                    metric_value=float(top_dup_value),
                    recommendation="Investigate repeated values for potential duplicates or system errors.",
                    domain_relevance=["finance", "sales", "inventory"],
                ))

        return insights

    def _detect_isolation_forest(self, df: pd.DataFrame, cols: list[str]) -> list[Insight]:
        """Use Isolation Forest for multivariate anomaly detection."""
        insights = []
        try:
            # Select top numeric columns by variance
            df_num = df[cols].dropna()
            if len(df_num) < 50 or len(cols) < 3:
                return insights

            # Standardize
            scaler = StandardScaler()
            scaled = scaler.fit_transform(df_num)

            # Fit Isolation Forest
            clf = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
            )
            predictions = clf.fit_predict(scaled)

            # Get anomalies
            anomaly_mask = predictions == -1
            if anomaly_mask.any():
                anomaly_count = anomaly_mask.sum()
                anomaly_pct = anomaly_count / len(df_num)

                # Get anomaly scores
                scores = clf.decision_function(scaled)
                anomaly_scores = scores[anomaly_mask]

                severity = "critical" if anomaly_pct > 0.15 else "high" if anomaly_pct > 0.1 else "medium"

                insights.append(Insight(
                    insight_type="anomaly",
                    title="Multivariate anomalies detected (Isolation Forest)",
                    description=(
                        f"Found {anomaly_count} records ({anomaly_pct*100:.1f}%) that are anomalous "
                        f"across multiple dimensions simultaneously. These may not be outliers in "
                        f"any single column but have unusual combinations of values."
                    ),
                    column="multiple",
                    severity=severity,
                    confidence=0.8,
                    affected_rows=df_num[anomaly_mask].index.tolist()[:20],
                    affected_count=int(anomaly_count),
                    metric_value=float(anomaly_scores.mean()),
                    recommendation="Review multivariate outliers for potential data quality issues or exceptional business cases.",
                    domain_relevance=["finance", "sales", "healthcare", "hr"],
                ))
        except Exception as e:
            pass  # Silently fail if ML detection doesn't work

        return insights

    def _find_churn_column(self, df: pd.DataFrame) -> str | None:
        """Find a column that likely represents churn."""
        churn_keywords = ['churn', 'attrition', 'left', 'terminated', 'resigned', 'cancelled', 'lost']
        for col in df.columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in churn_keywords):
                return col
        return None