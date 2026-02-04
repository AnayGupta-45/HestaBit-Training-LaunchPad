import json
import numpy as np
import faiss
from pathlib import Path

from src.utils.logger import logger
from src.config.settings import EMBEDDINGS_DIR

VECTORSTORE_DIR = Path("src/vectorstore/")
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = VECTORSTORE_DIR / "faiss.index"
META_PATH = VECTORSTORE_DIR / "metadata.json"

def main():
    logger.info("STEP 3 STARTED: FAISS vector store creation")

    embeddings_path = Path(EMBEDDINGS_DIR) / "embeddings.npy"
    vectors = np.load(embeddings_path)
    dim = vectors.shape[1]

    logger.info(f"Loaded embeddings: shape={vectors.shape}")

    metadata = []
    meta_jsonl = Path(EMBEDDINGS_DIR) / "metadata.jsonl"
    with open(meta_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            metadata.append(json.loads(line))

    logger.info(f"Loaded metadata records: {len(metadata)}")

    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    logger.info(f"FAISS index built. Total vectors: {index.ntotal}")

    faiss.write_index(index, str(INDEX_PATH))
    logger.info(f"FAISS index saved at: {INDEX_PATH}")

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Metadata saved at: {META_PATH}")
    logger.info("STEP 3 COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
