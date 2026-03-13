import os
import uuid
import json
from openai import OpenAI
from dotenv import load_dotenv

from memory.session_memory import SessionMemory
from memory.long_term_store import LongTermStore
from memory.vector_store import VectorStore

load_dotenv()


class MemoryManager:
    """
    Simple memory system.
    Handles:
    - session memory
    - fact extraction
    - vector storage
    - sqlite storage
    """

    def __init__(self):
        self.session = SessionMemory()
        self.long_term = LongTermStore()
        self.vector = VectorStore()

        self.llm = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def _new_id(self):
        return int(uuid.uuid4().int % (2**63 - 1))

    def extract_facts(self, user_msg: str, agent_msg: str):
        """
        Ask LLM to extract simple facts about the user.
        """

        prompt = f"""
Extract simple facts about the USER.

Return ONLY a JSON list.

Conversation:
USER: {user_msg}
AGENT: {agent_msg}
"""

        try:
            res = self.llm.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            raw = res.choices[0].message.content.strip()

            facts = json.loads(raw)

            return facts

        except Exception:
            return []

    def store_interaction(self, user_msg: str, agent_msg: str):

        # store conversation
        self.session.add("user", user_msg)
        self.session.add("agent", agent_msg)

        facts = self.extract_facts(user_msg, agent_msg)

        for fact in facts:

            memory_id = self._new_id()

            self.vector.add(memory_id, fact)

            self.long_term.save(memory_id, fact)

    def retrieve_context(self, query: str):

        session_context = self.session.get_recent()

        results = self.vector.search(query, top_k=3)

        memory_ids = [mem_id for mem_id, _ in results]

        facts = self.long_term.get_by_ids(memory_ids)

        facts_text = "\n".join(f"- {f}" for f in facts)

        return f"""
USER FACTS:
{facts_text}

RECENT CONVERSATION:
{session_context}
"""

    def clear_session(self):
        self.session.clear()
        print("Session memory cleared.")