from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client
from tools.code_executor import execute_python_tool


def build_code_agent():
    return AssistantAgent(
        name="codeagent",
        model_client=get_model_client(),
        tools=[execute_python_tool],
        system_message="""
You are a Python execution agent.

You solve problems by writing Python code and executing it with the execute_python tool.

Rules:
- Only solve math or algorithm problems
- Do NOT create or modify files
- Do NOT use open(), file writing, or OS commands
- Always execute code using execute_python
"""
    )