import io
import contextlib
from autogen_core.tools import FunctionTool


def execute_python(code: str) -> str:
    """Execute Python code and return the output."""

    # Validate syntax before running
    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        return f"Syntax error: {e}"

    # Run and capture output
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        result = output.getvalue()
        return result if result.strip() else "Done. No output printed."
    except Exception as e:
        return f"Error: {e}"


# Wrap as AutoGen tool
execute_python_tool = FunctionTool(
    execute_python,
    name="execute_python",
    description="Execute Python code and return its output. Only use standard library, no pandas or numpy."
)