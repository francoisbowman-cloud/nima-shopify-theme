import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

PRIMARY = os.getenv("NIMA_PRIMARY_URL", "https://nimapets.com").rstrip("/")
FALLBACK = os.getenv("NIMA_FALLBACK_URL", "https://gbe01p-0e.myshopify.com").rstrip("/")
THEME_ID = os.getenv("NIMA_PREVIEW_THEME_ID", "199660142673")
PRODUCT_HANDLE = os.getenv(
    "NIMA_PRODUCT_HANDLE",
    "anti-splash-water-bowl-for-dogs-1l-large-capacity-drinker-drinking-bowls-dog-waterer-for-puppy-cat-pet-accessories",
)
VARIANT_ID = int(os.getenv("NIMA_VARIANT_ID", "59833605062737"))
OUT = Path(os.getenv("NIMA_RENDER_OUT", "omni-render-evidence"))
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}
ROUTES = {
    "home": "",
    "collection": "collections/all",
    "pdp": f"products/{PRODUCT_HANDLE}",
    "search": "search?q=water",
}


def route_url(base: str, locale: str, route: str) -> str:
    locale_prefix = "" if locale == "en" else f"{locale}/"
    path = f"/{locale_prefix}{ROUTES[route]}"
    sep = "&" if "?" in path else "?"
    return f"{base}{path}{sep}{urlencode({'preview_theme_id': THEME_ID})}"


def cart_permalink(base: str, locale: str) -> str:
    locale_prefix = "" if locale == "en" else f"{locale}/"
    params = urlencode({"storefront": "true", "preview_theme_id": THEME_ID})
    return f"{base}/{locale_prefix}cart/{VARIANT_ID}:1?{params}"


async def settle(page):
    await page.wait_for_load_state("domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    await page.wait_for_timeout(800)


async def reveal(page):
    await page.evaluate("window.scrollTo(0, 0)")
    height = await page.evaluate("document.documentElement.scrollHeight")
    viewport = await page.evaluate("window.innerHeight")
    step = max(360, int(viewport * 0.75))
    y = 0
    while y < height:
        await page.evaluate("y => window.scrollTo(0, y)", y)
        await page.wait_for_timeout(90)
        y += step
        height = max(height, await page.evaluate("document.documentElement.scrollHeight"))
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(900)


async def choose_base(page):
    failures = []
    for base in (PRIMARY, FALLBACK):
        try:
            response = await page.goto(
                f"{base}/?preview_theme_id={THEME_ID}",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            if response and response.status < 500:
                await settle(page)
                return base
            failures.append(f"{base}: HTTP {response.status if response else 'none'}")
        except Exception as exc:
            failures.append(f"{base}: {type(exc).__name__}: {exc}")
    raise AssertionError("No preview endpoint reachable: " + " | ".join(failures))


async def assert_common(page, locale: str, route: str):
    assert await page.locator('link[href*="omni-evolve.css"]').count() > 0, "OMNI marker asset missing"
    lang = (await page.locator("html").get_attribute("lang") or "").lower()
    assert lang.startswith(locale), f"Expected locale {locale}, got html lang={lang!r}"
    body_text = (await page.locator("body").inner_text()).lower()
    assert "translation missing" not in body_text, "Visible translation missing marker"
    overflow = await page.evaluate(
        "() => ({scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth})"
    )
    assert overflow["scroll"] <= overflow["client"] + 2, f"Horizontal overflow: {overflow}"

    expected = {
        "home": ".shop-window",
        "collection": ".collection-head",
        "pdp": ".template-product .product",
        "search": ".search-head",
        "cart": ".cart-layout",
    }
    assert await page.locator(expected[route]).count() > 0, f"Expected OMNI surface missing on {route}"


async def assert_commerce_media(page, route: str):
    if route in {"home", "collection", "search"}:
        selector = ".pcard__media img"
    elif route == "pdp":
        selector = "[data-gallery-main]"
    else:
        selector = ".cart-item img"
    loc = page.locator(selector)
    count = await loc.count()
    if route != "cart" or await page.locator(".cart-item").count() > 0:
        assert count > 0, f"No commerce media found on {route}"
    checked = 0
    for i in range(min(count, 10)):
        el = loc.nth(i)
        if not await el.is_visible():
            continue
        style = await el.evaluate(
            "el => {const s=getComputedStyle(el); return {fit:s.objectFit, box:s.boxSizing, bg:s.backgroundColor};}"
        )
        assert style["fit"] == "contain", f"{route} commerce media object-fit={style['fit']}"
        checked += 1
    if count:
        assert checked > 0, f"Commerce media exists but none visible on {route}"


async def assert_surface_geometry(page, route: str, viewport: str):
    if route == "home":
        cards = page.locator(".shop-window__grid .pcard")
        assert await cards.count() >= 3, "Home shop window needs at least 3 product cards"
        lead = page.locator(".shop-window__item--lead .pcard")
        assert await lead.count() == 1, "Home lead commerce anchor missing"
    elif route == "collection":
        cards = page.locator(".product-grid .pcard")
        assert await cards.count() > 0, "Collection rendered no product cards"
        first = cards.first
        if viewport == "desktop":
            geometry = await first.evaluate(
                "el => {const s=getComputedStyle(el); return {column:s.gridColumnEnd,row:s.gridRowEnd};}"
            )
            assert "span 2" in geometry["column"] or "span 2" in geometry["row"], (
                "Desktop collection merchandising anchor did not span the grid: " + str(geometry)
            )
    elif route == "pdp":
        assert await page.locator("[data-gallery-main]").count() == 1, "PDP main gallery image missing"
        assert await page.locator("[data-product-form]").count() == 1, "PDP product form missing"
        add = page.locator("[data-add-btn]")
        assert await add.count() == 1, "PDP add-to-cart control missing"
    elif route == "search":
        assert await page.locator(".search-form input[name='q']").count() == 1, "Search query input missing"
        assert await page.locator(".search-form button[type='submit']").count() == 1, "Search submit missing"
    elif route == "cart":
        assert await page.locator(".cart-summary").count() == 1, "Cart summary missing"
        assert await page.locator("button[name='checkout']").count() == 1, "Checkout button missing"
        assert await page.locator("input[name='updates[]']").count() >= 1, "Cart quantity contract missing"


async def run_case(browser, base: str, locale: str, viewport: str, report: dict):
    context = await browser.new_context(viewport=VIEWPORTS[viewport], device_scale_factor=1)
    page = await context.new_page()
    page.set_default_timeout(15000)
    page.on(
        "console",
        lambda msg: report["console_errors"].append(
            {"locale": locale, "viewport": viewport, "message": msg.text}
        )
        if msg.type == "error"
        else None,
    )
    try:
        for route in ("home", "collection", "pdp", "search"):
            response = await page.goto(route_url(base, locale, route), wait_until="domcontentloaded", timeout=45000)
            assert response and response.status < 400, f"{route} HTTP {response.status if response else 'none'}"
            await settle(page)
            await reveal(page)
            await assert_common(page, locale, route)
            await assert_commerce_media(page, route)
            await assert_surface_geometry(page, route, viewport)
            shot = OUT / f"{locale}-{viewport}-{route}.png"
            await page.screenshot(path=str(shot), full_page=True)
            report["cases"].append(
                {"locale": locale, "viewport": viewport, "route": route, "url": page.url, "screenshot": shot.name, "status": "PASS"}
            )

        response = await page.goto(cart_permalink(base, locale), wait_until="domcontentloaded", timeout=45000)
        assert response and response.status < 400, f"cart HTTP {response.status if response else 'none'}"
        await settle(page)
        await reveal(page)
        assert await page.locator(".cart-item").count() >= 1, "Cart permalink did not populate the cart"
        await assert_common(page, locale, "cart")
        await assert_commerce_media(page, "cart")
        await assert_surface_geometry(page, "cart", viewport)
        shot = OUT / f"{locale}-{viewport}-cart.png"
        await page.screenshot(path=str(shot), full_page=True)
        report["cases"].append(
            {"locale": locale, "viewport": viewport, "route": "cart", "url": page.url, "screenshot": shot.name, "status": "PASS"}
        )
    finally:
        await context.close()


async def main():
    report = {"theme_id": THEME_ID, "status": "PASS", "cases": [], "console_errors": []}
    base = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        probe_context = await browser.new_context(viewport=VIEWPORTS["desktop"])
        probe = await probe_context.new_page()
        try:
            base = await choose_base(probe)
            report["selected_base"] = base
        finally:
            await probe_context.close()
        try:
            for locale in ("en", "es"):
                for viewport in ("desktop", "mobile"):
                    await run_case(browser, base, locale, viewport, report)
        except Exception as exc:
            report["status"] = "FAIL"
            report["failure"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            lines = [
                "# Nima × OMNI Render Gate",
                "",
                f"- Theme: `{THEME_ID}`",
                f"- Base: `{base}`",
                f"- Status: **{report['status']}**",
                f"- Cases completed: {len(report['cases'])}/20",
            ]
            if report.get("failure"):
                lines.append(f"- Failure: `{report['failure']}`")
            lines += ["", "## Evidence", ""]
            lines += [
                f"- {c['locale'].upper()} · {c['viewport']} · {c['route']} — PASS — `{c['screenshot']}`"
                for c in report["cases"]
            ]
            (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
