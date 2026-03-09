import sys
import  os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_chat_agent() -> AssistantAgent:
    return AssistantAgent(
        name="chat_agent",
        system_message=(
            "You are a helpful assistant with memory.\n"
            "You will receive:\n"
            "  - Relevant facts from long term memory\n"
            "  - Recent conversation history\n"
            "  - Current user query\n"
            "\n"
            "RULES:\n"
            "- If the answer is in the facts or conversation, use it directly.\n"
            "- Never say you don't have information if it exists in context.\n"
            "- Answer concisely and directly.\n"
            "- Do not talk about privacy or limitations.\n"
        ),
        model_client=get_model_client(),
    )