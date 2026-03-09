from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_orchestrator():
    return AssistantAgent(
        name="Orchestrator",
        model_client=get_model_client(),
        system_message="""You are an orchestrator. Decide which agents to use for the user query.

Available agents:
- dbagent   → any question about passengers, survival, age, gender, class (uses SQL)
- codeagent → run Python code, math, calculations, fibonacci, loops
- fileagent → inspect, read, or write files (only when user mentions a file)

Reply with agent names only, comma-separated, lowercase. No explanation.

Examples:
"how many passengers survived" → dbagent
"print fibonacci numbers"      → codeagent
"inspect titanic.csv"          → fileagent
"calculate sum of 1 to 100"    → codeagent"""
    )


def build_summarizer():
    return AssistantAgent(
        name="Summarizer",
        model_client=get_model_client(),
        system_message="""You are a summarizer.
Given the results from agents, write a short clear answer for the user.
Use only the information given. Keep it under 8 lines."""
    )