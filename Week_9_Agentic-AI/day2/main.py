import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from orchestrator.planner import build_planner_agent, parse_subtasks
from agents.worker_agent import build_worker_agent
from agents.reflection_agent import build_reflection_agent
from agents.validator import build_validator_agent


async def run_worker(worker_id: int, subtask: str) -> tuple[int, str]:
    """Run a single worker on a subtask, return (id, result)."""
    worker = build_worker_agent(worker_id)
    result = await worker.run(task=subtask)
    return worker_id, result.messages[-1].content


async def run_pipeline(query: str):

    # STEP 1 — PLAN
    print("\n--- STEP 1: PLANNER ---\n")
    planner = build_planner_agent()
    plan_result = await planner.run(task=query)
    plan_text = plan_result.messages[-1].content
    print(plan_text)

    subtasks = parse_subtasks(plan_text)
    if not subtasks:
        print("Planner returned no subtasks. Exiting.")
        return

    # STEP 2 — PARALLEL WORKERS
    print(f"\n--- STEP 2: WORKERS (running {len(subtasks)} in parallel) ---\n")
    worker_coroutines = [
        run_worker(i + 1, subtask) for i, subtask in enumerate(subtasks)
    ]
    worker_results = await asyncio.gather(*worker_coroutines)

    combined_output = ""
    for worker_id, result in sorted(worker_results):
        print(f"[Worker {worker_id}]\n{result}\n")
        combined_output += f"Worker {worker_id} Result:\n{result}\n\n"

    # STEP 3 — REFLECTION
    print("\n--- STEP 3: REFLECTION ---\n")
    reflection_agent = build_reflection_agent()
    reflection_input = f"Original Query: {query}\n\nWorker Outputs:\n{combined_output}"
    reflection_result = await reflection_agent.run(task=reflection_input)
    reflection_text = reflection_result.messages[-1].content
    print(reflection_text)

    # STEP 4 — VALIDATION
    print("\n--- STEP 4: VALIDATOR ---\n")
    validator_agent = build_validator_agent()
    validation_input = (
        f"Original Query: {query}\n\nResponse to Validate:\n{reflection_text}"
    )
    validation_result = await validator_agent.run(task=validation_input)
    validation_text = validation_result.messages[-1].content
    print(validation_text)

    # EXECUTION TREE
    print("\n--- EXECUTION TREE ---\n")
    print(f"Query: {query}")
    print("  └── Planner")
    for i, subtask in enumerate(subtasks):
        print(f"       ├── Worker {i + 1}: {subtask[:60]}...")
    print("       └── Reflection Agent")
    print("            └── Validator Agent")
    print("                 └── Final Answer")


if __name__ == "__main__":
    query = input("Enter your query: ")
    asyncio.run(run_pipeline(query))
