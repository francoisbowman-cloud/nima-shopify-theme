import asyncio
import os
from playwright.async_api import async_playwright

URL = os.getenv("NIMA_PRIMARY_URL", "https://nimapets.com").rstrip("/")
THEME_ID = os.getenv("NIMA_PREVIEW_THEME_ID", "199660142673")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(f"{URL}/pages/magazine?preview_theme_id={THEME_ID}", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(1500)
        text = await page.locator("body").inner_text()
        matches = [line.strip() for line in text.splitlines() if "translation missing" in line.lower()]
        print("MAGAZINE_TRANSLATION_MARKERS=" + repr(matches))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
