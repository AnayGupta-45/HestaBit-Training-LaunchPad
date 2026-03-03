import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_validator_agent() -> AssistantAgent:
    return AssistantAgent(
        name="validator_agent",
        system_message=(
            "You are a Validator Agent.\n"
            "You will receive a response and the original user query.\n"
            "Check for:\n"
            "1. Does it answer the original query?\n"
            "2. Are there any factual errors or contradictions?\n"
            "3. Is anything critical missing?\n"
            "If valid: start your response with [VALID] then give the final answer.\n"
            "If invalid: start with [INVALID] then explain what is wrong.\n"
            "Be strict but fair.\n"
        ),
        model_client=get_model_client(),
    )