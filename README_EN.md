# Unity Game Global Compliance Platform v5.3

Helps Unity game developers ship compliant apps on **App Store + Google Play** across the US, EU, UK, and other major markets — and stay up to date as platform policies change.

[中文文档](README.md)

---

## Quick Start

```bash
# Install dependencies
pip3 install flask

# Start the web interface
python3 launcher.py --mode web
# Open http://localhost:8080 in your browser
```

---

## Two Core Modes

### Mode A · New Game Compliance Guide

Enter your game's basic info and receive a complete compliance roadmap:

- Applicable regulations analysis (GDPR / COPPA / CCPA / UK AADC)
- Phase-by-phase implementation checklist (Legal → Account → Privacy → IAP → Ads → Testing)
- App Store Connect and Google Play Console configuration guides
- Unity C# / iOS Swift / Android Kotlin technical implementation notes

### Mode B · Existing Game Compliance Audit

Scan your existing Unity project code and receive a detailed compliance report:

- Code-level issue location (file path + line number + fix suggestion)
- Regulatory compliance check (data collection, child protection, user rights)
- Platform policy check against 22 core rules
- Risk-graded report (critical / high / medium / low)

---

## Policy Management

Click **「📋 Policy Management」** in the top-right corner of the web UI. Four tabs are available:

| Tab | Function |
|-----|----------|
| 📊 Status | Freshness of all 22 policy rules; shows LLM-detected change alerts |
| ⚙️ Config | Set LLM API keys and remote rules update URL (hot-reload, no restart needed) |
| 🔍 Check | Trigger RSS + page-hash monitoring + LLM auto-analysis (runs in background) |
| ⏰ Schedule | Configure automatic scheduled checks; view notification history |

### Policy Change Detection Loop

The platform continuously tracks official policy sources and automatically updates rule status:

```
RSS / Page hash change detected
        ↓
LLM analyzes what changed and which rules are affected
        ↓
Affected rules automatically flagged as "needs review" in the Status tab
        ↓
Developer reviews the alert and clicks "Mark as Reviewed"
        ↓
Alert cleared, rule freshness restored
```

This loop runs automatically on schedule (configurable: hourly / daily / weekly).  
No LLM key? The system still detects page changes — you just won't get automatic rule tagging.

---

## LLM Configuration (Optional)

Configure in the **Config** tab, or create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx   # Recommended (Claude)
OPENAI_API_KEY=sk-xxx          # Alternative (GPT-4o)
```

Changes take effect immediately — no server restart required.

---

## Rules Hot-Reload

The platform supports updating compliance rules without restarting:

- **Local mode**: Edit `config/compliance-rules.yaml` — the system detects file changes and reloads automatically
- **Remote mode**: Set `RULES_UPDATE_URL` in the Config tab to a remote YAML URL; the system fetches and applies updates automatically

---

## CLI Usage

```bash
# New game compliance guide
python3 launcher.py --mode guide

# Existing project audit
python3 launcher.py --mode audit --path /your/unity/project

# Policy monitoring
python3 launcher.py --mode check-policies --rss
python3 launcher.py --mode check-policies --watch

# Web server only
python3 launcher.py --mode web
```

---

## API Reference

The platform exposes a REST API on port 8080 (default):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Server health and rules version |
| POST | `/api/v1/guide/new-game` | Generate compliance guide for a new game |
| POST | `/api/v1/audit/game` | Audit an existing game project |
| GET | `/api/v1/policies/freshness` | Get freshness report for all 22 rules |
| POST | `/api/v1/policies/run-check` | Trigger policy check (async, returns `job_id`) |
| GET | `/api/v1/policies/check-status/<job_id>` | Poll async check result |
| POST | `/api/v1/policies/mark-verified` | Mark a rule as reviewed (clears alert) |
| GET/POST | `/api/v1/rules/update` | Check or trigger rules hot-reload |
| GET/POST | `/api/v1/policies/scheduler` | Get or configure scheduled check |
| GET | `/api/v1/notifications` | Get notification list and unread count |
| POST | `/api/v1/notifications/read` | Mark notifications as read |
| POST | `/api/v1/policies/save-config` | Save LLM keys / rules URL to `.env` |

---

## Project Structure

```
launcher.py                      Main entry point
api/compliance_api.py            Flask API server
web_interface.html               Web UI (single-file)
engines/
  ├── dev_guide.py               New game compliance roadmap
  ├── unified_audit.py           Comprehensive game audit
  ├── code_scanner.py            Static code analysis
  ├── code_template_generator.py Compliance code templates
  ├── advanced_rule_engine.py    Core compliance rule engine
  ├── policy_monitor.py          RSS + page-hash monitoring
  └── policy_diff_analyzer.py   LLM-powered policy diff analysis
config/
  └── compliance-rules.yaml     Rule definitions (hot-reloadable)
references/                      Policy knowledge base
policy_versions.json             22 rule version tracking (with change alerts)
.env                             API keys (create manually, not committed)
```

---

## Coverage

**Regulations**: GDPR · COPPA · CCPA · UK AADC

**Platforms**: App Store (Apple) · Google Play (Google)

**Markets**: United States · European Union · United Kingdom · Canada · Australia

**Tech stacks**: Unity C# · iOS Swift · Android Kotlin

---

## Requirements

- Python 3.8+
- Flask (`pip3 install flask`)
- Optional: `anthropic` or `openai` package for LLM features
- Optional: `python-dotenv` for `.env` file support

```bash
pip3 install -r requirements.txt
```

---

## License

MIT License — see [LICENSE](LICENSE)
