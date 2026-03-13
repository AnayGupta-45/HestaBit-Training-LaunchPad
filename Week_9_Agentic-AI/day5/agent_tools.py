from autogen_core.tools import FunctionTool
from typing import List
import tools


def get_coder_tools() -> List[FunctionTool]:
    return [
        FunctionTool(
            tools.write_file,
            description="Write code or configuration files. REQUIRED ARGS: filepath (string path), content (string file data)."
        ),
        FunctionTool(
            tools.read_file,
            description="Read existing code files"
        ),
        FunctionTool(
            tools.write_json,
            description="Write configuration or data files in JSON"
        ),
        FunctionTool(
            tools.list_directory,
            description="List files in project directory"
        ),
    ]


def get_analyst_tools() -> List[FunctionTool]:
    return [
        FunctionTool(
            tools.read_csv,
            description="Read CSV data for analysis"
        ),
        FunctionTool(
            tools.analyze_csv_columns,
            description="Get column statistics and insights"
        ),
        FunctionTool(
            tools.read_json,
            description="Read JSON data for analysis"
        ),
        FunctionTool(
            tools.list_directory,
            description="List files in provided directory"
        ),
        FunctionTool(
            tools.read_file,
            description="Read files"
        ),
    ]


def get_optimizer_tools() -> List[FunctionTool]:
    return [
        FunctionTool(
            tools.read_file,
            description="Read files to analyze for optimization"
        ),
        FunctionTool(
            tools.write_file,
            description="Write optimized versions of files. REQUIRED ARGS: filepath (string path), content (string file data)."
        ),
        FunctionTool(
            tools.read_json,
            description="Read configuration for optimization"
        ),
        FunctionTool(
            tools.list_directory,
            description="List files in provided directory"
        ),
    ]


def get_reporter_tools() -> List[FunctionTool]:
    return [
        FunctionTool(
            tools.write_file,
            description="Write reports and documentation. REQUIRED ARGS: filepath (string path), content (string file data)."
        ),
        FunctionTool(
            tools.read_file,
            description="Read source materials for reporting"
        ),
        FunctionTool(
            tools.read_logs,
            description="Review agent activity logs"
        ),
    ]


AGENT_TOOL_REGISTRY = {
    "coder": get_coder_tools,
    "analyst": get_analyst_tools,
    "optimizer": get_optimizer_tools,
    "reporter": get_reporter_tools,
}
