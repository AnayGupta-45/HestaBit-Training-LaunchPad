class SessionMemory:
    """
    Short term memory.
    Only lives during current run — gone when app closes.
    """

    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]

    def get_recent(self, limit: int = 6) -> str:
        if not self.messages:
            return "No conversation history yet."
        recent = self.messages[-limit:]
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )

    def clear(self):
        self.messages = []