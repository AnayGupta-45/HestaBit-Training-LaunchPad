import io
import contextlib

def execute_python(code: str) -> str:
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        result = output.getvalue()
        return result if result else "Code ran but produced no output."
    except Exception as e:
        return f"Execution Error: {str(e)}"