"""
Hard-filter helper for recipe shortlisting.

Reads data/recipes.json + memory/user-preferences.md and applies deterministic
rules (extra-cost exclusion, dietary requirements, cook-time cap).  Outputs a
trimmed candidate list so the agent can reason over a manageable context.

Usage
-----
# Print ≤20 candidates as JSON (for agent to rank):
    python3 src/shortlist.py --candidates

# Print the already-saved shortlist:
    python3 src/shortlist.py --show
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

RECIPES_PATH = Path("data/recipes.json")
PREFS_PATH = Path("memory/user-preferences.md")
SHORTLIST_PATH = Path("data/shortlist.json")
HISTORY_PATH = Path("data/history.json")

MAX_CANDIDATES = 20

# Map AGENTS.md dietary_requirements values → Recipe.dietary_tags values
# If a requirement is listed it means we REQUIRE that tag to be present.
_REQUIREMENT_TO_TAG = {
    "vegetarian": "V",
    "vegan": "VE",
    "plant-based": "PB",
    "gluten-free": "GF",
    "gluten free": "GF",
    "dairy-free": "DF",
    "dairy free": "DF",
}


# ---------------------------------------------------------------------------
# Preferences parsing
# ---------------------------------------------------------------------------

def _parse_yaml_list(value: str) -> List[str]:
    """Parse a YAML inline list like [nuts, gluten] or [] into a Python list."""
    value = value.strip()
    # Strip inline comment
    value = re.sub(r"\s*#.*$", "", value).strip()
    if value in ("[]", ""):
        return []
    # Strip brackets
    value = value.strip("[]")
    return [v.strip().strip("\"'") for v in value.split(",") if v.strip()]


def load_preferences() -> Dict[str, Any]:
    """Parse YAML frontmatter from memory/user-preferences.md."""
    if not PREFS_PATH.exists():
        return _default_prefs()

    text = PREFS_PATH.read_text(encoding="utf-8")
    # Extract frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return _default_prefs()

    fm = match.group(1)
    prefs = _default_prefs()

    for line in fm.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()

        if key == "dietary_requirements":
            prefs["dietary_requirements"] = _parse_yaml_list(raw)
        elif key == "allergies":
            prefs["allergies"] = _parse_yaml_list(raw)
        elif key == "dislikes":
            prefs["dislikes"] = _parse_yaml_list(raw)
        elif key == "household_size":
            try:
                prefs["household_size"] = int(re.sub(r"\s*#.*", "", raw).strip())
            except ValueError:
                pass
        elif key == "max_weeknight_cook_mins":
            try:
                prefs["max_weeknight_cook_mins"] = int(re.sub(r"\s*#.*", "", raw).strip())
            except ValueError:
                pass
        elif key == "exclude_extra_cost":
            raw_clean = re.sub(r"\s*#.*", "", raw).strip().lower()
            prefs["exclude_extra_cost"] = raw_clean == "true"
        elif key == "favourite_cuisines":
            prefs["favourite_cuisines"] = _parse_yaml_list(raw)

    return prefs


def _default_prefs() -> Dict[str, Any]:
    return {
        "dietary_requirements": [],
        "allergies": [],
        "dislikes": [],
        "household_size": 2,
        "max_weeknight_cook_mins": 30,
        "exclude_extra_cost": True,
        "favourite_cuisines": [],
    }


# ---------------------------------------------------------------------------
# Hard filtering
# ---------------------------------------------------------------------------

def _load_recent_names() -> set:
    """Return recipe names cooked in the last 4 weeks (from history.json)."""
    if not HISTORY_PATH.exists():
        return set()
    history = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    # history is a list of {"name": ..., "date": "YYYY-MM-DD"}
    from datetime import date, timedelta
    cutoff = date.today() - timedelta(weeks=4)
    recent = set()
    for entry in history:
        try:
            cooked = date.fromisoformat(entry["date"])
            if cooked >= cutoff:
                recent.add(entry["name"])
        except (KeyError, ValueError):
            pass
    return recent


def filter_recipes(prefs: Dict[str, Any]) -> List[Dict]:
    """Apply hard rules and return a sorted candidate list (≤ MAX_CANDIDATES)."""
    if not RECIPES_PATH.exists():
        print(f"ERROR: {RECIPES_PATH} not found. Run `python3 src/main.py` first.",
              file=sys.stderr)
        sys.exit(1)

    recipes: List[Dict] = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    recent = _load_recent_names()

    # Build required tags set from dietary_requirements
    required_tags = set()
    for req in prefs.get("dietary_requirements", []):
        tag = _REQUIREMENT_TO_TAG.get(req.lower())
        if tag:
            required_tags.add(tag)

    max_mins = prefs.get("max_weeknight_cook_mins", 9999)
    # Allow one longer recipe — cap at 1.5× for weekend slot
    weekend_cap = int(max_mins * 1.5)

    candidates = []
    for r in recipes:
        # --- Hard exclusions ---
        if prefs.get("exclude_extra_cost") and r.get("has_extra_cost"):
            continue

        # Must have ALL required dietary tags
        tags = set(r.get("dietary_tags", []))
        if required_tags and not required_tags.issubset(tags):
            continue

        # Cook time: exclude anything over the weekend cap
        cook = r.get("cook_time_mins")
        if cook is not None and cook > weekend_cap:
            continue

        # Dislikes: name-based substring match (rough but effective)
        name_lower = r["name"].lower()
        skip = False
        for dislike in prefs.get("dislikes", []):
            if dislike.lower() in name_lower:
                skip = True
                break
        if skip:
            continue

        # --- Soft scoring (for ordering before handing to agent) ---
        score = 0

        # Prefer recipes within weeknight limit
        if cook is not None and cook <= max_mins:
            score += 2

        # Prefer recently NOT cooked (novelty)
        if r["name"] not in recent:
            score += 1

        # Prefer favourite cuisines (crude name-based match)
        for fav in prefs.get("favourite_cuisines", []):
            if fav.lower() in name_lower:
                score += 1
                break

        candidates.append({**r, "_score": score})

    # Sort by score descending, then by name for stability
    candidates.sort(key=lambda x: (-x["_score"], x["name"]))

    # Remove internal score field before output
    for c in candidates:
        c.pop("_score", None)

    return candidates[:MAX_CANDIDATES]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_candidates() -> None:
    prefs = load_preferences()
    candidates = filter_recipes(prefs)
    print(json.dumps({"preferences": prefs, "candidates": candidates}, indent=2))


def cmd_show() -> None:
    if not SHORTLIST_PATH.exists():
        print("No shortlist found. Run the shortlist-recipes skill first.")
        sys.exit(1)
    data = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))
    print(f"\n🥘  This week's shortlist  (generated {data.get('generated_at', '?')})")
    print("─" * 50)
    for i, r in enumerate(data.get("recipes", []), 1):
        tags = " ".join(r.get("dietary_tags", []))
        tag_str = f"  [{tags}]" if tags else ""
        extra = "  +£{:.2f}".format(r["extra_cost_gbp"]) if r.get("has_extra_cost") else ""
        print(f"{i}. {r['name']} ({r.get('cook_time_mins', '?')} min, "
              f"{r.get('calories', '?')} kcal){tag_str}{extra}")
        print(f"   → {r.get('reason', '')}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Recipe shortlist helper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--candidates", action="store_true",
                       help="Print hard-filtered candidate list as JSON")
    group.add_argument("--show", action="store_true",
                       help="Print the saved shortlist in human-readable form")
    args = parser.parse_args()

    if args.candidates:
        cmd_candidates()
    elif args.show:
        cmd_show()


if __name__ == "__main__":
    main()
