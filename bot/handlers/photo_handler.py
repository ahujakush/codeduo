"""
Photo and Document Problem Solving Handler.
Processes images of equations, textbook questions, screenshots, and diagrams.
"""

import io
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from bot.config import config
from bot.memory.chat_memory import chat_memory
from bot.ai.base import BaseAISolver
from bot.utils.rate_limiter import rate_limiter
from bot.utils.telegram_format import send_smart_message

logger = logging.getLogger(__name__)


async def photo_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photos (compressed images)."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message or not message.photo:
        return

    # 1. Authorization & rate limiting
    if not config.is_user_allowed(user.id):
        await message.reply_text("⛔ You are not authorized to use this bot.")
        return

    if rate_limiter.is_rate_limited(user.id):
        await message.reply_text(
            "⏳ **Too many requests!** Please wait a moment before sending another image.",
            parse_mode="Markdown",
        )
        return

    # 2. Typing indicator
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # 3. Get the highest resolution photo
    photo = message.photo[-1]
    caption = message.caption or ""

    solver: BaseAISolver = context.bot_data.get("ai_solver")
    if not solver:
        await message.reply_text("❌ AI Solver is not initialized.")
        return

    persona = chat_memory.get_persona(chat.id, default=config.default_persona)

    # 4. Download photo from Telegram servers
    try:
        tg_file = await context.bot.get_file(photo.file_id)
        image_buffer = io.BytesIO()
        await tg_file.download_to_memory(out=image_buffer)
        image_bytes = image_buffer.getvalue()
    except Exception as err:
        logger.error(f"Failed to download photo from Telegram: {err}", exc_info=True)
        await message.reply_text(f"❌ Failed to download photo: {err}")
        return

    # 5. Let AI solve the image
    try:
        solution = await solver.solve_image(
            image_bytes=image_bytes,
            mime_type="image/jpeg",
            caption=caption,
            persona=persona,
        )
    except Exception as err:
        logger.error(f"Error during image AI solving: {err}", exc_info=True)
        solution = f"❌ An error occurred while analyzing the image: {err}"

    # 6. Deliver solution safely
    await send_smart_message(message, solution)


async def document_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uncompressed image documents (PNG, JPG sent as file)."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message or not message.document:
        return

    doc = message.document
    mime = doc.mime_type or ""

    if not (mime.startswith("image/") or doc.file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))):
        return  # Ignore non-image documents

    if not config.is_user_allowed(user.id):
        await message.reply_text("⛔ You are not authorized to use this bot.")
        return

    if rate_limiter.is_rate_limited(user.id):
        await message.reply_text("⏳ **Rate limit exceeded.** Please wait a moment.")
        return

    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    solver: BaseAISolver = context.bot_data.get("ai_solver")
    if not solver:
        await message.reply_text("❌ AI Solver is not initialized.")
        return

    persona = chat_memory.get_persona(chat.id, default=config.default_persona)
    caption = message.caption or ""

    try:
        tg_file = await context.bot.get_file(doc.file_id)
        buffer = io.BytesIO()
        await tg_file.download_to_memory(out=buffer)
        image_bytes = buffer.getvalue()

        solution = await solver.solve_image(
            image_bytes=image_bytes,
            mime_type=mime if mime.startswith("image/") else "image/jpeg",
            caption=caption,
            persona=persona,
        )
    except Exception as err:
        logger.error(f"Error analyzing document image: {err}", exc_info=True)
        solution = f"❌ Failed to process document image: {err}"

    await send_smart_message(message, solution)
