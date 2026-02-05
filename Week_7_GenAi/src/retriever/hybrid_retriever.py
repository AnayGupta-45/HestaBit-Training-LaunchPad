import json
import faiss
import numpy as np
import re
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from src.config.settings import CHUNKS_PATH, EMBEDDINGS_DIR, TOP_K_VECTOR, TOP_K_KEYWORD, EMBEDDINGS_FILE
from src.utils.logger import logger

class HybridRetriever:
    def __init__(self):
        logger.info("Initializing Hybrid Retriever")

        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.embeddings = np.load(EMBEDDINGS_FILE)
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

        self.chunks = []
        with open(CHUNKS_PATH, "r") as f:
            for line in f:
                self.chunks.append(json.loads(line))

        self.bm25 = BM25Okapi(
            [self._tokenize(c["text"]) for c in self.chunks]
        )

    def _tokenize(self, text):
        return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()

    def semantic_search(self, query):
        q_emb = self.model.encode([query], normalize_embeddings=True)
        scores, idxs = self.index.search(q_emb, TOP_K_VECTOR)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": idx,
                "text": chunk["text"],
                "metadata": chunk["metadata"],
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
            chunk = self.chunks[idx]
            results.append({
                "chunk_id": idx,
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "keyword_score": float(score),
                "source": "keyword"
            })
        return results

    def search(self, query):
        logger.info(f"Hybrid search for query: {query}")

        semantic = self.semantic_search(query)
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

        return list(merged.values())
