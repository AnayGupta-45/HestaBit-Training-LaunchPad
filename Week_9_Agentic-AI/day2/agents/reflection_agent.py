import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_reflection_agent() -> AssistantAgent:
    return AssistantAgent(
        name="reflection_agent",
        system_message=(
            "You are a Reflection Agent.\n"
            "You will receive combined outputs from multiple worker agents.\n"
            "Your job is to:\n"
            "1. Remove any duplicate information\n"
            "2. Fix any contradictions\n"
            "3. Improve clarity and flow\n"
            "Return a single improved, unified response.\n"
            "Maximum 8 lines.\n"
            "No meta-commentary like 'I improved this by...'.\n"
            "Just return the improved content.\n"
        ),
        model_client=get_model_client(),
    )