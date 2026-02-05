from sentence_transformers import CrossEncoder
from src.retriever.hybrid_retriever import HybridRetriever
from src.utils.logger import logger

class Reranker:
    def __init__(self):
        logger.info("Initializing reranker")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.retriever = HybridRetriever()

    def search(self, query):
        docs = self.retriever.search(query)

        pairs = [(query, d["text"]) for d in docs]
        scores = self.cross_encoder.predict(pairs)

        for d, s in zip(docs, scores):
            d["rerank_score"] = float(s)

        return sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
