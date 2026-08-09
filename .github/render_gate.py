import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

PRIMARY = os.environ.get("NIMA_PRIMARY_URL", "https://nimapets.com").rstrip("/")
FALLBACK = os.environ.get("NIMA_FALLBACK_URL", "https://gbe01p-0e.myshopify.com").rstrip("/")
THEME_ID = os.environ.get("NIMA_PREVIEW_THEME_ID", "199660142673")
PRODUCT_HANDLE = os.environ.get(
    "NIMA_PRODUCT_HANDLE",
    "anti-splash-water-bowl-for-dogs-1l-large-capacity-drinker-drinking-bowls-dog-waterer-for-puppy-cat-pet-accessories",
)
VARIANT_ID = int(os.environ.get("NIMA_VARIANT_ID", "59833605062737"))
OUT = Path(os.environ.get("NIMA_RENDER_OUT", "render-gate-evidence"))
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

ROUTES = {
    "home": "/",
    "collection": "/collections/frontpage",
    "pdp": f"/products/{PRODUCT_HANDLE}",
    "search": "/search?q=water",
    "cart": "/cart",
}


def localized_path(locale: str, path: str) -> str:
    if locale == "en":
        return path
    if path == "/":
        return "/es"
    return "/es" + path


def preview_url(base: str, locale: str, route: str) -> str:
    path = localized_path(locale, ROUTES[route])
    separator = "&" if "?" in path else "?"
    return f"{base}{path}{separator}{urlencode({'preview_theme_id': THEME_ID})}"


async def choose_base(page) -> str:
    errors = []
    for base in (PRIMARY, FALLBACK):
        try:
            response = await page.goto(
                f"{base}/?preview_theme_id={THEME_ID}",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            if response and response.status < 500:
                await page.wait_for_timeout(1000)
                return base
            errors.append(f"{base}: HTTP {response.status if response else 'no response'}")
        except Exception as exc:
            errors.append(f"{base}: {type(exc).__name__}: {exc}")
    raise AssertionError("No storefront preview endpoint was reachable: " + " | ".join(errors))


async def wait_stable(page):
    await page.wait_for_load_state("domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=12000)
    except Exception:
        pass
    await page.wait_for_timeout(900)


async def assert_preview_asset(page):
    count = await page.locator('link[href*="premium-experience.css"]').count()
    assert count > 0, "premium-experience.css is absent; preview RC may not be active"


async def assert_locale(page, locale: str):
    lang = (await page.locator("html").get_attribute("lang") or "").lower()
    assert lang.startswith(locale), f"Expected locale {locale}, got html lang={lang!r}"


async def assert_no_translation_marker(page):
    body = (await page.locator("body").inner_text()).lower()
    assert "translation missing" not in body, "Visible translation missing marker found"


async def assert_no_horizontal_overflow(page):
    metrics = await page.evaluate(
        """() => ({
          docScroll: document.documentElement.scrollWidth,
          docClient: document.documentElement.clientWidth,
          bodyScroll: document.body ? document.body.scrollWidth : 0,
          inner: window.innerWidth
        })"""
    )
    tolerance = 2
    assert metrics["docScroll"] <= metrics["docClient"] + tolerance, f"Horizontal overflow: {metrics}"


async def assert_commerce_media(page, route: str):
    selectors = []
    if route in {"home", "collection", "search"}:
        selectors.append(".pcard__media img")
    if route == "pdp":
        selectors.extend(["[data-gallery-main]", "[data-gallery-thumb] img"])
    if route == "cart":
        selectors.append(".cart-item__media img")

    checked = 0
    for selector in selectors:
        loc = page.locator(selector)
        count = min(await loc.count(), 8)
        for i in range(count):
            item = loc.nth(i)
            if not await item.is_visible():
                continue
            style = await item.evaluate(
                """el => {
                  const s = getComputedStyle(el);
                  const p = el.parentElement ? getComputedStyle(el.parentElement) : null;
                  return {fit:s.objectFit, box:s.boxSizing, bg:s.backgroundColor, parentBg:p?.backgroundColor || ''};
                }"""
            )
            assert style["fit"] == "contain", f"{selector} must use object-fit: contain, got {style}"
            assert style["box"] == "border-box", f"{selector} must use border-box, got {style}"
            checked += 1
    if route in {"collection", "pdp", "search", "cart"}:
        assert checked > 0, f"No visible commerce media checked on {route}"


async def assert_pdp_gallery(page, viewport_name: str):
    main = page.locator("[data-gallery-main]")
    assert await main.count() == 1, "PDP main gallery image missing"
    thumbs = page.locator("[data-gallery-thumb]")
    count = await thumbs.count()
    if count <= 1:
        return

    rects = []
    for i in range(min(count, 8)):
        box = await thumbs.nth(i).bounding_box()
        if box:
            rects.append(box)
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            x_overlap = min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"])
            y_overlap = min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"])
            assert not (x_overlap > 1 and y_overlap > 1), f"PDP thumbnails overlap: {a} vs {b}"

    if len(rects) >= 2:
        dx = abs(rects[1]["x"] - rects[0]["x"])
        dy = abs(rects[1]["y"] - rects[0]["y"])
        if viewport_name == "desktop":
            assert dy > dx, f"Desktop thumbnails are not a vertical rail: {rects[:2]}"
        else:
            assert dx > dy, f"Mobile thumbnails are not a horizontal rail: {rects[:2]}"

    old_src = await main.get_attribute("src")
    target = thumbs.nth(1)
    await target.click()
    await page.wait_for_timeout(250)
    new_src = await main.get_attribute("src")
    assert new_src and new_src != old_src, "Thumbnail click did not update PDP main image"


async def assert_variant_interaction(page):
    variants = page.locator("[data-variant-option]:not([disabled])")
    count = await variants.count()
    if count < 2:
        return
    hidden_id = page.locator('form[action*="/cart/add"] input[name="id"]')
    before = await hidden_id.get_attribute("value")
    await variants.nth(1).check(force=True)
    await page.wait_for_timeout(250)
    after = await hidden_id.get_attribute("value")
    assert after and after != before, f"Variant interaction did not update product form id: {before} -> {after}"


async def prepare_cart(page):
    result = await page.evaluate(
        """async (variantId) => {
          const root = (window.Shopify && window.Shopify.routes && window.Shopify.routes.root) || '/';
          await fetch(root + 'cart/clear.js', {method:'POST', headers:{'Accept':'application/json'}});
          const response = await fetch(root + 'cart/add.js', {
            method:'POST',
            headers:{'Content-Type':'application/json','Accept':'application/json'},
            body: JSON.stringify({id: variantId, quantity: 1})
          });
          return {ok: response.ok, status: response.status, text: await response.text()};
        }""",
        VARIANT_ID,
    )
    assert result["ok"], f"Could not seed cart session: HTTP {result['status']} {result['text'][:300]}"


async def run_case(browser, base: str, locale: str, viewport_name: str):
    viewport = VIEWPORTS[viewport_name]
    context = await browser.new_context(viewport=viewport, device_scale_factor=1)
    page = await context.new_page()
    page.set_default_timeout(15000)
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    results = []
    try:
        for route in ("home", "collection", "pdp", "search"):
            url = preview_url(base, locale, route)
            response = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            assert response and response.status < 400, f"{route} returned HTTP {response.status if response else 'none'}"
            await wait_stable(page)
            await assert_preview_asset(page)
            await assert_locale(page, locale)
            await assert_no_translation_marker(page)
            await assert_no_horizontal_overflow(page)
            await assert_commerce_media(page, route)
            if route == "pdp":
                await assert_pdp_gallery(page, viewport_name)
                await assert_variant_interaction(page)
                await prepare_cart(page)
            shot = OUT / f"{locale}-{viewport_name}-{route}.png"
            await page.screenshot(path=str(shot), full_page=True)
            results.append({"locale": locale, "viewport": viewport_name, "route": route, "url": page.url, "screenshot": shot.name, "status": "PASS"})

        cart_url = preview_url(base, locale, "cart")
        response = await page.goto(cart_url, wait_until="domcontentloaded", timeout=45000)
        assert response and response.status < 400, f"cart returned HTTP {response.status if response else 'none'}"
        await wait_stable(page)
        await assert_preview_asset(page)
        await assert_locale(page, locale)
        await assert_no_translation_marker(page)
        await assert_no_horizontal_overflow(page)
        await assert_commerce_media(page, "cart")
        assert await page.locator(".cart-item").count() >= 1, "Populated cart did not render a cart item"
        assert await page.locator(".cart-summary").count() == 1, "Cart summary missing"
        shot = OUT / f"{locale}-{viewport_name}-cart.png"
        await page.screenshot(path=str(shot), full_page=True)
        results.append({"locale": locale, "viewport": viewport_name, "route": "cart", "url": page.url, "screenshot": shot.name, "status": "PASS"})
    finally:
        await context.close()
    return results, console_errors


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        probe_context = await browser.new_context(viewport=VIEWPORTS["desktop"])
        probe = await probe_context.new_page()
        base = await choose_base(probe)
        await probe_context.close()

        report = {"theme_id": THEME_ID, "selected_base": base, "cases": [], "console_errors": [], "status": "PASS"}
        try:
            for locale in ("en", "es"):
                for viewport in ("desktop", "mobile"):
                    cases, errors = await run_case(browser, base, locale, viewport)
                    report["cases"].extend(cases)
                    report["console_errors"].extend({"locale": locale, "viewport": viewport, "message": e} for e in errors)
        except Exception as exc:
            report["status"] = "FAIL"
            report["failure"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
            lines = ["# Nima Render Gate", "", f"- Theme: `{THEME_ID}`", f"- Base: `{base}`", f"- Status: **{report['status']}**", f"- Cases completed: {len(report['cases'])}/20"]
            if report.get("failure"):
                lines.append(f"- Failure: `{report['failure']}`")
            lines.extend(["", "## Evidence", ""])
            for item in report["cases"]:
                lines.append(f"- {item['locale'].upper()} · {item['viewport']} · {item['route']} — PASS — `{item['screenshot']}`")
            (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
