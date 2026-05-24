"""
helpers.py — Shared utility functions used across services and components.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd


def configure_logging(log_dir: Path, level: int = logging.INFO):
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


def fmt_number(value: float, is_currency: bool = False, is_pct: bool = False) -> str:
    if is_pct:
        return f"{value:.1f}%"
    if is_currency:
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        return f"${value:.2f}"
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value/1_000:.1f}K"
    return f"{value:,.2f}"


def df_memory_mb(df: pd.DataFrame) -> float:
    return df.memory_usage(deep=True).sum() / (1024 ** 2)


def safe_filename(name: str) -> str:
    """Strip unsafe characters from a filename."""
    import re
    return re.sub(r"[^\w\-_\. ]", "_", name).strip()
