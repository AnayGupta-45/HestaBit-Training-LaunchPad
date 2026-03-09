from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client
from tools.code_executor import execute_python_tool


def build_code_agent():
    return AssistantAgent(
        name="CodeAgent",
        model_client=get_model_client(),
        tools=[execute_python_tool],
        system_message="""You are a Python code execution agent.
When given a task, write complete Python code and call execute_python to run it.
Only use Python standard library — no pandas, numpy, or external packages.
Always write complete runnable code, never partial snippets."""
    )