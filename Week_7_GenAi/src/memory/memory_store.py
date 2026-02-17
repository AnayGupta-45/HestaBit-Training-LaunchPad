import json
from pathlib import Path


class MemoryStore:

    def __init__(self, path="CHAT-LOGS.json", max_messages=5):
        self.path = Path(path)
        self.max_messages = max_messages
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data):
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_message(self, role, content):
        data = self._load()
        data.append({"role": role, "content": content})
        data = data[-self.max_messages :]
        self._save(data)

    def get_recent(self):
        return self._load()

    def clear(self):
        self._save([])
