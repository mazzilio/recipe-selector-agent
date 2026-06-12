# 🥘 Mise — AI Meal Planning Agent

> **Fuzzy Labs "Build an AI Agent" Hackathon 2026**  
> Team: **The Meal Deal**

---

## The Problem

Choosing Gousto meals every week is a chore. The menu opens on Monday with 200+ recipes and you have to scroll, filter, and second-guess yourself before settling on five. Decision fatigue is real, and it leads to lazy picks, unbalanced weeks, and meals that don't actually fit your schedule.

**Mise** automates that entire process — it scrapes the week's menu, knows what you like, and hands you a shortlist of five recipes that fit your diet, your time, and your taste.

---

## The Team — The Meal Deal

| Name | Role | Contribution |
|---|---|---|
| **Mariam** | Architect | Technical design, scraper, filtering logic, agent setup, OpenCode integration |
| **Maria** | Product Owner | PRD definition, requirements, user stories, acceptance criteria |
| **Thana** | Project Manager | Process, planning, sprint coordination, documentation |

---

## How We Built It

We used AI from the very first step — not just to write code, but to define *what* to build.

1. **PRD with AI** — We described the problem to a Copilot Chat agent and iterated on a Product Requirements Document together. The AI helped us think through edge cases, data contracts, and the right scope for an MVP.

2. **Splitting the work** — With the PRD as a shared reference, we divided the build into five steps (scrape → filter → email → calendar → meal plan) and worked through them in order, using the PRD as our source of truth for what "done" looks like.

3. **Agentic workflow** — Rather than building a traditional app, we built around agent primitives: skills (reusable task definitions in Markdown), memory (preferences persisted between sessions), and a named agent (Mise) that orchestrates everything in OpenCode.

---

## What We've Built

### Custom components

| Component | What it does |
|---|---|
| **`src/gousto_scraper.py`** | Headless Playwright scraper — navigates the Gousto React SPA, extracts all 205 recipe cards using stable `data-testing` DOM attributes |
| **`src/models.py`** | Pydantic `Recipe` model — name, cook time, calories, dietary tags, extra-cost flag, customisable flag |
| **`src/main.py`** | CLI entry point — runs the scraper, prints a summary, saves `data/recipes.json` |
| **`src/shortlist.py`** | Hard-filter helper — reads preferences + catalogue, applies dietary/cost/cook-time rules, returns ≤ 20 ranked candidates for the agent to reason over |
| **`memory/user-preferences.md`** | Persisted user profile — dietary requirements, allergies, dislikes, cook-time limit, favourite cuisines. Written by the agent, editable by hand |
| **`.opencode/agents/mise.md`** | Primary OpenCode agent — Mise's identity, constraints, and workflow overview |
| **`.opencode/skills/collect-preferences/`** | OpenCode skill — interviews the user one question at a time and saves preferences to memory |
| **`.opencode/skills/shortlist-recipes/`** | OpenCode skill — runs the hard-filter script, agent picks 5 recipes with reasoning, writes `data/shortlist.json` |

### What the pipeline looks like today

```
python3 src/main.py          →  scrape Gousto menu  →  data/recipes.json (205 recipes)
                                                              │
opencode --agent mise                                         ▼
  "collect my preferences"   →  interview user      →  memory/user-preferences.md
  "shortlist recipes"        →  filter + rank        →  data/shortlist.json (5 recipes)
```

### What's next

| Step | Feature | Status |
|---|---|---|
| 1 | Gousto menu scraper | ✅ Complete |
| 2 | Recipe filtering & shortlisting | ✅ Complete |
| 3 | User email review loop | 🔲 Not started |
| 4 | Calendar free/busy integration | 🔲 Not started |
| 5 | Meal plan generation | 🔲 Not started |

---

## What even *is* an agent?

Strip away the hype and an AI agent is a **loop** with five parts:

| Part | What it is | In this project |
|---|---|---|
| 🧠 **Model** | The brain that reasons and writes | Qwen3 Coder via OpenRouter (free tier) |
| 🔁 **Harness** | The loop that lets the model read, think, and act | **OpenCode** (open-source, runs in your terminal) |
| 📜 **Instructions** | Who the agent is and how it behaves | `AGENTS.md` + `.opencode/agents/mise.md` |
| 🛠️ **Skills** | Reusable "how to do X" recipes | `.opencode/skills/` |
| 💾 **Memory** | What it remembers between sessions | `memory/` folder |

A chatbot answers and forgets. An **agent** has instructions, can *do* things (skills), and *remembers* (memory). That's the whole difference.

---

## Setup

### 1. Install Python dependencies

```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

### 2. Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

### 3. Add your API key

```bash
cp .env.example .env
```

Open `.env` and fill in your [OpenRouter](https://openrouter.ai/keys) key (free tier, no credit card):

```
OPENROUTER_API_KEY=your-key-here
```

Load it into your shell:

```bash
set -a; source .env; set +a
```

---

## Running the agent

### Scrape the latest Gousto menu

```bash
python3 src/main.py
```

Run this each Monday when Gousto opens the new week. Saves ~205 recipes to `data/recipes.json`.

### Set your preferences (first time only)

```bash
opencode --agent mise
```

Then say: **"collect my preferences"**

The agent interviews you and saves your answers to `memory/user-preferences.md`. Edit it directly any time.

### Get your weekly shortlist

In the same OpenCode session, say: **"shortlist recipes"**

The agent filters the catalogue, picks 5 recipes with reasoning, and saves them to `data/shortlist.json`.

### Automate the scrape (optional)

See [ADR-001](docs/adr/ADR-001-automation-strategy.md) for a full comparison of scheduling options. Quick start with cron:

```bash
crontab -e
# Add — runs every Monday at 9am:
0 9 * * 1 cd /path/to/recipe-selector-agent && python3 src/main.py >> data/scraper.log 2>&1
```

---

## Using with GitHub Copilot instead of OpenCode

If you prefer VS Code + Copilot over OpenCode, the skills in `.opencode/skills/` are plain Markdown — you can paste them into a Copilot Chat session and it will follow them in the same way. The `memory/` folder works identically as a reference source.

---

## Project structure

```
recipe-selector-agent/
├── AGENTS.md                        ← agent constitution
├── PRD.md                           ← product requirements & progress tracker
├── opencode.json                    ← model config (Qwen3 via OpenRouter)
├── .env.example                     ← API key template
├── .opencode/
│   ├── agents/mise.md               ← Mise primary agent definition
│   └── skills/
│       ├── collect-preferences/     ← preference interview skill
│       ├── shortlist-recipes/       ← shortlisting skill
│       ├── capture-note/            ← memory write skill
│       └── recall/                  ← memory read skill
├── memory/
│   └── user-preferences.md         ← your dietary profile
├── src/
│   ├── main.py                      ← scraper entry point
│   ├── gousto_scraper.py            ← Playwright scraper
│   ├── models.py                    ← Recipe data model
│   └── shortlist.py                 ← hard-filter CLI helper
├── data/                            ← gitignored outputs
│   ├── recipes.json                 ← full scraped catalogue
│   ├── shortlist.json               ← this week's 5 recipes
│   └── history.json                 ← past meals (avoids repeats)
└── docs/
    ├── architecture.md
    ├── shortlisting-workflow.md
    └── adr/
        └── ADR-001-automation-strategy.md
```

---

## Links

- [Fuzzy Labs](https://fuzzylabs.ai) · Build an AI Agent Hackathon 2026
- [OpenCode docs](https://opencode.ai/docs/)
- [OpenRouter models](https://openrouter.ai/models)
- [Gousto menu](https://www.gousto.co.uk/menu)
- [PRD](PRD.md) · [Architecture](docs/architecture.md) · [ADR-001](docs/adr/ADR-001-automation-strategy.md)


