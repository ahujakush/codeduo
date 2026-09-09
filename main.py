"""
Main entry point for running the AI Problem-Solving Telegram Bot.
"""

import sys
import logging
from bot.config import config
from bot.bot_app import create_bot_application

# Configure logging
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("telegram_ai_bot")


def show_setup_help():
    """Print helpful instructions when token is not yet configured."""
    print("=" * 70)
    print("❌ TELEGRAM_BOT_TOKEN is missing or not configured in .env!")
    print("=" * 70)
    print("\n👉 How to set up your Telegram Bot with BotFather:")
    print("1. Open Telegram on your phone or computer.")
    print("2. Search for '@BotFather' and click 'Start'.")
    print("3. Send the command: /newbot")
    print("4. Give your bot a Name (e.g., 'Emmad AI Solver')")
    print("5. Give your bot a Username ending in '_bot' (e.g., 'emmad_solver_bot')")
    print("6. BotFather will provide an API token that looks like:")
    print("   1234567890:ABCdefGHIjklMNOpqrSTUvwxyz1234567")
    print("\n👉 Next steps:")
    print("7. Open '.env' in this folder and replace:")
    print("   TELEGRAM_BOT_TOKEN=your_token_from_botfather_here")
    print("8. (Optional) Add your GEMINI_API_KEY from https://aistudio.google.com")
    print("9. Run this script again: python main.py")
    print("=" * 70 + "\n")


def main():
    """Start the Telegram bot."""
    if not config.is_telegram_configured():
        show_setup_help()
        sys.exit(1)

    logger.info("Initializing Telegram AI Problem-Solving Bot...")
    try:
        app = create_bot_application(config)
        logger.info("Bot application successfully built. Starting polling...")
        print("\n" + "=" * 60)
        print("🤖 AI Problem Solver Bot is now RUNNING!")
        print("📱 Open Telegram, find your bot, and send /start")
        print("🛑 Press Ctrl+C to stop the bot")
        print("=" * 60 + "\n")
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt).")
    except Exception as err:
        logger.critical(f"Fatal error running bot: {err}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
