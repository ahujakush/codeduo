"""
Telegram bot handlers for /start, /help, /status commands and interactive welcome keyboards.
"""

import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import ContextTypes
from bot.config import config
from bot.memory.chat_memory import chat_memory
from bot.ai.base import BaseAISolver

BOT_START_TIME = time.time()


def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """Generate inline buttons for easy navigation."""
    keyboard = [
        [
            InlineKeyboardButton("🎭 Switch Mode", callback_data="cmd_mode"),
            InlineKeyboardButton("📊 Bot Status", callback_data="cmd_status"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help & Commands", callback_data="cmd_help"),
            InlineKeyboardButton("🧹 Clear History", callback_data="cmd_clear"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not update.effective_user or not update.effective_message:
        return

    user_id = update.effective_user.id
    if not config.is_user_allowed(user_id):
        await update.effective_message.reply_text("⛔ You are not authorized to use this bot.")
        return

    first_name = update.effective_user.first_name or "Friend"
    solver: BaseAISolver = context.bot_data.get("ai_solver")
    provider_name = solver.get_provider_name() if solver else "AI Solver"

    welcome_text = (
        f"👋 **Namaste & Welcome, {first_name}!**\n\n"
        f"I am your **AI Problem-Solving Assistant** powered by `{provider_name}`.\n\n"
        f"🎯 **What I can do for you:**\n"
        f"• 📐 **Math & Equations**: Step-by-step calculus, algebra, and physics.\n"
        f"• 💻 **Code & Debugging**: Write, fix, explain, and optimize code in any language.\n"
        f"• 🧠 **Logic & Reasoning**: Puzzles, complex reasoning, and structured solutions.\n"
        f"• 📸 **Photo Problem Solving**: Send a photo of a textbook, question, or diagram!\n"
        f"• 💬 **Multi-Turn Chat**: I remember your context within the conversation.\n\n"
        f"👉 **How to use me:**\n"
        f"Just type any problem or question directly, or send a photo of the problem!\n\n"
        f"Use the buttons below to customize your experience:"
    )

    await update.effective_message.reply_text(
        welcome_text,
        reply_markup=get_welcome_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.effective_message:
        return

    help_text = (
        "📖 **Bot Commands & Usage Guide**\n\n"
        "**Available Commands:**\n"
        "• `/start` - Start the bot and show welcome menu\n"
        "• `/help` - Show this help guide\n"
        "• `/solve <problem>` - Explicitly solve a problem (or just send text!)\n"
        "• `/mode` - Change AI persona (Solver, Coder, Math, Tutor, Concise)\n"
        "• `/clear` - Reset conversation memory context\n"
        "• `/status` - View bot health, active AI model, and uptime\n\n"
        "📸 **Photo Solving:**\n"
        "Take a photo or screenshot of any problem (math, question paper, code error) "
        "and send it to this chat with or without a caption!\n\n"
        "💡 **Tips for best results:**\n"
        "1. For math: State variables clearly (e.g. `Solve 3x^2 - 5x + 2 = 0`).\n"
        "2. For code: Mention language and error message.\n"
        "3. Use `/mode` to get the specialized persona for your task."
    )

    await update.effective_message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_welcome_keyboard(),
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    if not update.effective_message or not update.effective_chat:
        return

    chat_id = update.effective_chat.id
    solver: BaseAISolver = context.bot_data.get("ai_solver")
    provider = solver.get_provider_name() if solver else "Unknown"
    model = solver.get_model_name() if solver else "Unknown"
    current_persona = chat_memory.get_persona(chat_id, default=config.default_persona)

    stats = chat_memory.get_stats()
    history = chat_memory.get_history(chat_id)
    uptime_sec = int(time.time() - BOT_START_TIME)
    uptime_mins = uptime_sec // 60
    uptime_hours = uptime_mins // 60

    status_text = (
        "📊 **Bot Status & Health**\n\n"
        f"• **AI Provider**: `{provider}`\n"
        f"• **Active Model**: `{model}`\n"
        f"• **Current Chat Mode**: `{current_persona}`\n"
        f"• **Current Chat Memory**: `{len(history)} messages`\n"
        f"• **Total Active Sessions**: `{stats['active_chats']}`\n"
        f"• **Uptime**: `{uptime_hours}h {uptime_mins % 60}m {uptime_sec % 60}s`\n"
        f"• **System Status**: 🟢 Operational"
    )

    await update.effective_message.reply_text(
        status_text,
        parse_mode=ParseMode.MARKDOWN,
    )
