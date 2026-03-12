import os
import csv
import sqlite3
from autogen_core.tools import FunctionTool


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sample_data"))
DB_PATH = os.path.join(BASE_DIR, "sample.db")
CSV_PATH = os.path.join(BASE_DIR, "titanic.csv")


def setup_db():
    if os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE titanic (
            PassengerId INTEGER,
            Survived INTEGER,
            Pclass INTEGER,
            Name TEXT,
            Sex TEXT,
            Age REAL,
            SibSp INTEGER,
            Parch INTEGER,
            Ticket TEXT,
            Fare REAL,
            Cabin TEXT,
            Embarked TEXT
        )
    """)

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute(
                "INSERT INTO titanic VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row["PassengerId"],
                    row["Survived"],
                    row["Pclass"],
                    row["Name"],
                    row["Sex"],
                    float(row["Age"]) if row["Age"] else None,
                    row["SibSp"],
                    row["Parch"],
                    row["Ticket"],
                    float(row["Fare"]) if row["Fare"] else None,
                    row["Cabin"],
                    row["Embarked"],
                )
            )

    conn.commit()
    conn.close()


def run_query(sql: str) -> str:
    try:
        if not sql.strip().lower().startswith("select"):
            return "Only SELECT queries are allowed."

        setup_db()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(sql)

        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()

        conn.close()

        lines = [" | ".join(cols)]
        lines.append("-" * 40)

        for row in rows[:50]:
            lines.append(" | ".join(str(v) for v in row))

        if len(rows) > 50:
            lines.append("...output truncated...")

        return "\n".join(lines)

    except Exception as e:
        return f"Query error: {str(e)}"


run_query_tool = FunctionTool(
    run_query,
    name="run_query",
    description="Run a SQL SELECT query on the Titanic SQLite database. Table: titanic."
)