import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "long_term.db")


class LongTermStore:
    """
    Permanent memory using SQLite.
    Stores extracted facts on disk — persists across runs.
    """

    def __init__(self):
        self._setup_db()

    def _setup_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                fact TEXT,
                category TEXT,
                importance REAL,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self, memory_id: int, fact: str, category: str, importance: float):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO memories (id, fact, category, importance, created_at) VALUES (?, ?, ?, ?, ?)",
            (memory_id, fact, category, importance, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

    def get_by_ids(self, ids: list) -> list:
        if not ids:
            return []
        conn = sqlite3.connect(DB_PATH)
        placeholders = ",".join(["?"] * len(ids))
        rows = conn.execute(
            f"SELECT fact FROM memories WHERE id IN ({placeholders})", ids
        ).fetchall()
        conn.close()
        return [row[0] for row in rows]

    def delete(self, memory_id: int):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT id, fact, category, importance FROM memories"
        ).fetchall()
        conn.close()
        return rows