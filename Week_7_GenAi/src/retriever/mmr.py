import numpy as np
from sentence_transformers import SentenceTransformer

class MMR:
    def __init__(self, lambda_param=0.7):
        self.lambda_param = lambda_param
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    def select(self, query, docs, top_k):
        embeddings = self.model.encode(
            [d["text"] for d in docs],
            normalize_embeddings=True
        )
        q_emb = self.model.encode([query], normalize_embeddings=True)[0]

        selected = []
        candidates = list(range(len(docs)))

        while candidates and len(selected) < top_k:
            scores = []
            for idx in candidates:
                relevance = np.dot(q_emb, embeddings[idx])
                diversity = max(
                    [np.dot(embeddings[idx], embeddings[s]) for s in selected],
                    default=0
                )
                score = self.lambda_param * relevance - (1 - self.lambda_param) * diversity
                scores.append((score, idx))

            best = max(scores, key=lambda x: x[0])[1]
            selected.append(best)
            candidates.remove(best)

        return [docs[i] for i in selected]
