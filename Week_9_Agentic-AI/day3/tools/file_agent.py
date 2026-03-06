import os

def read_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        return f"Error: File not found at {filepath}"
    with open(filepath, "r") as f:
        return f.read()

def write_file(filepath: str, content: str) -> str:
    with open(filepath, "w") as f:
        f.write(content)
    return f"File written to {filepath}"