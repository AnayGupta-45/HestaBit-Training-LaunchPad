import json
import faiss
import numpy as np
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
from src.config.settings import VECTORSTORE_DIR, EMBEDDINGS_DIR, TOP_K_VECTOR, TOP_K_KEYWORD
from src.utils.logger import logger


class HybridRetriever:
    def __init__(self, embedder):
        logger.info("Initializing Hybrid Retriever (Production Mode)")

        self.model = embedder
        
        v_dir = Path(VECTORSTORE_DIR)
        index_path = v_dir / "index.faiss"
        meta_path = v_dir / "metadata.json"
        embeddings_path = Path(EMBEDDINGS_DIR) / "embeddings.npy"

        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}")

        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata not found at {meta_path}")

        self.index = faiss.read_index(str(index_path))

        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.embeddings = np.load(embeddings_path)

        self.bm25 = BM25Okapi(
            [self._tokenize(m["text"]) for m in self.metadata]
        )

    def _tokenize(self, text):
        return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()

    def semantic_search(self, query_emb):
        scores, idxs = self.index.search(query_emb, TOP_K_VECTOR)

        results = []

        for score, idx in zip(scores[0], idxs[0]):
            meta = self.metadata[idx]

            results.append({
                "chunk_id": idx,
                "text": meta["text"],
                "metadata": meta,
                "embedding": self.embeddings[idx],
                "vector_score": float(score),
                "source": "semantic"
            })

        return results

    def keyword_search(self, query):
        scores = self.bm25.get_scores(self._tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []

        for idx, score in ranked[:TOP_K_KEYWORD]:
            if score <= 0:
                continue

            meta = self.metadata[idx]

            results.append({
                "chunk_id": idx,
                "text": meta["text"],
                "metadata": meta,
                "embedding": self.embeddings[idx],
                "keyword_score": float(score),
                "source": "keyword"
            })

        return results

    def search(self, query):
        logger.info(f"Hybrid search for query: {query}")

        query_emb = self.model.encode([query], normalize_embeddings=True)

        semantic = self.semantic_search(query_emb)
        keyword = self.keyword_search(query)

        merged = {}

        for r in semantic:
            merged[r["chunk_id"]] = r

        for r in keyword:
            cid = r["chunk_id"]

            if cid in merged:
                merged[cid]["keyword_score"] = r["keyword_score"]
                merged[cid]["source"] = "both"
            else:
                merged[cid] = r

        return list(merged.values()), query_emb[0]
