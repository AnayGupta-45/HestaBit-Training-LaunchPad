import asyncio
from agents.orchestrator import build_orchestrator, build_summarizer
from agents.code_agent import build_code_agent
from agents.db_agent import build_db_agent
from agents.file_agent import build_file_agent

# All available agents
AGENTS = {
    "codeagent": build_code_agent(),
    "dbagent":   build_db_agent(),
    "fileagent": build_file_agent(),
}


async def run(query: str):

    # Step 1 — Orchestrator picks which agents to use
    print("\n--- STEP 1: ORCHESTRATOR ---")
    orchestrator = build_orchestrator()
    response = await orchestrator.run(task=query)
    decision = response.messages[-1].content.strip().lower()
    print(f"Decision: {decision}")

    # Parse agent names (deduplicated)
    selected = []
    for name in AGENTS:
        if name in decision and name not in selected:
            selected.append(name)

    if not selected:
        print("Could not decide an agent. Try rephrasing.")
        return

    # Step 2 — Run each selected agent
    print("\n--- STEP 2: RUNNING AGENTS ---")
    results = []
    for name in selected:
        print(f"\n[{name}]")
        try:
            res = await AGENTS[name].run(task=query)
            output = res.messages[-1].content
            print(output)
            results.append(f"{name}: {output}")
        except Exception as e:
            print(f"Error: {e}")
            results.append(f"{name}: Error — {str(e)[:150]}")

    # Step 3 — Summarizer gives final answer
    print("\n--- STEP 3: SUMMARY ---")
    summarizer = build_summarizer()
    summary_prompt = f"User asked: {query}\n\nResults:\n" + "\n\n".join(results)
    summary = await summarizer.run(task=summary_prompt)
    print(summary.messages[-1].content)


if __name__ == "__main__":
    query = input("\nEnter your query: ")
    asyncio.run(run(query))