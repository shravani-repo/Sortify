from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Iterator


class Database:
    def __init__(self, path: str | Path = "organizer.db") -> None:
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    undone INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS custom_rules (
                    extension TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

    def record_operations(self, batch_id: str, operations: list[tuple[str, str, str]]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connection() as connection:
            connection.executemany(
                "INSERT INTO operations(batch_id, source_path, destination_path, category, created_at) VALUES (?, ?, ?, ?, ?)",
                [(batch_id, source, destination, category, now) for source, destination, category in operations],
            )

    def list_batches(self, limit: int = 100) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute("""
                SELECT batch_id, MIN(created_at) AS created_at, COUNT(*) AS file_count,
                       MAX(undone) AS undone
                FROM operations GROUP BY batch_id ORDER BY created_at DESC LIMIT ?
            """, (limit,)).fetchall()

    def get_batch(self, batch_id: str) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return connection.execute("SELECT * FROM operations WHERE batch_id = ? ORDER BY id", (batch_id,)).fetchall()

    def mark_batch_undone(self, batch_id: str) -> None:
        with self.connection() as connection:
            connection.execute("UPDATE operations SET undone = 1 WHERE batch_id = ?", (batch_id,))

    def save_rule(self, extension: str, category: str) -> None:
        extension = extension.strip().lower()
        if extension and not extension.startswith("."):
            extension = "." + extension
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO custom_rules(extension, category, created_at) VALUES (?, ?, ?) ON CONFLICT(extension) DO UPDATE SET category=excluded.category, created_at=excluded.created_at",
                (extension, category.strip(), datetime.now().isoformat(timespec="seconds")),
            )

    def delete_rule(self, extension: str) -> None:
        with self.connection() as connection:
            connection.execute("DELETE FROM custom_rules WHERE extension = ?", (extension,))

    def get_rules(self) -> dict[str, str]:
        with self.connection() as connection:
            rows = connection.execute("SELECT extension, category FROM custom_rules ORDER BY extension").fetchall()
        return {row["extension"]: row["category"] for row in rows}
