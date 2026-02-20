import time
from llama_cpp import Llama

llm = Llama(
    model_path = "quantized/model.gguf",
    n_ctx      = 512,
    verbose    = False
)

prompt = "Write a Python function to check if a number is prime."

start  = time.time()
output = llm(prompt, max_tokens=100, echo=False)
end    = time.time()

response = output["choices"][0]["text"]
tokens   = output["usage"]["completion_tokens"]
speed    = round(tokens / (end - start), 2)

print("prompt  :", prompt)
print("response:", response)
print("speed   :", speed, "tokens/sec")