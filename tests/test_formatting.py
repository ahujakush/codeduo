"""
Unit tests for Telegram formatting and message splitting.
"""

from bot.utils.telegram_format import split_message, escape_markdown_v2, MAX_TELEGRAM_MESSAGE_LENGTH


def test_split_short_message():
    text = "Short problem solution."
    chunks = split_message(text, max_length=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_long_message():
    # Construct a message of 5000 chars with multiple paragraphs
    paragraphs = [f"Paragraph {i}: " + "A" * 80 for i in range(50)]
    long_text = "\n\n".join(paragraphs)
    assert len(long_text) > 4000

    chunks = split_message(long_text, max_length=1000)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 1000


def test_split_preserves_code_blocks():
    text = (
        "Here is the code:\n```python\n"
        + ("x = 1\n" * 50)
        + "```\nAnd here is the rest of the explanation."
    )
    chunks = split_message(text, max_length=200)
    assert len(chunks) > 1
    # Verify that code blocks are properly balanced with triple backticks
    for chunk in chunks:
        assert chunk.count("```") % 2 == 0


def test_escape_markdown_v2():
    raw_text = "Here is *bold*, _italic_, and a dot. Plus 2 + 2 = 4!"
    escaped = escape_markdown_v2(raw_text)
    # Punctuation should be escaped
    assert r"\." in escaped
    assert r"\+" in escaped
    assert r"\=" in escaped
    assert r"\!" in escaped


def test_escape_markdown_v2_leaves_code_blocks_intact():
    raw_text = "Check this code:\n```python\nx = 2 + 2\n```\nDone."
    escaped = escape_markdown_v2(raw_text)
    # The code block ```python\nx = 2 + 2\n``` should remain unescaped inside
    assert "```python\nx = 2 + 2\n```" in escaped
    # The dot outside should be escaped
    assert r"\." in escaped
