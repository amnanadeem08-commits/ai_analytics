"""
recommendation_engine.py — AI-powered business recommendation engine.

Generates actionable recommendations based on detected insights,
domain context, and business best practices.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Literal
from services.domain_service import DomainConfig
from services.kpi_service import KPIResult
from services.insight_detector import InsightReport, Insight
from services.insight_engine import InsightEngineReport, ExecutiveInsight


@dataclass
class Recommendation:
    """A single actionable business recommendation."""
    category: Literal["immediate", "short_term", "strategic", "investigation"]
    title: str
    description: str
    priority: int  # 1 = highest, 5 = lowest
    effort: Literal["low", "medium", "high"]
    impact: Literal["low", "medium", "high"]
    related_insights: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    estimated_timeline: str = ""  # e.g., "1-2 weeks"
    owner_role: str = ""  # e.g., "Data Analyst", "Marketing Manager"


@dataclass
class RecommendationReport:
    """Complete recommendation report."""
    recommendations: list[Recommendation] = field(default_factory=list)
    immediate_actions: list[Recommendation] = field(default_factory=list)
    short_term_actions: list[Recommendation] = field(default_factory=list)
    strategic_actions: list[Recommendation] = field(default_factory=list)
    investigation_items: list[Recommendation] = field(default_factory=list)
    total_recommendations: int = 0
    high_priority_count: int = 0

    @property
    def top_3_actions(self) -> list[Recommendation]:
        """Return top 3 highest priority recommendations."""
        sorted_recs = sorted(self.recommendations, key=lambda x: x.priority)
        return sorted_recs[:3]

    @property
    def summary(self) -> str:
        """Generate a summary of recommendations."""
        parts = [f"{self.total_recommendations} recommendations generated:"]
        if self.immediate_actions:
            parts.append(f"🔴 {len(self.immediate_actions)} immediate actions required")
        if self.short_term_actions:
            parts.append(f"🟡 {len(self.short_term_actions)} short-term actions")
        if self.strategic_actions:
            parts.append(f"🟢 {len(self.strategic_actions)} strategic initiatives")
        return " ".join(parts)


class RecommendationEngine:
    """
    AI-powered business recommendation engine.
    
    Generates actionable recommendations based on detected insights,
    domain context, and business best practices.
    """

    def __init__(self):
        self.domain_recommendations = {
            "ecommerce": self._ecommerce_recommendations,
            "finance": self._finance_recommendations,
            "hr": self._hr_recommendations,
            "healthcare": self._healthcare_recommendations,
            "sales": self._sales_recommendations,
            "marketing": self._marketing_recommendations,
            "inventory": self._inventory_recommendations,
            "telecom": self._telecom_recommendations,
            "education": self._education_recommendations,
        }

    def generate_recommendations(
        self,
        insight_report: InsightEngineReport,
        domain_cfg: DomainConfig,
        df: pd.DataFrame,
        kpis: list[KPIResult] | None = None,
    ) -> RecommendationReport:
        """
        Generate actionable recommendations based on insights.
        
        Args:
            insight_report: The insight engine report with detected patterns
            domain_cfg: Domain configuration for business context
            df: The analyzed DataFrame
            kpis: Pre-computed KPIs (optional)
            
        Returns:
            RecommendationReport with prioritized actions
        """
        report = RecommendationReport()
        
        # Generate recommendations from insights
        for insight in insight_report.executive_insights:
            recs = self._insight_to_recommendation(insight, domain_cfg)
            report.recommendations.extend(recs)
        
        # Add domain-specific recommendations
        domain_recs = self._get_domain_recommendations(domain_cfg.key, df, kpis)
        report.recommendations.extend(domain_recs)
        
        # Categorize by priority
        for rec in report.recommendations:
            if rec.category == "immediate":
                report.immediate_actions.append(rec)
            elif rec.category == "short_term":
                report.short_term_actions.append(rec)
            elif rec.category == "strategic":
                report.strategic_actions.append(rec)
            else:
                report.investigation_items.append(rec)
        
        # Sort each category by priority
        for category_list in [
            report.immediate_actions,
            report.short_term_actions,
            report.strategic_actions,
            report.investigation_items,
        ]:
            category_list.sort(key=lambda x: x.priority)
        
        report.total_recommendations = len(report.recommendations)
        report.high_priority_count = sum(1 for r in report.recommendations if r.priority <= 2)
        
        # Remove duplicates based on title
        seen = set()
        unique_recs = []
        for rec in sorted(report.recommendations, key=lambda x: x.priority):
            if rec.title not in seen:
                seen.add(rec.title)
                unique_recs.append(rec)
        report.recommendations = unique_recs[:20]  # Limit to top 20
        
        return report

    def _insight_to_recommendation(
        self,
        insight: ExecutiveInsight,
        domain_cfg: DomainConfig,
    ) -> list[Recommendation]:
        """Convert an insight to actionable recommendations."""
        recommendations = []
        
        if insight.category == "risk" or insight.severity == "critical":
            # Critical risks need immediate action
            rec = Recommendation(
                category="immediate",
                title=f"Address: {insight.headline}",
                description=f"{insight.description} {insight.impact}",
                priority=1,
                effort="medium",
                impact="high",
                related_insights=[insight.headline],
                success_metrics=["Reduce anomaly count by 80%", "Improve data quality score"],
                estimated_timeline="Immediate (24-48 hours)",
                owner_role="Data Analyst / Domain Expert",
            )
            recommendations.append(rec)
            
            # Add investigation item
            rec_inv = Recommendation(
                category="investigation",
                title=f"Investigate root cause: {insight.headline}",
                description="Conduct deep-dive analysis to understand the underlying cause of this pattern.",
                priority=2,
                effort="medium",
                impact="high",
                related_insights=[insight.headline],
                success_metrics=["Identify root cause", "Document findings"],
                estimated_timeline="3-5 business days",
                owner_role="Senior Analyst",
            )
            recommendations.append(rec_inv)
            
        elif insight.severity == "high":
            # High priority issues need short-term action
            rec = Recommendation(
                category="short_term",
                title=f"Review: {insight.headline}",
                description=f"{insight.description} Consider reviewing affected records.",
                priority=2,
                effort="low",
                impact="medium",
                related_insights=[insight.headline],
                success_metrics=["Review 100% of affected records", "Implement corrective actions"],
                estimated_timeline="1-2 weeks",
                owner_role="Analyst",
            )
            recommendations.append(rec)
            
        elif insight.category == "trend":
            # Trends may indicate strategic opportunities or risks
            if "drop" in insight.headline.lower() or "decline" in insight.description.lower():
                rec = Recommendation(
                    category="short_term",
                    title=f"Address declining trend: {insight.headline}",
                    description=f"Analyze the cause of decline and develop mitigation strategy.",
                    priority=2,
                    effort="high",
                    impact="high",
                    related_insights=[insight.headline],
                    success_metrics=["Reverse negative trend", "Stabilize metric"],
                    estimated_timeline="2-4 weeks",
                    owner_role="Department Head",
                )
                recommendations.append(rec)
            else:
                rec = Recommendation(
                    category="strategic",
                    title=f"Capitalize on positive trend: {insight.headline}",
                    description="Analyze drivers of positive trend and consider scaling successful strategies.",
                    priority=3,
                    effort="medium",
                    impact="high",
                    related_insights=[insight.headline],
                    success_metrics=["Amplify positive trend", "Document success factors"],
                    estimated_timeline="1-3 months",
                    owner_role="Strategy Team",
                )
                recommendations.append(rec)
                
        elif insight.category == "anomaly":
            rec = Recommendation(
                category="investigation",
                title=f"Investigate anomaly: {insight.headline}",
                description=f"Review anomalous records to determine if they represent errors or exceptional cases.",
                priority=3,
                effort="low",
                impact="medium",
                related_insights=[insight.headline],
                success_metrics=["Classify anomalies", "Update data validation rules"],
                estimated_timeline="1 week",
                owner_role="Data Steward",
            )
            recommendations.append(rec)
            
        elif insight.category == "performance":
            rec = Recommendation(
                category="strategic",
                title=f"Optimize: {insight.headline}",
                description="Consider process improvements to leverage or address this pattern.",
                priority=3,
                effort="high",
                impact="medium",
                related_insights=[insight.headline],
                success_metrics=["Improve process efficiency", "Reduce variation"],
                estimated_timeline="1-3 months",
                owner_role="Process Owner",
            )
            recommendations.append(rec)
        
        return recommendations

    def _get_domain_recommendations(
        self,
        domain_key: str,
        df: pd.DataFrame,
        kpis: list[KPIResult] | None,
    ) -> list[Recommendation]:
        """Get domain-specific recommendations."""
        if domain_key in self.domain_recommendations:
            return self.domain_recommendations[domain_key](df, kpis)
        return self._generic_recommendations(df, kpis)

    # ─── Domain-Specific Recommendation Generators ───────────────────────────

    def _ecommerce_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """E-commerce specific recommendations."""
        recs = []
        
        # Check for churn/retention columns
        churn_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['churn', 'retention', 'return'])]
        if churn_cols:
            recs.append(Recommendation(
                category="strategic",
                title="Implement customer retention program",
                description="Develop targeted retention campaigns based on customer segmentation and purchase history.",
                priority=2,
                effort="high",
                impact="high",
                success_metrics=["Increase retention rate by 10%", "Reduce churn by 15%"],
                estimated_timeline="2-3 months",
                owner_role="Marketing Manager",
            ))
        
        # Check for revenue/order columns
        revenue_cols = [c for c in df.columns if 'revenue' in c.lower() or 'order' in c.lower()]
        if revenue_cols:
            recs.append(Recommendation(
                category="strategic",
                title="Optimize average order value (AOV)",
                description="Implement cross-sell and upsell strategies to increase average order value.",
                priority=3,
                effort="medium",
                impact="high",
                success_metrics=["Increase AOV by 15%", "Improve cross-sell conversion"],
                estimated_timeline="1-2 months",
                owner_role="E-commerce Manager",
            ))
        
        return recs

    def _finance_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Finance specific recommendations."""
        recs = []
        
        recs.append(Recommendation(
            category="immediate",
            title="Review data quality controls",
            description="Implement automated data validation rules to prevent financial data errors.",
            priority=1,
            effort="medium",
            impact="high",
            success_metrics=["Reduce data errors by 90%", "Achieve 99.9% data accuracy"],
            estimated_timeline="2-4 weeks",
            owner_role="Financial Controller",
        ))
        
        recs.append(Recommendation(
            category="strategic",
            title="Implement financial forecasting model",
            description="Build predictive models for revenue, expenses, and cash flow forecasting.",
            priority=3,
            effort="high",
            impact="high",
            success_metrics=["Improve forecast accuracy to 95%", "Reduce budget variance"],
            estimated_timeline="3-6 months",
            owner_role="FP&A Manager",
        ))
        
        return recs

    def _hr_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """HR specific recommendations."""
        recs = []
        
        # Check for attrition columns
        churn_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['churn', 'attrition', 'left', 'resigned'])]
        if churn_cols:
            recs.append(Recommendation(
                category="immediate",
                title="Implement employee retention strategy",
                description="Develop targeted retention programs for high-risk employee segments.",
                priority=1,
                effort="high",
                impact="high",
                success_metrics=["Reduce attrition by 20%", "Improve employee satisfaction scores"],
                estimated_timeline="2-3 months",
                owner_role="HR Director",
            ))
            
            recs.append(Recommendation(
                category="investigation",
                title="Conduct exit interview analysis",
                description="Analyze exit interview data to identify common reasons for departure.",
                priority=2,
                effort="medium",
                impact="high",
                success_metrics=["Identify top 3 departure reasons", "Develop targeted interventions"],
                estimated_timeline="2-4 weeks",
                owner_role="HR Business Partner",
            ))
        
        return recs

    def _healthcare_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Healthcare specific recommendations."""
        recs = []
        
        # Check for readmission columns
        readmit_cols = [c for c in df.columns if 'readmit' in c.lower()]
        if readmit_cols:
            recs.append(Recommendation(
                category="immediate",
                title="Implement readmission reduction program",
                description="Develop targeted interventions for high-risk patients to reduce readmissions.",
                priority=1,
                effort="high",
                impact="high",
                success_metrics=["Reduce readmission rate by 25%", "Improve patient outcomes"],
                estimated_timeline="3-6 months",
                owner_role="Clinical Director",
            ))
            
            recs.append(Recommendation(
                category="investigation",
                title="Analyze readmission risk factors",
                description="Conduct detailed analysis of patient characteristics associated with readmissions.",
                priority=2,
                effort="medium",
                impact="high",
                success_metrics=["Identify top risk factors", "Develop risk stratification model"],
                estimated_timeline="4-6 weeks",
                owner_role="Clinical Analyst",
            ))
        
        return recs

    def _sales_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Sales specific recommendations."""
        recs = []
        
        # Check for win/loss columns
        win_cols = [c for c in df.columns if 'win' in c.lower() or 'closed' in c.lower()]
        if win_cols:
            recs.append(Recommendation(
                category="strategic",
                title="Optimize sales process based on win/loss analysis",
                description="Analyze won vs lost deals to identify success factors and improvement areas.",
                priority=2,
                effort="medium",
                impact="high",
                success_metrics=["Increase win rate by 10%", "Reduce sales cycle by 15%"],
                estimated_timeline="2-3 months",
                owner_role="Sales Operations",
            ))
        
        recs.append(Recommendation(
            category="strategic",
            title="Implement sales forecasting model",
            description="Build predictive models for pipeline conversion and revenue forecasting.",
            priority=3,
            effort="high",
            impact="high",
            success_metrics=["Improve forecast accuracy to 90%", "Increase pipeline velocity"],
            estimated_timeline="3-4 months",
            owner_role="Revenue Operations",
        ))
        
        return recs

    def _marketing_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Marketing specific recommendations."""
        recs = []
        
        recs.append(Recommendation(
            category="strategic",
            title="Optimize marketing mix and budget allocation",
            description="Analyze channel performance and reallocate budget to highest-ROI channels.",
            priority=2,
            effort="high",
            impact="high",
            success_metrics=["Improve overall ROAS by 20%", "Reduce CAC by 15%"],
            estimated_timeline="2-3 months",
            owner_role="Marketing Director",
        ))
        
        return recs

    def _inventory_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Inventory specific recommendations."""
        recs = []
        
        recs.append(Recommendation(
            category="strategic",
            title="Implement demand forecasting system",
            description="Build predictive models for inventory optimization and reorder point calculation.",
            priority=2,
            effort="high",
            impact="high",
            success_metrics=["Reduce stockouts by 50%", "Optimize inventory turnover"],
            estimated_timeline="3-4 months",
            owner_role="Supply Chain Manager",
        ))
        
        return recs

    def _telecom_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Telecom specific recommendations."""
        recs = []
        
        # Check for churn columns
        churn_cols = [c for c in df.columns if 'churn' in c.lower()]
        if churn_cols:
            recs.append(Recommendation(
                category="immediate",
                title="Implement churn prevention program",
                description="Develop targeted retention campaigns for at-risk subscribers.",
                priority=1,
                effort="high",
                impact="high",
                success_metrics=["Reduce churn rate by 20%", "Improve customer lifetime value"],
                estimated_timeline="2-3 months",
                owner_role="Customer Retention Manager",
            ))
            
            recs.append(Recommendation(
                category="investigation",
                title="Build churn prediction model",
                description="Develop ML model to identify at-risk customers before they churn.",
                priority=2,
                effort="high",
                impact="high",
                success_metrics=["Achieve 85% churn prediction accuracy", "Enable proactive retention"],
                estimated_timeline="2-3 months",
                owner_role="Data Science Team",
            ))
        
        return recs

    def _education_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Education specific recommendations."""
        recs = []
        
        # Check for performance columns
        grade_cols = [c for c in df.columns if 'grade' in c.lower() or 'score' in c.lower() or 'pass' in c.lower()]
        if grade_cols:
            recs.append(Recommendation(
                category="strategic",
                title="Implement early warning system for at-risk students",
                description="Develop predictive model to identify students who may struggle academically.",
                priority=2,
                effort="high",
                impact="high",
                success_metrics=["Improve pass rates by 15%", "Enable timely interventions"],
                estimated_timeline="3-4 months",
                owner_role="Academic Affairs",
            ))
        
        return recs

    def _generic_recommendations(
        self, df: pd.DataFrame, kpis: list[KPIResult] | None
    ) -> list[Recommendation]:
        """Generic recommendations for any domain."""
        recs = []
        
        recs.append(Recommendation(
            category="strategic",
            title="Establish data quality monitoring framework",
            description="Implement automated data quality checks and monitoring dashboards.",
            priority=3,
            effort="medium",
            impact="medium",
            success_metrics=["Achieve 99% data quality score", "Reduce manual data cleaning by 50%"],
            estimated_timeline="2-3 months",
            owner_role="Data Engineering Team",
        ))
        
        recs.append(Recommendation(
            category="strategic",
            title="Develop self-service analytics capabilities",
            description="Build dashboards and reports to enable business users to explore data independently.",
            priority=4,
            effort="high",
            impact="medium",
            success_metrics=["Increase dashboard adoption by 50%", "Reduce ad-hoc requests by 30%"],
            estimated_timeline="3-6 months",
            owner_role="BI Team",
        ))
        
        return recs

    def generate_prioritized_action_plan(
        self,
        report: RecommendationReport,
        timeline_weeks: int = 12,
    ) -> dict:
        """Generate a prioritized action plan with timeline."""
        plan = {
            "week_1_2": [],
            "week_3_4": [],
            "week_5_8": [],
            "week_9_12": [],
            "beyond_12_weeks": [],
        }
        
        sorted_recs = sorted(report.recommendations, key=lambda x: x.priority)
        
        for i, rec in enumerate(sorted_recs):
            if i < 3:
                plan["week_1_2"].append(rec)
            elif i < 6:
                plan["week_3_4"].append(rec)
            elif i < 10:
                plan["week_5_8"].append(rec)
            elif i < 15:
                plan["week_9_12"].append(rec)
            else:
                plan["beyond_12_weeks"].append(rec)
        
        return plan