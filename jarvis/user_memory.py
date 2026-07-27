from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .platform_utils import app_dir


MEMORY_FILE = app_dir() / "memory" / "user_memory.json"


class UserMemory:
    """Small local preference store for JARVIS."""

    def __init__(self, path: Path = MEMORY_FILE) -> None:
        self.path = path
        self.data: dict[str, Any] = {"preferences": {}, "command_history": []}
        self.load()

    def load(self) -> None:
        try:
            if self.path.exists():
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data.update(loaded)
        except Exception:
            self.data = {"preferences": {}, "command_history": []}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def remember_preference(self, key: str, value: str) -> None:
        self.data.setdefault("preferences", {})[key] = value
        self.save()

    def preference(self, key: str, default: str = "") -> str:
        value = self.data.get("preferences", {}).get(key, default)
        return str(value)

    def add_command(self, command: str, limit: int = 30) -> None:
        history = [item for item in self.data.setdefault("command_history", []) if item != command]
        history.append(command)
        self.data["command_history"] = history[-limit:]
        self.save()

    def command_history(self) -> list[str]:
        history = self.data.get("command_history", [])
        if isinstance(history, list):
            return [str(item) for item in history]
        return []
