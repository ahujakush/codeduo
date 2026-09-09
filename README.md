# 🤖 AI-Powered Problem-Solving Telegram Bot

> **A feature-packed, production-ready AI Assistant for Telegram that solves mathematical equations, writes & debugs code, explains complex topics step-by-step, and analyzes photos/diagrams of homework or errors.**

---

## 🌟 Features

- 🧠 **Smart Problem Solving**: Solves math, physics, coding, logic puzzles, and general questions with clean, step-by-step reasoning.
- 📸 **Photo & Vision Problem Solving**: Send a photo of a textbook question, handwritten math equation, or error screenshot — the AI inspects the image and solves it.
- 💬 **Multi-Turn Conversation Memory**: Remembers previous questions and context per chat. Use `/clear` to reset memory anytime.
- 🎭 **5 Specialized Personas / Modes** (switchable via `/mode`):
  - 🧠 **Problem Solver**: Structured step-by-step analytical reasoning.
  - 💻 **Code & Debugger**: Writes optimized code, finds bugs, explains time/space complexity.
  - 📐 **Math Specialist**: Rigorous derivations, formulas, and verification.
  - 🎓 **Socratic Tutor**: Intuitive, easy-to-understand explanations with examples.
  - ⚡ **Quick & Concise**: Direct answers without filler.
- 🌐 **Multi-AI Engine Support**:
  - **Google Gemini** (`gemini-2.5-flash`, `gemini-1.5-flash`) via the modern `google-genai` SDK.
  - **OpenAI** (`gpt-4o-mini`, `gpt-4o`).
  - **Groq** (`llama-3.3-70b-versatile`) for ultra-fast responses.
  - **Local/Mock Solver**: Built-in SymPy math solver that runs offline even without API keys!
- 🛡️ **Production-Grade Resilience**:
  - Automatic splitting of long messages exceeding Telegram's 4,096-character limit.
  - Resilient Markdown formatting with automatic plain-text fallback.
  - Built-in per-user rate limiting to prevent spam.
  - Optional access control (`ALLOWED_USER_IDS`).

---

## 🚀 Quick Start Guide (English)

### 1. Clone & Setup Environment
```bash
# Clone the repository and navigate into the folder
cd emmad_project

# Run the automated setup script
./run.sh
```
Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Get Telegram Bot Token from @BotFather

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Click **Start** and send:
   ```text
   /newbot
   ```
3. BotFather will ask for a **Name** (e.g. `Emmad AI Solver`).
4. BotFather will ask for a **Username** (must end in `_bot`, e.g. `emmad_ai_solver_bot`).
5. BotFather will give you an **HTTP API Token**, which looks like:
   ```text
   7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ1234567
   ```
6. *(Optional)* Configure Bot Commands in BotFather:
   Send `/setcommands` to BotFather, select your bot, and paste:
   ```text
   start - Start the bot and show welcome menu
   solve - Solve a problem or equation
   mode - Switch AI persona / mode
   clear - Reset conversation history
   status - Check bot health & active AI model
   help - Guide and usage tips
   ```

---

### 3. Configure API Keys in `.env`

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set your keys:
```ini
# Telegram Token from @BotFather
TELEGRAM_BOT_TOKEN=7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ1234567

# Preferred AI: "gemini", "openai", "groq", or "mock"
AI_PROVIDER=gemini

# Google Gemini API Key (Free: https://aistudio.google.com/)
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
GEMINI_MODEL=gemini-2.5-flash

# (Optional) OpenAI API Key
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

### 4. Run the Bot

```bash
python3 main.py
```
Or:
```bash
./run.sh
```

Now open Telegram, find your bot username, and send `/start`!

---

## 🇮🇳 हिंदी / Hinglish Setup Guide (BotFather se Telegram Setup)

अगर आप पहली बार Telegram Bot बना रहे हैं, तो यह आसान स्टेप्स फॉलो करें:

### स्टेप 1: BotFather से Token लेना
1. Telegram ऐप खोलें और सर्च बार में लिखें: **`@BotFather`** (ब्लू टिक वाला ऑफिशियल बॉट)।
2. **Start** बटन दबाएं।
3. यह मैसेज भेजें:
   ```text
   /newbot
   ```
4. अपने बॉट का नाम रखें (जैसे: `My AI Solver`).
5. अपने बॉट का यूज़रनेम रखें जो `_bot` पर खत्म हो (जैसे: `my_problem_solver_bot`).
6. BotFather आपको एक **API Token** देगा (उदा. `123456789:AAHk...`). इस टोकन को कॉपी कर लें।

### स्टेप 2: टोकन को प्रोजेक्ट में डालना
1. प्रोजेक्ट फोल्डर में `.env` फाइल खोलें।
2. `TELEGRAM_BOT_TOKEN` के आगे अपना टोकन पेस्ट कर दें:
   ```ini
   TELEGRAM_BOT_TOKEN=123456789:AAHk...apna_token_yahan
   ```
3. [Google AI Studio](https://aistudio.google.com/) से फ्री **Gemini API Key** लेकर `GEMINI_API_KEY` में डालें।

### स्टेप 3: बॉट स्टार्ट करें
टर्मिनल में रन करें:
```bash
./run.sh
```
या
```bash
python3 main.py
```
अब अपने Telegram में बॉट खोलें और `/start` भेजें! 🎉

---

## 🧪 Testing in Terminal (Without Telegram)

You can test and chat with the AI Problem Solver directly in your terminal without Telegram:

```bash
# Solve a single math problem directly
python3 test_cli.py --test-query "Solve 3x + 15 = 45"

# Ask a coding question
python3 test_cli.py --test-query "Write a Python script to reverse a linked list"

# Interactive terminal chat
python3 test_cli.py
```

Run the automated test suite:
```bash
pytest -v tests/
```

---

## 📁 Project Structure

```
emmad_project/
├── bot/
│   ├── config.py              # Loads .env, validates tokens & permissions
│   ├── bot_app.py             # Telegram Application & handler registrations
│   ├── handlers/
│   │   ├── start_help.py      # /start, /help, /status & interactive menus
│   │   ├── problem_solver.py  # Problem solving text message handler & /solve
│   │   ├── photo_handler.py   # Photo/document image problem solving handler
│   │   └── settings.py        # /mode persona switcher & /clear memory
│   ├── ai/
│   │   ├── base.py            # AISolver interface & persona prompts
│   │   ├── gemini_solver.py   # Google Gemini 2.5 Flash / 1.5 Pro integration
│   │   ├── openai_solver.py   # OpenAI & Groq API integration
│   │   ├── mock_solver.py     # Local offline SymPy equation solver
│   │   └── factory.py         # AI provider selection & fallback logic
│   ├── memory/
│   │   └── chat_memory.py     # Sliding window conversation memory per chat
│   └── utils/
│       ├── telegram_format.py # Safe message splitting & Markdown escaping
│       └── rate_limiter.py    # Per-user flood prevention rate limiter
├── tests/                     # Comprehensive test suite (25 tests passing)
├── test_cli.py                # Terminal interactive simulation tool
├── main.py                    # Production entrypoint
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container image
├── docker-compose.yml         # Container orchestration
├── run.sh                     # Launch script
└── README.md                  # Documentation
```

---

## 🐳 Docker Deployment

Run 24/7 on any cloud server or VPS using Docker Compose:

```bash
# Build and run in background
docker-compose up -d --build

# View real-time logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

---

## 📜 License
MIT License. Built with ❤️ for seamless problem solving on Telegram!
