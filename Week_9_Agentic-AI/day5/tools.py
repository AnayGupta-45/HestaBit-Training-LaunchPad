import os
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime


def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    try:
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def append_file(filepath: str, content: str) -> str:
    try:
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully appended to {filepath}"
    except Exception as e:
        return f"Error appending file: {str(e)}"


def list_directory(dirpath: str) -> List[str]:
    try:
        return os.listdir(dirpath)
    except Exception as e:
        return [f"Error listing directory: {str(e)}"]


def read_csv(filepath: str) -> Dict[str, Any]:
    try:
        limit = 10

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            rows = []
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(dict(row))

        return {
            "headers": reader.fieldnames,
            "rows": rows,
            "row_count": len(rows),
            "note": f"Showing first {limit} rows only",
        }

    except Exception as e:
        return {"error": str(e)}


def write_csv(filepath: str, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    try:
        if not data:
            return "Error: No data to write"

        if headers is None:
            headers = list(data[0].keys())

        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        return f"Successfully wrote {len(data)} rows to {filepath}"

    except Exception as e:
        return f"Error writing CSV: {str(e)}"


def analyze_csv_columns(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            headers = reader.fieldnames

        if not headers:
            return {"error": "No headers found in CSV"}

        analysis = {}

        for header in headers:

            values = [row.get(header, "") for row in rows]
            non_empty = [v for v in values if str(v).strip()]

            numeric_values = []
            for v in non_empty:
                try:
                    numeric_values.append(float(v))
                except Exception:
                    pass

            col_data = {
                "total_values": len(values),
                "non_empty_values": len(non_empty),
                "empty_values": len(values) - len(non_empty),
                "unique_values": len(set(non_empty)),
                "sample_values": non_empty[:5],
            }

            if numeric_values:
                col_data["numeric_stats"] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": round(sum(numeric_values) / len(numeric_values), 4),
                }

            analysis[header] = col_data

        analysis["_meta"] = {
            "total_rows": len(rows),
            "total_columns": len(headers),
        }

        return analysis

    except Exception as e:
        return {"error": str(e)}


def read_json(filepath: str) -> Dict[str, Any]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def write_json(filepath: str, data: Any, indent: int = 2) -> str:
    try:
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)

        return f"Successfully wrote JSON to {filepath}"

    except Exception as e:
        return f"Error writing JSON: {str(e)}"


def create_log_entry(log_file: str, agent_name: str, action: str, details: Dict[str, Any]) -> str:
    try:
        parent = os.path.dirname(log_file)
        if parent:
            os.makedirs(parent, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "agent": agent_name,
            "action": action,
            "details": details,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_file

    except Exception as e:
        return f"Error creating log: {str(e)}"


def read_logs(log_dir: str) -> List[Dict[str, Any]]:
    logs = []
    limit = 8

    try:
        if not os.path.exists(log_dir):
            return logs

        for filename in os.listdir(log_dir):

            if not filename.endswith(".log"):
                continue

            filepath = os.path.join(log_dir, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        logs.append(json.loads(line))
                    except Exception:
                        continue

        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return logs[:limit]

    except Exception as e:
        return [{"error": str(e)}]
