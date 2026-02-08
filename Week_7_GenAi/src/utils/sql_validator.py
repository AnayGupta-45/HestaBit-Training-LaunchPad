import re

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]

def validate_sql(sql: str) -> str:
    sql = sql.strip()

    # Must start with SELECT
    if not sql.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    # Block dangerous keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql, re.IGNORECASE):
            raise ValueError(f"Forbidden keyword detected: {keyword}")

    # Only allow one query
    if sql.count(";") > 1:
        raise ValueError("Multiple SQL statements are not allowed.")

    return sql
