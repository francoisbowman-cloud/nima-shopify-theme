# Nima — Launch Cutover Checklist

Purpose: move from merge-ready code to a controlled live launch without adding new feature scope.

## Gate A — Theme preview

- [ ] Create or open a Shopify preview for `feat/nima-production-readiness-launch` / PR #4.
- [ ] Home desktop: hero → editorial shop window → split → Magazine teaser render in that order.
- [ ] Home mobile: no horizontal overflow; product cards stack cleanly; CTA remains visible.
- [ ] PDP desktop: gallery, variants, price, availability, add-to-cart, OVL story, routine cross-sell.
- [ ] PDP mobile: purchase controls remain readable and tappable; cross-sell does not crowd the buy flow.
- [ ] Collection page: filters/sort/product cards still render after locale changes.
- [ ] EN and ES: no raw translation keys appear.
- [ ] Announcement bar switches language correctly.

## Gate B — Catalog / commercial truth

- [ ] Confirm every launch-priority product has a commerce-primary image on a consistent white background.
- [ ] Confirm no supplier/AliExpress/AutoDS branding is visible in launch-priority images or alt text.
- [ ] Confirm premium outlier prices are intentional before traffic starts.
- [ ] Confirm compare-at prices, if present, are real and not artificial markdowns.
- [ ] Confirm product availability and shipping expectations match AutoDS/source truth.

## Gate C — Shipping and policy truth

- [ ] Verify `Free shipping from $50` / `Envío gratis desde $50` is an actual active shipping rule.
- [ ] If not real, change the announcement copy before publish; never advertise an inactive benefit.
- [ ] Confirm United States is an active market and shippable destination.
- [ ] Confirm refund/return policy actually supports the 30-day statement used in theme copy.
- [ ] Confirm contact/support information is reachable.

## Gate D — Payment and checkout

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

This gate is separate from storefront code and must not be confused with PR #4.

- [ ] Run the residual edge-matte implementation on the original feeding-mat asset.
- [ ] Compare pre-warp and post-warp against white, mid-gray, and dark backgrounds.
- [ ] Confirm no material erosion of valid product edges.
- [ ] If clean: mark `HALO FIX VALIDATED` and close v0.3.1.
- [ ] If residual fringe remains: preserve evidence; do not tune thresholds blindly.

For launch, prioritize already-clean commerce-primary assets. Do not block the entire store because one contextual pipeline edge case still requires validation.

## Cutover sequence

Execute only after Gates A–E pass for the storefront:

1. Final review PR #4.
2. Merge PR #4 into `main`.
3. Confirm resulting `main` SHA.
4. Publish/update the Shopify theme from the validated merged revision.
5. Re-run Home/PDP/checkout smoke test on the live domain.
6. Record launch timestamp and baseline metrics.
7. Start controlled traffic with organic/editorial channels first.
8. Do not increase paid acquisition until checkout and fulfillment are proven with real orders.

## First-sales operating loop

After launch, Nima leaves build mode. Prioritize:

`traffic → product view → add to cart → checkout → purchase → fulfillment → feedback → optimization`

For the first sales, optimize only from observed bottlenecks. Do not add features merely because they are common in other stores.

## Stop conditions

Pause acquisition immediately if any of the following occurs:

- checkout cannot complete;
- shipping price/rules differ from advertised copy;
- AutoDS does not synchronize orders correctly;
- product price or availability is materially wrong;
- primary product imagery misrepresents the real product;
- refund/support path is unavailable.

This checklist is the release contract for Nima's first controlled production launch.