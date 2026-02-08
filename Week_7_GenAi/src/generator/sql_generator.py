import re
from src.generator.llm_client import generate

class SQLGenerator:

    def generate_sql(self, question: str, schema_text: str) -> str:
        prompt = f"""
You are an expert SQLite SQL generator.

Schema:
{schema_text}

User question:
{question}

Rules:
- Generate only ONE SELECT query
- Use valid SQLite syntax
- Do NOT explain
- Do NOT include comments
- Return ONLY SQL ending with semicolon
"""

        output = generate(prompt)

        match = re.search(
            r"(select\s+.*?;)",
            output,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            raise ValueError(f"Failed to extract SQL from LLM output:\n{output}")

        return match.group(1).strip()
