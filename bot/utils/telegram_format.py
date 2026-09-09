"""
Telegram Message Formatting and Splitting Utilities.
Ensures messages comply with Telegram's 4096-character limit and avoids Markdown parsing errors.
"""

import re
import logging
from typing import List
from telegram import Message
from telegram.constants import ParseMode
from telegram.error import BadRequest

logger = logging.getLogger(__name__)

# Telegram maximum message length
MAX_TELEGRAM_MESSAGE_LENGTH = 4000


def split_message(text: str, max_length: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> List[str]:
    """
    Split a long message into smaller chunks that fit within Telegram's limits.
    Prefers splitting at code block boundaries, double newlines, single newlines, or spaces.
    """
    if not text:
        return [""]

    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while len(remaining) > max_length:
        # Search for a natural split point
        split_pos = -1

        # 1. Try splitting at triple backticks (code block boundary)
        code_split = remaining.rfind("```", 0, max_length)
        if code_split > max_length // 2:
            # Check if closing or opening
            prefix = remaining[:code_split]
            backtick_count = prefix.count("```")
            if backtick_count % 2 == 1:
                # Inside code block: close it for this chunk and reopen in next
                split_pos = code_split + 3

        # 2. Try splitting at paragraph / double newline
        if split_pos == -1:
            double_newline = remaining.rfind("\n\n", 0, max_length)
            if double_newline > max_length // 3:
                split_pos = double_newline + 2

        # 3. Try splitting at single newline
        if split_pos == -1:
            single_newline = remaining.rfind("\n", 0, max_length)
            if single_newline > max_length // 4:
                split_pos = single_newline + 1

        # 4. Try splitting at space
        if split_pos == -1:
            space = remaining.rfind(" ", 0, max_length)
            if space > max_length // 4:
                split_pos = space + 1

        # 5. Hard split if no good boundary found
        if split_pos == -1:
            split_pos = max_length

        chunk = remaining[:split_pos].rstrip()
        remaining = remaining[split_pos:].lstrip()

        # Handle unclosed code block formatting across chunks
        if chunk.count("```") % 2 != 0:
            chunk += "\n```"
            remaining = "```\n" + remaining

        chunks.append(chunk)

    if remaining:
        chunks.append(remaining)

    return chunks


def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2 while preserving code blocks.
    Special characters in MarkdownV2: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    # Characters that must be escaped outside code blocks
    special_chars = r"_*[]()~`>#+-=|{}.!"
    
    # Split text by code blocks (inline ` and multiline ```)
    parts = re.split(r"(```[\s\S]*?```|`[^`]*?`)", text)
    result = []
    
    for part in parts:
        if part.startswith("```") or (part.startswith("`") and part.endswith("`")):
            # Inside code block: minimal escaping required by Telegram
            result.append(part)
        else:
            # Outside code: escape special characters
            escaped = re.sub(r"([\\_*\[\]\(\)~>#+\-=|{}.!])", r"\\\1", part)
            result.append(escaped)

    return "".join(result)


async def send_smart_message(message: Message, text: str) -> List[Message]:
    """
    Safely send a message, splitting into chunks and falling back to plain text
    if Markdown parsing errors occur.
    """
    chunks = split_message(text)
    sent_messages = []

    for chunk in chunks:
        try:
            # First attempt: Markdown
            sent = await message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
            sent_messages.append(sent)
        except BadRequest as err:
            logger.warning(f"Markdown send failed ({err}), falling back to plain text")
            try:
                # Second attempt: Plain text fallback
                sent = await message.reply_text(chunk, parse_mode=None)
                sent_messages.append(sent)
            except Exception as e:
                logger.error(f"Failed to send plain text message chunk: {e}")
                raise

    return sent_messages
