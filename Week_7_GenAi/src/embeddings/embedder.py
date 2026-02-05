import json
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from src.utils.logger import logger
from src.config.settings import EMBEDDING_MODEL, CHUNKS_PATH, EMBEDDINGS_DIR

def main():
    logger.info("STEP 2 STARTED: Embedding generation")
    
    embeddings_dir = Path(EMBEDDINGS_DIR)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    batch_size = 32
    batch_texts = []
    batch_metadatas = []
    all_vectors = []
    
    metadata_file = open(embeddings_dir / "metadata.jsonl", "w", encoding="utf-8")

    total_chunks = sum(1 for _ in open(CHUNKS_PATH, "r", encoding="utf-8"))

    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=total_chunks, desc="Embedding", unit="chunk"):
            record = json.loads(line)
            batch_texts.append(record["text"])
            batch_metadatas.append(record["metadata"])
            
            if len(batch_texts) >= batch_size:
                vectors = model.encode(batch_texts, normalize_embeddings=True)
                all_vectors.append(vectors)
                
                for meta in batch_metadatas:
                    metadata_file.write(json.dumps(meta, ensure_ascii=False) + "\n")
                
                batch_texts = []
                batch_metadatas = []

    if batch_texts:
        vectors = model.encode(batch_texts, normalize_embeddings=True)
        all_vectors.append(vectors)
        for meta in batch_metadatas:
            metadata_file.write(json.dumps(meta, ensure_ascii=False) + "\n")

    metadata_file.close()

    if all_vectors:
        final_vectors = np.vstack(all_vectors)
        np.save(embeddings_dir / "embeddings.npy", final_vectors)
        logger.info(f"Saved {final_vectors.shape[0]} vectors to {EMBEDDINGS_DIR}")
    else:
        logger.error("No vectors generated")

if __name__ == "__main__":
    main()