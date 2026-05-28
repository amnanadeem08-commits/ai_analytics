"""
tabs/deep_analysis.py — Deep Analysis tab.

Contains:
  - Data preview
  - Data understanding panel
  - Correlation heatmap
  - Custom Chart Builder

BUG FIX: custom chart title no longer shows "undefined".
  Root cause: selection["title"] was None/empty when chart_type was user-selected.
  Fix: fall back to a constructed title from x_col + chart_type when title is falsy.
"""

from __future__ import annotations

import streamlit as st

from components.insights import render_data_preview
from tabs.dashboard import _render_data_understanding, render_chart


def _safe_chart_title(selection: dict, x_col, y_col, chart_type: str) -> str:
    """
    BUG FIX — returns a meaningful title regardless of what validate_chart_selection
    returns. Prevents 'undefined' from appearing in the UI.
    """
    title = selection.get("title") or selection.get("recommended_title")
    if title and title.strip().lower() not in ("", "undefined", "none"):
        return title
    # Construct a fallback title from available info
    parts = [chart_type]
    if x_col:
        parts.append(x_col.replace("_", " ").title())
    if y_col:
        parts.append("vs " + y_col.replace("_", " ").title())
    return " — ".join(parts)


def render(
    filtered_df,
    domain_cfg,
    cleaning_report,
    data_understanding_report,
    chart_svc,
) -> None:
    st.markdown("### 🔍 Deep Analysis")

    render_data_preview(filtered_df, cleaning_report.summary())

    st.markdown("**Automatic Data Understanding**")
    _render_data_understanding(data_understanding_report)

    # Correlation heatmap
    numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_cols) >= 3:
        st.markdown("**Correlation Matrix**")
        fig = chart_svc.correlation_heatmap(filtered_df, numeric_cols[:12])
        render_chart(fig, key="deep_corr")

    # ── Custom Chart Builder ──────────────────────────────────────────────────
    st.markdown("**Custom Chart Builder**")

    chart_options  = ["Bar", "Line", "Scatter", "Histogram", "Pie", "Heatmap", "Count Plot"]
    all_cols       = filtered_df.columns.tolist()
    numeric_cols   = filtered_df.select_dtypes(include=["number"]).columns.tolist()
    category_cols  = [c for c in all_cols if c not in numeric_cols]

    col_x, col_y, col_type = st.columns([3, 3, 2])
    with col_type:
        chart_type = st.selectbox("Chart type", chart_options, key="cb_type")

    x_col = y_col = None

    if chart_type == "Histogram":
        with col_x:
            x_col = st.selectbox(
                "Numeric column", numeric_cols or all_cols, key="cb_x"
            )
        with col_y:
            st.markdown("Histogram uses one numeric column to show distribution.")

    elif chart_type == "Count Plot":
        with col_x:
            x_col = st.selectbox(
                "Category", category_cols or all_cols, key="cb_x"
            )
        with col_y:
            st.markdown("Count Plot uses one categorical field to show frequency.")

    elif chart_type == "Heatmap":
        with col_x:
            st.markdown("Heatmap uses all numeric columns automatically.")
        with col_y:
            st.markdown("")

    else:
        with col_x:
            x_col = st.selectbox("X axis / Category", all_cols, key="cb_x")
        with col_y:
            y_col = st.selectbox(
                "Y axis (numeric)", numeric_cols or all_cols, key="cb_y"
            )

    if st.button("Generate Chart", type="primary"):
        selection = chart_svc.validate_chart_selection(x_col, y_col, chart_type, filtered_df)

        for warning in selection["warnings"]:
            st.warning(warning)

        if not selection["is_valid"]:
            st.error("Selected combination is invalid — see recommended chart below.")
            recommended = selection.get("recommended_chart")
            if recommended:
                st.info(f"Recommended: {recommended.replace('_', ' ').title()}")
                fig = chart_svc.build_custom_chart(
                    recommended, selection["cleaned_df"], x_col, y_col
                )
                if fig is not None:
                    # BUG FIX: use _safe_chart_title instead of selection['recommended_title']
                    title = _safe_chart_title(selection, x_col, y_col, recommended)
                    st.markdown(f"**{title}**")
                    render_chart(fig, key="custom_chart_rec")
                    insight = chart_svc.generate_chart_insight(
                        selection["cleaned_df"], x_col, y_col,
                        recommended, selection.get("aggregation"),
                    )
                    st.info(insight)
        else:
            try:
                fig = chart_svc.build_custom_chart(
                    selection["chart_type"], selection["cleaned_df"], x_col, y_col
                )
                if fig is None:
                    raise ValueError("Unable to build chart for selected combination.")

                # BUG FIX: was st.markdown(f"**{selection['title']}**") — title could be None
                title = _safe_chart_title(selection, x_col, y_col, selection["chart_type"])
                st.markdown(f"**{title}**")
                render_chart(fig, key="custom_chart")

                insight = chart_svc.generate_chart_insight(
                    selection["cleaned_df"], x_col, y_col,
                    selection["chart_type"], selection.get("aggregation"),
                )
                st.info(insight)

            except Exception as exc:
                st.error(f"Chart error: {exc}")

    # Descriptive statistics
    if numeric_cols:
        st.markdown("**Descriptive Statistics**")
        st.dataframe(
            filtered_df[numeric_cols].describe().T.style.format("{:.2f}"),
            use_container_width=True,
        )
