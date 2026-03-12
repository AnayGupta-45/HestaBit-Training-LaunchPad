from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_orchestrator():
    return AssistantAgent(
        name="orchestrator",
        model_client=get_model_client(),
        system_message="""
You are a routing system.

Your job is to select which agent should handle the user query.

Available agents:

dbagent   -> SQL queries about Titanic passengers
codeagent -> Python math, algorithms, calculations
fileagent -> read, inspect, or write files (.csv, .txt, .py)

Rules:
- Output ONLY agent names
- Output must be exactly one line
- Allowed outputs:
  dbagent
  codeagent
  fileagent
  codeagent,fileagent

Do NOT explain.
Do NOT generate code.

Examples:

how many passengers survived
dbagent

calculate fibonacci numbers
codeagent

inspect titanic.csv
fileagent

generate a python file named prime.py
fileagent
"""
    )


def build_summarizer():
    return AssistantAgent(
        name="summarizer",
        model_client=get_model_client(),
        system_message="""
You summarize agent outputs into a final answer.

Rules:
- Use only agent outputs
- Be concise
- Maximum 8 lines
"""
    )