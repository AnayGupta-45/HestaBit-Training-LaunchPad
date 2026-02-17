import json
import numpy as np
import faiss
from pathlib import Path
from src.utils.logger import logger
from src.config.settings import EMBEDDINGS_DIR, VECTORSTORE_DIR


def main():
    logger.info("STEP 3 STARTED: FAISS vector store creation")

    v_dir = Path(VECTORSTORE_DIR)
    v_dir.mkdir(parents=True, exist_ok=True)

    embeddings_path = Path(EMBEDDINGS_DIR) / "embeddings.npy"
    meta_jsonl = Path(EMBEDDINGS_DIR) / "metadata.jsonl"

    index_path = v_dir / "index.faiss"
    meta_json = v_dir / "metadata.json"

    if not embeddings_path.exists():
        logger.error(f"Embeddings file not found at {embeddings_path}")
        return

    if not meta_jsonl.exists():
        logger.error(f"Metadata file not found at {meta_jsonl}")
        return

    vectors = np.load(embeddings_path)
    dim = vectors.shape[1]

    metadata = []
    with open(meta_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            metadata.append(json.loads(line))

    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    faiss.write_index(index, str(index_path))

    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"FAISS index built with {index.ntotal} vectors")


if __name__ == "__main__":
    main()
