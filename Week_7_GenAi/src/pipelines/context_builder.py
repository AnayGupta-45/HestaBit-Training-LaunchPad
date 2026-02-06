from src.retriever.reranker import Reranker
from src.retriever.mmr import MMR
from sentence_transformers import SentenceTransformer


class ContextBuilder:
    def __init__(self):
        self.embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.reranker = Reranker(self.embedder)
        self.mmr = MMR()

    def run(self, query, top_k=5):
        reranked, query_emb = self.reranker.search(query)
        selected = self.mmr.select(query_emb, reranked, top_k)

        context_blocks = []
        sources = []

        for i, doc in enumerate(selected, 1):
            source_name = doc["metadata"]["source"]
            page = doc["metadata"].get("page")
            chunk = doc["metadata"].get("chunk_index")

            block = (
                f"{doc['text'].strip()}\n\n"
                f"(Source: {source_name}, Page: {page}, Chunk: {chunk})"
            )

            context_blocks.append(block)

            sources.append({
                "id": i,
                "source": source_name,
                "page": page,
                "chunk": chunk,
                "score": doc["rerank_score"],
                "retrieval_type": doc["source"]
            })

        return {
            "context": "\n\n---\n\n".join(context_blocks),
            "sources": sources
        }


if __name__ == "__main__":
    cb = ContextBuilder()
    query = input("Enter query: ").strip()
    result = cb.run(query)

    print("\nFINAL CONTEXT\n")
    print(result["context"])
