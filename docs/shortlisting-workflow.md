# Shortlisting Workflow

## Overview

This document describes the two-stage process for producing a weekly recipe shortlist.

```
┌──────────────────────────────────────────────────────────────────┐
│                    Stage 1: Collect Preferences                   │
│                                                                   │
│  User: "collect my preferences"                                  │
│         │                                                         │
│         ▼                                                         │
│  Agent runs collect-preferences skill (AGENTS.md)               │
│         │  asks questions one at a time                          │
│         ▼                                                         │
│  memory/user-preferences.md  ◄── written / updated              │
│  (YAML frontmatter + prose summary, Obsidian-compatible)         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼  (one-off, re-run to update)

┌──────────────────────────────────────────────────────────────────┐
│                    Stage 2: Shortlist Recipes                     │
│                                                                   │
│  User: "shortlist recipes"                                       │
│         │                                                         │
│         ▼                                                         │
│  Agent reads memory/user-preferences.md                         │
│         │                                                         │
│         ▼                                                         │
│  python3 src/shortlist.py --candidates                           │
│         │  hard filters: extra cost, dietary tags, cook time     │
│         │  outputs ≤20 candidates as JSON                        │
│         ▼                                                         │
│  Agent reasons over candidates                                   │
│         │  soft criteria: variety, cuisine, novelty, balance     │
│         ▼                                                         │
│  data/shortlist.json  ◄── 5 recipes + per-recipe reasoning      │
│         │                                                         │
│         ▼                                                         │
│  Terminal summary printed                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Why this split?

| Concern | Where it lives | Why |
|---|---|---|
| Hard rules (no extra cost, must be GF) | `src/shortlist.py` | Deterministic; never ask the LLM to enforce an allergy |
| Soft ranking (variety, cuisine match) | Agent prompt in `AGENTS.md` | Requires contextual reasoning |
| User preferences | `memory/user-preferences.md` | Persists across sessions; human-editable |
| Scraped catalogue | `data/recipes.json` | Written by `src/gousto_scraper.py` |
| Shortlist output | `data/shortlist.json` | Read by future steps (email, calendar) |
| Cook history | `data/history.json` | Written after user confirms meals; used to avoid repeats |

---

## Preference fields

Defined in `memory/user-preferences.md` YAML frontmatter:

| Field | Type | Description |
|---|---|---|
| `dietary_requirements` | list | e.g. `[vegetarian, halal]` — filters by dietary tag |
| `allergies` | list | e.g. `[nuts, gluten]` — hard-excludes matching recipes |
| `dislikes` | list | Substring-matched against recipe names |
| `household_size` | int | Number of portions |
| `max_weeknight_cook_mins` | int | Cook-time cap for weeknight slots |
| `exclude_extra_cost` | bool | If true, removes all `+£X` recipes |
| `favourite_cuisines` | list | Boosted in soft-ranking |

---

## Updating preferences

Just say **"update my preferences"** or **"collect my preferences"** in any OpenCode session. The agent will re-run the `collect-preferences` skill and overwrite `memory/user-preferences.md`.

You can also edit the file directly in any text editor or Obsidian.

---

## History tracking

After the user confirms their final 5 recipes, the agent appends to `data/history.json`:

```json
[
  { "name": "Butter Chicken With Coriander Rice", "date": "2026-06-12" },
  ...
]
```

Recipes cooked within the last 4 weeks are deprioritised (but not excluded) in future shortlists.

---

## Related files

- `AGENTS.md` — skill definitions (`collect-preferences`, `shortlist-recipes`)
- `memory/user-preferences.md` — persisted user preferences
- `src/shortlist.py` — hard-filter CLI tool
- `src/gousto_scraper.py` — scraper that produces `data/recipes.json`
- `PRD.md` — full product requirements
