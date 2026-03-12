import io
import contextlib
from autogen_core.tools import FunctionTool


SAFE_BUILTINS = {
    "print": print,
    "range": range,
    "len": len,
    "sum": sum,
    "min": min,
    "max": max,
    "sorted": sorted,
    "enumerate": enumerate,
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
}


def execute_python(code: str) -> str:
    try:
        compile(code, "<string>", "exec")

        buffer = io.StringIO()

        exec_globals = {"__builtins__": SAFE_BUILTINS}
        exec_locals = {}

        with contextlib.redirect_stdout(buffer):
            exec(code, exec_globals, exec_locals)

        output = buffer.getvalue().strip()

        if not output:
            return "Done. No output printed."

        if len(output) > 2000:
            return output[:2000] + "\n...output truncated..."

        return output

    except SyntaxError as e:
        return f"Syntax error: {e}"

    except Exception as e:
        return f"Error: {e}"


execute_python_tool = FunctionTool(
    execute_python,
    name="execute_python",
    description="Execute Python code and return printed output. Only Python standard library allowed."
)