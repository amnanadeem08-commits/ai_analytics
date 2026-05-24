"""
cleaning_service.py — Automated data cleaning pipeline.
Handles missing values, duplicates, type inference, outliers, and time-series detection.
"""

import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import Optional
from config import MISSING_DROP_THRESHOLD, DUPLICATE_KEEP, OUTLIER_STD_MULTIPLIER

logger = logging.getLogger(__name__)


@dataclass
class CleaningReport:
    original_shape: tuple
    cleaned_shape: tuple
    dropped_columns: list = field(default_factory=list)
    filled_columns: dict = field(default_factory=dict)   # col -> strategy
    duplicates_removed: int = 0
    dtype_changes: dict = field(default_factory=dict)
    outliers_flagged: dict = field(default_factory=dict)
    date_columns: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def rows_removed(self) -> int:
        return self.original_shape[0] - self.cleaned_shape[0]

    @property
    def cols_removed(self) -> int:
        return self.original_shape[1] - self.cleaned_shape[1]

    def summary(self) -> str:
        parts = [
            f"Original: {self.original_shape[0]:,} rows × {self.original_shape[1]} cols",
            f"Cleaned:  {self.cleaned_shape[0]:,} rows × {self.cleaned_shape[1]} cols",
            f"Rows removed: {self.rows_removed:,} (duplicates: {self.duplicates_removed:,})",
            f"Columns dropped: {len(self.dropped_columns)}",
        ]
        if self.date_columns:
            parts.append(f"Date columns detected: {', '.join(self.date_columns)}")
        return "\n".join(parts)


class CleaningService:
    """Full data cleaning pipeline. Returns cleaned DataFrame + CleaningReport."""

    def clean(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        report = CleaningReport(original_shape=df.shape, cleaned_shape=df.shape)
        df = df.copy()

        df = self._normalize_columns(df)
        df = self._drop_index_noise(df)
        df, report = self._drop_high_missing(df, report)
        df, report = self._remove_duplicates(df, report)
        df, report = self._infer_types(df, report)
        df, report = self._fill_missing(df, report)
        df, report = self._flag_outliers(df, report)

        report.cleaned_shape = df.shape
        logger.info("Cleaning complete. %s", report.summary())
        return df, report

    # ── internal steps ─────────────────────────────────────────────────────────

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"[\s\-\/\(\)]+", "_", regex=True)
            .str.replace(r"[^\w]", "", regex=True)
            .str.strip("_")
        )
        return df

    def _drop_index_noise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exported row-index columns that are not business metrics."""
        drop = [
            c for c in df.columns
            if str(c).lower() in ("index", "unnamed", "unnamed_0")
            or str(c).lower().startswith("unnamed")
        ]
        if drop:
            logger.info("Dropping index noise columns: %s", drop)
            return df.drop(columns=drop, errors="ignore")
        return df

    def _drop_high_missing(
        self, df: pd.DataFrame, report: CleaningReport
    ) -> tuple[pd.DataFrame, CleaningReport]:
        missing_ratio = df.isnull().mean()
        to_drop = missing_ratio[missing_ratio > MISSING_DROP_THRESHOLD].index.tolist()
        if to_drop:
            report.dropped_columns.extend(to_drop)
            report.warnings.append(
                f"Dropped {len(to_drop)} column(s) with >{MISSING_DROP_THRESHOLD*100:.0f}% missing: {to_drop}"
            )
            df = df.drop(columns=to_drop)
        return df, report

    def _remove_duplicates(
        self, df: pd.DataFrame, report: CleaningReport
    ) -> tuple[pd.DataFrame, CleaningReport]:
        before = len(df)
        df = df.drop_duplicates(keep=DUPLICATE_KEEP)
        report.duplicates_removed = before - len(df)
        return df, report

    def _infer_types(
        self, df: pd.DataFrame, report: CleaningReport
    ) -> tuple[pd.DataFrame, CleaningReport]:
        date_cols = []
        for col in df.select_dtypes(include="object").columns:
            # try numeric
            converted = pd.to_numeric(df[col].str.replace(",", "").str.strip(), errors="coerce")
            if converted.notna().mean() > 0.85:
                report.dtype_changes[col] = "object → numeric"
                df[col] = converted
                continue

            # try datetime
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().mean() > 0.80:
                    report.dtype_changes[col] = "object → datetime"
                    df[col] = converted
                    date_cols.append(col)
            except Exception:
                pass

        report.date_columns = date_cols
        return df, report

    def _fill_missing(
        self, df: pd.DataFrame, report: CleaningReport
    ) -> tuple[pd.DataFrame, CleaningReport]:
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing == 0:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].median()
                strategy = f"median ({fill_val:.2f})"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                fill_val = df[col].mode().iloc[0] if not df[col].mode().empty else pd.NaT
                strategy = "mode"
            else:
                fill_val = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                strategy = f"mode ({fill_val!r})"

            df[col] = df[col].fillna(fill_val)
            report.filled_columns[col] = strategy

        return df, report

    def _flag_outliers(
        self, df: pd.DataFrame, report: CleaningReport
    ) -> tuple[pd.DataFrame, CleaningReport]:
        for col in df.select_dtypes(include=[np.number]).columns:
            mean, std = df[col].mean(), df[col].std()
            if std == 0:
                continue
            mask = (df[col] - mean).abs() > OUTLIER_STD_MULTIPLIER * std
            count = int(mask.sum())
            if count > 0:
                report.outliers_flagged[col] = count
        return df, report
