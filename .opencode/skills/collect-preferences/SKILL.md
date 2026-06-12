---
name: collect-preferences
description: Use when the user wants to set up their meal preferences, update what they like, or be onboarded. Interviews the user and saves their dietary requirements, allergies, dislikes, cook-time limits, and cuisine preferences to memory/user-preferences.md so every future session can use them without asking again.
---

# Collect Preferences

Interview the user about their meal preferences and persist them to `memory/user-preferences.md`.

## When to use this

User says things like "collect my preferences", "set up my profile", "update what I like",
"onboard me", "I want to change my dietary settings", or similar.

## Procedure

1. Check whether `memory/user-preferences.md` already exists and read it if so. Tell the
   user what you already know and ask if they want to update specific fields or start fresh.

2. Ask the following questions **one at a time** — wait for each answer before continuing:
   - "Do you have any dietary requirements or follow a specific diet?" (e.g. vegetarian,
     vegan, halal, kosher, pescatarian)
   - "Any allergies or ingredients you must always avoid?" (e.g. nuts, gluten, shellfish,
     dairy, eggs)
   - "Any cuisines or ingredients you simply don't enjoy?" (free text — the more specific
     the better)
   - "How many people are you cooking for?"
   - "On a typical weeknight, what's the maximum time you want to spend cooking?" (give
     examples: 20 min, 30 min, 45 min)
   - "Should I always exclude recipes that carry an extra charge (e.g. +£0.50 a portion)?"
   - "Any cuisines or meal types you'd love to see more of?" (optional — press enter to skip)

3. Summarise what you heard back to the user and ask them to confirm or correct before saving.

4. Get today's date with `date +%Y-%m-%d`.

5. Write `memory/user-preferences.md` using **exactly** this format (preserve all keys
   even if the value is `[]` or `null`):

```markdown
---
title: User Meal Preferences
created: <TODAY_DATE>
updated: <TODAY_DATE>
tags: [preferences, meal-planning]
dietary_requirements: []          # e.g. [vegetarian, halal]
allergies: []                     # e.g. [nuts, gluten]
dislikes: []                      # e.g. [blue cheese, offal, very spicy food]
household_size: 2
max_weeknight_cook_mins: 30
exclude_extra_cost: true
favourite_cuisines: []            # e.g. [Asian, Mediterranean]
---

<prose summary of the preferences in plain English>

Related: [[progress]] #preferences
```

6. Confirm: "Saved to memory/user-preferences.md. I'll use these every time I shortlist recipes."
