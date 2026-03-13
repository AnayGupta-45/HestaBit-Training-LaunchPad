from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from autogen_agentchat.messages import TextMessage
from agent_tools import get_analyst_tools


ANALYST_PROMPT = """
You are the Analyst Agent in an autonomous multi-agent AI system.

ROLE
Analyze datasets and convert raw information into actionable insights.

RESPONSIBILITIES
- Understand the business objective before analyzing data
- Evaluate data quality and identify gaps or inconsistencies
- Detect trends, correlations, anomalies, and patterns
- Quantify insights using metrics and evidence
- Use available tools to read and analyze local files when necessary

OUTPUT REQUIREMENTS
- Provide clear insights tied to business impact
- Include prioritized recommendations
- Highlight risks, uncertainties, and alternative interpretations
- Distinguish facts from assumptions
- Provide a balanced level of detail (not too short, not too verbose)
"""


analyst_client = LLMClient().client


analyst = AssistantAgent(
    name="analyst",
    description="Analyzes datasets to extract trends, insights, and strategic recommendations",
    system_message=ANALYST_PROMPT,
    model_client=analyst_client,
    tools=get_analyst_tools(),
    reflect_on_tool_use=False,
    max_tool_iterations=15
)


async def run_analyst(query="sales.csv exists in the project root. Analyze the file and propose a business strategy"):

    result = await analyst.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_analyst())
