#!/usr/bin/env bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

echo "========================================================"
echo "🦉 Starting DuoSolve - AI Problem Solver Web App..."
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
if ! python3 -c "import fastapi, uvicorn, openai, httpx" 2>/dev/null; then
    echo "📥 Installing required dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

PORT="${WEB_PORT:-8000}"
HOST="${WEB_HOST:-0.0.0.0}"

echo "========================================================"
echo "🚀 Web Application is live at: http://localhost:${PORT}"
echo "🧠 AI Brain: Azure OpenAI (gpt-5.4-mini)"
echo "🔊 Voice Engine: ElevenLabs TTS"
echo "🎨 UI Design: Duolingo Feather System"
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================================"

# Run uvicorn web server
exec uvicorn web.app:app --host "${HOST}" --port "${PORT}" --reload
