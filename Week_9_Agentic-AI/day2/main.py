import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pydantic import ValidationError
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow

from orchestrator.planner import Planner, PlannerResult
from agents.worker_agent import WorkerAgent
from agents.reflection_agent import build_reflection_agent
from agents.validator import build_validator_agent, ValidationResult


WORKER_LIMIT = 3


def build_dag(plan: PlannerResult):
    
    builder = DiGraphBuilder()

    reflection = build_reflection_agent()
    validator = build_validator_agent()

    builder.add_node(reflection)
    builder.add_node(validator)
    builder.add_edge(reflection, validator)

    workers = []
    for i, task in enumerate(plan.tasks):
        worker = WorkerAgent(i + 1, task.task, task.instructions)
        workers.append(worker.agent)
        builder.add_node(worker.agent)
        builder.add_edge(worker.agent, reflection)

    return builder.build(), workers, reflection, validator


def parse_validation_result(raw: str) -> ValidationResult:
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return ValidationResult.model_validate_json(cleaned)
    except ValidationError as e:
        raise ValueError(f"Validator returned invalid JSON:\n{cleaned}\n\nError:\n{e}")


def print_execution_tree(plan: PlannerResult):
    print("\n--- EXECUTION TREE ---\n")
    print("START → Planner")
    for i in range(len(plan.tasks)):
        print(f"   ├── worker_{i+1} → Reflection Agent")
    print("   ├── Reflection Agent → Validator Agent")
    print("   └── FINAL OUTPUT")


async def run_pipeline(query: str):

    # step 1 — planner breaks query into structured tasks
    print("\n--- STEP 1: PLANNER ---\n")
    try:
        planner = Planner(worker_limit=WORKER_LIMIT)
        plan = await planner.run(query)
        for i, task in enumerate(plan.tasks):
            print(f"Task {i+1}: {task.task}")
    except Exception as e:
        print(f"Planner failed: {e}")
        return

    # step 2 — build DAG with workers, reflection, validator
    print("\n--- STEP 2: BUILDING DAG ---\n")
    try:
        graph, workers, reflection, validator = build_dag(plan)
        print(f"DAG built with {len(workers)} worker(s).")
    except Exception as e:
        print(f"DAG build failed: {e}")
        return

    # step 3 — run DAG, workers execute in parallel
    print("\n--- STEP 3: EXECUTING DAG ---\n")
    try:
        flow = GraphFlow(
            participants=[*workers, reflection, validator],
            graph=graph,
        )
        result = await flow.run(task=query)
    except Exception as e:
        print(f"DAG execution failed: {e}")
        return

    # collect reflection and validator outputs from messages
    reflection_output = None
    validator_raw = None
    for msg in result.messages:
        if msg.source == reflection.name:
            reflection_output = msg.content
        elif msg.source == validator.name:
            validator_raw = msg.content

    if not reflection_output or not validator_raw:
        print("Missing output from reflection or validator.")
        return

    # step 4 — parse validation and print final answer
    try:
        validation = parse_validation_result(validator_raw)
    except ValueError as e:
        print(f"Validation parse error: {e}")
        return

    print("\n--- FINAL ANSWER ---\n")
    print(reflection_output)

    if validation.is_valid:
        print("\n[VALID] Answer passed validation.")
    else:
        print("\n[INVALID] Issues found:")
        for issue in validation.issues:
            print(f"  - {issue}")

    print_execution_tree(plan)


if __name__ == "__main__":
    try:
        query = input("Enter your query: ")
        asyncio.run(run_pipeline(query))
    except KeyboardInterrupt:
        print("\nExited.")