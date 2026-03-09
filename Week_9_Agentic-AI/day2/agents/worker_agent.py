import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


class WorkerAgent:
    # worker_id gives each worker a unique name like worker_1, worker_2
    def __init__(self, worker_id: int, task: str, instructions: str):
        self.agent = AssistantAgent(
            name=f"worker_{worker_id}",
            model_client=get_model_client(),
            system_message=(
                "You are a Worker Agent.\n"
                f"Your task: {task}\n"
                f"Instructions: {instructions}\n"
                "Return a clear concise result. Maximum 5 lines.\n"
                "No preamble. No meta-commentary. Just the result.\n"
            ),
        )