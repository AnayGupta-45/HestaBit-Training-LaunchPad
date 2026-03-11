# Deployment Notes (Day 5 Capstone)

## Objective

Deliver one integrated assistant that supports:

- Text RAG
- Image RAG
- SQL QA
- Conversational memory
- Answer refinement
- Hallucination/confidence evaluation
- Interactive UI

---

## Implemented Files

- `src/deployment/app.py`
- `src/pipelines/main_pipeline.py`
- `src/evaluation/rag_eval.py`
- `src/memory/memory_store.py`
- `CHAT-LOGS.json`

---

## System Components

### 1. Orchestrator (`EnterpriseAssistant`)

Defined in `src/pipelines/main_pipeline.py`.

It wires together:

- `ContextBuilder` for text retrieval
- `ImageSearch` for multimodal retrieval
- `SQLPipeline` for SQL QA
- `MemoryStore` for conversation history
- `RAGEvaluator` for faithfulness/confidence scoring

### 2. Memory

`src/memory/memory_store.py`:

- Stores chat messages in `CHAT-LOGS.json`
- Keeps only last 5 messages (`max_messages=5`)
- Supports load, append, clear

### 3. Refinement Loop

For text and SQL answers:

1. Generate initial answer
2. Run `_refine()` prompt: "Improve this answer for clarity and correctness"
3. Return refined answer to user

### 4. Evaluation Layer

`src/evaluation/rag_eval.py`:

- Embeds answer + context
- Computes cosine similarity as faithfulness score
- Marks hallucination if score < `0.5`
- Confidence is faithfulness percentage

### 5. UI Layer

`src/deployment/app.py` (Streamlit):

- Mode 1: Text RAG
- Mode 2: Image RAG
  - `text_to_image`
  - `image_to_image`
  - `image_to_text`
- Mode 3: SQL QA
- Sidebar option to clear memory

---

## Request Flow

### Text RAG

1. Retrieve and build grounded context
2. Add conversation history to prompt
3. Generate + refine answer
4. Evaluate faithfulness/confidence
5. Save user + assistant turns to memory

### Image RAG

1. Run selected image mode in `ImageSearch`
2. Build short answer/caption from retrieval result
3. Evaluate with same evaluator

### SQL QA

1. Run NL-to-SQL pipeline
2. Refine output
3. Evaluate
4. Save in memory

---

## Logging and Observability

- Runtime logger is configured in `src/utils/logger.py`
- Log files are written in `src/logs/` with timestamped names
- Chat history is persisted in `CHAT-LOGS.json`

---

## Run Instructions

From `Week_7_GenAi` root:

```bash
streamlit run src/deployment/app.py
```

Requirements:

- Valid `GROQ_API_KEY` in environment (used by `src/generator/llm_client.py`)
- Models and indexes already prepared (text + image FAISS artifacts)

---

## Status Against Day 5 Deliverables

Completed:

- Deployment app (`src/deployment/app.py`)
- Evaluation module (`src/evaluation/rag_eval.py`)
- Memory module (`src/memory/memory_store.py`)
- Chat logs persistence (`CHAT-LOGS.json`)
- Streamlit interface for all three pipelines
