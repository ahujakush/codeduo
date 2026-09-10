
---

## 📁 Project Structure

```
emmad_project/
├── web/
│   ├── app.py                 # FastAPI server & REST endpoints (/api/solve, /api/tts, etc.)
│   ├── config.py              # Configuration & GTM environment variable loader
│   ├── services/
│   │   ├── azure_solver.py    # Azure OpenAI gpt-5.4-mini brain integration
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
