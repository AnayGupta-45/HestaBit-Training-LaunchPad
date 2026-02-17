import os
import json
import numpy as np
import torch
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.config.settings import EMBEDDING_MODEL, CHUNKS_PATH, EMBEDDINGS_DIR


# Sets CPU threads for faster parallel processing
def configure_threads():
    cpu_count = os.cpu_count() or 4
    os.environ["OMP_NUM_THREADS"] = str(cpu_count)
    os.environ["MKL_NUM_THREADS"] = str(cpu_count)
    os.environ["NUMEXPR_NUM_THREADS"] = str(cpu_count)
    torch.set_num_threads(cpu_count)
    torch.set_num_interop_threads(cpu_count)


def main():
    logger.info("STEP 2 STARTED: Embedding generation")

    configure_threads()

    embeddings_dir = Path(EMBEDDINGS_DIR)
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(EMBEDDING_MODEL)

    batch_size = 128 
    batch_texts = []
    batch_records = []
    all_vectors = []

    metadata_path = embeddings_dir / "metadata.jsonl"
    metadata_file = open(metadata_path, "w", encoding="utf-8")

    total_chunks = sum(1 for _ in open(CHUNKS_PATH, "r", encoding="utf-8"))

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=total_chunks, desc="Embedding", unit="chunk"):
            record = json.loads(line)

            batch_texts.append(record["text"])
            batch_records.append(record)

            if len(batch_texts) >= batch_size:
                vectors = model.encode(
                    batch_texts,
                    batch_size=batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                all_vectors.append(vectors)

                for rec in batch_records:
                    metadata_file.write(json.dumps(rec, ensure_ascii=False) + "\n")

                batch_texts = []
                batch_records = []

    if batch_texts:
        vectors = model.encode(
            batch_texts,
            batch_size=len(batch_texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        all_vectors.append(vectors)

        for rec in batch_records:
            metadata_file.write(json.dumps(rec, ensure_ascii=False) + "\n")

    metadata_file.close()

    if all_vectors:
        final_vectors = np.vstack(all_vectors)
        np.save(embeddings_dir / "embeddings.npy", final_vectors)
        logger.info(f"Saved {final_vectors.shape[0]} vectors to {EMBEDDINGS_DIR}")
    else:
        logger.error("No vectors generated")


if __name__ == "__main__":
    main()
