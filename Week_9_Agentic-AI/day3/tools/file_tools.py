import os
import csv
from autogen_core.tools import FunctionTool

# All data files live here
DATA_DIR = os.path.join(os.path.dirname(__file__), "../sample_data")


def inspect_csv(filename: str) -> str:
    """Inspect a CSV file — returns column names and row count."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return f"File not found: {filename}"

    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        row_count = sum(1 for _ in reader)

    return f"Columns: {', '.join(headers)}\nRow count: {row_count}"


def read_csv(filename: str) -> str:
    """Read the first 5 rows of a CSV file."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return f"File not found: {filename}"

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for i, row in enumerate(reader) if i < 5]

    lines = [" | ".join(rows[0].keys())]
    for row in rows:
        lines.append(" | ".join(row.values()))
    return "\n".join(lines)


def write_file(filename: str, content: str) -> str:
    """Write content to a text file in the current directory."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written to {filename} successfully."


# Wrap as AutoGen tools
inspect_csv_tool = FunctionTool(
    inspect_csv,
    name="inspect_csv",
    description="Inspect a CSV file. Pass just the filename e.g. 'titanic.csv'. Returns columns and row count."
)

read_csv_tool = FunctionTool(
    read_csv,
    name="read_csv",
    description="Read first 5 rows of a CSV file. Pass just the filename e.g. 'titanic.csv'."
)

write_file_tool = FunctionTool(
    write_file,
    name="write_file",
    description="Write text content to a file. Pass filename and content."
)

FILE_TOOLS = [inspect_csv_tool, read_csv_tool, write_file_tool]