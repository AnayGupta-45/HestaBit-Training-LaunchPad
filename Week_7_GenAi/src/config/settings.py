from pathlib import Path

BASE_DIR = Path("src")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw"

CHUNKS_PATH = DATA_DIR / "chunks" / "chunks.jsonl"

EMBEDDINGS_DIR = DATA_DIR / "embeddings"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

EMBEDDINGS_FILE = EMBEDDINGS_DIR / "embeddings.npy"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

TOP_K_VECTOR = 10
TOP_K_KEYWORD = 10
FINAL_TOP_K = 5

IMAGE_DIR = DATA_DIR / "images"

IMAGE_METADATA_PATH = DATA_DIR / "clip_metadata.jsonl"

IMAGE_INDEX_FILE = VECTORSTORE_DIR / "image.faiss"
TEXT_INDEX_FILE = VECTORSTORE_DIR / "text.faiss"

