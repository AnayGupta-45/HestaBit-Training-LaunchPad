import asyncio
import json
import os
import shutil
from collections import defaultdict, deque
from autogen_agentchat.messages import TextMessage

from config import MAX_RETRIES_PER_AGENT, MAX_PLAN_RETRIES, LOG_FILE_PATH, OUTPUT_DIR
from tools import create_log_entry
from memory.memory_manager import MemoryManager

from agents.planner import planner, ExecutionPlan
from agents.researcher import researcher
from agents.coder import coder
from agents.analyst import analyst
from agents.critic import critic
from agents.optimizer import optimizer
from agents.validator import validator
from agents.reporter import reporter


AGENT_REGISTRY = {
    "Researcher": researcher,
    "Coder": coder,
    "Analyst": analyst,
    "Critic": critic,
    "Optimizer": optimizer,
    "Validator": validator,
    "Reporter": reporter,
}

memory_manager = MemoryManager()


def print_step(message: str):
    print(f"[STEP] {message}", flush=True)


def compute_levels(execution_plan):
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for step in execution_plan.steps:
        in_degree.setdefault(step.agent, 0)
        in_degree[step.agent] = len(step.depends_on)

        for dep in step.depends_on:
            graph[dep].append(step.agent)
            in_degree.setdefault(dep, 0)

    queue = deque([n for n in in_degree if in_degree[n] == 0])
    levels = []

    while queue:
        level = list(queue)
        levels.append(level)
        next_queue = deque()

        for node in level:
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)

        queue = next_queue

    return levels


def compress_context(context, limit=1200):
    formatted = []
    for agent, output in context.items():
        truncated = str(output)[:limit]
        formatted.append(f"{agent} OUTPUT:\n{truncated}\n")
    return "\n".join(formatted)


async def run_agent_with_retry(agent_name, instruction, global_context, user_query):

    agent = AGENT_REGISTRY[agent_name]
    last_error = None

    for attempt in range(MAX_RETRIES_PER_AGENT):
        print_step(f"{agent_name}: attempt {attempt + 1}/{MAX_RETRIES_PER_AGENT}")

        retry_info = f"\nPREVIOUS FAILURE:\n{last_error}\nFix the issue.\n" if last_error else ""
        context_text = compress_context(global_context)

        prompt = f"""
SYSTEM GOAL:
{user_query}

AGENT ROLE:
You are the {agent_name} agent in an autonomous AI system.

YOUR TASK:
{instruction}

CONTEXT FROM PREVIOUS AGENTS:
{context_text}

{retry_info}

Provide output for the next agent.
"""

        try:

            result = await agent.run(
                task=TextMessage(content=prompt, source="orchestrator")
            )

            output = result.messages[-1].content

            memory_manager.store_interaction(agent_name, output)

            create_log_entry(
                str(LOG_FILE_PATH),
                agent_name.lower(),
                "success",
                {"output": output},
            )

            print_step(f"{agent_name}: success")

            return {"agent": agent_name, "success": True, "output": output}

        except Exception as e:

            last_error = str(e)

            create_log_entry(
                str(LOG_FILE_PATH),
                agent_name.lower(),
                "retry",
                {"attempt": attempt + 1, "error": last_error},
            )

            short_error = last_error[:140].replace("\n", " ")
            print_step(f"{agent_name}: failed attempt {attempt + 1} ({short_error})")

    return {"agent": agent_name, "success": False, "error": last_error}


async def run_level(level_agents, step_map, context, user_query):

    tasks = [
        run_agent_with_retry(agent, step_map[agent], context, user_query)
        for agent in level_agents
    ]

    return await asyncio.gather(*tasks)


async def execute_plan(execution_plan, user_query):

    levels = compute_levels(execution_plan)
    print_step(f"Computed {len(levels)} execution level(s)")

    step_map = {step.agent: step.instruction for step in execution_plan.steps}

    global_context = {}

    for idx, level_agents in enumerate(levels, start=1):
        print_step(f"Running level {idx}/{len(levels)}: {', '.join(level_agents)}")

        level_results = await run_level(level_agents, step_map, global_context, user_query)

        for res in level_results:

            if not res["success"]:
                raise Exception(f"EXEC_FAIL::{res['agent']}::{res['error']}")

            global_context[res["agent"]] = res["output"]

            if res["agent"] == "Validator":

                if "FAIL" in res["output"].upper() or "REJECTED" in res["output"].upper():
                    raise Exception(f"VALIDATION_FAIL::{res['output']}")

    return global_context


async def run_autonomous_loop(initial_plan, user_query):

    current_plan = initial_plan
    validator_feedback = None

    for attempt in range(MAX_PLAN_RETRIES):
        print_step(f"Plan attempt {attempt + 1}/{MAX_PLAN_RETRIES}")
        try:

            results = await execute_plan(current_plan, user_query)
            return results

        except Exception as e:

            err = str(e)

            if err.startswith("VALIDATION_FAIL::"):
                print_step("Validation failed. Replanning with validator feedback.")

                validator_feedback = err.replace("VALIDATION_FAIL::", "")

                memory_manager.store_interaction("validator_feedback", validator_feedback)

                clear_output_dir()

                replan_prompt = f"""
SYSTEM GOAL:
{user_query}

VALIDATOR FEEDBACK:
{validator_feedback}

Generate a NEW improved execution plan fixing these issues.
Return JSON only.
"""

                result = await planner.run(
                    task=TextMessage(content=replan_prompt, source="orchestrator")
                )

                raw = result.messages[-1].content

                try:
                    plan_data = json.loads(raw)
                except Exception:
                    import re
                    match = re.search(r"\{.*\}", raw, re.DOTALL)
                    if not match:
                        raise
                    plan_data = json.loads(match.group())

                create_log_entry(
                    str(LOG_FILE_PATH),
                    "planner",
                    "updated_plan_generated",
                    {"steps": plan_data},
                )

                current_plan = ExecutionPlan(**plan_data)
                continue

            print_step(f"Execution aborted: {err}")
            return {"system_error": err}

    return {
        "warning": "Maximum retries reached. Returning best available result.",
        "validator_feedback": validator_feedback
    }


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
        except Exception:
            pass
