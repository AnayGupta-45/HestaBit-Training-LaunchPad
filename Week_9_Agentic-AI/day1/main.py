import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.research_agent import build_research_agent
from agents.summarizer_agent import build_summarizer_agent
from agents.answer_agent import build_answer_agent


async def run_pipeline(query: str):
    research_agent = build_research_agent()
    summarizer_agent = build_summarizer_agent()
    answer_agent = build_answer_agent()

    # STEP 1 — RESEARCH
    print("\nSTEP 1: RESEARCH\n")
    research_result = await research_agent.run(task=query)
    research_text = research_result.messages[-1].content
    print(research_text)

    # STEP 2 — SUMMARIZE
    print("\nSTEP 2: SUMMARIZE\n")
    summary_result = await summarizer_agent.run(task=research_text)
    summary_text = summary_result.messages[-1].content
    print(summary_text)

    # STEP 3 — FINAL ANSWER
    print("\nSTEP 3: FINAL ANSWER\n")

    final_prompt = f"""
User Question:
{query}

Summary:
{summary_text}

Answer the user's question using ONLY the summary.
"""

    final_result = await answer_agent.run(task=final_prompt)
    final_text = final_result.messages[-1].content
    print(final_text)


if __name__ == "__main__":
    query = input("What would you like to research? : ")
    asyncio.run(run_pipeline(query))