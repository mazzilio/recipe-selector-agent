# Architecture

## Overview

The Recipe Selector Agent uses a multi-agent architecture where each agent handles a specific aspect of the recipe discovery and cooking workflow.

## Component Architecture

```
┌─────────────────────────────────────┐
│     User Interface / CLI            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Agent Orchestration            │
│  (Mise — primary agent in OpenCode) │
└──────┬───────────────────────────┬──┘
       │                           │
   ┌───▼────────┐          ┌──────▼────┐
   │Recipe Agent │          │Constraint │
   │(Discovery)  │          │ Validator │
   └────────────┘          └──────────┘
       │
   ┌───▼────────┐
   │Data Layer  │
   │(APIs/DB)   │
   └────────────┘
```

## Agent Responsibilities

- **Mise (primary)**: Orchestrates the full meal planning workflow
- **Constraint Validator**: Checks dietary requirements and hard rules
- **Cooking Guide Agent**: Provides step-by-step instructions *(future)*
- **Ingredient Substitution**: Suggests alternatives *(future)*

## Data Flow

1. Scraper pulls latest Gousto menu → `data/recipes.json`
2. User preferences loaded from `memory/user-preferences.md`
3. Hard-filter script produces ≤ 20 candidates
4. Agent reasons over candidates → `data/shortlist.json`
5. Shortlist emailed to user for approval *(Step 3)*
6. Confirmed recipes written to `data/history.json`
7. Calendar queried for free/busy → day-by-day meal plan *(Steps 4–5)*

---

## Architecture Decision Records

| ADR | Title | Status |
|---|---|---|
| [ADR-001](adr/ADR-001-automation-strategy.md) | Automation Strategy for Weekly Pipeline | Proposed |

