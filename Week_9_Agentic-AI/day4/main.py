import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.chat_agent import build_chat_agent
from memory.memory_manager import MemoryManager


async def run_pipeline(query: str, memory: MemoryManager, agent):
    context = memory.retrieve_context(query)

    prompt = f"{context}\n\nCURRENT QUERY: {query}"

    result = await agent.run(task=prompt)
    response = result.messages[-1].content

    memory.store_interaction(query, response)

    return response


async def main():
    memory = MemoryManager()
    agent = build_chat_agent()

    print("\nMemory Agent ready. Type 'quit' to exit | 'clear' to reset session\n")

    while True:
        query = input("You: ").strip()

        if not query:
            continue
        if query.lower() == "quit":
            break
        if query.lower() == "clear":
            memory.clear_session()
            continue

        response = await run_pipeline(query, memory, agent)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
