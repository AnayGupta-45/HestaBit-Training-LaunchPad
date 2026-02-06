import numpy as np


class MMR:
    def __init__(self, lambda_param=0.7):
        self.lambda_param = lambda_param

    def select(self, query_emb, docs, top_k):
        embeddings = np.array([d["embedding"] for d in docs])

        selected = []
        candidates = list(range(len(docs)))

        while candidates and len(selected) < top_k:
            scores = []
            for idx in candidates:
                relevance = np.dot(query_emb, embeddings[idx])
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
