# AI Analytics Assistant — Version 4.0+ Systematic Roadmap

## **Strategic Phases (Build Order)**

All features grouped by **logical dependency** and **shared infrastructure**.

---

## **PHASE 1: Foundation Layer (Weeks 1-2)**
*Enhances existing analytics with depth, not new UI complexity.*

### **Sprint 1.1: Advanced Anomaly Detection**
**Why first:** Builds on existing `AnalyticsReport`, adds immediate value to dashboards.

**New Components:**
- `AnomalyDetectionService` (enhanced)
  - Z-score + IQR methods
  - Time-series change detection
  - Seasonality-aware alerts
  - Severity scoring (critical/warning/info)

- `AnomalyResult` dataclass
  - Anomaly type (outlier / trend shift / seasonal deviation)
  - Confidence score (0–1)
  - Recommended action

**UI Changes:**
- Dashboard KPI cards: Red highlight if anomaly detected
- "⚠️ Alert Banner" at top of dashboard
- Anomalies tab showing top 10 issues
- Click anomaly → drill to affected rows

**Dependencies:** None (uses existing analytics)
**Estimated effort:** 2–3 days
**File changes:**
  - `services/analytics_service.py` → add anomaly severity & type
  - `services/anomaly_narration_service.py` → enhance with time-series
  - `components/insights.py` → render anomaly alerts
  - `app.py` → add alert banner

---

### **Sprint 1.2: Data Quality Profiling**
**Why here:** Complements anomaly detection; helps identify data issues early.

**New Components:**
- `DataProfileService`
  - Column-level statistics
  - Null/duplicate heatmaps
  - Distribution shape analysis
  - Cardinality summary

- `ColumnProfile` dataclass (enhance)
  - Skewness / kurtosis
  - Data quality score (0–100)
  - Sample values

**UI Changes:**
- "Data Quality" tab with:
  - Overall score gauge
  - Per-column heatmap (null %, uniqueness, distribution)
  - Sample rows by column
  - Data completeness timeline (if date column exists)

**Dependencies:** Extends existing `profile_dataframe()`
**Estimated effort:** 2 days
**File changes:**
  - `services/data_quality_service.py` → enhance profiling
  - `components/data_quality.py` → add heatmaps
  - `app.py` → add profiling dashboard section

---

### **Sprint 1.3: Custom Metrics Builder**
**Why here:** Foundation for all downstream analytics (forecasting, segments, etc.).

**New Components:**
- `MetricsDefinitionService`
  - Parse metric formulas: `(Revenue - Cost) / Revenue`
  - Validate column references
  - Cache computed metrics

- `CustomMetric` dataclass
  - Name, formula, description
  - Data type (currency, %, number)
  - Formula AST (for validation)

- Metric templates (library)
  - Sales: `Win Rate = Wins / Total Deals`
  - Finance: `Margin = (Revenue - Cost) / Revenue`
  - HR: `Turnover = Departures / Avg Headcount`
  - Healthcare: `Readmission = Readmissions / Discharges`

**UI Changes:**
- Sidebar: "Define Custom Metrics"
- Formula builder with:
  - Dropdown column selector
  - Operator buttons (+, -, *, /)
  - Preset templates
  - Formula validation
- Save metric → reuse in KPI cards, charts

**Dependencies:** Uses existing column profiling
**Estimated effort:** 3–4 days
**File changes:**
  - New: `services/metrics_service.py`
  - `app.py` → add metrics sidebar
  - `components/sidebar.py` → custom metric builder
  - `services/kpi_service.py` → use custom metrics

---

**End of Phase 1 Output:**
- App detects & alerts on problems (anomalies)
- App understands data structure (profiling)
- Users can define custom KPIs (metrics builder)

---

## **PHASE 2: Predictive Intelligence (Weeks 3-4)**
*Forecast trends, predict outcomes, scenario model.*

### **Sprint 2.1: Time-Series Forecasting (Enhanced)**
**Why here:** Needs Phase 1's data quality understanding.

**New Components:**
- `AdvancedForecastingService`
  - Prophet (existing) + ARIMA + Exponential Smoothing
  - Auto-select best method
  - Confidence intervals (80%, 95%)
  - Seasonality detection
  - Forecast horizons: 3/6/12 months

- `ForecastResult` dataclass
  - Forecast values + bounds
  - Trend direction (↑ / → / ↓)
  - Confidence
  - Method used

**UI Changes:**
- "Forecast" tab with:
  - Interactive chart (actual + forecast + bounds)
  - Trend badge ("📈 Strong growth", "📉 Declining", "→ Flat")
  - Forecast table (next 12 months)
  - "Download forecast" CSV
  - Forecast assumptions explainer

**Dependencies:** Phase 1 (data quality helps validation)
**Estimated effort:** 3–4 days
**File changes:**
  - `services/forecasting_service.py` → add Prophet + ARIMA
  - New: `components/forecast.py` (forecast UI)
  - `app.py` → add forecast tab

---

### **Sprint 2.2: Predictive Models (Churn / Segmentation)**
**Why after forecasting:** Uses feature engineering from Phase 2.1.

**New Components:**
- `PredictiveModelService`
  - Churn prediction (logistic regression / XGBoost)
  - Customer segmentation (K-means + silhouette analysis)
  - Feature importance ranking
  - Model performance metrics (AUC, accuracy)

- `ChurnPrediction` dataclass
  - Customer ID, churn score (0–1), top risk factors

- `Segment` dataclass
  - Segment ID, size, characteristics, performance

**UI Changes:**
- "Predictive" tab with:
  - Churn prediction:
    - List of at-risk customers (sortable)
    - Risk factors for each customer
    - Recommended retention actions
  - Segmentation:
    - Segment distribution (pie/bar)
    - Segment profiles (avg metrics per segment)
    - Segment comparison heatmap
    - Cohort-specific KPIs

**Dependencies:** Phase 1 (data quality), Phase 2.1 (time-series features)
**Estimated effort:** 4–5 days
**File changes:**
  - New: `services/churn_prediction_service.py`
  - New: `services/segmentation_service.py`
  - New: `components/predictive.py`
  - `app.py` → add predictive tab

---

### **Sprint 2.3: What-If Scenario Modeling**
**Why last in phase:** Uses custom metrics + forecasting + predictions.

**New Components:**
- `ScenarioService`
  - User inputs: "If Revenue ↑ 20%, what happens to Profit?"
  - Sensitivity analysis (how much does each variable matter?)
  - Monte Carlo simulation (range of outcomes)
  - Output: Impact on KPIs + forecast

- `Scenario` dataclass
  - Name, assumptions (input changes), results

**UI Changes:**
- "Scenarios" tab with:
  - Scenario builder (input sliders)
  - Sensitivity tornado chart (which factors matter most?)
  - Impact on forecasts
  - Save / compare scenarios
  - Export scenario analysis

**Dependencies:** Phase 1 (metrics), Phase 2.1 (forecasts), Phase 2.2 (models)
**Estimated effort:** 3–4 days
**File changes:**
  - New: `services/scenario_service.py`
  - New: `components/scenarios.py`
  - `app.py` → add scenarios tab

---

**End of Phase 2 Output:**
- App forecasts future trends
- App predicts customer churn & segments
- App models "what-if" scenarios

---

## **PHASE 3: Exploration & Drill-Down (Weeks 5-6)**
*Deep dive into data, understand causation, interactive discovery.*

### **Sprint 3.1: Cohort Analysis Service**
**Why here:** Needs Phase 2 segmentation foundation.

**New Components:**
- `CohortAnalysisService`
  - Define cohorts by: acquisition date, segment, behavior
  - Track cohort metrics over time
  - Retention curves (% of cohort active each month)
  - Cohort comparison stats

- `Cohort` dataclass
  - Cohort ID, size, entry date, metrics over time

**UI Changes:**
- "Cohort Analysis" tab with:
  - Cohort selector (by date, segment, etc.)
  - Retention matrix (cohort × month)
  - Retention curve (Kaplan-Meier style)
  - Cohort performance comparison
  - Export cohort analysis

**Dependencies:** Phase 2 (segmentation)
**Estimated effort:** 2–3 days
**File changes:**
  - New: `services/cohort_service.py`
  - New: `components/cohort.py`
  - `app.py` → add cohort tab

---

### **Sprint 3.2: Interactive Drill-Down**
**Why here:** Integrates with existing charts + new cohort/segment views.

**New Components:**
- Drill-down state management in `session_service.py`
- Click event handlers for charts
- Row-level filtering UI

**UI Changes:**
- Charts become clickable:
  - Click bar → see underlying rows
  - Click line point → see date's data
  - Click pie slice → see category details
- "Drill-Down" modal:
  - Show matching rows (sortable table)
  - Apply secondary filters
  - Pivot or export drilled rows
- Breadcrumb navigation (Chart → Bar → Rows)

**Dependencies:** Phase 1 (data understanding)
**Estimated effort:** 3–4 days
**File changes:**
  - `services/session_service.py` → drill-down state
  - `app.py` → drill-down event handlers
  - New: `components/drill_down.py`

---

### **Sprint 3.3: Pivot Tables & Custom Aggregations**
**Why last in phase:** Requires drill-down infrastructure.

**New Components:**
- `PivotTableService`
  - Build pivot from rows/columns/values
  - Multiple aggregations (sum, avg, count, etc.)
  - Percentage calculations (% of total, % of row/col)

**UI Changes:**
- "Pivot Tables" tab or sidebar option
- Pivot builder:
  - Rows / Columns / Values dropdowns
  - Aggregation type selector
  - Grand totals
  - Export as CSV / Excel
- Pre-built pivots (templates):
  - `Revenue by Country × Month`
  - `Churn Rate by Segment × Cohort`

**Dependencies:** Phase 1 (metrics), Phase 3.2 (drill-down)
**Estimated effort:** 2–3 days
**File changes:**
  - New: `services/pivot_service.py`
  - New: `components/pivot_table.py`
  - `app.py` → add pivot tab

---

**End of Phase 3 Output:**
- App enables exploration via drill-down & pivots
- App analyzes cohorts & trends
- Users can answer "Why did X happen?" questions

---

## **PHASE 4: Advanced Analytics & Export (Weeks 7-8)**
*Multi-dataset comparison, rich export, optional text analysis.*

### **Sprint 4.1: Multi-Dataset Comparison**
**Why here:** Builds on stable v3 foundation.

**New Components:**
- `ComparisonService` (enhance)
  - Compare 2+ datasets
  - Statistical tests (t-test, chi-square, KS-test)
  - Difference heatmaps
  - Segment comparison matrices

**UI Changes:**
- "Compare" tab (extend existing):
  - Upload multiple CSVs
  - Side-by-side KPI comparison
  - Difference charts (what changed?)
  - Statistical significance indicators
  - Download comparison report

**Dependencies:** Phase 1 (metrics), existing comparison module
**Estimated effort:** 2–3 days
**File changes:**
  - `services/comparison_service.py` → multi-dataset + stats
  - `components/comparison.py` → enhance UI

---

### **Sprint 4.2: Advanced Export (HTML / Power BI / Scheduled)**
**Why here:** Uses all previous analytics.

**New Components:**
- `AdvancedExportService`
  - HTML interactive dashboard (Plotly standalone)
  - Power BI connector (JSON metadata)
  - Scheduled email reports (CronJob)
  - Report templates (Sales/Finance/HR)

- Report metadata
  - Report name, owner, schedule, recipients
  - Included sections (KPIs, charts, forecasts, etc.)
  - Branding (logo, colors)

**UI Changes:**
- "Export" tab (enhance):
  - Report builder (select sections)
  - Template gallery
  - Schedule settings (daily/weekly/monthly + time + email)
  - Report library (view all generated reports)
  - Interactive HTML preview

**Dependencies:** Phase 1–3 (all analytics)
**Estimated effort:** 4–5 days
**File changes:**
  - `services/export_service.py` → enhance
  - New: `services/report_scheduler_service.py`
  - New: `components/export_advanced.py`
  - `app.py` → scheduled task runner

---

### **Sprint 4.3: Sentiment Analysis (Optional, for Social Media)**
**Why here:** Standalone feature, no hard dependencies.

**New Components:**
- `SentimentAnalysisService`
  - LLM-based sentiment (positive/neutral/negative)
  - Emotion detection (joy, anger, sadness, etc.)
  - Topic extraction (LDA / LLM)
  - Sentiment over time (trend)

**UI Changes:**
- "Sentiment" tab (if text columns exist):
  - Sentiment distribution (pie)
  - Emotion breakdown
  - Sentiment trend over time
  - Topic cloud
  - Sample quotes by sentiment

**Dependencies:** None (but uses AI config)
**Estimated effort:** 2–3 days
**File changes:**
  - New: `services/sentiment_service.py`
  - New: `components/sentiment.py`
  - `app.py` → add sentiment tab (conditional)

---

**End of Phase 4 Output:**
- App supports multi-dataset comparison
- App exports rich, scheduled reports
- App analyzes sentiment in text (optional)

---

## **PHASE 5: Collaboration & Scale (Weeks 9+)**
*Long-term, requires infrastructure changes.*

### **Sprint 5.1: Collaborative Workspace**
- User accounts & authentication
- Shared workspaces & permissions
- Comments on findings
- Version history of reports

### **Sprint 5.2: Attribution & Marketing Mix**
- Multi-touch attribution (which channel drove sale?)
- Budget optimization
- Channel ROI analysis

### **Sprint 5.3: Mobile App**
- Responsive Streamlit views OR React frontend
- Native mobile app (optional)
- Push notifications for alerts

---

## **Dependency Graph (Visual)**

```
PHASE 1
├─ Anomaly Detection
├─ Data Quality Profiling
└─ Custom Metrics Builder

PHASE 2 (builds on Phase 1)
├─ Forecasting (enhanced)
├─ Churn / Segmentation (uses Phase 2.1)
└─ Scenarios (uses 2.1 + 2.2)

PHASE 3 (builds on Phases 1-2)
├─ Cohort Analysis (needs Phase 2.2)
├─ Drill-Down (independent but synergizes)
└─ Pivot Tables (uses drill-down)

PHASE 4 (builds on Phases 1-3, independent)
├─ Multi-Dataset Comparison
├─ Advanced Export
└─ Sentiment Analysis (optional, independent)

PHASE 5 (long-term, infrastructure)
├─ Workspace / Auth
├─ Attribution Modeling
└─ Mobile App
```

---

## **Timeline Summary**

| Phase | Duration | Key Output | Go-Live |
|-------|----------|-----------|---------|
| Phase 1 | 2 weeks | Anomaly detection, profiling, custom metrics | v4.0 Beta |
| Phase 2 | 2 weeks | Forecasting, churn, scenarios | v4.0 Release |
| Phase 3 | 2 weeks | Drill-down, cohorts, pivots | v4.1 Release |
| Phase 4 | 2 weeks | Comparison, advanced export, sentiment | v4.2 Release |
| Phase 5 | 4+ weeks | Workspace, attribution, mobile | v5.0+ |

**Total MVP (Phases 1–3): 6 weeks**
**Full Feature Set (Phases 1–4): 8 weeks**

---

## **Resource Allocation (1 Developer)**

- **Week 1–2:** Phase 1 (parallel: sprints 1.1 + 1.2 in week 1, 1.3 in week 2)
- **Week 3–4:** Phase 2 (sequential: forecasting → churn → scenarios)
- **Week 5–6:** Phase 3 (cohorts, then drill-down, then pivots)
- **Week 7–8:** Phase 4 (comparison + export in parallel, sentiment separate)
- **Week 9+:** Phase 5 (as needed)

---

## **Success Metrics (Per Phase)**

**Phase 1:**
- ✓ Anomalies detected & displayed
- ✓ Data quality score visible
- ✓ Custom metrics saved & reused

**Phase 2:**
- ✓ Forecast 12 months out with bounds
- ✓ Churn score for top 100 customers
- ✓ 3+ scenario models saved

**Phase 3:**
- ✓ Drill-down from chart → rows
- ✓ Cohort retention curves
- ✓ Pivot table with custom aggregations

**Phase 4:**
- ✓ Multi-dataset statistical comparison
- ✓ Scheduled weekly reports emailed
- ✓ Sentiment trends visible (if applicable)

---

## **Start with Phase 1 This Week**

Ready to begin Sprint 1.1 (Anomaly Detection)?

I can start today with:
1. Enhanced `AnomalyDetectionService` with severity scoring
2. Alert banner in dashboard
3. Anomalies explorer tab

Let me know and I'll begin coding.
