"""
Recipe Selector Agent - Main entry point

This module serves as the orchestrator for the recipe recommendation workflow.
"""

import asyncio
import json
import os
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from src.gousto_scraper import fetch_recipes


def main():
    load_dotenv()

    session_cookie = os.getenv("GOUSTO_SESSION_COOKIE") or None
    debug = "--debug" in sys.argv

    print("🍳 Recipe Selector Agent")
    print("=" * 40)
    print("Scraping Gousto menu — this may take ~30 s …")
    if session_cookie:
        print("  ↳ Using session cookie (personalised weekly menu)")
    else:
        print("  ↳ No session cookie — scraping public catalogue")

    recipes = asyncio.run(fetch_recipes(session_cookie=session_cookie, debug=debug))

    if not recipes:
        print("\n⚠️  No recipes found. Run with --debug to save an HTML snapshot.")
        sys.exit(1)

    # ── Terminal summary ──────────────────────────────────────────────────────
    tag_counts = Counter(tag for r in recipes for tag in r.dietary_tags)
    extra_cost = sum(1 for r in recipes if r.has_extra_cost)
    customisable = sum(1 for r in recipes if r.is_customisable)

    print(f"\n✅  {len(recipes)} recipes scraped\n")
    print("Dietary breakdown:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag:>4}  {count}")
    print(f"\nExtra-cost recipes : {extra_cost}")
    print(f"Customisable       : {customisable}")

    # ── Save JSON ─────────────────────────────────────────────────────────────
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "recipes.json"
    out_path.write_text(
        json.dumps([r.model_dump() for r in recipes], indent=2),
        encoding="utf-8",
    )
    print(f"\n💾  Saved to {out_path}")


if __name__ == "__main__":
    main()

