# Game Development AI Workshop

An AI-powered workshop covering the full game development lifecycle. 7 specialized roles driven by real LLM calls — each role delivers analysis tailored to your specific game, not generic templates.

---

## Roles

| Role | Responsibility | Key Output |
|------|---------------|------------|
| 🏗️ Unity Architect | Tech stack selection & system design | Framework, render pipeline, network, performance budget |
| 🗺️ System Designer | Gameplay skeleton | Core loops, MDA analysis, system interaction map |
| 📊 Numerical Designer | Numerical systems modeling | Combat formulas, growth curves, economy model, Gacha odds |
| 📖 Level & Narrative Designer | Level and story design | Narrative structure, level sequence, difficulty curve, tutorial |
| ⚙️ Implementation Wizard | Code scaffolding | Project structure, C# interfaces, DI setup, coding standards |
| 🧪 QA Engineer | Quality assurance | Test plans, platform-specific cases, bug matrix, release checklist |
| 📈 Data Analyst | Data-driven iteration | KPI system, event tracking, retention/monetization analysis, A/B tests |

---

## Quick Start

**Step 1: Install dependencies**

```bash
pip install anthropic        # Claude API (recommended)
# or
pip install openai           # OpenAI API
```

**Step 2: Configure API Key**

```bash
cp .env.example .env
# Edit .env and fill in:
# ANTHROPIC_API_KEY=sk-ant-your-key
```

**Step 3: Launch**

```bash
python launcher.py --mode web
# Open http://localhost:8080 in your browser
```

---

## How It Works

```
Fill in game description (name / type / platform / features)
        ↓
Choose a role → Submit
        ↓
LLM analyzes from that role's professional perspective
        ↓
Streaming Markdown output (typewriter effect)
        ↓
Copy result → Team discussion → Next role
```

Each role has a dedicated system prompt encoding domain-specific decision frameworks, industry benchmarks, and judgment criteria — not generic AI, but a customized professional role.

---

## Two Ways to Use

### Web Workshop (this project)

Best for: complete reports, team sharing, formal documentation

```bash
python launcher.py --mode web
```

### Cursor Agent Skills

Best for: real-time discussion during development, follow-up questions, letting AI write code directly

7 Agent Skills installed in `~/.agents/skills/`, auto-activated in Cursor conversations:

```
unity-architect            → Tech stack selection
game-system-designer       → Gameplay systems
game-numerical-designer    → Numerical design
game-level-narrative-designer → Level & narrative
unity-implementation-wizard → Code scaffolding
game-qa-engineer           → QA & testing
game-data-analyst          → Data & analytics
```

---

## Web Workshop vs Agent Skills

| | Web Workshop | Agent Skills |
|--|-------------|-------------|
| **Best for** | Formal deliverables, team sharing | Real-time help during development |
| **Output** | Complete structured report (Markdown) | Conversational, supports follow-up |
| **Code access** | Cannot read/write files | Can read code, generate files, edit implementation |
| **Context** | Fresh start each time | Full conversation history, continuous iteration |
| **Audience** | Product, design, PM | Developer themselves |

### Recommended Workflow

```
Project kickoff
  └─ Web Workshop: Unity Architect → Full tech selection report (for the team)

Development
  └─ Agent Skills: Unity Architect / Implementation Wizard
       → Ask questions while coding, let AI generate interfaces and modify code

Testing
  └─ Web Workshop: QA Engineer → Formal test plan document
  └─ Agent Skills: QA Engineer → Generate unit tests for specific code, find edge cases

Post-launch
  └─ Web Workshop: Data Analyst → KPI system and event tracking plan
  └─ Agent Skills: Data Analyst → Discuss retention drops with real data, adjust strategy
```

Both share the same role knowledge base. Web Workshop is for **producing documents**; Agent Skills is for **getting things done**.

---

## Project Structure

```
launcher.py                   Entry point
api/compliance_api.py         Flask API (with 7 streaming AI endpoints)
web_interface.html            Web UI (single file)
engines/
  ├── llm_client.py           Unified LLM client (Claude / OpenAI)
  ├── system_prompts.py       System prompts for all 7 roles
  ├── unity_architect_expert.py
  ├── system_designer_expert.py
  ├── numerical_designer_expert.py
  ├── level_narrative_designer_expert.py
  ├── implementation_wizard_expert.py
  ├── qa_engineer_expert.py
  └── data_analyst_expert.py
.env.example                  Configuration template
```

---

## AI Endpoints

Server runs at `http://localhost:8080`:

| Method | Path | Role |
|--------|------|------|
| POST | `/api/v1/ai/architect` | Unity Architect |
| POST | `/api/v1/ai/system-designer` | System Designer |
| POST | `/api/v1/ai/numerical-designer` | Numerical Designer |
| POST | `/api/v1/ai/level-narrative` | Level & Narrative Designer |
| POST | `/api/v1/ai/impl-wizard` | Implementation Wizard |
| POST | `/api/v1/ai/qa-engineer` | QA Engineer |
| POST | `/api/v1/ai/data-analyst` | Data Analyst |

All endpoints accept `{"game_profile": {...}}` JSON and return `text/event-stream` SSE.

**Example request:**

```bash
curl -X POST http://localhost:8080/api/v1/ai/architect \
  -H "Content-Type: application/json" \
  -d '{
    "game_profile": {
      "game_name": "My RPG",
      "game_type": "rpg",
      "target_platforms": ["mobile"],
      "features": ["multiplayer", "iap", "gacha"],
      "team_size": "small"
    }
  }'
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `anthropic` or `openai` | `anthropic` |
| `ANTHROPIC_API_KEY` | Claude API Key | — |
| `OPENAI_API_KEY` | OpenAI API Key | — |
| `LLM_MODEL` | Model name | `claude-sonnet-4-5` / `gpt-4o` |
| `LLM_MAX_TOKENS` | Max output tokens | `4096` |

Without an API Key, the system won't crash — it displays a setup guide in the output area instead.

---

## Requirements

- Python 3.8+
- `flask` `flask-cors` `flask-limiter`
- `anthropic>=0.30.0` or `openai>=1.30.0`

```bash
pip install -r requirements.txt
```
