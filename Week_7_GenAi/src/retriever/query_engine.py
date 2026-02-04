import json
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.config.settings import EMBEDDING_MODEL

VECTORSTORE_DIR = Path("src/vectorstore/")
CHUNKS_PATH = Path("src/data/chunks/chunks.jsonl")
INDEX_PATH = VECTORSTORE_DIR / "faiss.index"
META_PATH = VECTORSTORE_DIR / "metadata.json"

def load_chunks():
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def main():
    logger.info("STEP 4 STARTED: FAISS retrieval")

    index = faiss.read_index(str(INDEX_PATH))
    logger.info(f"FAISS index loaded with {index.ntotal} vectors")

    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    chunks = load_chunks()
    model = SentenceTransformer(EMBEDDING_MODEL)
    query = input("\nEnter your query: ").strip()

    if not query:
        logger.error("Empty query provided. Exiting.")
        return

    top_k = 5

    logger.info(f"User query: {query}")
    query_vector = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, indices = index.search(
        np.array(query_vector, dtype="float32"),
        top_k
    )

    print("\nTop results:\n")

    for rank, idx in enumerate(indices[0]):
        score = scores[0][rank]
        meta = metadata[idx]
        chunk_text = chunks[idx]["text"]

        print(f"Rank {rank + 1}")
        print(f"Score: {score:.4f}")
        print(f"Source: {meta['source']} | Page: {meta.get('page')}")
        print(f"Text:\n{chunk_text[:600]}")
        print("-" * 80)

    logger.info("STEP 4 COMPLETED")

if __name__ == "__main__":
    main()
