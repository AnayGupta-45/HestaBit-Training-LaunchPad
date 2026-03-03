import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_worker_agent(worker_id: int) -> AssistantAgent:
    return AssistantAgent(
        name=f"worker_agent_{worker_id}",
        system_message=(
            "You are a Worker Agent.\n"
            "You will receive a single subtask.\n"
            "Execute it and return a clear, concise result.\n"
            "Maximum 5 lines.\n"
            "No preamble. No meta-commentary.\n"
            "Just the result of the subtask.\n"
        ),
        model_client=get_model_client(),
    )