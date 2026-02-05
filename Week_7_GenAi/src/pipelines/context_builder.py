from src.retriever.reranker import Reranker
from src.retriever.mmr import MMR

class ContextBuilder:
    def __init__(self):
        self.reranker = Reranker()
        self.mmr = MMR()

    def run(self, query, top_k=5):
        reranked = self.reranker.search(query)
        selected = self.mmr.select(query, reranked, top_k)

        context = []
        sources = []

        for i, doc in enumerate(selected, 1):
            context.append(f"[Source {i}]\n{doc['text']}")
            sources.append({
                "id": i,
                "source": doc["metadata"]["source"],
                "page": doc["metadata"].get("page"),
                "chunk": doc["metadata"].get("chunk_index"),
                "score": doc["rerank_score"],
                "retrieval_type": doc["source"]
            })

        return {
            "context": "\n\n".join(context),
            "sources": sources
        }

if __name__ == "__main__":
    cb = ContextBuilder()
    query = input("Enter query: ").strip()
    result = cb.run(query)

    print("\nFINAL CONTEXT\n")
    print(result["context"])
