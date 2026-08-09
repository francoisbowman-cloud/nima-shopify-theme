# Nima — Launch Cutover Checklist

Purpose: move from merged launch code to a controlled live release without adding new feature scope.

Current storefront source: `main`

PR #4: **MERGED**

Launch merge commit: `d7c118872f089b4182aff6e1b065e990d88b27a9`

Commercial truth hardening after merge: through `fb35af45a53942b57ba5460cb3a66b54c56f8449`

## Gate A — Theme preview

- [ ] Open a Shopify preview from the current `main` revision.
- [ ] Home desktop: hero → editorial shop window → split → Magazine teaser render in that order.
- [ ] Home mobile: no horizontal overflow; product cards stack cleanly; CTA remains visible.
- [ ] PDP desktop: gallery, variants, price, availability, add-to-cart, OVL story, routine cross-sell.
- [ ] PDP mobile: purchase controls remain readable and tappable; cross-sell does not crowd the buy flow.
- [ ] Collection page: filters/sort/product cards still render after locale changes.
- [ ] EN and ES: no raw translation keys appear.
- [ ] Announcement bar switches language correctly.
- [ ] Run `shopify theme check theme --fail-level error` on this exact revision.
- [ ] Run `pytest -q tests/test_launch_theme_contract.py` on this exact revision.

## Gate B — Catalog / commercial truth

- [ ] Confirm every launch-priority product has a commerce-primary image on a consistent white background.
- [ ] Confirm no supplier/AliExpress/AutoDS branding is visible in launch-priority images or alt text.
- [x] Premium outlier prices are structurally coherent in the approved 2026-08-03 catalog export: Elevated Dog Bed `$165.01` vs cost `$133.13`; Critter Nation `$404.82` vs cost `$326.98`.
- [ ] Confirm those premium prices still match live Shopify before traffic starts.
- [ ] Confirm compare-at prices, if present, are real and not artificial markdowns.
- [ ] Confirm product availability and shipping expectations match AutoDS/source truth.

## Gate C — Shipping and policy truth

- [x] Removed the unverified `Free shipping from $50` promise from the theme.
- [x] Removed the unverified 30-day-return promise from the PDP fallback copy.
- [x] Theme now uses conservative copy: shipping within the United States + secure checkout, with returns delegated to the real policy.
- [ ] Confirm United States remains an active market and shippable destination in current Shopify configuration.
- [ ] Confirm the live shipping amount/rule at checkout. Historical project evidence records `Free Shipping` at `$0.00 USD`; checkout is final authority.
- [ ] Confirm refund/return policy content and URL are correct.
- [ ] Confirm contact/support information is reachable.

## Gate D — Payment and checkout

Historical project state records PayPal Business as configured/active, but current production behavior must be exercised.

- [ ] Verify PayPal Business is active in production mode.
- [ ] Verify guest/card checkout is available where the account permits it.
- [ ] Add one normal-priced product to cart from desktop.
- [ ] Repeat add-to-cart from mobile.
- [ ] Complete one end-to-end test purchase using a real shippable U.S. address and a controlled low-risk SKU/order.
- [ ] Confirm order appears in Shopify Admin.
- [ ] Confirm AutoDS receives/synchronizes the order as expected before scaling traffic.
- [ ] Confirm confirmation email and order status page are correct.
- [ ] Refund/cancel the controlled order if it was created only for validation and fulfillment is not desired.

## Gate E — Analytics baseline

Use Shopify native analytics as the minimum launch source of truth. Do not add duplicate GA/pixels blindly before launch.

- [ ] Confirm Shopify records an online-store session.
- [ ] Confirm add-to-cart activity is observable.
- [ ] Confirm checkout initiation is observable.
- [ ] Confirm the controlled purchase appears in sales/conversion reporting.
- [ ] Record baseline values before external traffic: sessions, conversion rate, AOV, add-to-cart rate, checkout rate, purchase count.

Optional external analytics can be added after the native funnel is verified and only with a clear measurement purpose.

## Gate F — Catalog AI v0.3.1

This gate is separate from storefront code.

- [ ] Run the residual edge-matte implementation on the original feeding-mat asset.
- [ ] Compare pre-warp and post-warp against white, mid-gray, and dark backgrounds.
- [ ] Confirm no material erosion of valid product edges.
- [ ] If clean: mark `HALO FIX VALIDATED` and close v0.3.1.
- [ ] If residual fringe remains: preserve evidence; do not tune thresholds blindly.

For launch, prioritize already-clean commerce-primary assets. Do not block the entire store because one contextual pipeline edge case still requires validation.

## Cutover sequence

Merge is already complete. Execute after Gates A–E pass for the storefront:

1. Record the exact validated `main` SHA.
2. Publish/update the Shopify theme from that validated revision.
3. Re-run Home/Collection/PDP/cart/checkout smoke tests on `nimapets.com`.
4. Verify EN/ES on the live domain.
5. Record launch timestamp and baseline metrics.
6. Start controlled traffic with organic/editorial channels first.
7. Confirm first real orders sync through Shopify → AutoDS before increasing acquisition.
8. Do not increase paid acquisition until checkout and fulfillment are proven with real orders.

## First-sales operating loop

After launch, Nima leaves build mode. Prioritize:

`traffic → product view → add to cart → checkout → purchase → fulfillment → feedback → optimization`

For the first sales, optimize only from observed bottlenecks. Do not add features merely because they are common in other stores.

## Stop conditions

Pause acquisition immediately if any of the following occurs:

- checkout cannot complete;
- shipping price/rules differ from displayed expectations;
- AutoDS does not synchronize orders correctly;
- product price or availability is materially wrong;
- primary product imagery misrepresents the real product;
- refund/support path is unavailable.

This checklist is the release contract for Nima's first controlled production launch.
