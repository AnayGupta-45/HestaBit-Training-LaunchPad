import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_planner_agent() -> AssistantAgent:
    return AssistantAgent(
        name="planner_agent",
        system_message=(
            "You are a Planner Agent.\n"
            "Your job is to break a user query into exactly 3 subtasks.\n"
            "Each subtask must be a clear, standalone instruction.\n"
            "Return ONLY a numbered list like this:\n"
            "1. <subtask one>\n"
            "2. <subtask two>\n"
            "3. <subtask three>\n"
            "No extra text. No explanation. Just the 3 numbered subtasks.\n"
        ),
        model_client=get_model_client(),
    )


def parse_subtasks(planner_output: str) -> list[str]:
    """Extract numbered subtasks from planner output."""
    lines = planner_output.strip().split("\n")
    subtasks = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            task = line.split(".", 1)[1].strip()
            if task:
                subtasks.append(task)
    return subtasks