# Product Requirements Document
## Meal Planning Agentic Workflow

**Version:** 1.1  
**Status:** In Progress  
**Last Updated:** June 2026

---

## Problem Statement

Users of meal kit and recipe services such as Gusto and HelloFresh experience decision fatigue when selecting weekly meals. This friction leads to poor planning outcomes, resulting in either skipped meal prep, unbalanced schedules, or meals that don't fit around the user's week. The goal is to automate the recipe selection, meal planning, and calendar coordination process — removing the decision burden while keeping the user in control of their final choices.

---

## Goals & Non-Goals

**Goals**
- Automatically browse the user's chosen meal kit site and shortlist recipes based on preferences
- Generate a structured meal plan that accounts for both weeknight cooking and weekend meal prep
- Integrate with the user's calendar to avoid scheduling conflicts
- Surface the shortlist to the user via email for lightweight approval and customisation
- Respect dietary requirements, allergies, and budget constraints at every step

**Non-Goals**
- Making payments or interacting with any checkout or billing flow
- Creating, overwriting, or deleting existing calendar entries
- Accessing the detail or content of calendar events (free/busy status only)
- Supporting services other than Gusto in the MVP

---

## Progress Tracker

| Step | Feature | Status |
|---|---|---|
| 1 | Gousto menu scraper | ✅ Complete |
| 2 | Recipe filtering & shortlisting | ✅ Complete |
| 3 | User email review loop | 🔲 Not started |
| 4 | Calendar free/busy integration | 🔲 Not started |
| 5 | Meal plan generation | 🔲 Not started |

---

## MVP Scope

### 1. Recipe Shortlisting (Gusto) ✅ Complete

The agent navigates to the Gusto website on the day the weekly menu opens (three weeks before the scheduled delivery date) and reviews the available recipe catalogue (~60 recipes). It selects a shortlist of **five recipes** based on:

- The user's stored dietary requirements and allergies
- Previous selections and stated preferences
- Exclusion of any recipes carrying an additional charge beyond the standard subscription price
- A balance of weeknight-cookable and freeze-friendly meals

The shortlist is compiled and sent to the user via **email** on the same day the menu opens.

#### What's been built (Step 1)

- **`src/models.py`** — `Recipe` Pydantic model with fields: `name`, `cook_time_mins`, `calories`, `dietary_tags` (GF/DF/V/PB), `categories`, `has_extra_cost`, `extra_cost_gbp`, `is_customisable`
- **`src/gousto_scraper.py`** — headless Playwright scraper targeting `https://www.gousto.co.uk/menu`; extracts all recipe cards from the React SPA using stable `data-testing` attributes; supports a `session_cookie` parameter (auth stub) and a `--debug` HTML snapshot mode
- **`src/main.py`** — CLI entry point; loads `.env`, runs the scraper, prints a dietary-tag breakdown, and saves the full catalogue to `data/recipes.json`
- **Output verified:** 205 recipes scraped including name, cook time, calories, dietary tags (DF: 93, GF: 60, V: 56, PB: 24), extra-cost flag (43 recipes), and customisable flag (95 recipes)

#### What's been built (Step 2)

- **`src/shortlist.py`** — hard-filter CLI: reads `data/recipes.json` + `memory/user-preferences.md`, applies deterministic rules (extra-cost exclusion, dietary tag matching, cook-time cap, dislike name-matching), scores candidates by soft criteria (weeknight fit, favourite cuisines, novelty), outputs ≤ 20 candidates as JSON
- **`memory/user-preferences.md`** — persisted user preference profile (YAML frontmatter + prose summary); populated via the `collect-preferences` skill; human-editable directly
- **`.opencode/skills/collect-preferences/SKILL.md`** — OpenCode skill: interviews the user one question at a time and writes their preferences to memory
- **`.opencode/skills/shortlist-recipes/SKILL.md`** — OpenCode skill: runs the hard-filter script, agent reasons over candidates (variety, cuisine, weeknight balance), writes `data/shortlist.json` with 5 recipes + per-recipe reasoning
- **`.opencode/agents/mise.md`** — primary OpenCode agent definition for Mise; knows all constraints, skills, and the full workflow
- **Verified end-to-end:** preferences parsed correctly (pescetarian, dislikes coriander/nuts, 30 min cap, Asian cuisine, exclude extra cost); 20 valid candidates returned; coriander/nut recipes correctly excluded

#### How to run

```bash
python3 src/main.py                  # Step 1: scrape menu → data/recipes.json
opencode --agent mise                # Step 2: "shortlist recipes" → data/shortlist.json
```

#### Remaining gap

- **History tracking** — `data/history.json` is read by the filter to deprioritise recent recipes but nothing writes to it yet. Will be populated in Step 3 when the user confirms their final selections.

---

### 2. User Review via Email

The email contains the five shortlisted recipes with brief descriptions. The user can reply to:

- **Keep** — accept a recipe as-is
- **Drop** — remove a recipe from the shortlist
- **Switch** — request an alternative suggestion for a specific slot

When a drop or switch is requested, the agent proposes a replacement from the remaining catalogue (excluding already-selected recipes and any extra-cost options) and confirms via a follow-up email. This loop continues until the user is satisfied or confirms their final five.

### 3. Meal Planning & Calendar Integration

Once the final recipe list is confirmed, the agent:

1. Queries the user's calendar for **free/busy status only** — no event titles, descriptions, or attendees are accessed or stored
2. Identifies evenings where the user is free to cook during the week
3. Assigns **weeknight-cookable** recipes to free evenings, avoiding any slots where the user is marked as busy
4. Assigns **freeze-friendly/meal prep** recipes to the weekend, scheduling cooking time and portioning for weekday lunches
5. Ensures cooking time and eating time do not overlap with any existing calendar commitments

The output is a structured meal plan (day-by-day) delivered to the user. **The agent does not create or modify any calendar events** in the MVP — the plan is advisory.

---

## User Preferences & Safety Constraints

The agent must capture and honour the following at onboarding and allow ongoing updates:

| Preference Type | Examples |
|---|---|
| Dietary requirements | Vegetarian, vegan, halal, kosher |
| Allergies | Nuts, gluten, shellfish, dairy |
| Dislikes | Specific ingredients or cuisines to avoid |
| Household size | Number of portions required |
| Cooking time limits | Max minutes per weeknight session |

These preferences are applied at the recipe browsing stage — not as a post-filter — to ensure no unsuitable recipe ever reaches the shortlist.

---

## MCP Tool Design Notes

### Calendar Tool
- **Read free/busy only** — the tool should expose a `get_free_busy(date_range)` interface and return only availability windows, not event metadata
- The tool must never read, log, or transmit event titles, locations, descriptions, or attendee information
- Write access (create, update, delete) is **explicitly out of scope** for this tool

### Browser / Web Agent Tool
- Scoped to the Gusto domain for MVP
- Must respect site terms of service; no form submission beyond recipe selection within the user's existing authenticated session
- Payment pages must be detected and skipped; the agent should abort and alert the user if it encounters a checkout flow

---

## Edge Cases

| Scenario | Handling |
|---|---|
| Recipe carries extra charge | Excluded automatically from shortlist; never surfaced to user |
| User is busy every weeknight | Agent flags the conflict, suggests all recipes as weekend batch-cook, and prompts user to review |
| Fewer than 5 suitable recipes in catalogue | Agent selects all suitable options and notifies user of the reduced shortlist |
| User doesn't reply to email | No plan is generated; agent sends a single reminder after 48 hours, then waits for next cycle |
| Menu opens late or date is ambiguous | Agent monitors for the menu-open trigger and sends the shortlist email on the day it detects availability |
| Duplicate recipe from previous week | Agent deprioritises recently served recipes; flags if unavoidable |

---

## Success Metrics (Post-MVP)

- Time from menu open to confirmed shortlist (target: same day)
- User drop/switch rate per shortlist cycle (lower = better preference matching)
- Plan adherence rate (meals cooked vs. planned)
- User-reported decision fatigue score (survey)

---

## Open Questions

1. How will the user authenticate the agent with their Gusto account? (OAuth session, saved credentials, or manual cookie hand-off?)
2. Which calendar provider is in scope for MVP — Google Calendar, Outlook, or both?
3. Should the meal plan be delivered as a reply email, a separate document, or added to a dedicated dashboard?
4. What is the fallback if the Gusto site structure changes and breaks the browser agent's navigation?
5. Should the agent support multiple household members with different dietary requirements, or is a single unified profile sufficient for MVP?

The email contains the five shortlisted recipes with brief descriptions. The user can reply to:

- **Keep** — accept a recipe as-is
- **Drop** — remove a recipe from the shortlist
- **Switch** — request an alternative suggestion for a specific slot

When a drop or switch is requested, the agent proposes a replacement from the remaining catalogue (excluding already-selected recipes and any extra-cost options) and confirms via a follow-up email. This loop continues until the user is satisfied or confirms their final five.

### 3. Meal Planning & Calendar Integration

Once the final recipe list is confirmed, the agent:

1. Queries the user's calendar for **free/busy status only** — no event titles, descriptions, or attendees are accessed or stored
2. Identifies evenings where the user is free to cook during the week
3. Assigns **weeknight-cookable** recipes to free evenings, avoiding any slots where the user is marked as busy
4. Assigns **freeze-friendly/meal prep** recipes to the weekend, scheduling cooking time and portioning for weekday lunches
5. Ensures cooking time and eating time do not overlap with any existing calendar commitments

The output is a structured meal plan (day-by-day) delivered to the user. **The agent does not create or modify any calendar events** in the MVP — the plan is advisory.

---

## User Preferences & Safety Constraints

The agent must capture and honour the following at onboarding and allow ongoing updates:

| Preference Type | Examples |
|---|---|
| Dietary requirements | Vegetarian, vegan, halal, kosher |
| Allergies | Nuts, gluten, shellfish, dairy |
| Dislikes | Specific ingredients or cuisines to avoid |
| Household size | Number of portions required |
| Cooking time limits | Max minutes per weeknight session |

These preferences are applied at the recipe browsing stage — not as a post-filter — to ensure no unsuitable recipe ever reaches the shortlist.

---

## MCP Tool Design Notes

### Calendar Tool
- **Read free/busy only** — the tool should expose a `get_free_busy(date_range)` interface and return only availability windows, not event metadata
- The tool must never read, log, or transmit event titles, locations, descriptions, or attendee information
- Write access (create, update, delete) is **explicitly out of scope** for this tool

### Browser / Web Agent Tool
- Scoped to the Gusto domain for MVP
- Must respect site terms of service; no form submission beyond recipe selection within the user's existing authenticated session
- Payment pages must be detected and skipped; the agent should abort and alert the user if it encounters a checkout flow

---

## Edge Cases

| Scenario | Handling |
|---|---|
| Recipe carries extra charge | Excluded automatically from shortlist; never surfaced to user |
| User is busy every weeknight | Agent flags the conflict, suggests all recipes as weekend batch-cook, and prompts user to review |
| Fewer than 5 suitable recipes in catalogue | Agent selects all suitable options and notifies user of the reduced shortlist |
| User doesn't reply to email | No plan is generated; agent sends a single reminder after 48 hours, then waits for next cycle |
| Menu opens late or date is ambiguous | Agent monitors for the menu-open trigger and sends the shortlist email on the day it detects availability |
| Duplicate recipe from previous week | Agent deprioritises recently served recipes; flags if unavoidable |

---

## Success Metrics (Post-MVP)

- Time from menu open to confirmed shortlist (target: same day)
- User drop/switch rate per shortlist cycle (lower = better preference matching)
- Plan adherence rate (meals cooked vs. planned)
- User-reported decision fatigue score (survey)

---

## Open Questions

1. How will the user authenticate the agent with their Gusto account? (OAuth session, saved credentials, or manual cookie hand-off?)
2. Which calendar provider is in scope for MVP — Google Calendar, Outlook, or both?
3. Should the meal plan be delivered as a reply email, a separate document, or added to a dedicated dashboard?
4. What is the fallback if the Gusto site structure changes and breaks the browser agent's navigation?
5. Should the agent support multiple household members with different dietary requirements, or is a single unified profile sufficient for MVP?