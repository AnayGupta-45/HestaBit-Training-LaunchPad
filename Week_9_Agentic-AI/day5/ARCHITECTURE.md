# DAY5 AI — Autonomous Multi-Agent System Architecture

This project is a production of the Nexus‑AI architecture. .

The system is built around a planner/orchestrator pipeline with specialized agents and an extensible memory layer. Functionality mirrors the original implementation: plan decomposition, parallel agent execution, tool invocation, long‑term/session memory, validation, and retry loops.

## System Overview

```
User Query
    │
    ▼
Planner Agent
    │
Execution Plan (DAG)
    │
    ▼
Orchestrator
    │
Parallel Agent Execution
    │
    ▼
Researcher → Analyst → Coder
        │
        ▼
       Critic
        │
        ▼
      Optimizer
        │
        ▼
      Validator
        │
        ▼
      Reporter
        │
        ▼
     Final Output
```

Agents communicate via a shared context managed by the orchestrator. Tools are exposed through the `tools.py`/`agent_tools.py` helper modules. Memory is handled by the `memory` package and can ingest facts from interactions.

### Configuration

- `config.py` defines filesystem paths and retry limits.
- `requirements.txt` lists the Python packages needed for the stack.

### Running the Shell

```bash
cd Week_9_Agentic-AI/day5
python main.py
```

Type `exit` to quit. Enter a task and the system will generate a plan and execute each agent in order, logging activity to `logs/day5.log` and writing outputs to `Output/`.

---

This document can be expanded with architecture diagrams, performance notes and usage examples as your project evolves.
