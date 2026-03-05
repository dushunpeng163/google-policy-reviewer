# Web Interface Guide

[中文指南](WEB_GUIDE.md)

## Starting the Server

```bash
python3 launcher.py --mode web
# Open http://localhost:8080 in your browser
```

---

## Main Screen

Two entry cards are displayed on launch:

**"New Game"**
→ Fill in game name, type, target age, features, markets, and platforms  
→ Click "Generate Compliance Guide"  
→ View a phase-by-phase development roadmap and platform configuration checklist

**"Audit Existing Game"**
→ Fill in game info, click "📁 Browse" to select your Unity project path  
→ Click "Start Audit"  
→ View code scan results and a compliance issue list with file-level detail

---

## Policy Management Modal

Click **「📋 Policy Management」** in the top-right header to open the modal. Four tabs are available:

---

### 📊 Status Tab

Displays the freshness of all 22 compliance rules across Apple App Store and Google Play:

- **Overall status**: Fresh / Needs Review / Critical
- **Change alerts**: When LLM detects a policy change affecting a rule, an alert card appears with:
  - Change summary from the LLM
  - Developer impact description
  - Recommended action
  - Detection timestamp and source
- **Mark as Reviewed**: Each alert card has two buttons:
  - ✅ "No rule change needed" — acknowledges the alert, restores freshness
  - ✏️ "Rule updated, clear alert" — confirms you've updated your rule, clears the alert
- **All rule details**: Expandable section showing every rule's status and age

---

### ⚙️ Config Tab

**LLM API Keys**

| Field | Description |
|-------|-------------|
| Anthropic API Key | Claude (recommended for policy analysis) |
| OpenAI API Key | GPT-4o (alternative) |

Enter a key and click "Save Config" — takes effect immediately, no server restart needed.  
To remove a key, clear the field and save.

**Compliance Rules Hot-Reload**

| Field | Description |
|-------|-------------|
| Remote Rules URL | Optional URL to a remote `compliance-rules.yaml` |
| Current version | Hash of the currently loaded rules file |

- Leave the URL blank to use local file mode (the system watches `config/compliance-rules.yaml` for changes)
- Set a URL to enable remote rules auto-update
- Click "Check for Updates" to trigger an immediate update check

---

### 🔍 Check Tab

Three check modes — all run in the **background** (switching tabs will not interrupt the check):

| Button | Action |
|--------|--------|
| 📡 RSS Announcements | Fetch Apple/Google developer blogs and filter for policy-related posts |
| 🔍 Page Change Detection | Compare official policy page content hashes against cached versions |
| ⚡ Full Check | RSS + page detection + LLM auto-analysis (one click) |

**How it works:**

1. Click a check button — the job starts immediately in the background
2. The UI polls every 2 seconds for progress ("Elapsed: N seconds")
3. When done, results appear automatically — even if you switched tabs while waiting

**With LLM configured**, full check also:
- Analyzes what changed on any detected page
- Identifies which of your 22 rules are affected
- Automatically flags those rules as "needs review" in the Status tab

**Without LLM**, the system still detects page changes (hash comparison), but cannot automatically determine which rules are affected.

---

### ⏰ Schedule Tab

Configure automatic background monitoring:

**Scheduler status**: Running / Stopped, with current interval

**Interval options**:
- Every 6 hours
- Every 12 hours  
- Every 24 hours (recommended)
- Every week

**Notification history**: Lists recent policy change alerts with timestamps. Click "Mark All Read" to clear the unread badge.

The scheduler runs the same Full Check logic automatically at your chosen interval. Results appear in the notification bell (🔔) in the header — the badge shows the unread count.

---

## Bottom Action Button

The primary action button in the bottom-right of the modal changes with the active tab:

| Active Tab | Button |
|------------|--------|
| 📊 Status | 🔄 Refresh Status |
| ⚙️ Config | 💾 Save Config |
| 🔍 Check | ⚡ Full Check |
| ⏰ Schedule | ✅ Mark All Read |

---

## Notification Bell (🔔)

- Located in the top-right header
- Badge shows unread notification count
- Notifications are generated when:
  - A scheduled check detects an RSS policy announcement
  - A page hash change is detected
  - LLM flags rules as needing review
- Open the Schedule tab to view and dismiss notifications
