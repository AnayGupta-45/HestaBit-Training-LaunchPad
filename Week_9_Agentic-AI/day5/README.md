# Day 5 - Autonomous Multi-Agent System

This folder contains a simple autonomous multi-agent workflow:

1. `Planner` creates an execution plan (JSON steps).
2. `Orchestrator` runs agents level-by-level (parallel when possible).
3. `Validator` checks quality.
4. If validation fails, the plan is regenerated and retried.
5. Logs, outputs, and memory are stored locally.

## Agents

- `Researcher`
- `Analyst`
- `Coder`
- `Critic`
- `Optimizer`
- `Validator`
- `Reporter`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add env variable in `.env`:

```env
LLM_API_KEY=your_key_here
```

## Run

From this folder:

```bash
python3 -u main.py
```

Then enter a task in the interactive shell.

- Type `exit` or `quit` to stop.

## What you will see in terminal

- Generated execution plan steps.
- Live progress logs like:
  - `[STEP] Plan attempt 1/2`
  - `[STEP] Running level 1/3: Researcher, Analyst`
  - `[STEP] Coder: attempt 1/2`
  - `[STEP] Coder: success`

## Output locations

- Run logs: `logs/day5.log`
- Generated artifacts: `Output/`
- Memory index: `memory/faiss.index`
- Long-term memory DB: `memory/long_term.db`

## Notes

- First run may be slower because embedding model files are loaded.
- If API key is missing/invalid, agents will fail at runtime.
