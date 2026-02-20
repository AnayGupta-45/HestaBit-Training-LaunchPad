# Quantisation Report - Week 8 Day 3

## What We Did

We took the fine-tuned TinyLlama model from Day 2 and converted it into three
smaller formats — INT8, INT4, and GGUF. The goal was to reduce model size while
keeping quality acceptable, and to enable CPU inference using GGUF.

## Model

- base_model : TinyLlama/TinyLlama-1.1B-Chat-v1.0
- fine_tuned : Yes (Day 2 QLoRA adapters merged)
- tool_used : BitsAndBytes (INT8/INT4), llama.cpp (GGUF)

## Comparisons

### FP16 Format

- size : 2.20 GB
- speed : 21.15 tokens/sec
- device : GPU (T4)
- notes : baseline, full precision

### INT8 Format

- size : 1.24 GB
- speed : 8.90 tokens/sec
- device : GPU (T4)
- notes : 44% smaller, slower due to INT8 compute overhead

### INT4 Format

- size : 0.81 GB
- speed : 23.13 tokens/sec
- device : GPU (T4)
- notes : 63% smaller, fastest on GPU due to NF4 optimization

### GGUF Format - (q8_0)

- size : 1.17 GB
- speed : 15.82 tokens/sec
- device : CPU (local machine)
- notes : no GPU needed, runs on any laptop

## Key Observations

INT8 is the slowest despite being smaller than FP16. This is because every
computation requires converting INT8 weights back to FP16 at runtime, which
adds overhead.

INT4 is actually faster than FP16 on GPU because the NF4 format is specifically
optimized for GPU memory access patterns.

GGUF running at 15.82 tokens/sec on CPU is the most practical format for
deployment on machines without a GPU.

## Output Files

- quantized/model-fp16/ → merged model in full precision
- quantized/model-int8/ → 8-bit quantized model
- quantized/model-int4/ → 4-bit quantized model
- quantized/model.gguf → GGUF format for CPU inference
