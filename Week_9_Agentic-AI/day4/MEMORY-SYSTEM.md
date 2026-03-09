# DAY 4 — MEMORY SYSTEMS

## Session Memory + Long Term Storage + Vector Search

---

## What We Built

Until Day 3, agents had no memory — every run was a fresh start.
Day 4 gives the agent actual memory that persists across sessions.

---

## How It Works

```
User Query
    ↓
Retrieve relevant facts from FAISS + recent session history
    ↓
Inject context into agent prompt
    ↓
Agent responds with full context
    ↓
LLM extracts important facts from the conversation
    ↓
Facts saved to SQLite + FAISS
```

---

## Three Types of Memory

**Session Memory** (`memory/session_memory.py`)
Tracks conversation within the current run only.
Simple list — gone when app closes.

**Long Term Store** (`memory/long_term_store.py`)
Saves extracted facts permanently to SQLite on disk.
Survives across runs. Facts have category and importance score.

**Vector Store** (`memory/vector_store.py`)
Stores facts as vectors using FAISS.
Used for similarity search — finds relevant past facts for any query.
Index is saved to disk so it reloads on next run.

---

## What Makes This Different

We don't save raw conversations.
After each turn, an LLM call extracts only important facts:

```
USER: I am learning about AI agents
→ fact saved: "User is learning about AI agents" (importance: 0.9)

USER: hello how are you
→ nothing saved (small talk, not important)
```

Duplicate facts are automatically skipped.
Contradicting facts replace old ones.

---

## File Structure

```
day4/
├── main.py
├── loader.py
├── MEMORY-SYSTEM.md
├── agents/
│   └── chat_agent.py
└── memory/
    ├── session_memory.py
    ├── long_term_store.py
    ├── vector_store.py
    ├── memory_manager.py
    ├── long_term.db           ← created automatically
    └── faiss.index            ← created automatically
```

---

## Key Concepts Practiced

**RAG (Retrieval Augmented Generation)** — relevant facts are retrieved
and injected into the prompt before the LLM responds.

**Fact extraction** — instead of storing everything, we use an LLM
to extract only meaningful long term facts from each conversation.

**Persistent vector index** — FAISS index is saved to disk so similarity
search works across sessions without reloading from scratch.
