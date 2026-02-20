# APEX Organism v0.1

A living digital organism that orchestrates multiple AI services, learns autonomously, and stores all knowledge permanently.

## Architecture

```
apex_organism/
├── apex_main.py          # Entry point (CLI + Dashboard)
├── config.yaml           # Configuration (API keys, Oracle DB, settings)
├── requirements.txt      # Python dependencies
├── core/
│   ├── apex_core.py      # Central orchestrator
│   ├── oracle_sync.py    # Oracle DB + SQLite fallback memory
│   ├── mcp_client.py     # Multi-AI connection layer (6 AI organs)
│   ├── natural_language.py  # NL command processor
│   ├── evolution_engine.py  # Autonomous capability acquisition
│   ├── swarm_orchestrator.py  # Parallel agent deployment
│   └── money_gate.py     # Cost approval system
├── dashboard/
│   └── api_server.py     # FastAPI web dashboard
├── plugins/              # Learned capabilities stored here
├── scripts/
│   └── deploy_oracle.sh  # One-click Oracle Cloud deployment
└── tests/
    └── test_basic.py     # Unit tests
```

## Quick Start

### Local (CLI mode)
```bash
pip install -r requirements.txt
python apex_main.py
```

### Local (Dashboard mode)
```bash
python apex_main.py --dashboard
# Open http://localhost:8080
```

### Android One-Tap (Termux)
```bash
# Install Termux, clone this repo, then run:
bash scripts/android_oneclick.sh
# The dashboard auto-opens at http://127.0.0.1:8080; add it to your home screen.
```

### Oracle Cloud Deployment
```bash
bash scripts/deploy_oracle.sh
```

## Configuration

`config.yaml` is created automatically from `config.yaml.example` on first run. Edit it to:
- Connect to Oracle Database (or use SQLite fallback)
- Enable AI organs (Perplexity, DeepSeek, Gemini, MiniMax, Kimi)
- Set spending limits via Money Gate
- Configure swarm agent limits

## Features

- **6 AI Organs**: Connect to Perplexity, DeepSeek, Gemini, MiniMax, Kimi, or any OpenAI-compatible API
- **Oracle Memory**: Permanent knowledge storage (with SQLite fallback)
- **Evolution Engine**: Teaches itself new capabilities on-demand
- **Swarm Mode**: Deploy 1-20 parallel agents for massive speedup
- **Money Gate**: All paid operations require approval above threshold
- **Web Dashboard**: Real-time monitoring and control via browser
- **Natural Language**: Just speak naturally, APEX figures it out
