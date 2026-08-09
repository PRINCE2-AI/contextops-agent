from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

from app.schemas import MemoryItem, MemoryType


class MemoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    importance REAL NOT NULL,
                    private INTEGER NOT NULL,
                    pinned INTEGER NOT NULL,
                    tags TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add(
        self,
        content: str,
        type: MemoryType = MemoryType.NOTE,
        provenance: str = "manual",
        importance: float = 0.5,
        private: bool = False,
        pinned: bool = False,
        tags: tuple[str, ...] = (),
    ) -> MemoryItem:
        item = MemoryItem(
            id=uuid.uuid4().hex[:12],
            type=type,
            content=content.strip(),
            provenance=provenance,
            importance=max(0.0, min(1.0, importance)),
            private=private,
            pinned=pinned,
            tags=tags,
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO memories (id, type, content, provenance, importance, private, pinned, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (item.id, item.type.value, item.content, item.provenance, item.importance, int(item.private), int(item.pinned), json.dumps(item.tags)),
            )
        return item

    def list(self) -> tuple[MemoryItem, ...]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM memories ORDER BY pinned DESC, importance DESC, created_at ASC").fetchall()
        return tuple(self._row_to_item(row) for row in rows)

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> MemoryItem:
        return MemoryItem(
            id=row["id"],
            type=MemoryType(row["type"]),
            content=row["content"],
            provenance=row["provenance"],
            importance=float(row["importance"]),
            private=bool(row["private"]),
            pinned=bool(row["pinned"]),
            tags=tuple(json.loads(row["tags"])),
        )

