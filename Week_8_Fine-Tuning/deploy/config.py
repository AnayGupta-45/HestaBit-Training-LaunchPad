import os

MODEL_PATH = "quantized/model.gguf"

N_CTX = 2048
N_THREADS = os.cpu_count()
N_GPU_LAYERS = 0
N_BATCH = 512