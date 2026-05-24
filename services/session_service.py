"""
session_service.py — Serialize and restore analysis sessions to JSON + parquet.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from config import SESSIONS_DIR

logger = logging.getLogger(__name__)


@dataclass
class SessionMeta:
    """Metadata for a saved session file."""

    session_id: str
    filename: str
    domain_key: str
    saved_at: str
    row_count: int


class SessionService:
    """Persists and loads session snapshots without Streamlit dependencies."""

    def __init__(self):
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        session_id: str,
        meta: dict[str, Any],
        df: pd.DataFrame | None,
    ) -> Path:
        """
        Save session metadata JSON and optional DataFrame parquet.
        Returns path to the JSON manifest.
        """
        folder = SESSIONS_DIR / session_id
        folder.mkdir(parents=True, exist_ok=True)

        if df is not None and not df.empty:
            df.to_csv(folder / "data.csv", index=False)

        manifest_path = folder / "session.json"
        meta["session_id"] = session_id
        meta["saved_at"] = datetime.now().isoformat()
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, default=str)

        logger.info("Session saved: %s", manifest_path)
        return manifest_path

    def load(self, session_id: str) -> tuple[dict[str, Any], pd.DataFrame | None]:
        """
        Load session manifest and DataFrame if present.
        """
        folder = SESSIONS_DIR / session_id
        manifest_path = folder / "session.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        with manifest_path.open(encoding="utf-8") as f:
            meta = json.load(f)

        df = None
        csv_path = folder / "data.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path, low_memory=False)

        return meta, df

    def list_sessions(self) -> list[SessionMeta]:
        """Return metadata for all saved sessions, newest first."""
        sessions: list[SessionMeta] = []
        if not SESSIONS_DIR.exists():
            return sessions

        for folder in SESSIONS_DIR.iterdir():
            if not folder.is_dir():
                continue
            manifest = folder / "session.json"
            if not manifest.exists():
                continue
            try:
                with manifest.open(encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append(SessionMeta(
                    session_id=data.get("session_id", folder.name),
                    filename=data.get("filename", "unknown"),
                    domain_key=data.get("domain_key", "generic"),
                    saved_at=data.get("saved_at", ""),
                    row_count=int(data.get("row_count", 0)),
                ))
            except Exception as e:
                logger.warning("Skipping corrupt session %s: %s", folder.name, e)

        sessions.sort(key=lambda s: s.saved_at, reverse=True)
        return sessions
