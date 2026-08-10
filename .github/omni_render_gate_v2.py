import asyncio

import omni_render_gate as gate


async def assert_home_fundamentals(page, viewport: str):
    assert await page.locator('link[href*="fundamentals.css"]').count() > 0, "Fundamentals protection layer missing"

    story = page.locator(".premium-story")
    copy = page.locator(".premium-story__copy")
    media = page.locator(".premium-story__media")
    assert await story.count() == 1, "Home care story missing"
    assert await copy.count() == 1 and await media.count() == 1, "Home story must keep separate copy and media regions"

    geometry = await page.evaluate(
        """() => {
          const copy = document.querySelector('.premium-story__copy');
          const media = document.querySelector('.premium-story__media');
          const heading = copy && copy.querySelector('h2');
          const paragraph = copy && copy.querySelector('p');
          const c = copy.getBoundingClientRect();
          const m = media.getBoundingClientRect();
          const copyStyle = getComputedStyle(copy);
          const headingStyle = getComputedStyle(heading);
          const paragraphStyle = getComputedStyle(paragraph);
          return {
            copy: {x:c.x,y:c.y,w:c.width,h:c.height,right:c.right,bottom:c.bottom},
            media: {x:m.x,y:m.y,w:m.width,h:m.height,right:m.right,bottom:m.bottom},
            copyPosition: copyStyle.position,
            copyBgColor: copyStyle.backgroundColor,
            copyBgImage: copyStyle.backgroundImage,
            headingColor: headingStyle.color,
            paragraphColor: paragraphStyle.color,
            headingSize: parseFloat(headingStyle.fontSize),
            paragraphSize: parseFloat(paragraphStyle.fontSize)
          };
        }"""
    )

    c = geometry["copy"]
    m = geometry["media"]
    overlap_x = max(0, min(c["right"], m["right"]) - max(c["x"], m["x"]))
    overlap_y = max(0, min(c["bottom"], m["bottom"]) - max(c["y"], m["y"]))
    overlap_area = overlap_x * overlap_y
    assert overlap_area <= 2, f"Home story text overlaps lifestyle image: {geometry}"

    has_opaque_color = geometry["copyBgColor"] not in {"rgba(0, 0, 0, 0)", "transparent"}
    has_background_image = geometry["copyBgImage"] not in {"none", ""}
    assert has_opaque_color or has_background_image, f"Home story copy panel has no readable background: {geometry}"
    assert geometry["headingSize"] >= 34, f"Home story heading became too small: {geometry}"
    assert geometry["paragraphSize"] >= 14, f"Home story body became too small: {geometry}"

    if viewport == "desktop":
        assert c["right"] <= m["x"] + 2 or m["right"] <= c["x"] + 2, f"Desktop story must be side-by-side: {geometry}"
    else:
        assert m["bottom"] <= c["y"] + 2, f"Mobile story must place media before copy without overlay: {geometry}"


async def assert_surface_geometry(page, route: str, viewport: str):
    if route == "home":
        cards = page.locator(".shop-window__grid .pcard")
        assert await cards.count() >= 3, "Home shop window needs at least 3 product cards"
        if viewport == "desktop":
            grid = page.locator(".shop-window__grid")
            columns = await grid.evaluate("el => getComputedStyle(el).gridTemplateColumns")
            assert len(columns.split()) >= 4, f"Desktop Home commerce grid not stable: {columns}"
        await assert_home_fundamentals(page, viewport)
    elif route == "collection":
        cards = page.locator("[data-product-grid] .pcard")
        assert await cards.count() > 0, "Collection rendered no product cards"
        first = cards.first
        geometry = await first.evaluate(
            "el => {const s=getComputedStyle(el);return {columnStart:s.gridColumnStart,columnEnd:s.gridColumnEnd,rowStart:s.gridRowStart,rowEnd:s.gridRowEnd}}"
        )
        assert "span 2" not in " ".join(geometry.values()), f"Collection first SKU is still oversized: {geometry}"
        if viewport == "desktop":
            columns = await page.locator("[data-product-grid]").evaluate("el => getComputedStyle(el).gridTemplateColumns")
            assert len(columns.split()) >= 4, f"Desktop Collection does not expose four-column commerce rhythm: {columns}"
    elif route == "pdp":
        assert await page.locator("[data-gallery-main]").count() == 1, "PDP main gallery image missing"
        assert await page.locator("[data-product-form]").count() == 1, "PDP product form missing"
        assert await page.locator("[data-add-btn]").count() == 1, "PDP add-to-cart control missing"
    elif route == "search":
        assert await page.locator(".search-form input[name='q']").count() == 1, "Search query input missing"
        assert await page.locator(".search-form button[type='submit']").count() == 1, "Search submit missing"
    elif route == "cart":
        assert await page.locator(".cart-summary").count() == 1, "Cart summary missing"
        assert await page.locator("button[name='checkout']").count() == 1, "Checkout button missing"
        assert await page.locator("input[name='updates[]']").count() >= 1, "Cart quantity contract missing"


gate.assert_surface_geometry = assert_surface_geometry

if __name__ == "__main__":
    asyncio.run(gate.main())
