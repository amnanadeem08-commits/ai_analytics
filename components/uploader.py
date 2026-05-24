"""
uploader.py — Handles CSV/XLSX upload, validation, and initial parsing.
"""

import io
import logging
from pathlib import Path

import pandas as pd
import streamlit as st

from config import MAX_UPLOAD_MB, MAX_ROWS_ANALYSIS, UPLOADS_DIR

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = ["csv", "xlsx", "xls"]


def render_uploader() -> tuple[pd.DataFrame | None, str]:
    """
    Renders the file uploader widget.
    Returns (DataFrame or None, filename or '').
    """
    st.markdown("""
    <div style="
        border: 2px dashed #C7D2FE;
        border-radius: 16px;
        padding: 2rem 2rem 1.5rem;
        text-align: center;
        background: #F5F3FF;
        margin-bottom: 1rem;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
        <div style="font-weight: 700; color: #4338CA; font-size: 1.1rem;">
            Upload your data file
        </div>
        <div style="color: #6B7280; font-size: 0.85rem; margin-top: 0.3rem;">
            CSV or Excel (.xlsx, .xls) · Max {mb}MB
        </div>
    </div>
    """.format(mb=MAX_UPLOAD_MB), unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload file",
        type=SUPPORTED_TYPES,
        label_visibility="collapsed",
        help=f"Supported formats: {', '.join(SUPPORTED_TYPES).upper()}. Max size: {MAX_UPLOAD_MB}MB.",
    )

    if uploaded is None:
        return None, ""

    # Size check
    size_mb = uploaded.size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        st.error(f"File too large ({size_mb:.1f}MB). Maximum allowed: {MAX_UPLOAD_MB}MB.")
        return None, ""

    with st.spinner("Parsing file..."):
        df, error = _parse_file(uploaded)

    if error:
        st.error(f"Could not parse file: {error}")
        return None, ""

    if len(df) > MAX_ROWS_ANALYSIS:
        st.warning(
            f"Dataset has {len(df):,} rows. Sampling {MAX_ROWS_ANALYSIS:,} rows for analysis."
        )
        df = df.sample(MAX_ROWS_ANALYSIS, random_state=42).reset_index(drop=True)

    # Save raw copy
    save_path = UPLOADS_DIR / uploaded.name
    try:
        if uploaded.name.endswith(".csv"):
            df.to_csv(save_path, index=False)
        else:
            df.to_excel(save_path, index=False)
    except Exception:
        pass

    st.success(f"✅ Loaded **{uploaded.name}** — {len(df):,} rows × {len(df.columns)} columns")
    return df, uploaded.name


def _parse_file(uploaded) -> tuple[pd.DataFrame | None, str]:
    try:
        name = uploaded.name.lower()
        content = uploaded.read()
        buf = io.BytesIO(content)

        if name.endswith(".csv"):
            # Try common encodings
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    buf.seek(0)
                    df = pd.read_csv(buf, encoding=enc, low_memory=False)
                    return df, ""
                except UnicodeDecodeError:
                    continue
            return None, "Could not decode CSV with common encodings."

        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(buf, engine="openpyxl")
            return df, ""

        return None, f"Unsupported extension: {name}"

    except Exception as e:
        logger.error("File parse error: %s", e)
        return None, str(e)
