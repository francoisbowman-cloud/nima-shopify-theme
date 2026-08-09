import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlencode

from playwright.async_api import async_playwright

PRIMARY = os.getenv("NIMA_PRIMARY_URL", "https://nimapets.com").rstrip("/")
FALLBACK = os.getenv("NIMA_FALLBACK_URL", "https://gbe01p-0e.myshopify.com").rstrip("/")
THEME_ID = os.getenv("NIMA_PREVIEW_THEME_ID", "199660142673")
OUT = Path(os.getenv("NIMA_EDITORIAL_MEDIA_OUT", "editorial-media-gate-evidence"))
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {"desktop": {"width": 1440, "height": 900}, "mobile": {"width": 390, "height": 844}}
ROUTES = {
    "magazine": "pages/magazine",
    "grooming-gloves": "products/pet-grooming-gloves-dog-brush-mitt-deshedding-hair-removal-massage-horse-pair",
    "denim-overalls": "products/dog-costume-clothes-cute-denim-overalls-for-small-medium-pets-boy-girl-dogs-coats-jeans-t-shirts-sweatshirts",
}


def preview_url(base, root, route):
    root = root if root.startswith("/") else "/" + root
    if not root.endswith("/"):
        root += "/"
    sep = "&" if "?" in ROUTES[route] else "?"
    return f"{base}{root}{ROUTES[route]}{sep}{urlencode({'preview_theme_id': THEME_ID})}"


async def settle(page):
    await page.wait_for_load_state("domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    await page.wait_for_timeout(700)


async def reveal_page(page):
    height = await page.evaluate("document.documentElement.scrollHeight")
    viewport = await page.evaluate("window.innerHeight")
    for y in range(0, max(height, viewport), max(320, int(viewport * 0.7))):
        await page.evaluate("y => window.scrollTo(0, y)", y)
        await page.wait_for_timeout(100)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(1900)


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


async def establish_locale(page, base, locale):
    response = await page.goto(f"{base}/?preview_theme_id={THEME_ID}", wait_until="domcontentloaded", timeout=45000)
    assert response and response.status < 400
    await settle(page)
    switcher = page.locator(f'.language-switcher__option[value="{locale}"]')
    current = (await page.locator("html").get_attribute("lang") or "").lower()
    if not current.startswith(locale):
        assert await switcher.count() == 1 and await switcher.is_visible(), f"Locale {locale} unavailable"
        async with page.expect_navigation(wait_until="domcontentloaded", timeout=45000):
            await switcher.click()
        await settle(page)
    active = (await page.locator("html").get_attribute("lang") or "").lower()
    assert active.startswith(locale), f"Expected {locale}, got {active}"
    root = await page.evaluate("window.Shopify && window.Shopify.routes ? window.Shopify.routes.root : '/' ")
    assert isinstance(root, str) and root.startswith("/")
    return root


async def common_checks(page, locale):
    assert await page.locator('link[href*="premium-experience.css"]').count() > 0, "premium-experience.css missing"
    lang = (await page.locator("html").get_attribute("lang") or "").lower()
    assert lang.startswith(locale)
    text = (await page.locator("body").inner_text()).lower()
    assert "translation missing" not in text
    overflow = await page.evaluate("() => ({scroll:document.documentElement.scrollWidth, client:document.documentElement.clientWidth})")
    assert overflow["scroll"] <= overflow["client"] + 2, f"Horizontal overflow: {overflow}"


async def magazine_checks(page):
    hero = page.locator(".mag-hero")
    assert await hero.count() == 1 and await hero.is_visible(), "Magazine hero missing"
    content = page.locator(".mag-hero__content")
    assert await content.count() == 1 and await content.is_visible(), "Magazine hero copy missing"
    color = await content.evaluate("el => getComputedStyle(el).color")
    assert color in {"rgb(255, 255, 255)", "rgba(255, 255, 255, 1)"}, f"Magazine hero copy not white: {color}"
    assert await page.locator(".mag-grid .feature").count() >= 1, "Magazine feature story missing"
    assert await page.locator(".mag-grid .side-story").count() >= 1, "Magazine side stories missing"


async def commerce_pdp_checks(page, label):
    main = page.locator("[data-gallery-main]")
    assert await main.count() == 1 and await main.is_visible(), f"{label}: main commerce image missing"
    style = await main.evaluate("el => { const s=getComputedStyle(el); return {fit:s.objectFit,box:s.boxSizing,bg:s.backgroundColor}; }")
    assert style["fit"] == "contain", f"{label}: object-fit={style['fit']}"
    assert style["box"] == "border-box", f"{label}: box-sizing={style['box']}"
    parent_bg = await main.evaluate("el => getComputedStyle(el.parentElement).backgroundColor")
    whites = {"rgb(255, 255, 255)", "rgba(255, 255, 255, 1)"}
    assert parent_bg in whites or style["bg"] in whites, f"{label}: canvas not white: image={style['bg']} parent={parent_bg}"
    rect = await main.bounding_box()
    assert rect and rect["width"] > 120 and rect["height"] > 120, f"{label}: image collapsed: {rect}"


async def run_context(browser, base, locale, viewport_name, report):
    context = await browser.new_context(viewport=VIEWPORTS[viewport_name], device_scale_factor=1)
    page = await context.new_page()
    page.set_default_timeout(15000)
    try:
        root = await establish_locale(page, base, locale)
        for route in ROUTES:
            response = await page.goto(preview_url(base, root, route), wait_until="domcontentloaded", timeout=45000)
            assert response and response.status < 400, f"{route}: HTTP {response.status if response else 'none'}"
            await settle(page)
            await reveal_page(page)
            await common_checks(page, locale)
            if route == "magazine":
                await magazine_checks(page)
            else:
                await commerce_pdp_checks(page, route)
            shot = OUT / f"{locale}-{viewport_name}-{route}.png"
            await page.screenshot(path=str(shot), full_page=True)
            report["cases"].append({"locale": locale, "viewport": viewport_name, "route": route, "url": page.url, "screenshot": shot.name, "status": "PASS"})
    finally:
        await context.close()


async def main():
    report = {"theme_id": THEME_ID, "cases": [], "status": "PASS"}
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
            total = len(ROUTES) * 4
            lines = ["# Nima Editorial + Media Gate", "", f"- Theme: `{THEME_ID}`", f"- Base: `{base}`", f"- Status: **{report['status']}**", f"- Cases completed: {len(report['cases'])}/{total}"]
            if report.get("failure"):
                lines.append(f"- Failure: `{report['failure']}`")
            lines += ["", "## Evidence", ""] + [f"- {c['locale'].upper()} · {c['viewport']} · {c['route']} — PASS — `{c['screenshot']}`" for c in report["cases"]]
            (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
