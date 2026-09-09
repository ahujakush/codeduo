"""
Unit tests for Telegram Bot handlers and rate limiting.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Chat, Message
from bot.config import BotConfig
from bot.handlers.start_help import start_command, help_command, status_command
from bot.handlers.settings import clear_command, mode_command
from bot.handlers.problem_solver import solve_command, text_message_handler
from bot.ai.mock_solver import MockAISolver
from bot.utils.rate_limiter import UserRateLimiter


@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    user.first_name = "TestUser"
    chat = MagicMock(spec=Chat)
    chat.id = 9999

    message = MagicMock(spec=Message)
    message.reply_text = AsyncMock()
    message.text = "t1 = a + b"

    update.effective_user = user
    update.effective_chat = chat
    update.effective_message = message
    return update


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.bot_data = {"ai_solver": MockAISolver()}
    context.bot = MagicMock()
    context.bot.send_chat_action = AsyncMock()
    context.args = []
    return context


@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    await start_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called_once()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Namaste & Welcome" in call_args or "Welcome" in call_args
    assert "TestUser" in call_args


@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    await help_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called_once()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Bot Commands & Usage Guide" in call_args


@pytest.mark.asyncio
async def test_status_command(mock_update, mock_context):
    await status_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called_once()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Bot Status & Health" in call_args


@pytest.mark.asyncio
async def test_clear_command(mock_update, mock_context):
    await clear_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called_once()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Conversation context cleared" in call_args


@pytest.mark.asyncio
async def test_solve_command_without_args(mock_update, mock_context):
    mock_context.args = []
    await solve_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called_once()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Please provide a problem" in call_args


@pytest.mark.asyncio
async def test_solve_command_with_args(mock_update, mock_context):
    mock_context.args = ["t1", "=", "4", "*", "2"]
    await solve_command(mock_update, mock_context)
    mock_update.effective_message.reply_text.assert_called()
    call_args = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Optimized Intermediate Code" in call_args or "IR Analysis" in call_args


def test_rate_limiter():
    limiter = UserRateLimiter(max_requests=3, window_seconds=10.0)
    uid = 888
    assert limiter.is_rate_limited(uid) is False
    assert limiter.is_rate_limited(uid) is False
    assert limiter.is_rate_limited(uid) is False
    assert limiter.is_rate_limited(uid) is True


def test_allowed_users_authorization():
    cfg = BotConfig(allowed_user_ids={111, 222})
    assert cfg.is_user_allowed(111) is True
    assert cfg.is_user_allowed(222) is True
    assert cfg.is_user_allowed(333) is False

    cfg_open = BotConfig(allowed_user_ids=set())
    assert cfg_open.is_user_allowed(999) is True
