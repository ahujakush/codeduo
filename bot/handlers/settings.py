"""
Settings and persona management handlers (/mode, /clear, inline button callbacks).
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from bot.config import config
from bot.memory.chat_memory import chat_memory
from bot.handlers.start_help import help_command, status_command

logger = logging.getLogger(__name__)

PERSONA_LABELS = {
    "solver": "🧠 Problem Solver (Step-by-Step)",
    "coder": "💻 Code & Debugger",
    "math": "📐 Math Specialist",
    "tutor": "🎓 Socratic Tutor",
    "concise": "⚡ Quick & Concise",
}


def get_persona_keyboard(current_persona: str) -> InlineKeyboardMarkup:
    """Generate inline buttons for selecting persona."""
    keyboard = []
    for key, label in PERSONA_LABELS.items():
        prefix = "✅ " if key == current_persona else ""
        keyboard.append([
            InlineKeyboardButton(f"{prefix}{label}", callback_data=f"set_persona_{key}")
        ])
    return InlineKeyboardMarkup(keyboard)


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /mode command to switch persona."""
    if not update.effective_message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    current_persona = chat_memory.get_persona(chat_id, default=config.default_persona)

    text = (
        "🎭 **Choose AI Persona / Mode**\n\n"
        f"Current active mode: **{PERSONA_LABELS.get(current_persona, current_persona)}**\n\n"
        "Select the mode that best fits your current problem:"
    )

    await update.effective_message.reply_text(
        text,
        reply_markup=get_persona_keyboard(current_persona),
        parse_mode=ParseMode.MARKDOWN,
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command to reset conversational memory."""
    if not update.effective_message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    chat_memory.clear_history(chat_id)

    await update.effective_message.reply_text(
        "🧹 **Conversation context cleared!**\n"
        "Your subsequent questions will be treated as fresh queries.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle interactive inline keyboard button clicks."""
    query = update.callback_query
    if not query or not update.effective_chat:
        return

    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    if data == "cmd_help":
        await help_command(update, context)
    elif data == "cmd_status":
        await status_command(update, context)
    elif data == "cmd_clear":
        chat_memory.clear_history(chat_id)
        await query.edit_message_text(
            "🧹 **Conversation memory cleared!** Ready for new questions.",
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data == "cmd_mode":
        current_persona = chat_memory.get_persona(chat_id, default=config.default_persona)
        await query.edit_message_text(
            "🎭 **Select AI Persona / Mode:**",
            reply_markup=get_persona_keyboard(current_persona),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif data.startswith("set_persona_"):
        new_persona = data.replace("set_persona_", "")
        if new_persona in PERSONA_LABELS:
            chat_memory.set_persona(chat_id, new_persona)
            await query.edit_message_text(
                f"✅ **Mode updated to**: {PERSONA_LABELS[new_persona]}\n\n"
                "Send me your problem or question!",
                parse_mode=ParseMode.MARKDOWN,
            )
