from typing import List
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from loader import get_model_client


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str]


def build_validator_agent() -> AssistantAgent:
    return AssistantAgent(
        name="validator_agent",
        model_client=get_model_client(),
        system_message=(
            "You are a Validator Agent.\n"
            "Check if the response correctly answers the original query.\n"
            "Return ONLY valid JSON. No markdown. No extra text.\n"
            'Format: {"is_valid": true, "issues": []}\n'
            'Or: {"is_valid": false, "issues": ["issue 1", "issue 2"]}\n'
        ),
    )