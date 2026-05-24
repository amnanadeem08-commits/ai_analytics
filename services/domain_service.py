"""
domain_service.py — Business domain detection and domain-specific configuration.
Drives KPI selection, chart defaults, chatbot persona, and report style.
"""

import pandas as pd
from dataclasses import dataclass, field
from config import DOMAINS


@dataclass
class DomainConfig:
    key: str
    label: str
    kpi_columns: list[str]       # preferred column name fragments for KPIs
    primary_kpis: list[str]      # display names of key metrics
    chart_preferences: list[str] # preferred chart types in order
    analyst_persona: str         # chatbot system prompt persona
    currency_kpis: list[str]     # KPIs that should be formatted as currency
    pct_kpis: list[str]          # KPIs that should be formatted as percentage
    insights_focus: list[str]    # topics the AI should emphasize


DOMAIN_CONFIGS: dict[str, DomainConfig] = {
    "sales": DomainConfig(
        key="sales",
        label="Sales Analytics",
        kpi_columns=["revenue", "sales", "amount", "deal", "quota", "pipeline", "win", "close"],
        primary_kpis=["Total Revenue", "Deals Won", "Win Rate", "Avg Deal Size", "Pipeline Value"],
        chart_preferences=["bar", "line", "funnel", "scatter"],
        analyst_persona=(
            "You are a senior sales analyst with 10+ years of experience. "
            "You think in terms of pipeline, quota attainment, win rates, and deal velocity. "
            "Always relate metrics to revenue impact and growth opportunity."
        ),
        currency_kpis=["Total Revenue", "Avg Deal Size", "Pipeline Value"],
        pct_kpis=["Win Rate"],
        insights_focus=["revenue trends", "top performers", "deal velocity", "quota attainment"],
    ),
    "finance": DomainConfig(
        key="finance",
        label="Finance Analytics",
        kpi_columns=["profit", "loss", "expense", "cost", "budget", "revenue", "margin", "cash", "ebitda"],
        primary_kpis=["Net Profit", "Gross Margin", "Operating Expenses", "EBITDA", "Cash Flow"],
        chart_preferences=["line", "bar", "waterfall", "area"],
        analyst_persona=(
            "You are a senior financial analyst and CFO advisor. "
            "You think in terms of P&L, margins, EBITDA, and cash flow. "
            "Frame every insight around profitability, cost control, and financial health."
        ),
        currency_kpis=["Net Profit", "Operating Expenses", "EBITDA", "Cash Flow"],
        pct_kpis=["Gross Margin"],
        insights_focus=["profitability", "expense breakdown", "margin trends", "cash position"],
    ),
    "ecommerce": DomainConfig(
        key="ecommerce",
        label="E-commerce Analytics",
        kpi_columns=["order", "product", "customer", "cart", "conversion", "revenue", "return", "session"],
        primary_kpis=["Gross Revenue", "Orders", "Conversion Rate", "Avg Order Value", "Return Rate"],
        chart_preferences=["bar", "line", "heatmap", "funnel"],
        analyst_persona=(
            "You are a senior e-commerce growth analyst. "
            "You live and breathe conversion rates, cohort analysis, and customer LTV. "
            "Always think about funnel optimization, product performance, and retention."
        ),
        currency_kpis=["Gross Revenue", "Avg Order Value"],
        pct_kpis=["Conversion Rate", "Return Rate"],
        insights_focus=["top products", "conversion funnel", "customer behavior", "return trends"],
    ),
    "hr": DomainConfig(
        key="hr",
        label="HR Analytics",
        kpi_columns=["employee", "headcount", "attrition", "turnover", "hire", "salary", "department", "tenure"],
        primary_kpis=["Headcount", "Attrition Rate", "Avg Tenure", "Time to Hire", "Salary Median"],
        chart_preferences=["bar", "pie", "line", "box"],
        analyst_persona=(
            "You are a senior HR analytics professional and people operations expert. "
            "You focus on workforce trends, attrition risk, talent acquisition, and compensation equity. "
            "Frame insights around business impact of people decisions."
        ),
        currency_kpis=["Salary Median"],
        pct_kpis=["Attrition Rate"],
        insights_focus=["attrition risk", "hiring trends", "department distribution", "tenure analysis"],
    ),
    "healthcare": DomainConfig(
        key="healthcare",
        label="Healthcare Analytics",
        kpi_columns=["patient", "admission", "discharge", "diagnosis", "treatment", "readmission", "length_of_stay", "bed"],
        primary_kpis=["Total Patients", "Avg Length of Stay", "Readmission Rate", "Bed Occupancy", "Treatment Success"],
        chart_preferences=["bar", "line", "heatmap", "pie"],
        analyst_persona=(
            "You are a senior healthcare data analyst with clinical operations expertise. "
            "You focus on patient outcomes, operational efficiency, and resource utilization. "
            "Always frame insights in terms of patient care quality and operational sustainability."
        ),
        currency_kpis=[],
        pct_kpis=["Readmission Rate", "Bed Occupancy", "Treatment Success"],
        insights_focus=["patient volume", "length of stay", "readmission risk", "treatment outcomes"],
    ),
    "marketing": DomainConfig(
        key="marketing",
        label="Marketing Analytics",
        kpi_columns=["campaign", "impression", "click", "ctr", "cpc", "roas", "lead", "conversion", "spend"],
        primary_kpis=["Total Spend", "Impressions", "CTR", "ROAS", "Leads Generated"],
        chart_preferences=["bar", "line", "funnel", "scatter"],
        analyst_persona=(
            "You are a senior performance marketing analyst. "
            "You think in ROAS, CAC, LTV, and channel attribution. "
            "Always connect spend to measurable pipeline and revenue outcomes."
        ),
        currency_kpis=["Total Spend"],
        pct_kpis=["CTR", "ROAS"],
        insights_focus=["channel performance", "spend efficiency", "lead quality", "campaign ROI"],
    ),
    "inventory": DomainConfig(
        key="inventory",
        label="Inventory Analytics",
        kpi_columns=["stock", "sku", "quantity", "reorder", "turnover", "warehouse", "supplier", "lead_time"],
        primary_kpis=["Total SKUs", "Stock Turnover", "Out-of-Stock Rate", "Avg Lead Time", "Inventory Value"],
        chart_preferences=["bar", "line", "scatter", "heatmap"],
        analyst_persona=(
            "You are a senior supply chain and inventory analyst. "
            "You focus on stock optimization, turnover rates, and supplier performance. "
            "Frame insights around working capital efficiency and fulfillment reliability."
        ),
        currency_kpis=["Inventory Value"],
        pct_kpis=["Out-of-Stock Rate", "Stock Turnover"],
        insights_focus=["stock levels", "turnover efficiency", "reorder points", "supplier performance"],
    ),
    "generic": DomainConfig(
        key="generic",
        label="General Analytics",
        kpi_columns=[],
        primary_kpis=["Row Count", "Unique Values", "Numeric Columns", "Date Range"],
        chart_preferences=["bar", "line", "scatter", "histogram"],
        analyst_persona=(
            "You are a senior data and business analyst with broad business intelligence experience. "
            "Identify patterns, trends, and anomalies in the data and translate them into business impact, executive recommendations, and clear action items."
        ),
        currency_kpis=[],
        pct_kpis=[],
        insights_focus=["data distribution", "trends", "correlations", "anomalies"],
    ),
}

# Education and Telecom inherit from generic with minor tweaks
DOMAIN_CONFIGS["education"] = DomainConfig(
    key="education",
    label="Education Analytics",
    kpi_columns=["student", "enrollment", "grade", "pass", "fail", "attendance", "score", "course"],
    primary_kpis=["Enrollment", "Pass Rate", "Avg Score", "Attendance Rate", "Course Completion"],
    chart_preferences=["bar", "line", "histogram", "heatmap"],
    analyst_persona=(
        "You are a senior education data analyst. "
        "You focus on student outcomes, engagement, and institutional performance. "
        "Frame insights to support educators and administrators in improving learning results."
    ),
    currency_kpis=[],
    pct_kpis=["Pass Rate", "Attendance Rate", "Course Completion"],
    insights_focus=["student performance", "attendance trends", "course outcomes", "grade distribution"],
)
DOMAIN_CONFIGS["telecom"] = DomainConfig(
    key="telecom",
    label="Telecom Analytics",
    kpi_columns=["subscriber", "churn", "arpu", "data_usage", "call", "plan", "activation", "network"],
    primary_kpis=["Total Subscribers", "Churn Rate", "ARPU", "Data Usage", "Net Additions"],
    chart_preferences=["line", "bar", "heatmap", "funnel"],
    analyst_persona=(
        "You are a senior telecom business analyst. "
        "You think in subscriber growth, churn, and ARPU optimization. "
        "Frame insights around subscriber lifetime value and network monetization."
    ),
    currency_kpis=["ARPU"],
    pct_kpis=["Churn Rate"],
    insights_focus=["churn risk", "ARPU trends", "subscriber growth", "plan distribution"],
)


class DomainService:
    """Detects or resolves the business domain and returns its DomainConfig."""

    def auto_detect(self, df: pd.DataFrame) -> str:
        """Score columns against domain keyword lists and return best match key."""
        col_text = " ".join(df.columns.tolist()).lower()
        scores = {}
        for key, cfg in DOMAIN_CONFIGS.items():
            if key == "generic":
                continue
            score = sum(1 for kw in cfg.kpi_columns if kw in col_text)
            scores[key] = score

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "generic"

    def get_config(self, domain_key: str) -> DomainConfig:
        return DOMAIN_CONFIGS.get(domain_key, DOMAIN_CONFIGS["generic"])

    def domain_options(self) -> dict[str, str]:
        return DOMAINS
