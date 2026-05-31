"""
tabs/custom_metrics.py — Power BI-style custom metric builder (no code required).

Users define KPIs from columns + operations; results render as KPI cards or charts.
"""

from __future__ import annotations

import re

import pandas as pd
import plotly.express as px
import streamlit as st

from components.kpi_cards import _get_icon_for_kpi

_FORBIDDEN_FORMULA = frozenset({"import", "exec", "open", "os", "sys"})


def _formula_is_unsafe(formula: str) -> bool:
    """Block dangerous keywords (word-aware so 'cost' does not match 'os')."""
    if "__" in formula:
        return True
    low = formula.lower()
    return any(re.search(rf"\b{re.escape(kw)}\b", low) for kw in _FORBIDDEN_FORMULA)


def compute_metric(df: pd.DataFrame, metric_def: dict):
    """Compute a custom metric from its definition dict."""
    col = metric_def["base_col"]
    op = metric_def["operation"]
    group = metric_def["group_col"]

    if op == "SUM":
        return df[col].sum() if not group else df.groupby(group, observed=True)[col].sum()
    if op == "AVERAGE":
        return df[col].mean() if not group else df.groupby(group, observed=True)[col].mean()
    if op == "COUNT":
        return df[col].count() if not group else df.groupby(group, observed=True)[col].count()
    if op == "MIN":
        return df[col].min() if not group else df.groupby(group, observed=True)[col].min()
    if op == "MAX":
        return df[col].max() if not group else df.groupby(group, observed=True)[col].max()
    if op == "% of Total":
        total = df[col].sum()
        if total == 0:
            return 0.0 if not group else pd.Series(dtype=float)
        if not group:
            return 100.0
        return df.groupby(group, observed=True)[col].sum() / total * 100
    if op == "Growth % (vs previous)":
        sorted_vals = df[col].dropna().values
        if len(sorted_vals) >= 2 and sorted_vals[-2] != 0:
            return (sorted_vals[-1] - sorted_vals[-2]) / sorted_vals[-2] * 100
        return 0.0
    if op == "Ratio (col A / col B)" and metric_def.get("col_b"):
        col_b = metric_def["col_b"]
        denom = df[col_b].sum()
        return df[col].sum() / denom if denom != 0 else 0.0
    if op == "Custom formula" and metric_def.get("formula"):
        formula = metric_def["formula"].strip()
        if _formula_is_unsafe(formula):
            return "Error: Invalid formula"
        try:
            allowed_cols = {c: df[c] for c in df.select_dtypes(include="number").columns}
            result = eval(formula, {"__builtins__": {}}, allowed_cols)
            if hasattr(result, "sum"):
                return float(result.sum())
            return float(result)
        except Exception as exc:
            return f"Error: {exc}"
    return None


def _format_scalar(value, operation: str) -> str:
    if isinstance(value, str):
        return value
    if operation in ("% of Total", "Growth % (vs previous)"):
        return f"{float(value):,.2f}%"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.2f}"
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    return f"{value:,}"


def _render_kpi_card(name: str, formatted: str) -> None:
    icon = _get_icon_for_kpi(name)
    st.markdown(
        f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(108,99,255,0.25);
                    border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:0.5rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <span style="font-size:0.72rem;font-weight:700;color:#9CA3AF;
                             text-transform:uppercase;letter-spacing:0.08em;">{name}</span>
                <div style="width:34px;height:34px;border-radius:10px;display:flex;
                            align-items:center;justify-content:center;font-size:1rem;
                            background:rgba(108,99,255,0.16);
                            border:1px solid rgba(108,99,255,0.3);">{icon}</div>
            </div>
            <div style="font-family:'JetBrains Mono',ui-monospace,monospace;
                        font-size:1.9rem;font-weight:700;color:#F3F4F6;line-height:1.1;
                        margin-top:0.35rem;">{formatted}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_grouped_chart(series: pd.Series, metric_name: str, metric_col: str) -> None:
    chart_df = series.reset_index()
    chart_df.columns = ["group", "value"]
    fig = px.bar(
        chart_df,
        x="group",
        y="value",
        color="value",
        color_continuous_scale=["#1A1D2E", "#6C63FF"],
        text="value",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8F0", family="Inter, system-ui, sans-serif"),
        margin=dict(l=8, r=8, t=36, b=8),
        height=320,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickangle=-25),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        title=dict(text=metric_name, font=dict(size=13, color="#E8E8F0"), x=0),
    )
    fig.update_traces(marker_line_width=0, texttemplate="%{text:,.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True, key=f"cm_chart_{metric_name}")

    table_df = chart_df.sort_values("value", ascending=False).reset_index(drop=True)
    table_df.index += 1
    st.dataframe(table_df, use_container_width=True, hide_index=False)


def render(df: pd.DataFrame, domain_cfg) -> None:
    """Entry point — custom metric builder tab."""
    st.markdown("### 📐 Custom Metrics")
    st.caption(
        "Build your own KPIs like Power BI **New Measure** — pick a column, an operation, "
        "and optionally group by category. No code required."
    )

    if "custom_metrics_list" not in st.session_state:
        st.session_state.custom_metrics_list = []

    if df is None or df.empty:
        st.info("Upload a dataset with numeric columns to create custom metrics.")
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found in this dataset.")
        return

    # ── Builder form ─────────────────────────────────────────────────────────
    st.markdown("### ➕ Create a new metric")

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        metric_name = st.text_input("Metric name", placeholder="e.g. Profit Margin %")
    with col2:
        base_col = st.selectbox("Column", numeric_cols, key="cm_base_col")
    with col3:
        operation = st.selectbox(
            "Operation",
            [
                "SUM", "AVERAGE", "COUNT", "MIN", "MAX",
                "% of Total", "Growth % (vs previous)",
                "Ratio (col A / col B)", "Custom formula",
            ],
            key="cm_operation",
        )

    col_b = None
    if operation == "Ratio (col A / col B)":
        other = [c for c in numeric_cols if c != base_col]
        if not other:
            st.warning("Need at least two numeric columns for a ratio.")
        else:
            col_b = st.selectbox("Divide by column", other, key="cm_col_b")

    group_col = st.selectbox(
        "Group by (optional)", ["None"] + categorical_cols, key="cm_group",
    )
    if group_col == "None":
        group_col = None

    formula = None
    if operation == "Custom formula":
        st.caption(
            "Use column names in formula. Example: `revenue - cost`  or  `profit / revenue * 100`"
        )
        formula = st.text_input("Formula", placeholder="revenue - cost", key="cm_formula")
        if formula and _formula_is_unsafe(formula):
            st.error("Invalid formula — disallowed keywords detected.")

    if st.button("Add metric", type="primary", key="cm_add_btn"):
        if not metric_name or not base_col:
            st.error("Please enter a metric name and select a column.")
        elif operation == "Custom formula" and formula and _formula_is_unsafe(formula):
            st.error("Invalid formula")
        elif operation == "Ratio (col A / col B)" and not col_b:
            st.error("Please select a second column for the ratio.")
        else:
            st.session_state.custom_metrics_list.append({
                "name": metric_name.strip(),
                "base_col": base_col,
                "operation": operation,
                "col_b": col_b,
                "group_col": group_col,
                "formula": formula,
            })
            st.success(f"Metric '{metric_name.strip()}' added!")
            st.rerun()

    st.divider()

    # ── Display saved metrics ────────────────────────────────────────────────
    st.markdown("### 📊 Your custom metrics")

    if not st.session_state.custom_metrics_list:
        st.info("No custom metrics yet. Use the form above to create one.")
        return

    for i, metric_def in enumerate(st.session_state.custom_metrics_list):
        header_col, del_col = st.columns([6, 1])
        with header_col:
            op_label = metric_def["operation"]
            base = metric_def["base_col"]
            st.markdown(f"**{metric_def['name']}** · `{op_label}` on `{base}`")
        with del_col:
            if st.button("✕", key=f"del_{i}", help="Remove this metric"):
                st.session_state.custom_metrics_list.pop(i)
                st.rerun()

        result = compute_metric(df, metric_def)

        if isinstance(result, pd.Series):
            _render_grouped_chart(result, metric_def["name"], metric_def["base_col"])
        elif result is not None:
            formatted = _format_scalar(result, metric_def["operation"])
            _render_kpi_card(metric_def["name"], formatted)
        else:
            st.warning("Could not compute this metric with the current settings.")

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
