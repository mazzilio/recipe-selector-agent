"""
Gousto menu scraper using Playwright.

Usage:
    import asyncio
    from src.gousto_scraper import fetch_recipes

    recipes = asyncio.run(fetch_recipes())
"""

from typing import List, Optional

import asyncio
import re
from pathlib import Path

from playwright.async_api import async_playwright

from src.models import Recipe

MENU_URL = "https://www.gousto.co.uk/menu"
_COOKIE_DOMAIN = "www.gousto.co.uk"


async def fetch_recipes(
    session_cookie: Optional[str] = None,
    debug: bool = False,
) -> List[Recipe]:
    """
    Navigate to the Gousto public menu and extract all recipe cards.

    Args:
        session_cookie: Value of the ``gousto_session`` cookie. When provided the
            scraper impersonates a logged-in user and returns the personalised
            weekly menu instead of the full public catalogue.
        debug: When True, saves an HTML snapshot to ``data/debug_menu.html`` so
            you can inspect DOM structure and tune selectors without re-running
            the full scrape.

    Returns:
        A list of :class:`~src.models.Recipe` objects.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        if session_cookie:
            await context.add_cookies(
                [
                    {
                        "name": "gousto_session",
                        "value": session_cookie,
                        "domain": _COOKIE_DOMAIN,
                        "path": "/",
                    }
                ]
            )

        page = await context.new_page()
        await page.goto(MENU_URL, wait_until="domcontentloaded", timeout=60_000)

        # Dismiss cookie consent banner if present
        try:
            accept_btn = page.get_by_role("button", name=re.compile(r"accept all", re.I))
            await accept_btn.wait_for(timeout=8_000)
            await accept_btn.click()
        except Exception:
            pass  # Banner may not appear in headless / already accepted

        # Wait for at least one recipe card to appear
        card_selector = '[data-testing="menuRecipeViewDetails"]'
        try:
            await page.wait_for_selector(card_selector, timeout=30_000)
        except Exception:
            # Fallback: wait for network to settle and grab whatever rendered
            await page.wait_for_load_state("networkidle", timeout=30_000)

        # Scroll to the bottom to trigger any lazy-loading
        await _scroll_to_bottom(page)

        if debug:
            _save_debug_snapshot(await page.content())

        raw_cards = await page.evaluate(_EXTRACT_JS)
        await browser.close()

    return [_parse_card(card) for card in raw_cards]


async def _scroll_to_bottom(page) -> None:
    """Gradually scroll the page so lazy-loaded cards are rendered."""
    for _ in range(10):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        await asyncio.sleep(0.4)
    # Scroll back up so the full DOM is stable
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.5)


def _save_debug_snapshot(html: str) -> None:
    out = Path("data/debug_menu.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[debug] HTML snapshot saved to {out}")


# ---------------------------------------------------------------------------
# JavaScript injected into the page to pull structured data from recipe cards.
# Gousto's React app renders data into the DOM; we read visible text rather
# than relying on internal JS state so the selectors stay stable across builds.
# ---------------------------------------------------------------------------
_EXTRACT_JS = """
() => {
    const DIETARY_MAP = {
        "gluten free":  "GF",
        "dairy free":   "DF",
        "vegetarian":   "V",
        "vegan":        "VE",
        "plant-based":  "PB",
        "plant based":  "PB",
    };

    const results = [];
    const cards = document.querySelectorAll('[data-testing="menuRecipeViewDetails"]');

    for (const card of cards) {
        const rawLabel = card.getAttribute("aria-label") || "";
        if (!rawLabel) continue;

        // Decode HTML entities via a throwaway element
        const tmp = document.createElement("textarea");
        tmp.innerHTML = rawLabel;
        const label = tmp.value;

        // Format: "Name. [Dietary tag. ...] N mins. N calories"
        const parts = label.split(". ").map(s => s.trim()).filter(Boolean);
        if (parts.length < 2) continue;

        // Last two parts are always "N mins" and "N calories"
        const calPart   = parts.pop();
        const timePart  = parts.pop();

        const calMatch   = calPart.match(/(\\d+)/);
        const timeMatch  = timePart.match(/(\\d+)/);
        const calories       = calMatch  ? parseInt(calMatch[1],  10) : null;
        const cook_time_mins = timeMatch ? parseInt(timeMatch[1], 10) : null;

        // Partition remaining parts into dietary tags vs. name fragments.
        // Names can contain ". " so we re-join non-dietary parts.
        const DIETARY_KEYS = Object.keys(DIETARY_MAP);
        const dietary_tags = [];
        const nameParts    = [];
        for (const part of parts) {
            if (DIETARY_MAP[part.toLowerCase()]) {
                dietary_tags.push(DIETARY_MAP[part.toLowerCase()]);
            } else {
                nameParts.push(part);
            }
        }
        const name = nameParts.join(". ");
        if (!name) continue;

        // Surcharge
        const surchargeEl = card.querySelector('[data-testing="menuRecipeCardSurchargeAmount"]');
        const surchargeText = surchargeEl ? surchargeEl.textContent.trim() : "";
        const costMatch = surchargeText.match(/\\+?£(\\d+\\.\\d{2})/);
        const extra_cost_gbp = costMatch ? parseFloat(costMatch[1]) : null;
        const has_extra_cost = extra_cost_gbp !== null;

        // Customisable
        const is_customisable = !!card.querySelector('[data-testid="SwapAlternativeOptionsButton"]');

        // Categories (badge-style tags visible on the card)
        const categories = [];
        card.querySelectorAll('[class*="badge"], [class*="Badge"], [class*="Tag"], [class*="tag"]')
            .forEach(el => {
                const t = el.textContent.trim();
                const tUp = t.toUpperCase();
                if (t && t.length < 40 && !["GF","DF","V","VE","PB"].includes(tUp)
                    && !t.match(/^\\d/))
                    categories.push(t);
            });
        const unique_cats = [...new Set(categories)];

        results.push({
            name,
            cook_time_mins,
            calories,
            dietary_tags,
            categories: unique_cats,
            has_extra_cost,
            extra_cost_gbp,
            is_customisable,
        });
    }
    return results;
}
"""


def _parse_card(card: dict) -> Recipe:
    return Recipe(
        name=card["name"],
        cook_time_mins=card.get("cook_time_mins"),
        calories=card.get("calories"),
        dietary_tags=card.get("dietary_tags", []),
        categories=card.get("categories", []),
        has_extra_cost=card.get("has_extra_cost", False),
        extra_cost_gbp=card.get("extra_cost_gbp"),
        is_customisable=card.get("is_customisable", False),
    )
