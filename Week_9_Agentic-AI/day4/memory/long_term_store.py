import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "long_term.db")


class LongTermStore:
    """
    Simple SQLite memory store.
    """

    def __init__(self):
        self._setup()

    def _setup(self):

        conn = sqlite3.connect(DB_PATH)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY,
            fact TEXT,
            created_at TEXT
        )
        """)

        conn.commit()
        conn.close()

    def save(self, memory_id: int, fact: str):

        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "INSERT INTO memories VALUES (?, ?, ?)",
            (memory_id, fact, datetime.utcnow().isoformat())
        )

        conn.commit()
        conn.close()

    def get_by_ids(self, ids):

        if not ids:
            return []

        conn = sqlite3.connect(DB_PATH)

        placeholders = ",".join(["?"] * len(ids))

        rows = conn.execute(
            f"SELECT fact FROM memories WHERE id IN ({placeholders})",
            ids
        ).fetchall()

        conn.close()

        return [row[0] for row in rows]

    def delete(self, memory_id):

        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,)
        )

        conn.commit()
        conn.close()