# 🦉 DuoSolve - AI Problem Solver (Duolingo Design Edition)

> **An interactive, gamified AI Problem-Solving Web Application inspired by the [Duolingo Design System](https://blog.duolingo.com/hub/design/). Powered by Azure OpenAI Brain (`gpt-5.4-mini`), ElevenLabs Voice Narration (Bella), Google Gemini Vision, and local SymPy math.**

---

## 🌟 Key Features

- 🎨 **Duolingo "Feather" Design System**:
  - **Tactile 3D Buttons**: Signature pill and rounded-2xl buttons with 4px drop-shadows and springy `:active` transitions.
  - **Animated Mascot (Duo)**: Interactive vector owl with dynamic mood expressions (welcoming, thinking, speaking, and victory celebration).
  - **Gamification Suite**: Top navigation with Streak 🔥 days, Gems 💎, Hearts ❤️, and XP ⚡ counters.
  - **Audio Effects**: Authentic synthesized chimes, button pops, and victory fanfares via the Web Audio API.
- 🧠 **Azure OpenAI Brain**:
  - Primary reasoning engine powered by Azure OpenAI (`gpt-5.4-mini` / `gpt-4o-mini`) using credentials imported from your GTM plan.
  - Generates clear, step-by-step solutions with concepts, derivations, code blocks, and final answers.
- 🔊 **ElevenLabs Voice Narration**:
  - Click **"🔊 Listen with ElevenLabs"** on any solution to hear natural, high-fidelity speech (Bella voice, `eleven_turbo_v2_5`).
  - Integrated speech sanitizer translates mathematical equations (e.g. `\(3x + 15 = 45\)`) and code into natural spoken English.
  - Sound wave animations display in real time while audio is playing.
- 📸 **Photo & Homework Solver**:
  - Drag and drop or browse photos/screenshots of textbook questions, handwritten math, diagrams, or programming errors.
- 📐 **Math & Code Rendering**:
  - KaTeX typesetting for math formulas.
  - Syntax-highlighted code blocks with 1-click **Copy Code** button.

---

## 🚀 Quick Start

### 1. Launch the Web Application
```bash
./run.sh
```
Or manually:
```bash
source .venv/bin/activate
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open in Browser
Visit: **[http://localhost:8000](http://localhost:8000)**

---

## 🔑 Environment Configuration

Keys have been automatically imported from `/Users/kushahuja/build your company/gtm/.env.local`:

```ini
# Primary AI Provider
AI_PROVIDER=azure

# Azure OpenAI Brain (gpt-5.4-mini)
AZURE_OPENAI_API_KEY=5MnRvnsmC7RzcP0L72S30q2mEh6CfIGRM514pPb4abzkNc0cxslyJQQJ99CDACHYHv6XJ3w3AAAAACOGhzib
AZURE_OPENAI_ENDPOINT=https://mirofish-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.4-mini

# ElevenLabs Voice Narration
ELEVENLABS_API_KEY=sk_cc5fafc59759de1efa0e91a9c4e048a7ea1cea8d6d4354d0
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL
ELEVENLABS_MODEL_ID=eleven_turbo_v2_5

# Fallback Vision & Models
GEMINI_API_KEY=AIzaSyBScNxbKZ7UpxsFDF7uGvlkjiFx8j12M5s
OPENAI_API_KEY=sk-proj-WiM8...
```

---

## 🧪 Testing

Run the automated test suite (32 unit & API tests):
```bash
source .venv/bin/activate && pytest -v tests/
```

Test problem solving directly in terminal:
```bash
python3 test_cli.py --test-query "Solve 3x + 15 = 45"
```

---

## 📁 Project Structure

```
emmad_project/
├── web/
│   ├── app.py                 # FastAPI server & REST endpoints (/api/solve, /api/tts, etc.)
│   ├── config.py              # Configuration & GTM environment variable loader
│   ├── services/
│   │   ├── azure_solver.py    # Azure OpenAI gpt-5.4-mini brain integration
│   │   └── elevenlabs_service.py # ElevenLabs TTS & text-to-speech sanitizer
│   └── static/
│       ├── index.html         # Duolingo Feather UI frontend layout
│       ├── css/style.css      # Duolingo 3D buttons, cards, animations & color palette
│       └── js/app.js          # Web Audio synth, mascot emotions, audio player, KaTeX
├── bot/                       # Core AI solvers, sympy fallback, and memory manager
├── tests/                     # 32 automated unit and API integration tests
├── test_cli.py                # Terminal interactive simulation runner
├── run.sh                     # Launch script (starts web server at http://localhost:8000)
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation
```
