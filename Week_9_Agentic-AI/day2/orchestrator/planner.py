import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import List
from pydantic import BaseModel, ValidationError
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from loader import get_model_client


class Task(BaseModel):
    task: str
    instructions: str


class PlannerResult(BaseModel):
    tasks: List[Task]


class Planner:
    def __init__(self, worker_limit: int = 4):
        self.worker_limit = worker_limit
        self.agent = AssistantAgent(
            name="planner_agent",
            model_client=get_model_client(),
            system_message=(
                "You are a Planner Agent.\n"
                "Break the user request into independent parallel tasks.\n"
                f"Maximum tasks allowed: {worker_limit}. Minimum 1.\n"
                "Combine related tasks if needed to stay within the limit.\n\n"
                "Return ONLY valid JSON in this format:\n"
                '{"tasks": [{"task": "", "instructions": ""}]}\n'
                "No explanations. No markdown. No extra text.\n"
            ),
        )

    async def run(self, query: str) -> PlannerResult:
        response = await self.agent.run(
            task=TextMessage(content=query, source="user")
        )
        raw = response.messages[-1].content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            result = PlannerResult.model_validate_json(raw)
            result.tasks = result.tasks[:self.worker_limit]
            return result
        except ValidationError as e:
            raise ValueError(f"Planner returned invalid JSON:\n{raw}\n\nError:\n{e}")