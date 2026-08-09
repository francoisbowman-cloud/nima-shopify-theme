# Nima — External Launch Gates

This file tracks only release checks that cannot be completed from GitHub source alone.

Current storefront source: `main`

Current cutover state: storefront launch code merged; Shopify publish not yet executed from this environment.

## Shopify preview / runtime

- [ ] Run Shopify preview from current `main`.
- [ ] Run `shopify theme check theme --fail-level error`.
- [ ] Run `pytest -q tests/test_launch_theme_contract.py`.
- [ ] Review Home, Collection and PDP desktop/mobile.
- [ ] Verify EN/ES rendering and announcement bar.

## Commerce runtime

- [ ] Verify current U.S. market and live shipping rule.
- [ ] Verify PayPal Business production checkout.
- [ ] Verify guest/card checkout where available.
- [ ] Complete one controlled purchase.
- [ ] Verify order in Shopify Admin.
- [ ] Verify Shopify → AutoDS synchronization.
- [ ] Verify confirmation email/order-status page.
- [ ] Cancel/refund the controlled order if fulfillment is not desired.

## Analytics

- [ ] Verify session in Shopify Analytics.
- [ ] Verify add-to-cart.
- [ ] Verify checkout initiation.
- [ ] Verify purchase event/sale.
- [ ] Record launch baseline: sessions, conversion rate, AOV, add-to-cart rate, checkout rate, purchases.

## Catalog AI residual validation

- [ ] Run the v0.3.1 residual edge matte against the original local feeding-mat source.
- [ ] Approve or reject the residual halo fix from white/mid-gray/dark comparisons.

## Release

When the Shopify runtime gates pass:

1. Record validated `main` SHA.
2. Publish the validated theme revision.
3. Smoke-test `nimapets.com`.
4. Begin controlled traffic.
5. Confirm first real order fulfillment before paid scaling.
