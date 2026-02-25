# Week 8 Final Report

## Fine-Tuning, Quantization & Deployment of TinyLlama

---

## 1. Project Overview

The objective of this project was to fine-tune TinyLlama (1.1B) on a coding dataset, optimize it for fast inference, and deploy it as a local production-style LLM system with streaming and guardrails.

Pipeline:

Dataset → Fine-Tuning (QLoRA) → Quantization → Optimization → Deployment

---

## 2. Dataset (Day 1 - Summary)

- Dataset: CodeAlpaca-20k
- Cleaned and filtered samples
- Final split:
  - Train: 1,200
  - Validation: 300
- Domain: Programming tasks (Python, SQL, algorithms, debugging)

---

## 3. Fine-Tuning (Day 2 - Summary)

- Base Model: TinyLlama-1.1B-Chat-v1.0
- Method: QLoRA (4-bit loading)
- Trainable Params: 2,252,800 (0.20%)
- Rank (r): 16
- Epochs: 3
- Learning Rate: 2e-4

Training loss decreased consistently.  
Validation loss remained stable (no overfitting).

---

## 4. Quantization (Day 3 - Summary)

Converted model to:

- FP16
- INT8
- INT4
- GGUF

Key Result:

| Format | Size   | Speed (tok/sec) | Device |
| ------ | ------ | --------------- | ------ |
| FP16   | 2.20GB | 21.15           | GPU    |
| INT4   | 0.81GB | 23.13           | GPU    |
| GGUF   | 1.17GB | 15.82           | CPU    |

GGUF enabled CPU-only inference with strong performance.

---

## 5. Inference Optimization (Day 4 - Summary)

Compared:

- Transformers (PyTorch)
- llama.cpp

CPU Results:

| Model      | Engine       | Speed        |
| ---------- | ------------ | ------------ |
| Base       | Transformers | 1.94 tok/sec |
| Fine-Tuned | Transformers | 2.85 tok/sec |
| GGUF       | llama.cpp    | 7.41 tok/sec |

llama.cpp was **2.6× faster** on CPU.

---

## 6. Day 5 – Deployment

### Backend (FastAPI)

- Streaming token generation
- Single prompt mode
- Chat mode with memory
- Context trimming
- Logging
- Context-aware guardrails
- Domain restriction (programming-only)

### Guardrails

- Prompt tightening
- Backend keyword-based + context-aware filtering
- Non-programming queries are blocked deterministically

### Frontend (Streamlit)

- Professional chatbot UI
- Enter-to-send
- Clear chat button
- Streaming output
- Latency + tokens/sec display

### Docker Deployment

Includes:

- requirements.txt
- Dockerfile
- .dockerignore
- CPU-only inference using GGUF

Run:

docker build -t tinyllama-app .
docker run -p 8000:8000 -p 8501:8501 tinyllama-app

---

## 7. Final Architecture

User (Streamlit UI)
↓
FastAPI Backend
↓
Context-Aware Guardrail
↓
TinyLlama GGUF (llama.cpp)
↓
Streaming Response

---

## 8. Key Learnings

- QLoRA enables efficient fine-tuning on low VRAM.
- Quantization significantly reduces model size.
- llama.cpp is optimized for CPU inference.
- Guardrails are necessary to control hallucination.
- Fine-tuning shifts behavior but does not replace base model knowledge.
- Docker ensures reproducible deployment.

---

## Final Conclusion

This project successfully implemented an end-to-end LLM pipeline:

- Fine-tuning
- Quantization
- CPU optimization
- Streaming inference
- Guardrails
- Full-stack deployment

The final system runs efficiently on CPU without GPU dependency and performs strongly on coding tasks.

Project completed successfully.
