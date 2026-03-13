from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from pydantic import BaseModel
from typing import List, Optional
from agent_tools import get_coder_tools
from autogen_agentchat.messages import TextMessage
from config import OUTPUT_DIR


class CodeOutput(BaseModel):
    language: str
    code: str
    dependencies: List[str]
    setup_instructions: str
    test_cases: Optional[str] = None


CODER_PROMPT = f"""
You are the DAY5 Coder Agent operating inside an autonomous multi-agent system.

PRIMARY RESPONSIBILITY
Build software systems by writing files using tools.

IMPORTANT EXECUTION RULES

You MUST create files using the write_file tool.
Do NOT print code in chat unless absolutely necessary.

WORKFLOW

PHASE 1 - DESIGN
- Understand the system requested
- Decide the project architecture
- Define folder structure and modules

PHASE 2 - IMPLEMENTATION
For each required file:
1. Generate the full file content
2. Immediately write the file using the write_file tool

Files must be written one at a time.

PHASE 3 - PROJECT STRUCTURE
Always include when appropriate:
- dependency file (requirements.txt / package.json)
- entry point (main.py / app.js)
- configuration files
- README.md with setup and run instructions

ENGINEERING STANDARDS

- Production-grade architecture
- Modular code
- Error handling
- Logging
- No hardcoded secrets
- Clean naming conventions
- Scalable design

PATH RULES

All files must be written inside:

{OUTPUT_DIR}/

Example paths:
{OUTPUT_DIR}/main.py
{OUTPUT_DIR}/src/service.py
{OUTPUT_DIR}/config/settings.py

FINAL OUTPUT

After all files are written provide:
1. Short system summary
2. Final file tree

Do not output large code blocks in chat.
"""


coder_client = LLMClient().client


coder = AssistantAgent(
    name="coder",
    description="Builds software systems and writes project files",
    system_message=CODER_PROMPT,
    model_client=coder_client,
    tools=get_coder_tools(),
    reflect_on_tool_use=False,
    max_tool_iterations=20,
)


async def run_coder(query="generate code to add two integers"):

    result = await coder.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_coder())
