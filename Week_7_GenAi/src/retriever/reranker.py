from sentence_transformers import CrossEncoder
from src.retriever.hybrid_retriever import HybridRetriever
from src.utils.logger import logger


class Reranker:
    def __init__(self, embedder):
        logger.info("Initializing reranker")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
        self.retriever = HybridRetriever(embedder)

    def search(self, query):
        docs, query_emb = self.retriever.search(query)

        pairs = [(query, d["text"]) for d in docs]
        scores = self.cross_encoder.predict(pairs)

        for d, s in zip(docs, scores):
            d["rerank_score"] = float(s)

        reranked = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)
        return reranked, query_emb
