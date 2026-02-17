import json
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.config.settings import EMBEDDING_MODEL, VECTORSTORE_DIR, CHUNKS_PATH


def load_chunks():
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def main():
    logger.info("STEP 4 STARTED: FAISS retrieval")

    index_path = Path(VECTORSTORE_DIR) / "index.faiss"
    meta_path = Path(VECTORSTORE_DIR) / "metadata.json"

    if not index_path.exists():
        logger.error("Index not found")
        return

    index = faiss.read_index(str(index_path))

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    chunks = load_chunks()
    model = SentenceTransformer(EMBEDDING_MODEL)

    query = input("\nEnter your query: ").strip()
    if not query:
        return

    query_vector = model.encode([query], normalize_embeddings=True)

    scores, indices = index.search(np.array(query_vector, dtype="float32"), k=5)

    print(f"RESULTS FOR: '{query}'")
    print("-" * 80)

    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue

        meta = metadata[idx]
        chunk_text = chunks[idx]["text"]
        score = scores[0][rank]

        print(f"RANK {rank + 1} | Score: {score:.4f}")
        print(f"Source: {meta.get('source')} | Page: {meta.get('page')}")
        print("-" * 40)
        print(f"{chunk_text[:400]}...")
        print("\n" + "_" * 80 + "\n")


if __name__ == "__main__":
    main()
