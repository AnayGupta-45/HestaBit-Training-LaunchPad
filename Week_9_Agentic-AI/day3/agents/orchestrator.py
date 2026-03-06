import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_orchestrator() -> AssistantAgent:
    return AssistantAgent(
        name="orchestrator",
        system_message=(
            "You are an Orchestrator Agent.\n"
            "Decide which tools are needed to answer the user query.\n"
            "Available tools:\n"
            "  file_agent  — read a file or dataset from disk\n"
            "  code_agent  — analyze data or do computation\n"
            "  db_agent    — run SQL queries on structured data\n"
            "\n"
            "STRICT RULES:\n"
            "- Reply with tool names ONLY\n"
            "- Comma separated, nothing else\n"
            "- No explanation, no reasoning, no extra words\n"
            "- Only use tools that are clearly needed\n"
            "\n"
            "Examples:\n"
            "db_agent\n"
            "file_agent, code_agent\n"
            "file_agent, code_agent, db_agent\n"
        ),
        model_client=get_model_client(),
    )


def build_summarizer() -> AssistantAgent:
    return AssistantAgent(
        name="summarizer",
        system_message=(
            "You are a Summarizer Agent.\n"
            "You will receive results from one or more tools.\n"
            "Summarize the key insights clearly and concisely.\n"
            "Use only what is provided. Do not add new information.\n"
            "Keep it under 10 lines.\n"
        ),
        model_client=get_model_client(),
    )