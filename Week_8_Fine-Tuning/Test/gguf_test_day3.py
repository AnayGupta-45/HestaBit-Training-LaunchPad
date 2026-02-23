import os
import time
from llama_cpp import Llama

MODEL_PATH = "quantized/model.gguf"
PROMPT = "Write a Python function to check if a number is prime."
MAX_TOKENS = 128
N_CTX = 512


def get_model_size(path):
    size_bytes = os.path.getsize(path)
    return round(size_bytes / (1024**3), 2)  # GB


def benchmark_gguf_cpu():
    print("Loading GGUF model (CPU)...")

    llm = Llama(
        model_path=MODEL_PATH, n_ctx=N_CTX, n_threads=os.cpu_count(), verbose=False
    )

    print("Running inference...")
    start = time.time()

    output = llm(PROMPT, max_tokens=MAX_TOKENS, temperature=0.0)

    end = time.time()
    tokens_generated = output["usage"]["completion_tokens"]
    tokens_per_sec = tokens_generated / (end - start)

    print("\n==GGUF CPU BENCHMARK ==")
    print(f"Model size: {get_model_size(MODEL_PATH)} GB")
    print(f"Tokens/sec: {tokens_per_sec:.2f}")
    print("\n== SAMPLE OUTPUT ==")
    print(output["choices"][0]["text"])


if __name__ == "__main__":
    benchmark_gguf_cpu()
