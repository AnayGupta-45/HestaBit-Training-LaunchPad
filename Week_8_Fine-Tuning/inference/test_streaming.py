from llama_cpp import Llama
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
GGUF_MODEL_PATH = str(SCRIPT_DIR / "quantized" / "model.gguf")

llm = Llama(
    model_path=GGUF_MODEL_PATH,
    n_ctx=2048,
    n_threads=os.cpu_count(),
    verbose=False
)

prompt = "Write a Python function to check if a number is prime."
print(f"Prompt: {prompt}\nResponse: ", end="")

stream = llm(
    prompt,
    max_tokens=256,
    stream=True
)

for chunk in stream:
    text = chunk["choices"][0]["text"]
    print(text, end="", flush=True)

print("\n")