import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tools.file_agent import read_file
from tools.code_executor import execute_python
from tools.db_agent import run_query
from agents.orchestrator import build_orchestrator, build_summarizer


CSV_PATH = os.path.join(os.path.dirname(__file__), "sample_data/titanic.csv")


def run_file_agent() -> str:
    print("\n--- FILE AGENT ---\n")
    content = read_file(CSV_PATH)
    preview = "\n".join(content.split("\n")[:4])
    print(preview)
    print("... (truncated)")
    return content


def run_code_agent() -> str:
    print("\n--- CODE AGENT ---\n")
    code = f"""
import csv
from collections import defaultdict

with open(r"{CSV_PATH}") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total Passengers: {{len(rows)}}")

survived = sum(1 for r in rows if r['Survived'] == '1')
print(f"Overall Survival Rate: {{survived/len(rows)*100:.1f}}%")

by_class = defaultdict(lambda: [0, 0])
for r in rows:
    by_class[r['Pclass']][0] += int(r['Survived'])
    by_class[r['Pclass']][1] += 1
print("\\nSurvival Rate by Class:")
for cls, (s, t) in sorted(by_class.items()):
    print(f"  Class {{cls}}: {{s/t*100:.1f}}% survived ({{s}}/{{t}})")

fares = [float(r['Fare']) for r in rows if r['Fare']]
print(f"\\nAverage Fare: ${{sum(fares)/len(fares):.2f}}")
print(f"Highest Fare: ${{max(fares):.2f}}")

by_gender = defaultdict(lambda: [0, 0])
for r in rows:
    by_gender[r['Sex']][0] += int(r['Survived'])
    by_gender[r['Sex']][1] += 1
print("\\nSurvival Rate by Gender:")
for gender, (s, t) in sorted(by_gender.items()):
    print(f"  {{gender}}: {{s/t*100:.1f}}% survived ({{s}}/{{t}})")
"""
    result = execute_python(code)
    print(result)
    return result


def run_db_agent() -> str:
    print("\n--- DB AGENT ---\n")
    result = run_query("""
        SELECT Pclass, Sex,
               COUNT(*) as total,
               SUM(Survived) as survived,
               ROUND(AVG(Fare), 2) as avg_fare
        FROM titanic
        GROUP BY Pclass, Sex
        ORDER BY Pclass, Sex
    """)
    print(result)
    return result


async def run_pipeline(query: str):

    print("\n--- STEP 1: ORCHESTRATOR (deciding tools) ---\n")
    orchestrator = build_orchestrator()
    plan_result = await orchestrator.run(task=query)
    raw = plan_result.messages[-1].content.strip().lower()

    known_tools = ["file_agent", "code_agent", "db_agent"]
    selected_tools = [t for t in known_tools if t in raw]
    print(f"Tools selected: {selected_tools}")

    if not selected_tools:
        print("No tools selected. Exiting.")
        return

    tool_results = {}

    if "file_agent" in selected_tools:
        tool_results["file_agent"] = run_file_agent()

    if "code_agent" in selected_tools:
        tool_results["code_agent"] = run_code_agent()

    if "db_agent" in selected_tools:
        tool_results["db_agent"] = run_db_agent()

    print("\n--- STEP 3: SUMMARIZER ---\n")
    summarizer = build_summarizer()
    summary_input = f"User Query: {query}\n\n"
    for tool_name, result in tool_results.items():
        summary_input += f"{tool_name} result:\n{result}\n\n"

    summary_result = await summarizer.run(task=summary_input)
    print(summary_result.messages[-1].content)

if __name__ == "__main__":
    query = input("Enter your query: ")
    asyncio.run(run_pipeline(query))