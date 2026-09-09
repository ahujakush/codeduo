"""
Chat Memory and Session Management module.
Stores per-user/chat conversation history and active persona settings.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)


class ChatMemoryManager:
    """Manages short-term conversation context and preferences per Telegram chat."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._history: Dict[int, List[ChatMessage]] = {}
        self._personas: Dict[int, str] = {}

    def get_history(self, chat_id: int) -> List[ChatMessage]:
        """Retrieve recent conversation history for a given chat."""
        return self._history.get(chat_id, []).copy()

    def add_message(self, chat_id: int, role: str, content: str) -> None:
        """Add a message to the chat's history and enforce sliding window limit."""
        if chat_id not in self._history:
            self._history[chat_id] = []

        self._history[chat_id].append(ChatMessage(role=role, content=content))

        # Keep only the last max_turns * 2 messages (each turn is user + assistant)
        max_messages = self.max_turns * 2
        if len(self._history[chat_id]) > max_messages:
            self._history[chat_id] = self._history[chat_id][-max_messages:]

    def clear_history(self, chat_id: int) -> None:
        """Reset the conversation context for a given chat."""
        if chat_id in self._history:
            self._history[chat_id].clear()

    def set_persona(self, chat_id: int, persona: str) -> None:
        """Set active persona for a given chat."""
        self._personas[chat_id] = persona.lower()

    def get_persona(self, chat_id: int, default: str = "solver") -> str:
        """Get active persona for a given chat."""
        return self._personas.get(chat_id, default)

    def get_stats(self) -> Dict[str, Any]:
        """Return memory statistics."""
        active_chats = len(self._history)
        total_messages = sum(len(msgs) for msgs in self._history.values())
        return {
            "active_chats": active_chats,
            "total_messages": total_messages,
        }


# Global memory manager instance
chat_memory = ChatMemoryManager()
