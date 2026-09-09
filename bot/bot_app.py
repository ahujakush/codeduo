"""
Telegram Bot Application initialization and handler wiring.
"""

import logging
from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.config import BotConfig, config
from bot.ai.factory import create_ai_solver
from bot.handlers.start_help import start_command, help_command, status_command
from bot.handlers.settings import mode_command, clear_command, button_callback_handler
from bot.handlers.problem_solver import solve_command, text_message_handler
from bot.handlers.photo_handler import photo_message_handler, document_image_handler

logger = logging.getLogger(__name__)


async def set_default_commands(application: Application) -> None:
    """Register command menu with Telegram."""
    commands = [
        BotCommand("start", "Start the bot & show welcome menu"),
        BotCommand("solve", "Solve a problem or equation: /solve <problem>"),
        BotCommand("mode", "Change AI persona/mode"),
        BotCommand("clear", "Reset conversation memory context"),
        BotCommand("status", "Check AI model and bot status"),
        BotCommand("help", "How to use the bot and tips"),
    ]
    try:
        await application.bot.set_my_commands(commands)
        logger.info("Default bot commands registered successfully with Telegram.")
    except Exception as err:
        logger.warning(f"Could not register commands with Telegram: {err}")


async def error_handler(update: object, context) -> None:
    """Global error handler for unhandled exceptions."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)


def create_bot_application(cfg: BotConfig = config) -> Application:
    """Create and configure the python-telegram-bot Application."""
    if not cfg.is_telegram_configured():
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not configured! Please provide a valid token from @BotFather in your .env file."
        )

    # Initialize AI Solver
    solver = create_ai_solver(cfg)

    # Build Application
    app = (
        ApplicationBuilder()
        .token(cfg.telegram_bot_token)
        .post_init(set_default_commands)
        .build()
    )

    # Store shared solver in bot_data
    app.bot_data["ai_solver"] = solver

    # Command Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler("status", CommandHandler("status", status_command))
    app.add_handler(CommandHandler("solve", solve_command))
    app.add_handler(CommandHandler("mode", mode_command))
    app.add_handler(CommandHandler("persona", mode_command))
    app.add_handler(CommandHandler("clear", clear_command))

    # Inline Keyboard Callbacks
    app.add_handler(CallbackQueryHandler(button_callback_handler))

    # Photo & Document Handlers
    app.add_handler(MessageHandler(filters.PHOTO, photo_message_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_image_handler))

    # Text Problem Solver Handler (must be last message handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    # Global Error Handler
    app.add_error_handler(error_handler)

    return app
