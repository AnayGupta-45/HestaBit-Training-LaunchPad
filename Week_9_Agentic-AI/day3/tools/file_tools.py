import os
import csv
from autogen_core.tools import FunctionTool


DATA_DIR = os.path.join(os.path.dirname(__file__), "../sample_data")
DATA_DIR = os.path.abspath(DATA_DIR)


def _get_path(filename: str):
    return os.path.join(DATA_DIR, filename)


def inspect_csv(filename: str) -> str:
    path = _get_path(filename)

    if not os.path.exists(path):
        return f"File not found: {filename}"

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)

            if not headers:
                return "CSV file is empty."

            row_count = sum(1 for _ in reader)

        return f"Columns: {', '.join(headers)}\nRow count: {row_count}"

    except Exception as e:
        return f"Error inspecting CSV: {str(e)}"


def read_csv(filename: str) -> str:
    path = _get_path(filename)

    if not os.path.exists(path):
        return f"File not found: {filename}"

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            rows = []
            for i, row in enumerate(reader):
                if i >= 5:
                    break
                rows.append(row)

        if not rows:
            return "CSV has no data rows."

        lines = [" | ".join(rows[0].keys())]

        for row in rows:
            lines.append(" | ".join(row.values()))

        return "\n".join(lines)

    except Exception as e:
        return f"Error reading CSV: {str(e)}"


def write_file(filename: str, content: str) -> str:
    path = _get_path(filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Written to {filename} successfully."

    except Exception as e:
        return f"Error writing file: {str(e)}"


inspect_csv_tool = FunctionTool(
    inspect_csv,
    name="inspect_csv",
    description="Inspect a CSV file. Pass filename like 'titanic.csv'. Returns column names and row count."
)

read_csv_tool = FunctionTool(
    read_csv,
    name="read_csv",
    description="Read first 5 rows of a CSV file. Pass filename like 'titanic.csv'."
)

write_file_tool = FunctionTool(
    write_file,
    name="write_file",
    description="Write text content to a file. Pass filename and content."
)

FILE_TOOLS = [
    inspect_csv_tool,
    read_csv_tool,
    write_file_tool
]