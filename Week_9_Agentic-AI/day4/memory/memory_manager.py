import os
import uuid
import json
from openai import OpenAI
from dotenv import load_dotenv

from memory.session_memory import SessionMemory
from memory.long_term_store import LongTermStore
from memory.vector_store import VectorStore

load_dotenv()

DUP_THRESHOLD = 0.93
SIM_THRESHOLD = 0.80


class MemoryManager:
    """
    Ties everything together.
    Extracts facts, stores them, retrieves them.
    This is the only thing main.py talks to.
    """

    def __init__(self):
        self.session = SessionMemory()
        self.long_term = LongTermStore()
        self.vector = VectorStore()
        self.llm = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def _new_id(self) -> int:
        return int(uuid.uuid4().int % (2**63 - 1))

    def extract_facts(self, user_msg: str, agent_msg: str) -> list:
        """
        Ask LLM to extract important long term facts from the conversation.
        """
        prompt = f"""
Extract important long-term facts about the USER from this conversation.

Store facts about:
- user's name or identity
- user's goals or projects
- user's skills or background
- topics user is learning about
- topics user is curious about or asking questions about
- subjects user wants to understand

DO NOT store:
- greetings or small talk
- assistant explanations or definitions
- generic questions with no personal context

Return ONLY a JSON list. No extra text. No markdown.

Format:
[
  {{"fact": "...", "category": "...", "importance": 0.0}}
]

Conversation:
USER: {user_msg}
AGENT: {agent_msg}
"""
        try:
            response = self.llm.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content.strip()

            # strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            return json.loads(raw)
        except Exception:
            return []

    def store_interaction(self, user_msg: str, agent_msg: str):
        """
        After each turn:
        1. Save to session memory
        2. Extract facts using LLM
        3. Save important facts to SQLite + FAISS
        """
        self.session.add("user", user_msg)
        self.session.add("agent", agent_msg)

        facts = self.extract_facts(user_msg, agent_msg)

        for fact in facts:
            if fact.get("importance", 0) >= 0.5:
                self._store_fact(fact)

    def _store_fact(self, fact_obj: dict):
        """
        Store fact only if not duplicate.
        Replace if contradicts existing fact.
        """
        new_fact = fact_obj["fact"]
        candidates = self.vector.search(new_fact, top_k=3)

        for mem_id, score in candidates:
            if score >= DUP_THRESHOLD:
                return  # duplicate, skip
            if score >= SIM_THRESHOLD:
                # contradicts or updates existing — replace
                self.vector.delete(mem_id)
                self.long_term.delete(mem_id)

        memory_id = self._new_id()
        self.vector.add(memory_id, new_fact)
        self.long_term.save(
            memory_id,
            new_fact,
            fact_obj.get("category", "general"),
            fact_obj.get("importance", 0.5)
        )

    def retrieve_context(self, query: str) -> str:
        """
        Build context for the agent:
        - relevant facts from long term memory
        - recent session history
        """
        session_context = self.session.get_recent()

        results = self.vector.search(query, top_k=3)
        memory_ids = [mem_id for mem_id, _ in results]
        facts = self.long_term.get_by_ids(memory_ids)

        facts_text = (
            "\n".join(f"- {f}" for f in facts)
            if facts else "No relevant facts found."
        )

        return (
            f"RELEVANT FACTS FROM MEMORY:\n{facts_text}\n\n"
            f"RECENT CONVERSATION:\n{session_context}"
        )

    def clear_session(self):
        self.session.clear()
        print("Session memory cleared.")