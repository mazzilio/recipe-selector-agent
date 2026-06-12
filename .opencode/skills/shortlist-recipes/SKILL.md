---
name: shortlist-recipes
description: Use when the user wants to shortlist recipes, pick meals for the week, generate a shortlist, or find out what to cook this week. Reads user preferences and the scraped Gousto catalogue, filters by hard rules, then picks the best 5 recipes with reasoning.
---

# Shortlist Recipes

Produce a ranked shortlist of 5 Gousto recipes tailored to the user's preferences.

## When to use this

User says things like "shortlist recipes", "pick my recipes", "what should I cook this
week", "generate a shortlist", or similar.

## Procedure

1. Check that `memory/user-preferences.md` exists and is filled in (not the blank
   template). If it isn't, run the `collect-preferences` skill first.

2. Check that `data/recipes.json` exists. If not, tell the user to run:
   ```
   python3 src/main.py
   ```
   and wait for them to confirm before continuing.

3. Run the hard-filter script to get a manageable candidate list:
   ```
   python3 src/shortlist.py --candidates
   ```
   This applies hard rules (extra-cost exclusion, dietary tag matching, cook-time cap)
   and outputs ≤ 20 candidates as JSON.

4. From those candidates, select **exactly 5** using these soft criteria:
   - **Variety** — aim for a mix of proteins and cuisines across the 5 slots
   - **Weeknight fit** — prioritise recipes at or under `max_weeknight_cook_mins`; allow
     one longer recipe for a weekend slot
   - **Favourites first** — if `favourite_cuisines` is set, include at least one match
   - **Novelty** — if `data/history.json` exists, deprioritise recipes cooked in the last
     4 weeks

5. For each selected recipe write a one-sentence `reason` explaining why it was chosen.

6. Get the current timestamp with `date -u +"%Y-%m-%dT%H:%M:%SZ"`.

7. Write `data/shortlist.json` in this exact format:
   ```json
   {
     "generated_at": "<ISO timestamp>",
     "preferences_snapshot": { ... },
     "recipes": [
       {
         "name": "...",
         "cook_time_mins": 30,
         "calories": 565,
         "dietary_tags": ["GF"],
         "has_extra_cost": false,
         "reason": "Quick weeknight option that matches your gluten-free requirement."
       }
     ]
   }
   ```

8. Print a human-readable summary:
   ```
   🥘  This week's shortlist
   ──────────────────────────
   1. Recipe Name (30 min, 565 kcal) — GF
      → Reason
   ...
   ```

9. Tell the user: "Shortlist saved to data/shortlist.json. Reply with keep / drop /
   switch <number> to refine it."
