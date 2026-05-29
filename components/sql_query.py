"""
sql_query.py — SQL Query Engine UI (Phase 3).
Rendered inside the Data Copilot tab; does not alter global app layout.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from services.sql_engine import SQLEngine, SqlQueryResult

SUGGESTED_SQL_QUESTIONS = [
    "What are the top 10 rows by the main numeric column?",
    "How many records are there in total?",
    "What is the average of each numeric column?",
    "Show the count of records grouped by the first categorical column.",
    "What are the minimum and maximum values for numeric columns?",
]


def render_sql_query(df: pd.DataFrame, sql_engine: SQLEngine, source_name: str = "") -> None:
    st.markdown("#### 🗄️ SQL Query Engine")
    st.caption("Ask a question in plain English — AI writes SQL, runs it safely (SELECT only), and explains the result.")

    try:
        schema = sql_engine.ensure_loaded(df, source_name=source_name or "dataset")
    except Exception as exc:
        st.error(f"Could not initialize SQL database: {exc}")
        return

    with st.expander("📋 Table schema", expanded=False):
        st.markdown(f"**Table:** `{schema.table_name}` · **Rows:** {schema.row_count:,}")
        schema_df = pd.DataFrame(
            [{"Column": c.name, "Type": c.dtype} for c in schema.columns]
        )
        st.dataframe(schema_df, use_container_width=True, hide_index=True)

    for i, q in enumerate(SUGGESTED_SQL_QUESTIONS[:3]):
        if st.button(q, key=f"sql_suggest_{i}", use_container_width=True):
            st.session_state.sql_question_input = q
            st.rerun()

    question = st.text_input(
        "Your question",
        value=st.session_state.get("sql_question_input", ""),
        placeholder="e.g. What is the average order value by country?",
        key="sql_question_input",
    )

    col_run, col_clear = st.columns([1, 1])
    with col_run:
        run = st.button("▶ Run SQL query", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.pop("sql_query_result", None)
            st.session_state.sql_question_input = ""
            st.rerun()

    if run and question.strip():
        with st.spinner("Generating SQL and running query…"):
            result = sql_engine.ask(question.strip())
            st.session_state.sql_query_result = result

    result: SqlQueryResult | None = st.session_state.get("sql_query_result")
    if result:
        _render_result(result)


def _render_result(result: SqlQueryResult) -> None:
    st.markdown("---")
    st.markdown("**Your question**")
    st.info(result.question)

    st.markdown("**Generated SQL**")
    st.code(result.sql or "-- no SQL generated --", language="sql")

    if not result.success:
        st.error(result.error or "Query failed.")
        return

    st.markdown("**Query results**")
    if result.result_df is not None and len(result.result_df):
        st.dataframe(result.result_df, use_container_width=True)
        st.caption(f"{len(result.result_df):,} row(s)")
    else:
        st.warning("Query succeeded but returned no rows.")

    st.markdown("**Explanation**")
    st.write(result.explanation)
