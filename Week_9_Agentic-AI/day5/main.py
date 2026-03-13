import os
import warnings

import asyncio
import json
import shutil
import re
from autogen_agentchat.messages import TextMessage

from agents.planner import planner, ExecutionPlan
from agents.orchestrator import run_autonomous_loop, memory_manager
from config import OUTPUT_DIR, LOG_DIR, LOG_FILE_PATH
from tools import create_log_entry

# suppress noisy warnings from external libraries
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


def initialize_workspace(clear_output=True):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    if clear_output:
        clear_output_dir()


def clear_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        return

    for f in os.listdir(OUTPUT_DIR):
        p = os.path.join(OUTPUT_DIR, f)

        try:
            if os.path.isfile(p):
                os.unlink(p)
            else:
                shutil.rmtree(p)
        except Exception as e:
            print(f"Warning: Could not delete {p}: {e}")


async def generate_execution_plan(query):

    memory_context = memory_manager.retrieve_context(query)

    enhanced_query = f"""
USER REQUEST:
{query}

MEMORY CONTEXT:
{memory_context[:800]}
"""

    result = await planner.run(
        task=TextMessage(content=enhanced_query, source="user")
    )

    raw = result.messages[-1].content

    try:
        plan_data = json.loads(raw) ## This converts into a python dictionary ... 

    except json.JSONDecodeError: ## sometimes LLM doesnt return simple JSON text it mixes it with other extra text ... 
        match = re.search(r"\{.*\}", raw, re.DOTALL) ## this return the exact text .. 

        if match:
            plan_data = json.loads(match.group()) ## this returns the exact JSON format 
        else:
            raise ValueError(f"Planner returned non-JSON response:\n{raw}")

    execution_plan = ExecutionPlan(**plan_data)

    print("\nExecution Plan:")
    for i, step in enumerate(execution_plan.steps, start=1):
        deps = ", ".join(step.depends_on) if step.depends_on else "None"
        print(f"  {i}. {step.agent} (depends_on: {deps})")
        print(f"     - {step.instruction}")
    print()

    create_log_entry(
        str(LOG_FILE_PATH),
        "planner",
        "plan_generated",
        {"steps": plan_data},
    )

    return execution_plan


async def run_day5(query, clear_output=True):

    # clear workspace if requested
    initialize_workspace(clear_output)

    execution_plan = await generate_execution_plan(query)

    # execution plan info omitted for brevity
    results = await run_autonomous_loop(execution_plan, query)

    return {
        "success": True,
        "query": query,
        "results": results,
    }


async def main():

    print("\nDAY5 Interactive Shell")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:

        query = input("Enter your task: ").strip()

        if not query:
            print("Please enter a query.\n")
            continue

        if query.lower() in ["exit", "quit"]:
            print("Shutting down Day5 AI.")
            break

        # always clear previous output automatically
        try:
            result = await run_day5(query, clear_output=True)

            print("\n" + "=" * 60)
            print("EXECUTION COMPLETE")
            print("=" * 60)

            results = result.get("results", {})

            for agent_name, agent_result in results.items():

                if isinstance(agent_result, dict):
                    status = "✔" if agent_result.get("success") else "✘"
                    output = str(agent_result.get("output", ""))[:120]
                else:
                    status = "✔"
                    output = str(agent_result)[:120]

                print(f"  {status} {agent_name}: {output}")

            print("=" * 60 + "\n")

            create_log_entry(
                str(LOG_FILE_PATH),
                "system",
                "run_complete",
                {
                    "query": query,
                    "agents_run": list(results.keys()),
                },
            )

        except Exception as e:

            print(f"\n[FATAL ERROR] {e}")

            create_log_entry(
                str(LOG_FILE_PATH),
                "system",
                "fatal_error",
                {"error": str(e)},
            )


if __name__ == "__main__":
    asyncio.run(main())
