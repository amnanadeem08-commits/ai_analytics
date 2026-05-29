"""
rag_engine.py — Lightweight AI Insight Engine (light RAG).

Pipeline:
    DataFrame → knowledge-base chunks (schema, stats, samples)
             → local embeddings (offline, sklearn hashing)
             → vector store (FAISS, with numpy fallback)
             → retrieve(question) → LLM → structured insight

Kept intentionally simple: no external embedding API, no multi-agent logic.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from utils.llm_client import call_llm

logger = logging.getLogger(__name__)

_EMBED_DIM = 1024


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class KnowledgeChunk:
    chunk_id: str
    kind: str          # "overview" | "column" | "sample" | "stats"
    title: str
    text: str


@dataclass
class RAGInsightResult:
    question: str
    summary: str
    key_findings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    context_titles: list[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Local embeddings (offline, deterministic — no downloads, no torch)
# ─────────────────────────────────────────────────────────────────────────────
def _embed_texts(texts: list[str]) -> np.ndarray:
    """Hash-based bag-of-words embeddings, L2-normalized. Stable & offline."""
    from sklearn.feature_extraction.text import HashingVectorizer

    vectorizer = HashingVectorizer(
        n_features=_EMBED_DIM,
        alternate_sign=False,
        norm=None,
        stop_words="english",
    )
    matrix = vectorizer.transform(texts).toarray().astype("float32")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


# ─────────────────────────────────────────────────────────────────────────────
# Vector store: FAISS when available, numpy cosine fallback otherwise
# ─────────────────────────────────────────────────────────────────────────────
class _VectorStore:
    def __init__(self) -> None:
        self._matrix: np.ndarray | None = None
        self._index = None
        self._backend = "numpy"
        try:
            import faiss  # noqa: F401
            self._backend = "faiss"
        except Exception:
            self._backend = "numpy"

    @property
    def backend(self) -> str:
        return self._backend

    def build(self, vectors: np.ndarray) -> None:
        self._matrix = vectors
        if self._backend == "faiss":
            import faiss
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            self._index = index

    def search(self, query_vec: np.ndarray, k: int) -> list[int]:
        if self._matrix is None or len(self._matrix) == 0:
            return []
        k = min(k, len(self._matrix))
        if self._backend == "faiss" and self._index is not None:
            _, idx = self._index.search(query_vec, k)
            return [int(i) for i in idx[0] if i >= 0]
        scores = (self._matrix @ query_vec[0])
        return np.argsort(scores)[::-1][:k].tolist()


# ─────────────────────────────────────────────────────────────────────────────
# RAG Insight Engine
# ─────────────────────────────────────────────────────────────────────────────
class RAGInsightEngine:
    """Builds a dataset knowledge base and answers insight questions via RAG."""

    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []
        self._store = _VectorStore()
        self._fingerprint: str | None = None
        self._dataset_name: str = "the dataset"

    # ── Build / cache ────────────────────────────────────────────────────────
    @staticmethod
    def _fingerprint_df(df: pd.DataFrame) -> str:
        payload = json.dumps([list(df.shape), df.columns.tolist()], sort_keys=True)
        return hashlib.md5(payload.encode()).hexdigest()

    def ensure_built(self, df: pd.DataFrame, source_name: str = "") -> None:
        fp = self._fingerprint_df(df)
        if self._fingerprint == fp and self._chunks:
            return
        self.build_knowledge_base(df, source_name)

    def build_knowledge_base(self, df: pd.DataFrame, source_name: str = "") -> list[KnowledgeChunk]:
        if df is None or df.empty:
            raise ValueError("Cannot build knowledge base from an empty dataset.")

        self._dataset_name = source_name or "the dataset"
        self._chunks = self._build_chunks(df)
        vectors = _embed_texts([c.text for c in self._chunks])
        self._store = _VectorStore()
        self._store.build(vectors)
        self._fingerprint = self._fingerprint_df(df)
        logger.info(
            "RAG knowledge base built: %d chunks (%s backend)",
            len(self._chunks), self._store.backend,
        )
        return self._chunks

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    @property
    def backend(self) -> str:
        return self._store.backend

    # ── Knowledge base construction ──────────────────────────────────────────
    def _build_chunks(self, df: pd.DataFrame) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        n_rows = len(df)

        overview = (
            f"Dataset overview for {self._dataset_name}. "
            f"{n_rows:,} rows and {len(df.columns)} columns. "
            f"Columns: {', '.join(map(str, df.columns))}. "
            f"Numeric columns: {', '.join(numeric_cols) or 'none'}."
        )
        chunks.append(KnowledgeChunk("overview", "overview", "Dataset overview", overview))

        for col in df.columns:
            chunks.append(self._column_chunk(df, col))

        if numeric_cols:
            try:
                desc = df[numeric_cols].describe().T.round(3)
                stats_lines = [
                    f"{idx}: mean={row['mean']}, min={row['min']}, max={row['max']}, std={row.get('std', float('nan'))}"
                    for idx, row in desc.iterrows()
                ]
                stats_text = "Statistical summary of numeric columns (mean, min, max, std). " + " | ".join(stats_lines)
                chunks.append(KnowledgeChunk("stats", "stats", "Numeric statistics", stats_text))
            except Exception as exc:
                logger.debug("stats chunk skipped: %s", exc)

            if len(numeric_cols) >= 2:
                try:
                    corr = df[numeric_cols].corr(numeric_only=True)
                    pairs = []
                    cols = corr.columns.tolist()
                    for i in range(len(cols)):
                        for j in range(i + 1, len(cols)):
                            val = corr.iloc[i, j]
                            if pd.notna(val) and abs(val) >= 0.5:
                                pairs.append(f"{cols[i]}~{cols[j]}={val:.2f}")
                    if pairs:
                        chunks.append(KnowledgeChunk(
                            "corr", "stats", "Correlations",
                            "Notable correlations between numeric columns (trend relationships): "
                            + ", ".join(pairs),
                        ))
                except Exception as exc:
                    logger.debug("corr chunk skipped: %s", exc)

        sample = df.head(5)
        try:
            sample_text = "Sample rows from the dataset: " + sample.to_csv(index=False).replace("\n", " | ")
            chunks.append(KnowledgeChunk("sample", "sample", "Sample rows", sample_text[:1500]))
        except Exception as exc:
            logger.debug("sample chunk skipped: %s", exc)

        return chunks

    def _column_chunk(self, df: pd.DataFrame, col: str) -> KnowledgeChunk:
        series = df[col]
        unique_count = int(series.nunique(dropna=True))
        missing_pct = round(float(series.isna().mean() * 100), 1)
        parts = [
            f"Column '{col}'.",
            f"Data type: {series.dtype}.",
            f"Unique values: {unique_count}.",
            f"Missing: {missing_pct}%.",
        ]
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if len(valid):
                parts.append(
                    f"Numeric measure with mean={valid.mean():.3f}, "
                    f"min={valid.min():.3f}, max={valid.max():.3f}, median={valid.median():.3f}."
                )
        else:
            top = series.dropna().astype(str).value_counts().head(5)
            if not top.empty:
                top_text = ", ".join(f"{k} ({v})" for k, v in top.items())
                parts.append(f"Categorical dimension. Top values: {top_text}.")
        return KnowledgeChunk(f"col::{col}", "column", f"Column: {col}", " ".join(parts))

    # ── Retrieval ────────────────────────────────────────────────────────────
    def retrieve(self, question: str, k: int = 6) -> list[KnowledgeChunk]:
        if not self._chunks:
            return []
        query_vec = _embed_texts([question])
        idxs = self._store.search(query_vec, k)
        return [self._chunks[i] for i in idxs]

    def _always_include(self) -> list[KnowledgeChunk]:
        """Overview + stats chunks are always provided as grounding context."""
        return [c for c in self._chunks if c.kind in ("overview", "stats")]

    # ── Ask ──────────────────────────────────────────────────────────────────
    def ask(self, question: str, k: int = 6) -> RAGInsightResult:
        question = (question or "").strip()
        if not question:
            return RAGInsightResult(question="", summary="", success=False, error="Please enter a question.")
        if not self._chunks:
            return RAGInsightResult(
                question=question, summary="", success=False,
                error="Knowledge base is empty. Upload and process a dataset first.",
            )

        retrieved = self.retrieve(question, k=k)
        # Merge always-included grounding with retrieved, de-duplicated, order-stable.
        seen: set[str] = set()
        context_chunks: list[KnowledgeChunk] = []
        for c in self._always_include() + retrieved:
            if c.chunk_id not in seen:
                seen.add(c.chunk_id)
                context_chunks.append(c)

        context_text = "\n".join(f"[{c.title}] {c.text}" for c in context_chunks)
        result = self._llm_insight(question, context_text)
        result.context_titles = [c.title for c in context_chunks]
        return result

    def _llm_insight(self, question: str, context_text: str) -> RAGInsightResult:
        system = (
            "You are a senior data analyst. Use ONLY the provided dataset context to "
            "answer. Be specific and reference real column names and numbers. "
            "Respond strictly as minified JSON with keys: "
            '"summary" (string, 2-3 sentences), '
            '"key_findings" (array of 3-6 short strings), '
            '"suggestions" (array of 3-5 short strings of KPIs or analysis directions). '
            "Do not include any text outside the JSON."
        )
        user = (
            f"Dataset context:\n{context_text}\n\n"
            f"Question: {question}\n\n"
            "Return the JSON now."
        )
        raw = call_llm(user, system_prompt=system, max_tokens=900)
        if not raw:
            return RAGInsightResult(
                question=question, summary="", success=False,
                error="The AI service is unavailable right now (no valid key or all models rate-limited). "
                      "Please retry in a moment.",
            )

        parsed = _parse_json_block(raw)
        if parsed is None:
            # Graceful fallback: return raw text as the summary.
            return RAGInsightResult(
                question=question,
                summary=raw.strip(),
                key_findings=[],
                suggestions=[],
                success=True,
            )

        return RAGInsightResult(
            question=question,
            summary=str(parsed.get("summary", "")).strip(),
            key_findings=[str(x).strip() for x in parsed.get("key_findings", []) if str(x).strip()],
            suggestions=[str(x).strip() for x in parsed.get("suggestions", []) if str(x).strip()],
            success=True,
        )


def _parse_json_block(raw: str) -> dict | None:
    text = raw.strip()
    block = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if block:
        text = block.group(1).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except Exception:
        return None
