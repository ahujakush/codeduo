"""
Text Problem Solving Handler.
Processes incoming text problems, questions, and /solve commands.
"""

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


async def solve_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle explicit /solve command (e.g. /solve Find the derivative of sin(x)*e^x)."""
    if not update.effective_message:
        return

    # Check if arguments were provided
    if not context.args:
        await update.effective_message.reply_text(
            "❓ **Please provide a problem after /solve**\n\n"
            "Example:\n"
            "• `/solve 3x + 12 = 30`\n"
            "• `/solve How do I reverse a linked list in Python?`\n"
            "• Or simply send your problem as a regular message!",
            parse_mode="Markdown",
        )
        return

    prompt = " ".join(context.args)
    await _process_and_solve_text(update, context, prompt)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ordinary text messages as problem-solving inputs."""
    if not update.effective_message or not update.effective_message.text:
        return

    prompt = update.effective_message.text.strip()
    # Ignore slash commands handled elsewhere
    if prompt.startswith("/"):
        return

    await _process_and_solve_text(update, context, prompt)


async def _process_and_solve_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str
) -> None:
    """Core logic to invoke AI solver, manage history, and reply."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not user or not chat or not message:
        return

    # 1. Authorization check
    if not config.is_user_allowed(user.id):
        await message.reply_text("⛔ You are not authorized to use this bot.")
        return

    # 2. Rate limiting check
    if rate_limiter.is_rate_limited(user.id):
        await message.reply_text(
            "⏳ **Too many requests!** Please wait a moment before sending another problem.",
            parse_mode="Markdown",
        )
        return

    # 3. Send typing indicator
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # 4. Retrieve solver and context
    solver: BaseAISolver = context.bot_data.get("ai_solver")
    if not solver:
        await message.reply_text("❌ AI Solver is not initialized. Please contact admin.")
        return

    persona = chat_memory.get_persona(chat.id, default=config.default_persona)
    history = chat_memory.get_history(chat.id)

    # 5. Generate AI solution
    try:
        solution = await solver.solve_text(prompt=prompt, history=history, persona=persona)
    except Exception as err:
        logger.error(f"Error during AI solving: {err}", exc_info=True)
        solution = f"❌ An unexpected error occurred while solving: {err}"

    # 6. Update memory with turn
    chat_memory.add_message(chat.id, role="user", content=prompt)
    chat_memory.add_message(chat.id, role="assistant", content=solution)

    # 7. Deliver solution safely to Telegram
    await send_smart_message(message, solution)
