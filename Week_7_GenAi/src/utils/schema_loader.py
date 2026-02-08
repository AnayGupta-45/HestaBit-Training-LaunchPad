import sqlite3

DB_PATH = "src/data/sales.db"

def load_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        schema[table_name] = [
            {
                "column_name": col[1],
                "data_type": col[2]
            }
            for col in columns
        ]

    conn.close()
    return schema


def schema_as_text():
    schema = load_schema()
    text = ""

    for table, columns in schema.items():
        text += f"Table: {table}\n"
        for col in columns:
            text += f"  - {col['column_name']} ({col['data_type']})\n"
        text += "\n"

    return text
