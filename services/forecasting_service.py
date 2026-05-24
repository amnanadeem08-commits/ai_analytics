"""
forecasting_service.py — Time-series forecasts via linear regression and exponential smoothing.
"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from config import FORECAST_PERIODS

logger = logging.getLogger(__name__)


@dataclass
class ForecastPoint:
    """Single forecasted observation."""

    period_label: str
    value: float
    method: str


@dataclass
class ForecastResult:
    """Forecast output for one numeric column over a date axis."""

    column: str
    date_column: str
    method: str
    historical_mean: float
    forecast_points: list[ForecastPoint] = field(default_factory=list)
    trend_direction: str = "flat"
    summary: str = ""


class ForecastingService:
    """Produces lightweight forecasts without heavy ML models."""

    def forecast(
        self,
        df: pd.DataFrame,
        periods: int | None = None,
        max_series: int = 3,
    ) -> list[ForecastResult]:
        """
        Forecast up to max_series numeric columns when a datetime column exists.
        """
        if df is None or df.empty:
            return []

        n_periods = periods or FORECAST_PERIODS
        date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        if not date_cols:
            return []

        date_col = date_cols[0]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_series]
        results: list[ForecastResult] = []

        for col in numeric_cols:
            try:
                result = self._forecast_column(df, date_col, col, n_periods)
                if result:
                    results.append(result)
            except Exception as e:
                logger.warning("Forecast failed for %s: %s", col, e)

        return results

    def _forecast_column(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str,
        periods: int,
    ) -> ForecastResult | None:
        """Build linear and EWM-blended forecast for one series."""
        work = df[[date_col, value_col]].dropna().sort_values(date_col)
        if len(work) < 5:
            return None

        y = work[value_col].astype(float).values
        x = np.arange(len(y))

        slope, intercept, r, _, _ = stats.linregress(x, y)
        direction = "up" if slope > 0 else ("down" if slope < 0 else "flat")

        ewm = pd.Series(y).ewm(span=min(7, len(y)), adjust=False).mean()
        last_ewm = float(ewm.iloc[-1])
        last_linear = float(intercept + slope * (len(y) - 1))

        points: list[ForecastPoint] = []
        for i in range(1, periods + 1):
            linear_val = intercept + slope * (len(y) - 1 + i)
            ewm_val = last_ewm + (ewm.diff().dropna().mean() if len(ewm) > 1 else 0) * i
            blended = 0.5 * linear_val + 0.5 * ewm_val
            points.append(ForecastPoint(
                period_label=f"T+{i}",
                value=round(blended, 2),
                method="linear+ewm",
            ))

        hist_mean = float(np.mean(y))
        summary = (
            f"{value_col.replace('_', ' ').title()} is trending {direction} "
            f"(linear slope {slope:+.4f}/period). "
            f"Next {periods} periods projected via blended linear + exponential smoothing."
        )

        return ForecastResult(
            column=value_col,
            date_column=date_col,
            method="linear+ewm",
            historical_mean=hist_mean,
            forecast_points=points,
            trend_direction=direction,
            summary=summary,
        )
