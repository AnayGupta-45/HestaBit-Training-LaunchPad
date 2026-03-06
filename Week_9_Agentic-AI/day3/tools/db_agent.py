import sqlite3
import csv
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../sample_data/sample.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "../sample_data/titanic.csv")


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS titanic")
    cursor.execute("""
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

    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO titanic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row["PassengerId"],
                    row["Survived"],
                    row["Pclass"],
                    row["Name"],
                    row["Sex"],
                    row["Age"] if row["Age"] else None,
                    row["SibSp"],
                    row["Parch"],
                    row["Ticket"],
                    row["Fare"] if row["Fare"] else None,
                    row["Cabin"],
                    row["Embarked"],
                ),
            )

    conn.commit()
    conn.close()


def run_query(sql: str) -> str:
    try:
        setup_database()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not rows:
            return "Query returned no results."

        result = ", ".join(columns) + "\n"
        result += "\n".join([", ".join(str(v) for v in row) for row in rows])
        return result

    except Exception as e:
        return f"DB Error: {str(e)}"