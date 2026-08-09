import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

PRIMARY = os.getenv("NIMA_PRIMARY_URL", "https://nimapets.com").rstrip("/")
FALLBACK = os.getenv("NIMA_FALLBACK_URL", "https://gbe01p-0e.myshopify.com").rstrip("/")
THEME_ID = os.getenv("NIMA_PREVIEW_THEME_ID", "199660142673")
PRODUCT_HANDLE = os.getenv("NIMA_PRODUCT_HANDLE", "anti-splash-water-bowl-for-dogs-1l-large-capacity-drinker-drinking-bowls-dog-waterer-for-puppy-cat-pet-accessories")
VARIANT_ID = int(os.getenv("NIMA_VARIANT_ID", "59833605062737"))
OUT = Path(os.getenv("NIMA_RENDER_OUT", "render-gate-evidence"))
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {"desktop": {"width": 1440, "height": 900}, "mobile": {"width": 390, "height": 844}}
ROUTES = {
    "home": "/",
    "collection": "/collections/frontpage",
    "pdp": f"/products/{PRODUCT_HANDLE}",
    "search": "/search?q=water",
    "cart": "/cart",
}


def path_for(locale, route):
    path = ROUTES[route]
    if locale == "es":
        path = "/es" if path == "/" else "/es" + path
    return path


def url_for(base, locale, route):
    path = path_for(locale, route)
    sep = "&" if "?" in path else "?"
    return f"{base}{path}{sep}{urlencode({'preview_theme_id': THEME_ID})}"


def cart_permalink(base, locale):
    prefix = "/es" if locale == "es" else ""
    params = urlencode({"storefront": "true", "preview_theme_id": THEME_ID})
    return f"{base}{prefix}/cart/{VARIANT_ID}:1?{params}"


async def settle(page):
    await page.wait_for_load_state("domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    await page.wait_for_timeout(500)


async def reveal_page(page):
    # IntersectionObserver-driven content should be captured after a realistic scroll pass.
    await page.evaluate("window.scrollTo(0, 0)")
    height = await page.evaluate("document.documentElement.scrollHeight")
    viewport = await page.evaluate("window.innerHeight")
    step = max(320, int(viewport * 0.7))
    y = 0
    while y < height:
        await page.evaluate("y => window.scrollTo(0, y)", y)
        await page.wait_for_timeout(120)
        y += step
        height = max(height, await page.evaluate("document.documentElement.scrollHeight"))
    await page.evaluate("window.scrollTo(0, 0)")
    # The storefront has a hard visibility failsafe at 1.8s; let that window close.
    await page.wait_for_timeout(2000)


async def select_base(page):
    failures = []
    for base in (PRIMARY, FALLBACK):
        try:
            response = await page.goto(f"{base}/?preview_theme_id={THEME_ID}", wait_until="domcontentloaded", timeout=45000)
            if response and response.status < 500:
                await settle(page)
                return base
            failures.append(f"{base}: HTTP {response.status if response else 'none'}")
        except Exception as exc:
            failures.append(f"{base}: {type(exc).__name__}: {exc}")
    raise AssertionError("No preview endpoint reachable: " + " | ".join(failures))


async def assert_visible_product_cards(page, route):
    if route not in {"collection", "search"}:
        return
    cards = page.locator(".product-grid .pcard")
    count = await cards.count()
    if route == "collection":
        assert count > 0, "Collection reports products but rendered no product cards"
    if count == 0:
        return
    visible = 0
    for i in range(min(count, 12)):
        card = cards.nth(i)
        if not await card.is_visible():
            continue
        geometry = await card.evaluate(
            """el => {
              const r = el.getBoundingClientRect();
              const s = getComputedStyle(el);
              return {width:r.width,height:r.height,opacity:parseFloat(s.opacity),visibility:s.visibility,display:s.display};
            }"""
        )
        assert geometry["width"] > 40 and geometry["height"] > 80, f"{route} card collapsed: {geometry}"
        assert geometry["opacity"] > 0.95, f"{route} card remained transparent: {geometry}"
        assert geometry["visibility"] != "hidden" and geometry["display"] != "none", f"{route} card hidden: {geometry}"
        visible += 1
    assert visible > 0, f"{route} contains product cards but none are visually visible"


async def invariant_checks(page, locale, route):
    assert await page.locator('link[href*="premium-experience.css"]').count() > 0, "RC marker asset missing"
    lang = (await page.locator("html").get_attribute("lang") or "").lower()
    assert lang.startswith(locale), f"Expected {locale}, got html lang={lang!r}"
    text = (await page.locator("body").inner_text()).lower()
    assert "translation missing" not in text, "Visible translation missing marker"
    overflow = await page.evaluate("() => ({scroll:document.documentElement.scrollWidth, client:document.documentElement.clientWidth})")
    assert overflow["scroll"] <= overflow["client"] + 2, f"Horizontal overflow: {overflow}"

    await assert_visible_product_cards(page, route)

    selectors = []
    if route in {"home", "collection", "search"}:
        selectors = [".pcard__media img"]
    elif route == "pdp":
        selectors = ["[data-gallery-main]", "[data-gallery-thumb] img"]
    elif route == "cart":
        selectors = [".cart-item__media img"]

    checked = 0
    for selector in selectors:
        loc = page.locator(selector)
        for i in range(min(await loc.count(), 8)):
            el = loc.nth(i)
            if not await el.is_visible():
                continue
            style = await el.evaluate("el => {const s=getComputedStyle(el); return {fit:s.objectFit, box:s.boxSizing};}")
            assert style["fit"] == "contain", f"{selector} fit={style['fit']}"
            assert style["box"] == "border-box", f"{selector} box-sizing={style['box']}"
            checked += 1
    if route in {"collection", "pdp", "search", "cart"}:
        assert checked > 0, f"No visible commerce media checked on {route}"


async def gallery_checks(page, viewport_name):
    main = page.locator("[data-gallery-main]")
    assert await main.count() == 1, "PDP main image missing"
    thumbs = page.locator("[data-gallery-thumb]")
    count = await thumbs.count()
    if count <= 1:
        return
    rects = [box for i in range(min(count, 8)) if (box := await thumbs.nth(i).bounding_box())]
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            xo = min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"])
            yo = min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"])
            assert not (xo > 1 and yo > 1), f"Thumbnail overlap: {a} vs {b}"
    if len(rects) >= 2:
        dx, dy = abs(rects[1]["x"] - rects[0]["x"]), abs(rects[1]["y"] - rects[0]["y"])
        assert (dy > dx) if viewport_name == "desktop" else (dx > dy), f"Wrong thumbnail rail orientation: {rects[:2]}"
    old = await main.get_attribute("src")
    await thumbs.nth(1).click()
    await page.wait_for_timeout(250)
    new = await main.get_attribute("src")
    assert new and new != old, "Thumbnail click did not change main image"


async def variant_checks(page):
    variants = page.locator("[data-variant-option]:not([disabled])")
    if await variants.count() < 2:
        return
    target = variants.nth(1)
    form = target.locator("xpath=ancestor::form[1]")
    hidden = form.locator('input[name="id"]')
    before = await hidden.get_attribute("value")
    label = target.locator("xpath=ancestor::label[1]")
    assert await label.count() == 1 and await label.is_visible(), "Visible variant label missing"
    await label.click()
    await page.wait_for_timeout(300)
    checked = await target.is_checked()
    after = await hidden.get_attribute("value")
    assert checked, "Visible variant control did not select its radio input"
    assert after and after != before, f"Variant form id did not update: {before} -> {after}"


async def populate_cart_with_permalink(page, base, locale):
    response = await page.goto(cart_permalink(base, locale), wait_until="domcontentloaded", timeout=45000)
    assert response and response.status < 400, f"Cart permalink HTTP {response.status if response else 'none'}"
    await settle(page)
    assert "verifying your connection" not in (await page.title()).lower(), "Shopify connection challenge intercepted cart permalink"
    assert await page.locator(".cart-item").count() >= 1, "Cart permalink did not render a populated cart"


async def run_context(browser, base, locale, viewport_name, report):
    context = await browser.new_context(viewport=VIEWPORTS[viewport_name], device_scale_factor=1)
    page = await context.new_page()
    page.set_default_timeout(15000)
    page.on("console", lambda msg: report["console_errors"].append({"locale": locale, "viewport": viewport_name, "message": msg.text}) if msg.type == "error" else None)
    try:
        for route in ("home", "collection", "pdp", "search"):
            response = await page.goto(url_for(base, locale, route), wait_until="domcontentloaded", timeout=45000)
            assert response and response.status < 400, f"{route} HTTP {response.status if response else 'none'}"
            await settle(page)
            await reveal_page(page)
            await invariant_checks(page, locale, route)
            shot = OUT / f"{locale}-{viewport_name}-{route}.png"
            await page.screenshot(path=str(shot), full_page=True)
            report["cases"].append({"locale": locale, "viewport": viewport_name, "route": route, "screenshot": shot.name, "status": "PASS"})
            if route == "pdp":
                await gallery_checks(page, viewport_name)
                await variant_checks(page)

        await populate_cart_with_permalink(page, base, locale)
        await reveal_page(page)
        await invariant_checks(page, locale, "cart")
        assert await page.locator(".cart-summary").count() == 1, "Cart summary missing"
        shot = OUT / f"{locale}-{viewport_name}-cart.png"
        await page.screenshot(path=str(shot), full_page=True)
        report["cases"].append({"locale": locale, "viewport": viewport_name, "route": "cart", "screenshot": shot.name, "status": "PASS"})
    finally:
        await context.close()


async def main():
    report = {"theme_id": THEME_ID, "cases": [], "console_errors": [], "status": "PASS"}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        probe_context = await browser.new_context(viewport=VIEWPORTS["desktop"])
        probe = await probe_context.new_page()
        base = await select_base(probe)
        report["selected_base"] = base
        await probe_context.close()
        try:
            for locale in ("en", "es"):
                for viewport in ("desktop", "mobile"):
                    await run_context(browser, base, locale, viewport, report)
        except Exception as exc:
            report["status"] = "FAIL"
            report["failure"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            lines = ["# Nima Render Gate", "", f"- Theme: `{THEME_ID}`", f"- Base: `{base}`", f"- Status: **{report['status']}**", f"- Cases completed: {len(report['cases'])}/20"]
            if report.get("failure"):
                lines.append(f"- Failure: `{report['failure']}`")
            lines += ["", "## Evidence", ""] + [f"- {c['locale'].upper()} · {c['viewport']} · {c['route']} — PASS — `{c['screenshot']}`" for c in report["cases"]]
            (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
