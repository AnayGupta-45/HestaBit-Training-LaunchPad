from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from loader import LLMClient
from pydantic import BaseModel, Field
from typing import Literal, List


AgentName = Literal[
    "Researcher",
    "Coder",
    "Analyst",
    "Critic",
    "Optimizer",
    "Validator",
    "Reporter"
]


class PlanStep(BaseModel):
    agent: AgentName
    instruction: str
    depends_on: List[AgentName] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    steps: List[PlanStep]


PLANNER_PROMPT = """
You are an expert Planner Agent for a multi-agent AI system.

Your role is to generate an execution plan for solving the user's request.

You must:
1. Decompose the user request into concrete steps
2. Assign each step to the most appropriate agent
3. Define dependencies between agents to enable parallel execution
4. Return ONLY valid JSON following the ExecutionPlan schema

IMPORTANT RULES

• Do NOT execute tasks  
• Do NOT analyze the problem deeply  
• Only create the plan  

AVAILABLE AGENTS

Researcher:
- Research topics
- Gather knowledge
- Perform competitive analysis

Analyst:
- Analyze datasets
- Perform statistics or business analysis

Coder:
- Generate code
- Design architectures
- Implement technical solutions

Critic:
- Review outputs
- Identify weaknesses
- Provide improvement suggestions

Optimizer:
- Improve performance
- Optimize solutions

Validator:
- Validate final solution against the user's goal
- Ensure correctness and completeness

Reporter:
- Generate final report
- Summarize results

PLANNING RULES

• Each agent may appear AT MOST once  
• Only include agents that are required  
• Use dependencies to enforce execution order  
• Agents with empty dependencies can run in parallel  

DEPENDENCY GUIDELINES

• Research usually happens early  
• Analysis or coding may follow research  
• Critic reviews outputs before optimization  
• Optimizer improves based on critic feedback  
• Validator should depend on most agents  
• Reporter should depend on Validator  

OUTPUT FORMAT

Return ONLY JSON matching this schema:

{
  "steps": [
    {
      "agent": "Researcher",
      "instruction": "Research AI healthcare startups",
      "depends_on": []
    }
  ]
}

Do NOT include markdown.
Do NOT include explanations.
Return ONLY JSON.
"""


planner_client = LLMClient(ExecutionPlan).client


planner = AssistantAgent(
    name="planner",
    description="Creates structured execution plans for the autonomous agent system",
    system_message=PLANNER_PROMPT,
    model_client=planner_client,
)


async def run_planner(query="plan an ai healthcare startup"):
    result = await planner.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_planner())
