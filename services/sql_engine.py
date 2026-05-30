"""
sql_engine.py — In-memory SQL engine for uploaded datasets (DuckDB).

Phase 3: Natural language → SQL → safe execution → results + explanation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import duckdb
import pandas as pd

from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

DEFAULT_TABLE = "analytics_data"
_FORBIDDEN_SQL = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|REPLACE|"
    r"ATTACH|DETACH|GRANT|REVOKE|COPY|LOAD|INSTALL|EXPORT|IMPORT|PRAGMA)\b",
    re.IGNORECASE,
)


@dataclass
class ColumnSchema:
    name: str
    dtype: str


@dataclass
class TableSchema:
    table_name: str
    columns: list[ColumnSchema]
    row_count: int


@dataclass
class SqlQueryResult:
    question: str
    sql: str
    result_df: pd.DataFrame | None
    explanation: str
    success: bool
    error: str | None = None


def _dataframe_fingerprint(df: pd.DataFrame) -> str:
    payload = json.dumps([list(df.shape), df.columns.tolist()], sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()


def _sanitize_table_name(source_name: str) -> str:
    stem = Path(source_name).stem if source_name else DEFAULT_TABLE
    name = re.sub(r"[^a-zA-Z0-9_]", "_", stem).strip("_").lower()
    if not name or name[0].isdigit():
        name = f"dataset_{name}" if name else DEFAULT_TABLE
    return name[:48] or DEFAULT_TABLE


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _sql_str(value: str) -> str:
    """Escape a Python string into a single-quoted SQL literal."""
    return "'" + str(value).replace("'", "''") + "'"


# Words to ignore when keyword-matching a question against column values.
_STOPWORDS = frozenset({
    "show", "me", "all", "the", "a", "an", "records", "record", "rows", "row",
    "data", "where", "find", "list", "get", "of", "for", "with", "in", "and",
    "or", "is", "are", "that", "who", "which", "customers", "customer", "people",
    "users", "user", "give", "display", "only", "from", "by", "to",
})


def validate_sql(sql: str) -> tuple[bool, str]:
    """Allow only read-only SELECT (or WITH … SELECT) queries."""
    if not sql or not sql.strip():
        return False, "SQL query is empty."

    cleaned = re.sub(r"--[^\n]*", "", sql)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    if _FORBIDDEN_SQL.search(cleaned):
        return False, "Only read-only SELECT queries are allowed (no DROP/DELETE/UPDATE/etc.)."

    upper = cleaned.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False, "Query must start with SELECT or WITH (read-only)."

    if ";" in cleaned.rstrip().rstrip(";"):
        return False, "Multiple SQL statements are not allowed."

    return True, ""


def _extract_sql(raw: str) -> str:
    text = (raw or "").strip()
    block = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if block:
        text = block.group(1).strip()
    text = text.strip().rstrip(";")
    return text


class SQLEngine:
    """Loads a DataFrame into DuckDB and supports NL → SQL → execution."""

    def __init__(self) -> None:
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._schema: TableSchema | None = None
        self._fingerprint: str | None = None

    def load_dataframe(
        self,
        df: pd.DataFrame,
        source_name: str = "",
        table_name: str | None = None,
    ) -> TableSchema:
        """Register dataframe as a DuckDB table and capture schema metadata."""
        if df is None or df.empty:
            raise ValueError("Cannot load an empty dataframe into the SQL engine.")

        table = table_name or _sanitize_table_name(source_name)
        fingerprint = _dataframe_fingerprint(df)

        if self._conn is not None and self._fingerprint == fingerprint and self._schema:
            if self._schema.table_name == table:
                return self._schema

        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass

        conn = duckdb.connect(database=":memory:")
        conn.register("_df_stage", df)
        conn.execute(f"CREATE OR REPLACE TABLE {_quote_ident(table)} AS SELECT * FROM _df_stage")
        conn.unregister("_df_stage")

        describe = conn.execute(f"DESCRIBE {_quote_ident(table)}").fetchdf()
        columns = [
            ColumnSchema(name=str(row["column_name"]), dtype=str(row["column_type"]))
            for _, row in describe.iterrows()
        ]
        row_count = int(conn.execute(f"SELECT COUNT(*) FROM {_quote_ident(table)}").fetchone()[0])

        self._conn = conn
        self._schema = TableSchema(table_name=table, columns=columns, row_count=row_count)
        self._fingerprint = fingerprint
        logger.info("SQL engine loaded table '%s' (%d rows, %d cols)", table, row_count, len(columns))
        return self._schema

    def ensure_loaded(self, df: pd.DataFrame, source_name: str = "") -> TableSchema:
        """Reload only when the dataframe shape/columns changed."""
        fp = _dataframe_fingerprint(df)
        if self._schema is None or self._fingerprint != fp:
            return self.load_dataframe(df, source_name=source_name)
        return self._schema

    def get_schema(self) -> TableSchema | None:
        return self._schema

    def schema_prompt(self) -> str:
        schema = self._schema
        if not schema:
            return "No table loaded."
        lines = [
            f"Table: {schema.table_name} ({schema.row_count:,} rows)",
            "Columns:",
        ]
        for col in schema.columns:
            lines.append(f"  - {_quote_ident(col.name)} ({col.dtype})")
        return "\n".join(lines)

    def generate_sql(self, question: str) -> str:
        if not self._schema or not self._conn:
            raise RuntimeError("No dataset loaded. Upload and process a file first.")

        system = (
            "You are an expert SQL analyst. Generate exactly one DuckDB-compatible "
            "SELECT query. Use only the table and columns provided. "
            "Double-quote column names that contain spaces or special characters. "
            "Return ONLY the SQL query with no markdown and no explanation."
        )
        user = (
            f"{self.schema_prompt()}\n\n"
            f"User question: {question}\n\n"
            f"SQL query (SELECT only, single statement):"
        )
        raw = call_llm(user, system_prompt=system, max_tokens=512)
        sql = _extract_sql(raw) if raw else ""
        if sql:
            return sql

        # LLM unavailable (no key / rate-limited) → try a deterministic
        # keyword-based fallback so simple filters still work offline.
        fallback = self._heuristic_sql(question)
        if fallback:
            return f"-- AI unavailable - generated locally by keyword match\n{fallback}"

        raise RuntimeError(
            "The AI service is unavailable right now (no valid key or all models rate-limited), "
            "and the question couldn't be matched to your columns automatically. "
            "Try simple filters like \"male, france\" or set a working key in .env / Streamlit secrets."
        )

    def _match_value_to_column(
        self, value: str, text_cols: list[str], exclude: set[str]
    ) -> tuple[str, str] | None:
        """Find the first text column whose values exactly match `value` (case-insensitive)."""
        table = _quote_ident(self._schema.table_name)
        for col in text_cols:
            if col in exclude:
                continue
            try:
                row = self._conn.execute(
                    f"SELECT 1 FROM {table} "
                    f"WHERE CAST({_quote_ident(col)} AS VARCHAR) ILIKE ? LIMIT 1",
                    [value],
                ).fetchone()
            except Exception:
                continue
            if row:
                return col, value
        return None

    def _heuristic_sql(self, question: str) -> str:
        """
        Best-effort NL→SQL without an LLM. Splits the question into candidate
        values and maps each to the column that actually contains it, e.g.
        "male, france" → WHERE gender ILIKE 'male' AND country ILIKE 'france'.
        """
        schema = self._schema
        if not schema or not self._conn:
            return ""

        table = _quote_ident(schema.table_name)
        text_cols = [
            c.name for c in schema.columns
            if any(t in c.dtype.upper() for t in ("CHAR", "TEXT", "STRING"))
        ]
        q = question.strip().lower()
        count_intent = bool(re.search(r"\bhow many\b|\bcount\b|\bnumber of\b|\btotal number\b", q))

        # Split on separators but NOT plain spaces (keeps multi-word values intact).
        phrases = [p.strip(" .?!") for p in re.split(r"[,/&]|\band\b|\bwith\b|\bin\b", q) if p.strip(" .?!")]

        matched: dict[str, str] = {}

        def try_match(val: str) -> None:
            val = val.strip(" .?!")
            if not val or val in _STOPWORDS or len(val) < 2:
                return
            hit = self._match_value_to_column(val, text_cols, set(matched))
            if hit:
                matched[hit[0]] = hit[1]

        for phrase in phrases:
            before = len(matched)
            try_match(phrase)
            if len(matched) == before:           # phrase didn't match → try its words
                for word in phrase.split():
                    try_match(word)

        if not matched:
            return "SELECT COUNT(*) AS count FROM " + table if count_intent else ""

        where = " AND ".join(
            f"{_quote_ident(col)} ILIKE {_sql_str(val)}" for col, val in matched.items()
        )
        if count_intent:
            return f"SELECT COUNT(*) AS count FROM {table} WHERE {where}"
        return f"SELECT * FROM {table} WHERE {where} LIMIT 1000"

    def execute(self, sql: str) -> pd.DataFrame:
        if not self._conn:
            raise RuntimeError("SQL engine is not initialized.")

        ok, msg = validate_sql(sql)
        if not ok:
            raise ValueError(msg)

        try:
            return self._conn.execute(sql).fetchdf()
        except Exception as exc:
            raise RuntimeError(f"SQL execution failed: {exc}") from exc

    def explain_result(
        self,
        question: str,
        sql: str,
        result_df: pd.DataFrame,
    ) -> str:
        preview = result_df.head(8).to_string(index=False) if len(result_df) else "(no rows)"
        system = (
            "You are a data analyst. In 2-4 short sentences, explain what the SQL "
            "result shows in plain English for a business user. Be specific about "
            "numbers when present. Do not repeat the full SQL."
        )
        user = (
            f"Question: {question}\n"
            f"SQL: {sql}\n"
            f"Rows returned: {len(result_df)}\n"
            f"Sample of results:\n{preview}\n\n"
            "Brief explanation:"
        )
        text = call_llm(user, system_prompt=system, max_tokens=300)
        if text:
            return text.strip()
        return self._fallback_explanation(question, result_df)

    @staticmethod
    def _fallback_explanation(question: str, result_df: pd.DataFrame) -> str:
        n = len(result_df)
        if n == 0:
            return "The query ran successfully but returned no rows for this question."
        cols = ", ".join(result_df.columns[:5].tolist())
        return (
            f"The query returned {n:,} row(s) with columns: {cols}. "
            f"Review the table below for details related to: {question}"
        )

    def ask(self, question: str) -> SqlQueryResult:
        question = (question or "").strip()
        if not question:
            return SqlQueryResult(
                question="",
                sql="",
                result_df=None,
                explanation="",
                success=False,
                error="Please enter a question.",
            )

        sql = ""
        try:
            sql = self.generate_sql(question)
            ok, msg = validate_sql(sql)
            if not ok:
                return SqlQueryResult(
                    question=question,
                    sql=sql,
                    result_df=None,
                    explanation="",
                    success=False,
                    error=f"Generated SQL was rejected: {msg}",
                )

            result_df = self.execute(sql)
            explanation = self.explain_result(question, sql, result_df)
            return SqlQueryResult(
                question=question,
                sql=sql,
                result_df=result_df,
                explanation=explanation,
                success=True,
            )
        except Exception as exc:
            logger.warning("SQL ask failed: %s", exc)
            return SqlQueryResult(
                question=question,
                sql=sql,
                result_df=None,
                explanation="",
                success=False,
                error=str(exc),
            )
