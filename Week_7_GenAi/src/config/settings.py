CHUNK_SIZE = 750
CHUNK_OVERLAP = 100

RAW_DATA_PATH = "src/data/raw"
CHUNKS_PATH = "src/data/chunks/chunks.jsonl"

EMBEDDINGS_DIR = "src/data/embeddings"
VECTORSTORE_DIR = "src/vectorstore"
EMBEDDINGS_FILE = "src/data/embeddings/embeddings.npy"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

TOP_K_VECTOR = 10
TOP_K_KEYWORD = 10
FINAL_TOP_K = 5