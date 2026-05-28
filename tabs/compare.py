"""tabs/compare.py — Dataset Comparison tab."""

from __future__ import annotations

import logging

import streamlit as st

from components.comparison import render_comparison_results, render_comparison_upload

logger = logging.getLogger(__name__)


def render(filtered_df, domain_cfg, comparison_svc) -> None:
    st.markdown("### ⚖️ Dataset Comparison")
    st.caption(f"Baseline: **{st.session_state.filename}** ({len(filtered_df):,} rows)")

    compare_df, compare_name = render_comparison_upload()
    if compare_df is not None:
        st.session_state.compare_df       = compare_df
        st.session_state.compare_filename = compare_name

    if st.session_state.get("compare_df") is not None:
        if st.button("Run comparison", type="primary"):
            try:
                report = comparison_svc.compare(
                    filtered_df,
                    st.session_state.compare_df,
                    domain_cfg,
                    baseline_label=st.session_state.filename,
                    compare_label=st.session_state.compare_filename or "Dataset B",
                )
                st.session_state.comparison_report = report
            except Exception as exc:
                st.error(f"Comparison failed: {exc}")

        if st.session_state.get("comparison_report"):
            render_comparison_results(st.session_state.comparison_report)
