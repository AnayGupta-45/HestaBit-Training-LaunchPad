# DAY 3 — TOOL CALLING AGENTS

## Orchestrator → Tools → Summarizer

---

## What We Built

In Day 1 and Day 2, agents were only doing LLM reasoning — thinking and returning text.
Day 3 agents actually do real things — read files from disk, execute Python code,
and run SQL queries on a real database. The LLM decides what to do, real Python functions do it.

---

## The Core Idea

Day 1 & 2 → LLM imagines the answer

Day 3 → LLM directs, Python executes, results are real

---

## Execution Flow

```
User Query
    ↓
Orchestrator        → reads query, decides which tools are needed
    ↓
File Agent          → reads actual file from disk        (if needed)
Code Agent          → executes real Python code          (if needed)
DB Agent            → runs SQL on real SQLite database   (if needed)
    ↓
Summarizer          → reads all tool results, gives final answer
```

---

## What Each Tool Does

**File Agent** (`tools/file_agent.py`)
A plain Python function that reads any file from disk using `open()`.
No LLM involved. Just reads and returns raw content.
Also supports writing files back to disk.

**Code Agent** (`tools/code_executor.py`)
Takes a Python code string and runs it using `exec()`.
Captures the stdout output and returns it.
This means real computation happens — not LLM guessing numbers.

**DB Agent** (`tools/db_agent.py`)
Loads titanic.csv into a real SQLite database file.
Runs actual SQL queries on it and returns formatted results.
Every run recreates the table fresh from the CSV.

---

## What Each Agent Does

**Orchestrator** (`agents/orchestrator.py`)
Runs first. Reads the user query and returns which tools are needed.
We safely parse its response by scanning for known tool names —
because small local models like phi3 sometimes return extra text along with the answer.

```python
known_tools = ["file_agent", "code_agent", "db_agent"]
selected_tools = [t for t in known_tools if t in raw]
```

**Summarizer** (`agents/orchestrator.py`)
Runs last. Receives all tool results together and produces
a clean, concise final answer. This is the only LLM step that touches the results.

---

## File Structure

```
day3/
├── main.py                     # entry point, runs full pipeline
├── loader.py                   # ollama + phi3 client
├── TOOL-CHAIN.md
├── agents/
│   └── orchestrator.py         # orchestrator + summarizer agents
├── tools/
│   ├── file_agent.py           # reads and writes files
│   ├── code_executor.py        # executes python code strings
│   └── db_agent.py             # loads csv into sqlite, runs sql
└── sample_data/
    ├── titanic.csv              # 100 rows of titanic passenger data
    └── sample.db                # sqlite database generated at runtime
```

---

## Key Concepts Practiced

**Real tool execution** — tools are Python functions, not LLM calls.
Results are factual, not generated.

**Defensive parsing** — small models don't always follow strict formatting.
We scan the response for known keywords instead of trusting exact output.

**Separation of concerns** — orchestrator only plans, tools only execute,
summarizer only synthesizes. Each piece has one job.

---

## What Changed vs Day 2

Day 2 was still fully LLM-based — workers reasoned and returned text answers.
Day 3 introduces real execution. The LLM is now a director, not the worker.

This is the foundation of real agentic systems — LLMs decide, code executes.
