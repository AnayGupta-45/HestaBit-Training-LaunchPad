import numpy as np
from sentence_transformers import SentenceTransformer


class RAGEvaluator:
   
    def __init__(self, model_name="BAAI/bge-base-en-v1.5"):
        self.model = SentenceTransformer(model_name)

    def evaluate(self, answer, context):
        answer_emb = self.model.encode([answer], normalize_embeddings=True)[0]
        context_emb = self.model.encode([context], normalize_embeddings=True)[0]

        faithfulness = float(np.dot(answer_emb, context_emb))
        hallucination = faithfulness < 0.5
        confidence = round(faithfulness * 100, 2)

        return {
            "faithfulness": round(faithfulness, 4),
            "hallucination": hallucination,
            "confidence": confidence,
        }
