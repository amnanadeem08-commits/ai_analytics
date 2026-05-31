# AI Data Reporting & Analytics Assistant

> **🌐 Live website (portfolio & services):**  
> **https://amnanadeem08-commits.github.io/ai_analytics/**  
>  
> This README is the **code repo**. Your **client-facing website** is the link above — not this page.

An AI-powered workflow analytics platform that behaves like a senior business/data analyst.
Upload any CSV or Excel file, and the platform automatically cleans it, detects your business domain, computes KPIs, generates visualisations, produces an AI executive summary, and exports professional reports.

---

## Features (Version 1)

| Capability | Details |
|---|---|
| **Data Engine** | CSV/XLSX upload, schema detection, missing value fill, deduplication, type inference, time-series detection |
| **Domain Detection** | Auto-detects from 10 business domains or manual override: Sales, Finance, E-commerce, HR, Healthcare, Marketing, Inventory, Education, Telecom, Generic |
| **KPI Engine** | Domain-aware KPI computation, currency/percentage formatting, trend deltas |
| **Analytics** | Statistical summary, trend detection (linear regression), anomaly detection (3σ), correlation matrix, distribution skew |
| **Visualisations** | Auto-selected Plotly charts: line, bar, scatter, histogram, heatmap, pie, sparklines |
| **AI Executive Summary** | LLM-generated domain-specific business narrative (Anthropic Claude or OpenAI GPT-4o) |
| **Data Copilot** | Stateful domain-aware chatbot with session history, suggested questions, context from full dataset |
| **Excel Export** | Multi-sheet XLSX: KPI summary, cleaned data, descriptive statistics |
| **PDF Export** | Professional A4 PDF with KPI grid, executive summary |
| **PPTX Export** | Branded slide deck: cover, KPI cards, exec summary, chart slides |

---

## Quickstart

### 1. Clone and set up environment

```bash
git clone <your-repo>
cd ai_analytics

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure AI provider

Copy `.env` and add your key:

```bash
cp .env .env.local
```

Edit `.env`:

```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

Or use OpenAI:

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

> The app works without an API key — AI summary and chatbot will gracefully degrade to statistical fallbacks.

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Project Structure

```
ai_analytics/
├── app.py                    ← Main Streamlit entry point
├── config.py                 ← Paths, constants, env vars
├── requirements.txt
├── .env                      ← API keys (never commit)
│
├── components/               ← UI building blocks
│   ├── uploader.py           ← File upload + validation
│   ├── sidebar.py            ← Domain selector, nav, filters
│   ├── kpi_cards.py          ← KPI metric cards
│   ├── chatbot.py            ← Copilot UI
│   └── insights.py           ← Summary + analytics panels
│
├── services/                 ← Business logic (no Streamlit)
│   ├── cleaning_service.py   ← Automated data pipeline
│   ├── domain_service.py     ← Domain detection + config
│   ├── kpi_service.py        ← KPI computation
│   ├── analytics_service.py  ← Stats, trends, anomalies
│   ├── chart_service.py      ← Plotly chart factory
│   ├── ai_summary_service.py ← LLM executive summary
│   ├── chatbot_service.py    ← Stateful Data Copilot
│   └── export_service.py     ← Excel / PDF / PPTX
│
├── data/raw/                 ← Original uploads preserved
├── uploads/                  ← Uploaded files
├── exports/                  ← Generated reports
└── logs/                     ← Application logs
```

---

## Supported Business Domains

Each domain changes KPIs, chart types, chatbot persona, and AI analysis focus:

| Domain | Key KPIs | Chatbot Persona |
|---|---|---|
| Sales | Revenue, Win Rate, Pipeline, Deal Size | Senior sales analyst |
| Finance | Profit, Margin, EBITDA, Cash Flow | CFO advisor |
| E-commerce | GMV, Conversion, AOV, Return Rate | Growth analyst |
| HR | Headcount, Attrition, Time-to-Hire | People ops expert |
| Healthcare | Patients, LoS, Readmissions, Occupancy | Clinical analyst |
| Marketing | ROAS, CTR, Spend, Leads | Performance marketer |
| Inventory | Turnover, Out-of-Stock, Lead Time | Supply chain analyst |
| Education | Pass Rate, Attendance, Enrollment | Ed-tech analyst |
| Telecom | ARPU, Churn, Subscribers | Telecom analyst |

---

## Roadmap

- **v1** ✅ Core platform (this release)
- **v2** Advanced chatbot reasoning, anomaly narration, smart chart selection, PDF/PPT polish
- **v3** Auth, multi-user, cloud storage, scheduled reports, API
- **v4** Autonomous analyst agents, forecasting, continuous monitoring

---

## Deployment

### GitHub Pages website (portfolio / services site)

| Page | URL |
|------|-----|
| **Your website** (share with clients) | **https://amnanadeem08-commits.github.io/ai_analytics/** |
| **GitHub repo** (source code — not the website) | https://github.com/amnanadeem08-commits/ai_analytics |

Built from `ai-services-web/` → published to the `docs/` folder.

**One-time setup:** GitHub → **Settings → Pages** → Source: **Deploy from branch** → Branch: `main` → Folder: **`/docs`**.

**Add website to repo profile:** On the repo home page, click the ⚙️ next to **About** → paste the website URL above → Save.

### Streamlit Cloud (live DataBot demo app)
1. Push the repository to GitHub.
2. Open https://share.streamlit.io and connect your GitHub account.
3. Create a new app and select:
   - Repository: `amnanadeem08-commits/ai_analytics`
   - Branch: `master`
   - Main file: `app.py`
4. Add the required secrets in Streamlit Cloud:
   - `AI_PROVIDER=anthropic` or `openai`
   - `ANTHROPIC_API_KEY=<your-key>` or `OPENAI_API_KEY=<your-key>`
5. Deploy and visit the generated Streamlit URL.

> The app will run without an AI API key, but LLM-based summaries and chatbot features will gracefully fall back to statistical summaries.

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Render / Railway
Point to `streamlit run app.py` as the start command and set env vars in the dashboard.
