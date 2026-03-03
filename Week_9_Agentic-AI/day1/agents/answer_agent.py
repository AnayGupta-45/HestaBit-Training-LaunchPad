import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client

def build_answer_agent() -> AssistantAgent:
    return AssistantAgent(
        name="answer_agent",
        system_message=(
            "You are an Answer Agent.\n"
            "You will receive a user question and a summary.\n"
            "Answer the question directly and concisely.\n"
            "Use ONLY information from the summary.\n"
            "Do not introduce new information.\n"
            "Do not expand beyond the question.\n"
            "Return a clean final answer only.\n"
        ),
        model_client=get_model_client(),
    )