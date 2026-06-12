"""Email bodies for the shortlist review loop (PRD step 2)."""

from __future__ import annotations


def review_id_from_generated_at(generated_at: str) -> str:
    """e.g. 2026-06-12T14:55:21Z -> week-2026-06-12"""
    day = generated_at[:10]
    return f"week-{day}"


def shortlist_email(review_id: str, shortlist: dict) -> tuple[str, str]:
    """Build subject and plain-text body for the initial shortlist review email."""
    recipes = shortlist["recipes"]
    generated = shortlist.get("generated_at", "")

    subject = f"[Gusto Review {review_id}] Your 5 recipe picks"

    lines = [
        "Your Gousto shortlist",
        "=====================",
        "",
    ]

    for slot, recipe in enumerate(recipes, start=1):
        tags = ", ".join(recipe.get("dietary_tags", [])) or "—"
        lines.append(f"{slot}. {recipe['name']}")
        lines.append(
            f"   {recipe['cook_time_mins']} min · {recipe['calories']} kcal · {tags}"
        )
        lines.append(f"   {recipe.get('reason', '')}")
        lines.append("")

    lines.extend(
        [
            "Reply with one line per recipe:",
            "  1. Keep",
            "  2. Drop",
            "  3. Switch",
            "  4. Keep",
            "  5. Keep",
            "",
            "Or reply CONFIRM ALL if you're happy with all five.",
            "",
            f"Generated: {generated}",
            f"Review ID: {review_id}",
        ]
    )

    return subject, "\n".join(lines)
