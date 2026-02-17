from src.pipelines.context_builder import ContextBuilder
from src.retriever.image_search import ImageSearch
from src.scripts.sql_pipeline import SQLPipeline
from src.generator.llm_client import generate
from src.memory.memory_store import MemoryStore
from src.evaluation.rag_eval import RAGEvaluator


class EnterpriseAssistant:
    def __init__(self):
        self.text_engine = ContextBuilder()
        self.image_engine = ImageSearch()
        self.sql_engine = SQLPipeline()
        self.memory = MemoryStore()
        self.evaluator = RAGEvaluator()

    def _build_prompt(self, context, query):
        history = self.memory.get_recent()
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history])

        return f"""
You are an enterprise AI assistant.
Answer ONLY from the given context.
If the answer is not present, say: Not found in documents.

Conversation History:
{history_text}

Context:
{context}

Question:
{query}
"""

    def _refine(self, answer):
        prompt = f"Improve this answer for clarity and correctness:\n{answer}"
        return generate(prompt)

    def handle_text(self, query):
        result = self.text_engine.run(query)
        context = result["context"]
        sources = result["sources"]

        prompt = self._build_prompt(context, query)
        answer = generate(prompt)
        refined = self._refine(answer)

        eval_result = self.evaluator.evaluate(refined, context)

        self.memory.add_message("user", query)
        self.memory.add_message("assistant", refined)

        return {
            "answer": refined,
            "sources": sources,
            **eval_result,
        }

    def handle_image(self, mode, query=None, image_path=None):

        # TEXT → IMAGE
        if mode == "text_to_image":
            results = self.image_engine.text_to_image(query)

            image_paths = [r["image_path"] for r in results]
            context = "\n".join([r["retrieval_text"] for r in results])

            answer_text = f"Retrieved {len(image_paths)} relevant images."
            eval_result = self.evaluator.evaluate(answer_text, context)

            return {
                "images": image_paths,
                **eval_result,
            }

        # IMAGE → IMAGE
        elif mode == "image_to_image":
            results = self.image_engine.image_to_image(image_path)

            image_paths = [r["image_path"] for r in results]
            context = "\n".join([r["retrieval_text"] for r in results])

            answer_text = f"Found {len(image_paths)} similar images."
            eval_result = self.evaluator.evaluate(answer_text, context)

            return {
                "images": image_paths,
                **eval_result,
            }

        # IMAGE → TEXT
        elif mode == "image_to_text":
            caption = self.image_engine.image_to_text(image_path)

            context = caption
            eval_result = self.evaluator.evaluate(caption, context)

            return {
                "answer": caption,
                **eval_result,
            }

    def handle_sql(self, query):
        answer = self.sql_engine.run(query)
        refined = self._refine(answer)

        context = answer

        eval_result = self.evaluator.evaluate(refined, context)

        self.memory.add_message("user", query)
        self.memory.add_message("assistant", refined)

        return {
            "answer": refined,
            "sources": [],
            **eval_result,
        }
