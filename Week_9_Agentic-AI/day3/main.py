import asyncio

from agents.orchestrator import build_orchestrator, build_summarizer
from agents.code_agent import build_code_agent
from agents.db_agent import build_db_agent
from agents.file_agent import build_file_agent


def build_agent_registry():
    return {
        "codeagent": build_code_agent(),
        "dbagent": build_db_agent(),
        "fileagent": build_file_agent(),
    }


async def run_agent(name, agent, query):
    try:
        print(f"\nRunning {name}...")

        res = await agent.run(task=query)
        output = res.messages[-1].content

        print(output)
        return f"{name}: {output}"

    except Exception as e:
        err = f"{name} failed: {str(e)}"
        print(err)
        return err


async def run(query: str):

    agents = build_agent_registry()

    print("\n--- STEP 1: ORCHESTRATOR ---")

    orchestrator = build_orchestrator()
    response = await orchestrator.run(task=query)

    decision = response.messages[-1].content.strip().lower()
    print("Decision:", decision)

    selected_agents = []

    decision_clean = decision.replace(" ", "").strip()

    if decision_clean in agents:
        selected_agents = [decision_clean]

    elif "," in decision_clean:
        for name in decision_clean.split(","):
            if name in agents:
                selected_agents.append(name)

    if not selected_agents:
        print("No agent selected. Try rephrasing.")
        return

    print("\n--- STEP 2: RUNNING AGENTS ---")

    tasks = [
        run_agent(name, agents[name], query)
        for name in selected_agents
    ]

    results = await asyncio.gather(*tasks)

    print("\n--- STEP 3: SUMMARY ---")

    summarizer = build_summarizer()

    summary_prompt = f"""
User Query:
{query}

Agent Results:
{chr(10).join(results)}

Provide the final answer for the user.
"""

    summary = await summarizer.run(task=summary_prompt)

    print("\nFINAL ANSWER\n")
    print(summary.messages[-1].content)


if __name__ == "__main__":

    query = input("\nEnter your query: ")

    asyncio.run(run(query))