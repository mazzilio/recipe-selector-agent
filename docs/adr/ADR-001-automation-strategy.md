# ADR-001: Automation Strategy for Weekly Pipeline

**Date:** 2026-06-12  
**Status:** Proposed  
**Deciders:** Mariam Hussein

---

## Context

The pipeline (scrape menu → filter → shortlist → email user) needs to run automatically each week when Gousto opens the new menu, without manual intervention. Several scheduling and automation approaches are available.

**Decision drivers:**
- Should work reliably on a developer's MacBook
- Minimal infrastructure overhead
- Should handle the email send + reply loop, not just the scrape
- Free or low cost

---

## Options Considered

### Option A: cron

Standard Unix job scheduler. Simple one-liner to schedule `python3 src/main.py`.

| | |
|---|---|
| ✅ | Zero setup, universally available |
| ✅ | Easy to read and modify |
| ❌ | Silently skips if Mac is asleep at scheduled time |
| ❌ | No built-in retry or failure alerting |
| ❌ | Handles scrape only — email loop needs extra work |

```
0 9 * * 1 cd /path/to/repo && python3 src/main.py >> data/scraper.log 2>&1
```

---

### Option B: launchd (macOS native) ⭐ Recommended for local scheduling

Apple's native job scheduler. Defined as a `.plist` file in `~/Library/LaunchAgents/`. Runs even after sleep/wake and can restart on failure.

| | |
|---|---|
| ✅ | Survives Mac sleep/wake cycles |
| ✅ | Built-in retry and failure handling |
| ✅ | No third-party dependencies |
| ❌ | Verbose XML config compared to cron |
| ❌ | Still local — won't run if Mac is off |
| ❌ | Handles scrape only — email loop needs extra work |

```xml
<!-- ~/Library/LaunchAgents/com.mise.weekly-scrape.plist -->
<key>StartCalendarInterval</key>
<dict>
  <key>Weekday</key><integer>1</integer>  <!-- Monday -->
  <key>Hour</key><integer>9</integer>
  <key>Minute</key><integer>0</integer>
</dict>
```

---

### Option C: GitHub Actions

Scheduled CI workflow that runs the pipeline in the cloud on a cron schedule.

| | |
|---|---|
| ✅ | Runs in the cloud — Mac doesn't need to be on |
| ✅ | Free for public repos |
| ✅ | Full audit log of every run |
| ❌ | `data/recipes.json` must be committed back or sent elsewhere |
| ❌ | Secrets (email credentials) need to go into GitHub Secrets |
| ❌ | Adds latency vs local run; not ideal for personal data |

---

### Option D: Python `schedule` library

A long-running Python process that fires tasks at set intervals. Simple to write, but requires a persistent process.

| | |
|---|---|
| ✅ | Pure Python, easy to extend |
| ✅ | Can chain scrape → filter → email in one process |
| ❌ | Process must always be running |
| ❌ | No persistence across reboots without extra setup |

---

### Option E: n8n (self-hosted no-code workflow) ⭐ Recommended for email loop

Visual workflow tool that can trigger scripts, send emails, parse replies via webhooks, and chain steps together. Self-hostable and free.

| | |
|---|---|
| ✅ | Handles the full email send + reply parsing loop natively |
| ✅ | Visual workflow — easy to modify without code |
| ✅ | Built-in retry, error handling, and run history |
| ✅ | Can call `python3 src/main.py` as an exec step |
| ❌ | Requires a running n8n instance (Docker or cloud) |
| ❌ | Slightly more setup than cron/launchd |

---

## Decision

Use a **two-layer approach**:

| Layer | Tool | Why |
|---|---|---|
| Local scheduling (scrape + shortlist) | **launchd** | Reliable on Mac, survives sleep/wake, no dependencies |
| Email send + reply loop (Step 3) | **n8n** | Handles email webhooks natively, visual and easy to extend |

---

## Consequences

- `launchd` plist to be added to `docs/launchd/` with setup instructions when Step 3 is implemented
- n8n workflow definition to be added when Step 3 (email review loop) is built
- GitHub Actions remains an option if the project moves to a server or shared CI environment
- Python `schedule` and cron are not selected but remain valid fallbacks for simpler setups
