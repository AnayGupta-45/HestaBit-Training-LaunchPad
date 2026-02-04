import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

from src.utils.logger import logger
from src.config.settings import (
    EMBEDDING_MODEL,
    CHUNKS_PATH,
    EMBEDDINGS_DIR
)

def main():
    logger.info("STEP 2 STARTED: Embedding generation")

    embeddings_dir = Path(EMBEDDINGS_DIR)
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    embeddings_file = embeddings_dir / "embeddings.npy"
    metadata_file = embeddings_dir / "metadata.jsonl"

    texts = []
    metadatas = []

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            texts.append(record["text"])
            metadatas.append({
                "chunk_id": record["chunk_id"],
                "source": record["metadata"]["source"],
                "page": record["metadata"].get("page"),
                "chunk_index": record["metadata"]["chunk_index"]
            })

    logger.info(f"Chunks loaded for embedding: {len(texts)}")

    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info(f"Embedding model loaded: {EMBEDDING_MODEL}")

    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    logger.info(f"Embeddings generated with shape: {vectors.shape}")

    np.save(embeddings_file, vectors)
    logger.info(f"Embeddings saved at: {embeddings_file}")

    with open(metadata_file, "w", encoding="utf-8") as f:
        for meta in metadatas:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

    logger.info(f"Metadata saved at: {metadata_file}")
    logger.info("STEP 2 COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
