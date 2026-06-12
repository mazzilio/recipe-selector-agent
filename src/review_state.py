"""Persist shortlist review state between send and reply handling."""

from __future__ import annotations

import json
from pathlib import Path

REVIEWS_DIR = Path("data/reviews")
SHORTLIST_PATH = Path("data/shortlist.json")


def load_shortlist() -> dict:
    if not SHORTLIST_PATH.exists():
        raise FileNotFoundError(
            f"No shortlist at {SHORTLIST_PATH}. Run the shortlist-recipes skill first."
        )
    return json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))


def review_path(review_id: str) -> Path:
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    return REVIEWS_DIR / f"{review_id}.json"


def load_review(review_id: str) -> dict | None:
    path = review_path(review_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_review(state: dict) -> None:
    path = review_path(state["review_id"])
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
