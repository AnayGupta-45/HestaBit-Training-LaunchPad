import sqlite3
import pandas as pd
from pathlib import Path

CSV_PATH = "src/data/raw/product.csv"
DB_PATH = "src/data/sales.db"

def create_database():
    Path("src/data").mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS products")

    cursor.execute("""
        CREATE TABLE products (
            idx INTEGER,
            name TEXT,
            description TEXT,
            brand TEXT,
            category TEXT,
            price REAL,
            currency TEXT,
            stock INTEGER,
            ean TEXT,
            color TEXT,
            size TEXT,
            availability TEXT,
            internal_id TEXT
        )
    """)

    df.columns = [
        "idx", "name", "description", "brand", "category",
        "price", "currency", "stock", "ean",
        "color", "size", "availability", "internal_id"
    ]

    df.to_sql("products", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print("Database created successfully at:", DB_PATH)

if __name__ == "__main__":
    create_database()
