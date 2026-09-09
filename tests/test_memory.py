"""
Unit tests for Chat Memory Manager.
"""

from bot.memory.chat_memory import ChatMemoryManager, ChatMessage


def test_add_and_retrieve_history():
    memory = ChatMemoryManager(max_turns=3)
    chat_id = 12345

    memory.add_message(chat_id, "user", "Hello")
    memory.add_message(chat_id, "assistant", "Hi! How can I help?")

    history = memory.get_history(chat_id)
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"
    assert history[1].content == "Hi! How can I help?"


def test_sliding_window_limit():
    # max_turns=2 means max 4 messages (2 user + 2 assistant)
    memory = ChatMemoryManager(max_turns=2)
    chat_id = 100

    for i in range(6):
        memory.add_message(chat_id, "user" if i % 2 == 0 else "assistant", f"Msg {i}")

    history = memory.get_history(chat_id)
    assert len(history) == 4
    # The oldest messages (0 and 1) should have been pruned
    assert history[0].content == "Msg 2"
    assert history[-1].content == "Msg 5"


def test_clear_history():
    memory = ChatMemoryManager()
    chat_id = 200

    memory.add_message(chat_id, "user", "Problem 1")
    assert len(memory.get_history(chat_id)) == 1

    memory.clear_history(chat_id)
    assert len(memory.get_history(chat_id)) == 0


def test_persona_management():
    memory = ChatMemoryManager()
    chat_id = 300

    assert memory.get_persona(chat_id, default="solver") == "solver"
    memory.set_persona(chat_id, "coder")
    assert memory.get_persona(chat_id) == "coder"


def test_memory_stats():
    memory = ChatMemoryManager()
    memory.add_message(1, "user", "Hi")
    memory.add_message(2, "user", "Hey")
    memory.add_message(2, "assistant", "Hello")

    stats = memory.get_stats()
    assert stats["active_chats"] == 2
    assert stats["total_messages"] == 3
