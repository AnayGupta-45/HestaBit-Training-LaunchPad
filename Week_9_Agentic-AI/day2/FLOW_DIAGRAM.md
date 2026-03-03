# DAY 2 — MULTI-AGENT ORCHESTRATION

## Planner → Workers → Reflection → Validator

---

## What We Built

A 4-agent hierarchical pipeline. Unlike Day 1 where agents ran one after another,
today the workers run in parallel and we added a reflection and validation step.

---

## Execution Flow

```
User Query
    ↓
Planner Agent          → breaks the query into 3 subtasks
    ↓
Worker 1 | Worker 2 | Worker 3    → all 3 run at the same time
    ↓
Reflection Agent       → merges all worker outputs into one clean answer
    ↓
Validator Agent        → checks if the answer actually addresses the query
    ↓
Final Answer
```

---

## What Each Agent Does

**Planner** (`orchestrator/planner.py`)
Looks at the user query and splits it into 3 clear subtasks.
A helper function `parse_subtasks()` extracts them into a list.

**Worker** (`agents/worker_agent.py`)
One worker is created per subtask. All 3 run in parallel using `asyncio.gather()`.
Each worker only knows its own subtask — they don't talk to each other.

**Reflection Agent** (`agents/reflection_agent.py`)
Receives all 3 worker outputs together.
Merges them, removes duplicates, and returns one clean unified response.

**Validator Agent** (`agents/validator.py`)
Takes the reflection output and the original query.
Checks if the answer is complete and correct.
Responds with `[VALID]` or `[INVALID]` and explains why.

---

## File Structure

```
day2/
├── main.py
├── loader.py
├── FLOW-DIAGRAM.md
├── orchestrator/
│   └── planner.py
└── agents/
    ├── worker_agent.py
    ├── reflection_agent.py
    └── validator.py
```

---

## Key Concepts Practiced

**Parallel execution** — workers don't wait for each other, they all run at once.
This is done using `asyncio.gather()` which fires all coroutines simultaneously.

**Reflection step** — instead of directly validating raw worker output,
we first merge and clean it. This improves the quality of the final answer.

**Validation gate** — the validator is the last checkpoint.
Nothing goes to the user without passing through it.

**Dynamic agent creation** — workers are not hardcoded.
They are created at runtime based on however many subtasks the planner returns.

---

## What Changed vs Day 1

Day 1 was strictly linear — research → summarize → answer, one by one.

Day 2 introduces parallelism, a merging step, and a validation layer on top.
The system is now more robust and closer to how real agent pipelines work.
