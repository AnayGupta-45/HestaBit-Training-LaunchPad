# DAY 3 — TOOL-CALLING AGENTS

## Orchestrator + Specialized Agents + Real Functions

---

## What We Built

Day 3 moves from "LLM-only reasoning" to "LLM + executable tools".

We built a small multi-agent system with:

- **Orchestrator**: chooses which agent(s) should handle the query
- **CodeAgent**: writes and runs Python through `execute_python`
- **DBAgent**: runs SQL on Titanic SQLite through `run_query`
- **FileAgent**: inspects/reads CSV and writes text files
- **Summarizer**: merges outputs from selected agents into final answer

---

## Actual Runtime Flow (`main.py`)

```text
User Query
   ↓
Orchestrator (returns: dbagent/codeagent/fileagent)
   ↓
Selected agents run one-by-one on the same query
   ↓
Collect raw outputs
   ↓
Summarizer writes final response (<= 8 lines)
```

Implementation detail:

- Orchestrator reply is parsed as lowercase text.
- Agent selection is keyword-based (`codeagent`, `dbagent`, `fileagent`) and deduplicated.
- If no valid agent name appears, execution stops with: `Could not decide an agent.`

---

## Agents and Tools

### 1) CodeAgent

- Tool: `execute_python(code: str) -> str`
- File: `tools/code_executor.py`
- Behavior:
  - Compiles code first (syntax check)
  - Executes with Python standard library only policy (prompt-level rule)
  - Captures printed stdout and returns it
  - Returns explicit `Syntax error: ...` or `Error: ...` when execution fails

### 2) DBAgent

- Tool: `run_query(sql: str) -> str`
- File: `tools/db_tools.py`
- Database: `sample_data/sample.db`
- Source CSV: `sample_data/titanic.csv`
- Behavior:
  - Auto-creates DB/table from CSV on first use (`setup_db()`)
  - Expects SQL `SELECT` usage via system prompt
  - Returns tabular text: header + separator + rows
  - Returns `Query error: ...` on SQL/runtime failures

### 3) FileAgent

- Tools (in `tools/file_tools.py`):
  - `inspect_csv(filename)` → columns + row count
  - `read_csv(filename)` → first 5 rows
  - `write_file(filename, content)` → writes text file
- Behavior:
  - CSV operations resolve files from `sample_data/`
  - Write operation writes to current working directory

---

## Model Setup (`loader.py`)

- Provider: Groq via OpenAI-compatible endpoint
- Model: `llama-3.3-70b-versatile`
- Function calling: enabled (`"function_calling": True`)

This is critical because Day 3 depends on reliable tool-calling behavior.

---

## What Changed vs Day 2

- Day 2 focused on planning/orchestration patterns (DAG + validation).
- Day 3 focuses on **grounded execution**:
  - LLM decides _which tool to call_
  - Python functions do the real work
  - Results come from code/SQL/files, not model memory

---

## Example Query Routing

- "How many passengers survived?" -> `dbagent`
- "Print fibonacci till 50" -> `codeagent`
- "Inspect titanic.csv" -> `fileagent`
- "Find survivors and write summary to output.txt" -> likely multiple agents

---

## Practical Limitations (Current Version)

- Orchestrator decision parsing is simple string matching.
- Agents run sequentially, not parallel.
- `run_query` does not enforce hard SQL safety checks beyond prompt guidance.
- `read_csv` assumes there is at least one row after headers.

These are acceptable for Day 3 learning goals and can be hardened later.

---

## Key Day 3 Lesson

In earlier days, LLMs mostly generated text.
In Day 3, LLMs become **controllers** that invoke deterministic tools.

That shift (reasoning + execution) is the foundation of reliable agentic systems.
