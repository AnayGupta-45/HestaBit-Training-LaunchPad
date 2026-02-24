import time
import os
import csv
import gc
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer, util

# BASIC CONFIG
DEVICE = "cpu"
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_MODEL_PATH = BASE_DIR / "quantized" / "base_model-fp16"
FT_MODEL_PATH = BASE_DIR / "quantized" / "model_FP16"
GGUF_MODEL_PATH = BASE_DIR / "quantized" / "model.gguf"
RESULTS_PATH = BASE_DIR / "benchmarks" / "results.csv"
MAX_NEW_TOKENS = 128

# EVALUATION DATA
PROMPTS = [
    "Write a Python function to check if a number is prime.",
    "Fix the syntax error in this code: def hello_world() print('hello')",
    "Explain what a List Comprehension is in Python with a simple example."
]

GROUND_TRUTH = [
    "def is_prime(n): return n > 1 and all(n % i for i in range(2, int(n**0.5) + 1))",
    "def hello_world(): print('hello')",
    "List comprehension is a concise way to create lists. Example: [x**2 for x in range(5)]"
]

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

# HELPER FUNCTIONS
def calculate_semantic_accuracy(predictions, references):
    pred_embeddings = embedder.encode(predictions, convert_to_tensor=True)
    ref_embeddings = embedder.encode(references, convert_to_tensor=True)
    similarity = util.cos_sim(pred_embeddings, ref_embeddings)
    return round(similarity.diag().mean().item(), 3)


def calculate_metrics(responses, start_time, end_time):
    duration = end_time - start_time
    total_tokens = sum(len(r.split()) for r in responses)
    tokens_per_sec = total_tokens / duration
    accuracy = calculate_semantic_accuracy(responses, GROUND_TRUTH)

    return round(tokens_per_sec, 2), round(duration, 2), accuracy

# TRANSFORMERS BENCHMARK
def benchmark_transformers(model_path, model_name):
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return None

    print(f"\nTesting {model_name} (Transformers)...")

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float32,
        device_map="cpu",
        local_files_only=True
    )

    inputs = tokenizer(PROMPTS, return_tensors="pt", padding=True)

    start = time.time()
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
    end = time.time()

    responses = [tokenizer.decode(o, skip_special_tokens=True) for o in outputs]

    tps, total_time, acc = calculate_metrics(responses, start, end)

    del model, tokenizer
    gc.collect()

    return {
        "model": model_name,
        "engine": "transformers",
        "device": "CPU",
        "tokens_per_sec": tps,
        "total_time_sec": total_time,
        "accuracy": acc
    }

# GGUF BENCHMARK
def benchmark_gguf():
    if not os.path.exists(GGUF_MODEL_PATH):
        print(f"GGUF file not found: {GGUF_MODEL_PATH}")
        return None

    print("\nTesting GGUF (llama.cpp)...")

    llm = Llama(
        model_path=str(GGUF_MODEL_PATH),
        n_ctx=2048,
        n_threads=os.cpu_count(),
        verbose=False
    )

    responses = []

    start = time.time()
    for prompt in PROMPTS:
        result = llm(prompt, max_tokens=MAX_NEW_TOKENS)
        responses.append(result["choices"][0]["text"])
    end = time.time()

    tps, total_time, acc = calculate_metrics(responses, start, end)

    return {
        "model": "GGUF-Q8",
        "engine": "llama.cpp",
        "device": "CPU",
        "tokens_per_sec": tps,
        "total_time_sec": total_time,
        "accuracy": acc
    }

# MAIN FUNCTION 
def main():
    os.makedirs(RESULTS_PATH.parent, exist_ok=True)

    results = []

    base_result = benchmark_transformers(BASE_MODEL_PATH, "Base-Model")
    if base_result:
        results.append(base_result)

    ft_result = benchmark_transformers(FT_MODEL_PATH, "Fine-Tuned")
    if ft_result:
        results.append(ft_result)

    gguf_result = benchmark_gguf()
    if gguf_result:
        results.append(gguf_result)

    if results:
        with open(RESULTS_PATH, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\nBenchmark Complete! Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()