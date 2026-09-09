#!/usr/bin/env bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

echo "========================================================"
echo "🚀 Starting AI Problem-Solving Telegram Bot..."
echo "========================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python3 -c "import telegram, google.genai" 2>/dev/null; then
    echo "📥 Installing required dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

# Run the bot
python3 main.py
