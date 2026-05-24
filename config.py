"""
config.py — Central configuration for AI Analytics Platform.
All environment variables, paths, and constants live here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEANED_DIR = DATA_DIR / "cleaned"
PROCESSED_DIR = DATA_DIR / "processed"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
SESSIONS_DIR = BASE_DIR / "sessions"
PROMPTS_DIR = BASE_DIR / "prompts"

for d in [RAW_DIR, CLEANED_DIR, PROCESSED_DIR, UPLOADS_DIR, EXPORTS_DIR, LOGS_DIR, SESSIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── AI Provider ────────────────────────────────────────────────────────────────
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")  # "anthropic" | "openai"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-opus-4-5")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "2048"))

# ── App settings ───────────────────────────────────────────────────────────────
APP_NAME = "AI Analytics Assistant"
APP_VERSION = "3.0.0"
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
MAX_ROWS_ANALYSIS = int(os.getenv("MAX_ROWS_ANALYSIS", "500_000"))

# ── Supported domains ──────────────────────────────────────────────────────────
DOMAINS = {
    "auto": "Auto-detect",
    "sales": "Sales Analytics",
    "finance": "Finance Analytics",
    "ecommerce": "E-commerce Analytics",
    "hr": "HR Analytics",
    "healthcare": "Healthcare Analytics",
    "marketing": "Marketing Analytics",
    "inventory": "Inventory Analytics",
    "education": "Education Analytics",
    "telecom": "Telecom Analytics",
    "generic": "General / Other",
}

# ── Chart palette ──────────────────────────────────────────────────────────────
CHART_COLORS = [
    "#5046E4", "#0E9F6E", "#E3A008", "#E74694",
    "#3F83F8", "#F98080", "#9061F9", "#31C48D",
]

# ── Cleaning thresholds ────────────────────────────────────────────────────────
MISSING_DROP_THRESHOLD = 0.60   # drop column if >60% missing
DUPLICATE_KEEP = "first"
OUTLIER_STD_MULTIPLIER = 3.0

# ── V2 settings ────────────────────────────────────────────────────────────────
FORECAST_PERIODS = int(os.getenv("FORECAST_PERIODS", "6"))
SMART_CHARTS_ENABLED = os.getenv("SMART_CHARTS_ENABLED", "true").lower() == "true"
SESSION_ID_LENGTH = 12
CHART_HEIGHT = int(os.getenv("CHART_HEIGHT", "420"))
CHART_MAX_CATEGORY_CARDINALITY = 40

# ── V3: category-wise analytics ────────────────────────────────────────────────
V3_CATEGORY_ANALYTICS_ENABLED = os.getenv("V3_CATEGORY_ANALYTICS_ENABLED", "true").lower() == "true"
V3_MAX_CATEGORY_COLUMNS = int(os.getenv("V3_MAX_CATEGORY_COLUMNS", "8"))
V3_CATEGORY_TOP_N = int(os.getenv("V3_CATEGORY_TOP_N", "20"))
V3_CHARTS_PER_CATEGORY = int(os.getenv("V3_CHARTS_PER_CATEGORY", "4"))
