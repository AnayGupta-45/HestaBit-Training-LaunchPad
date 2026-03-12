import io
import contextlib
from autogen_core.tools import FunctionTool


def execute_python(code: str) -> str:
    try:
        # Check if code has syntax errors
        compile(code, "<string>", "exec")

        # Buffer to capture print output
        buffer = io.StringIO()

        # Redirect print output to buffer
        with contextlib.redirect_stdout(buffer):
            exec(code)

        output = buffer.getvalue().strip()

        if not output:
            return "Done. No output printed."

        return output

    except SyntaxError as e:
        return f"Syntax error: {e}"

    except Exception as e:
        return f"Error: {e}"


execute_python_tool = FunctionTool(
    execute_python,
    name="execute_python",
    description="Execute Python code and return printed output."
)