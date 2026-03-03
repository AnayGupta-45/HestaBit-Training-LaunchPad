import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client

def build_research_agent() -> AssistantAgent:
    return AssistantAgent(
        name="research_agent",
        system_message=(
            "You are a STRICT Research Agent.\n"
            "Collect only factual information that directly answers the user's query.\n"
            "Maximum 5 bullet points.\n"
            "Each bullet must be 1-2 lines only.\n"
            "No examples.\n"
            "No applications unless explicitly asked.\n"
            "No history.\n"
            "No opinions.\n"
            "Do NOT summarize.\n"
            "Return bullet points only.\n"
        ),
        model_client=get_model_client(),
    )