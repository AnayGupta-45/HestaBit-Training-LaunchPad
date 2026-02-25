from llama_cpp import Llama
from .config import MODEL_PATH, N_CTX, N_THREADS, N_GPU_LAYERS, N_BATCH

_model = None

def get_model():
    global _model
    if _model is None:
        _model = Llama(
            model_path=MODEL_PATH,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            n_gpu_layers=N_GPU_LAYERS,
            n_batch=N_BATCH,
            use_mmap=True,
            use_mlock=True,
            verbose=False
        )
    return _model