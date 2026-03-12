from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


def build_reflection_agent() -> AssistantAgent:
    return AssistantAgent(
        name="reflection_agent",
        model_client=get_model_client(),
        system_message=(
            "You are a Reflection Agent.\n"
            "You receive outputs from multiple worker agents.\n"
            "Merge them into one clean unified response.\n"
            "Remove duplicates and fix contradictions.\n"
            "Do not add new facts. Maximum 8 lines.\n"
        ),
    )