import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client

def build_summarizer_agent() -> AssistantAgent:
    return AssistantAgent(
        name="summarizer_agent",
        system_message=(
            "You are a compression engine.\n"
            "Reduce the input to EXACTLY 3 bullet points.\n"
            "Each bullet must be under 20 words.\n"
            "Remove redundancy.\n"
            "Remove examples.\n"
            "Keep only the core definition and mechanism.\n"
            "Return bullet points only.\n"
        ),
        model_client=get_model_client(),
    )