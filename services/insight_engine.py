"""
insight_engine.py — AI-powered business insight generation engine.

Generates human-readable executive insights, domain-aware analysis,
and natural language summaries with confidence scoring.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Literal
from services.domain_service import DomainConfig, DomainService
from services.kpi_service import KPIResult
from services.analytics_service import AnalyticsReport
from services.insight_detector import InsightDetector, InsightReport, Insight
from utils.llm_client import call_llm
from config import AI_MAX_TOKENS
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveInsight:
    """A single executive-level insight with business context."""
    category: Literal["performance", "risk", "opportunity", "trend", "anomaly"]
    headline: str  # Short, punchy headline (max 80 chars)
    description: str  # Detailed explanation (2-3 sentences)
    impact: str  # Business impact statement
    confidence: float  # 0.0 to 1.0
    severity: Literal["critical", "high", "medium", "low"]
    related_kpis: list[str] = field(default_factory=list)
    related_columns: list[str] = field(default_factory=list)
    data_support: dict = field(default_factory=dict)  # Supporting statistics


@dataclass
class InsightEngineReport:
    """Complete insight engine report."""
    executive_insights: list[ExecutiveInsight] = field(default_factory=list)
    summary_paragraph: str = ""
    key_findings: list[str] = field(default_factory=list)
    risk_alerts: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    total_records_analyzed: int = 0
    data_quality_score: float = 0.0
    analysis_timestamp: str = ""

    @property
    def has_critical_insights(self) -> bool:
        return any(i.severity == "critical" for i in self.executive_insights)

    @property
    def insight_count_by_category(self) -> dict[str, int]:
        counts = {}
        for insight in self.executive_insights:
            counts[insight.category] = counts.get(insight.category, 0) + 1
        return counts


class InsightEngine:
    """
    AI-powered business insight generation engine.
    
    Combines statistical analysis, anomaly detection, and LLM-powered
    narrative generation to produce executive-level business insights.
    """

    def __init__(self, use_llm: bool = True):
        self.detector = InsightDetector()
        self.domain_svc = DomainService()
        self.use_llm = use_llm

    def generate_insights(
        self,
        df: pd.DataFrame,
        domain_cfg: DomainConfig,
        kpis: list[KPIResult] | None = None,
        analytics_report: AnalyticsReport | None = None,
        dataset_name: str = "the dataset",
    ) -> InsightEngineReport:
        """
        Generate comprehensive business insights from a dataset.
        
        Args:
            df: The cleaned DataFrame to analyze
            domain_cfg: Domain configuration for business context
            kpis: Pre-computed KPIs (optional)
            analytics_report: Pre-computed analytics (optional)
            dataset_name: Name of the dataset for reporting
            
        Returns:
            InsightEngineReport with executive insights and summaries
        """
        report = InsightEngineReport()
        report.total_records_analyzed = len(df)
        
        # Step 1: Run anomaly/pattern detection
        insight_report = self.detector.detect_all(
            df,
            domain_key=domain_cfg.key,
        )
        
        # Step 2: Generate executive insights from detected patterns
        report.executive_insights = self._generate_executive_insights(
            insight_report, df, domain_cfg, kpis
        )
        
        # Step 3: Generate key findings summary
        report.key_findings = self._generate_key_findings(
            report.executive_insights, kpis, analytics_report
        )
        
        # Step 4: Separate risk alerts and opportunities
        for insight in report.executive_insights:
            if insight.category in ["risk", "anomaly"] and insight.severity in ["critical", "high"]:
                report.risk_alerts.append(f"🚨 {insight.headline}: {insight.description}")
            elif insight.category == "opportunity":
                report.opportunities.append(f"💡 {insight.headline}: {insight.description}")
        
        # Step 5: Generate summary paragraph
        report.summary_paragraph = self._generate_summary_paragraph(
            report, domain_cfg, dataset_name, kpis
        )
        
        # Step 6: Calculate data quality score
        report.data_quality_score = self._calculate_data_quality_score(df, insight_report)
        
        return report

    def _generate_executive_insights(
        self,
        insight_report: InsightReport,
        df: pd.DataFrame,
        domain_cfg: DomainConfig,
        kpis: list[KPIResult] | None,
    ) -> list[ExecutiveInsight]:
        """Convert detected patterns into executive-level insights."""
        insights = []
        
        for detected in insight_report.insights[:15]:  # Limit to top 15
            # Determine category based on insight type
            category = self._map_to_category(detected.insight_type, detected.severity)
            
            # Generate headline
            headline = self._generate_headline(detected, domain_cfg)
            
            # Generate description with domain context
            description = self._generate_description(detected, domain_cfg, df)
            
            # Generate impact statement
            impact = self._generate_impact(detected, domain_cfg, kpis)
            
            # Get related KPIs
            related_kpis = self._find_related_kpis(detected.column, kpis) if kpis else []
            
            insight = ExecutiveInsight(
                category=category,
                headline=headline,
                description=description,
                impact=impact,
                confidence=detected.confidence,
                severity=detected.severity,
                related_kpis=related_kpis,
                related_columns=[detected.column],
                data_support={
                    "affected_count": detected.affected_count,
                    "metric_value": detected.metric_value,
                    "baseline_value": detected.baseline_value,
                    "change_pct": detected.change_pct,
                },
            )
            insights.append(insight)
        
        return insights

    def _map_to_category(
        self,
        insight_type: str,
        severity: str,
    ) -> Literal["performance", "risk", "opportunity", "trend", "anomaly"]:
        """Map detected insight type to executive category."""
        mapping = {
            "anomaly": "anomaly",
            "trend": "trend",
            "fraud": "risk",
            "churn": "risk",
            "missing": "risk",
            "pattern": "performance",
        }
        category = mapping.get(insight_type, "anomaly")
        
        # Upgrade to risk if severity is critical
        if severity == "critical" and category not in ["risk"]:
            category = "risk"
        
        return category

    def _generate_headline(self, detected: Insight, domain_cfg: DomainConfig) -> str:
        """Generate a short, punchy headline for the insight."""
        col_name = detected.column.replace('_', ' ').title()
        
        templates = {
            "anomaly": f"Unusual patterns detected in {col_name}",
            "trend": f"Significant trend change in {col_name}",
            "fraud": f"⚠️ Potential data integrity issues in {col_name}",
            "churn": f"📉 Critical churn alert: {detected.affected_count} records affected",
            "missing": f"Data quality issue: {col_name} has {detected.affected_count} missing values",
            "pattern": f"Notable distribution pattern in {col_name}",
        }
        
        headline = templates.get(detected.insight_type, detected.title)
        
        # Truncate if too long
        if len(headline) > 80:
            headline = headline[:77] + "..."
        
        return headline

    def _generate_description(
        self,
        detected: Insight,
        domain_cfg: DomainConfig,
        df: pd.DataFrame,
    ) -> str:
        """Generate a detailed description with domain context."""
        base_desc = detected.description
        
        # Add domain-specific context
        domain_context = ""
        if domain_cfg.key == "finance":
            domain_context = " From a financial controls perspective, this warrants immediate review."
        elif domain_cfg.key == "healthcare":
            domain_context = " In healthcare contexts, such patterns may impact patient outcomes."
        elif domain_cfg.key == "ecommerce":
            domain_context = " For e-commerce operations, this could affect customer experience and revenue."
        elif domain_cfg.key == "hr":
            domain_context = " From an HR analytics standpoint, this may indicate workforce trends."
        elif domain_cfg.key == "sales":
            domain_context = " In sales analytics, this pattern could signal pipeline health changes."
        
        return base_desc + domain_context

    def _generate_impact(
        self,
        detected: Insight,
        domain_cfg: DomainConfig,
        kpis: list[KPIResult] | None,
    ) -> str:
        """Generate business impact statement."""
        # Use the recommendation from detected insight
        base_impact = detected.recommendation
        
        # Add quantified impact if available
        if detected.change_pct is not None and abs(detected.change_pct) > 10:
            direction = "increase" if detected.change_pct > 0 else "decrease"
            base_impact += f" This represents a {abs(detected.change_pct):.1f}% {direction}."
        
        if detected.affected_count > 100:
            base_impact += f" Affects {detected.affected_count:,} records."
        
        return base_impact

    def _find_related_kpis(
        self,
        column: str,
        kpis: list[KPIResult] | None,
    ) -> list[str]:
        """Find KPIs related to the insight column."""
        if not kpis:
            return []
        
        related = []
        col_lower = column.lower()
        for kpi in kpis:
            if kpi.column and (col_lower in kpi.column.lower() or kpi.column.lower() in col_lower):
                related.append(kpi.name)
        
        return related[:3]

    def _generate_key_findings(
        self,
        insights: list[ExecutiveInsight],
        kpis: list[KPIResult] | None,
        analytics_report: AnalyticsReport | None,
    ) -> list[str]:
        """Generate a list of key findings."""
        findings = []
        
        # Add top insights as findings
        for insight in insights[:5]:
            if insight.severity in ["critical", "high"]:
                findings.append(f"{insight.headline}")
        
        # Add trend findings
        if analytics_report and analytics_report.trends:
            for trend in analytics_report.trends[:3]:
                findings.append(trend.summary)
        
        # Add KPI highlights
        if kpis:
            for kpi in kpis[:3]:
                if kpi.delta_pct and abs(kpi.delta_pct) > 5:
                    direction = "↑" if kpi.delta_pct > 0 else "↓"
                    findings.append(f"{kpi.name}: {kpi.formatted} ({direction} {abs(kpi.delta_pct):.1f}%)")
        
        return findings

    def _generate_summary_paragraph(
        self,
        report: InsightEngineReport,
        domain_cfg: DomainConfig,
        dataset_name: str,
        kpis: list[KPIResult] | None,
    ) -> str:
        """Generate an executive summary paragraph."""
        # Try LLM if available and enabled
        if self.use_llm:
            try:
                llm_summary = self._generate_llm_summary(report, domain_cfg, dataset_name, kpis)
                if llm_summary:
                    return llm_summary
            except Exception as e:
                logger.warning(f"LLM summary generation failed: {e}")
        
        # Fallback to template-based summary
        return self._generate_template_summary(report, domain_cfg, dataset_name, kpis)

    def _generate_llm_summary(
        self,
        report: InsightEngineReport,
        domain_cfg: DomainConfig,
        dataset_name: str,
        kpis: list[KPIResult] | None,
    ) -> str:
        """Use LLM to generate a natural language summary."""
        insights_text = "\n".join([
            f"- [{i.severity.upper()}] {i.headline}: {i.description}"
            for i in report.executive_insights[:8]
        ])
        
        kpi_text = "\n".join([f"- {k.name}: {k.formatted}" for k in kpis[:6]]) if kpis else "N/A"
        
        prompt = f"""You are a senior business analyst writing an executive summary.

Domain: {domain_cfg.label}
Dataset: {dataset_name}
Records analyzed: {report.total_records_analyzed:,}

Key Insights Detected:
{insights_text}

Key Metrics:
{kpi_text}

Write a concise 3-4 sentence executive summary that:
1. States the overall data health and key findings
2. Highlights the most critical insight
3. Provides a clear recommendation

Keep it professional, specific, and action-oriented."""

        result = call_llm(prompt, max_tokens=AI_MAX_TOKENS)
        return result if result else ""

    def _generate_template_summary(
        self,
        report: InsightEngineReport,
        domain_cfg: DomainConfig,
        dataset_name: str,
        kpis: list[KPIResult] | None,
    ) -> str:
        """Generate a template-based summary when LLM is unavailable."""
        parts = []
        
        # Opening
        parts.append(f"Analysis of {dataset_name} ({report.total_records_analyzed:,} records) in the {domain_cfg.label} domain.")
        
        # Critical findings
        critical = [i for i in report.executive_insights if i.severity == "critical"]
        if critical:
            parts.append(f"🔴 {len(critical)} critical issue(s) require immediate attention: {critical[0].headline}.")
        
        # High priority findings
        high = [i for i in report.executive_insights if i.severity == "high"]
        if high:
            parts.append(f"🟠 {len(high)} high-priority findings identified, including {high[0].headline}.")
        
        # Data quality
        if report.data_quality_score < 70:
            parts.append(f"Data quality score is {report.data_quality_score:.0f}/100 — review recommended.")
        
        # Top KPIs
        if kpis:
            top_kpi = kpis[0] if kpis else None
            if top_kpi:
                parts.append(f"Key metric: {top_kpi.name} = {top_kpi.formatted}.")
        
        return " ".join(parts)

    def _calculate_data_quality_score(
        self,
        df: pd.DataFrame,
        insight_report: InsightReport,
    ) -> float:
        """Calculate an overall data quality score (0-100)."""
        score = 100.0
        
        # Penalize for missing data issues
        missing_issues = [i for i in insight_report.insights if i.insight_type == "missing"]
        for issue in missing_issues:
            if issue.severity == "critical":
                score -= 15
            elif issue.severity == "high":
                score -= 10
            else:
                score -= 5
        
        # Penalize for anomalies
        anomaly_count = insight_report.total_anomalies
        score -= min(anomaly_count * 2, 20)
        
        # Penalize for fraud indicators
        score -= insight_report.fraud_indicators * 5
        
        # Bonus for completeness
        overall_null_rate = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if overall_null_rate < 0.05:
            score += 5
        
        return max(0, min(100, score))

    def generate_domain_specific_insights(
        self,
        df: pd.DataFrame,
        domain_key: str,
    ) -> list[str]:
        """Generate domain-specific insight templates."""
        domain = self.domain_svc.get_config(domain_key)
        insights = []
        
        if domain_key == "ecommerce":
            insights.extend(self._ecommerce_insights(df))
        elif domain_key == "finance":
            insights.extend(self._finance_insights(df))
        elif domain_key == "hr":
            insights.extend(self._hr_insights(df))
        elif domain_key == "healthcare":
            insights.extend(self._healthcare_insights(df))
        elif domain_key == "sales":
            insights.extend(self._sales_insights(df))
        
        return insights

    def _ecommerce_insights(self, df: pd.DataFrame) -> list[str]:
        """E-commerce specific insights."""
        insights = []
        
        # Check for order-related columns
        order_cols = [c for c in df.columns if 'order' in c.lower()]
        revenue_cols = [c for c in df.columns if 'revenue' in c.lower() or 'amount' in c.lower()]
        
        if order_cols and revenue_cols:
            avg_order_value = df[revenue_cols[0]].mean() if revenue_cols else 0
            if avg_order_value > 0:
                insights.append(f"Average order value is ${avg_order_value:.2f}")
        
        return insights

    def _finance_insights(self, df: pd.DataFrame) -> list[str]:
        """Finance specific insights."""
        insights = []
        
        # Check for profit/revenue columns
        profit_cols = [c for c in df.columns if 'profit' in c.lower() or 'margin' in c.lower()]
        expense_cols = [c for c in df.columns if 'expense' in c.lower() or 'cost' in c.lower()]
        
        if profit_cols and expense_cols:
            total_profit = df[profit_cols[0]].sum() if profit_cols else 0
            total_expense = df[expense_cols[0]].sum() if expense_cols else 0
            if total_expense > 0:
                roi = (total_profit / total_expense) * 100
                insights.append(f"ROI: {roi:.1f}% (Profit: ${total_profit:,.0f} / Expenses: ${total_expense:,.0f})")
        
        return insights

    def _hr_insights(self, df: pd.DataFrame) -> list[str]:
        """HR specific insights."""
        insights = []
        
        # Check for attrition/churn columns
        churn_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['churn', 'attrition', 'left', 'resigned'])]
        
        if churn_cols:
            churn_rate = df[churn_cols[0]].astype(bool).mean() * 100
            insights.append(f"Attrition rate: {churn_rate:.1f}%")
            
            if churn_rate > 15:
                insights.append("⚠️ Attrition rate exceeds healthy threshold (15%)")
        
        return insights

    def _healthcare_insights(self, df: pd.DataFrame) -> list[str]:
        """Healthcare specific insights."""
        insights = []
        
        # Check for readmission columns
        readmit_cols = [c for c in df.columns if 'readmit' in c.lower()]
        los_cols = [c for c in df.columns if 'length_of_stay' in c.lower() or 'los' in c.lower()]
        
        if readmit_cols:
            readmit_rate = df[readmit_cols[0]].astype(bool).mean() * 100
            insights.append(f"Readmission rate: {readmit_rate:.1f}%")
            
            if readmit_rate > 10:
                insights.append("⚠️ Readmission rate exceeds CMS threshold (10%)")
        
        if los_cols:
            avg_los = df[los_cols[0]].mean()
            insights.append(f"Average length of stay: {avg_los:.1f} days")
        
        return insights

    def _sales_insights(self, df: pd.DataFrame) -> list[str]:
        """Sales specific insights."""
        insights = []
        
        # Check for deal/win columns
        win_cols = [c for c in df.columns if 'win' in c.lower() or 'closed' in c.lower()]
        deal_cols = [c for c in df.columns if 'deal' in c.lower() or 'amount' in c.lower()]
        
        if win_cols:
            win_rate = df[win_cols[0]].astype(bool).mean() * 100
            insights.append(f"Win rate: {win_rate:.1f}%")
            
            if win_rate < 30:
                insights.append("⚠️ Win rate below target threshold (30%)")
            elif win_rate > 60:
                insights.append("✅ Win rate exceeds target threshold (60%)")
        
        if deal_cols:
            avg_deal = df[deal_cols[0]].mean()
            insights.append(f"Average deal size: ${avg_deal:,.0f}")
        
        return insights