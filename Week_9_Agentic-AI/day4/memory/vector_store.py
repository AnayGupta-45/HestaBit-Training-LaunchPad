import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
DIMENSION = 384

embedder = SentenceTransformer("all-MiniLM-L6-v2")


class VectorStore:
    """
    Vector memory using FAISS.
    Saves index to disk so it persists across runs.
    """

    def __init__(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        else:
            base = faiss.IndexFlatIP(DIMENSION)
            self.index = faiss.IndexIDMap(base)

    def add(self, memory_id: int, text: str):
        vector = self._embed(text)
        self.index.add_with_ids(vector, np.array([memory_id], dtype="int64"))
        self._save()

    def search(self, query: str, top_k: int = 3) -> list:
        if self.index.ntotal == 0:
            return []
        vector = self._embed(query)
        scores, ids = self.index.search(vector, top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx != -1:
                results.append((int(idx), float(score)))
        return results

    def delete(self, memory_id: int):
        self.index.remove_ids(np.array([memory_id], dtype="int64"))
        self._save()

    def _embed(self, text: str):
        vector = embedder.encode([text], normalize_embeddings=True)[0]
        return np.array([vector], dtype="float32")

    def _save(self):
        faiss.write_index(self.index, INDEX_PATH)