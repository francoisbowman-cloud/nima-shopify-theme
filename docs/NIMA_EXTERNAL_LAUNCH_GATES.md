# Nima — External Launch Gates

This file tracks release checks that require Shopify/runtime evidence rather than GitHub source alone.

Current storefront source: `main`

Current cutover state: launch source merged; Shopify Release Candidate prepared and runtime commerce configuration substantially validated; live theme not yet replaced.

## Shopify Release Candidate

- [x] Release Candidate created as unpublished theme: `Nima — Release Candidate 86a6b4b` (`199658373201`).
- [x] 16/16 launch theme files materialized successfully in Shopify.
- [x] Shopify schema rejection for the cross-sell section name found and fixed in GitHub (`41e53ab`) and the RC.
- [x] RC reports `processing=false` and `processingFailed=false`.
- [ ] Run `shopify theme check theme --fail-level error` when a CLI/runtime with theme-check access is available.
- [ ] Run `pytest -q tests/test_launch_theme_contract.py` when a local checkout/runtime is available.
- [ ] Perform visual Home / Collection / PDP review on desktop and mobile. The current assistant runtime cannot resolve/open the Shopify preview URL even though the RC exists.

## Localization

- [x] English published as primary locale.
- [x] Spanish enabled and published in Shopify.
- [x] Announcement/UI locale keys present in the RC.
- [x] 23/23 ACTIVE products now have native Spanish `title` and `body_html` translations.
- [x] Translation audit reports no `outdated:true` entries for the active products.
- [x] Spanish SEO title/description translations registered where the English source fields exist.

## Catalog / brand hygiene

- [x] 23/23 ACTIVE products are published to Online Store.
- [x] ACTIVE `vendor:PetDrop` count reduced to zero; active supplier vendor leakage replaced with `Nima` without changing SKU, price, inventory or fulfillment.
- [x] Seven clearly supplier-style product titles normalized while preserving their existing handles/URLs.
- [x] Active catalog sampled with featured product media present.

## U.S. commerce runtime

- [x] United States market is ACTIVE.
- [x] `shipsToCountries` currently contains only `US`.
- [x] 23 ACTIVE products belong to `AutoDS Free Shipping`; 0 ACTIVE products belong to the default $18.99 shipping profile.
- [x] Draft-order calculation using an ACTIVE feeding-mat variant and a U.S. address returns `Free Shipping` at `$0.00`, no alerts/errors, and does not create an order.
- [x] Feeding-mat inventory verified at AutoDS location: sellable inventory is held at the active AutoDS fulfillment location, not the manual location.
- [x] AutoDS fulfillment service and location are active and configured to fulfill online orders.
- [ ] Verify enabled payment gateway in a real checkout. Admin GraphQL does not expose the configured gateway list; Shopify documents it under the REST PaymentGateway resource with a separate `payment_gateways` scope not exposed by the installed connector.
- [ ] Complete one controlled purchase.
- [ ] Verify order in Shopify Admin.
- [ ] Verify Shopify → AutoDS synchronization on that order.
- [ ] Verify confirmation email/order-status page.
- [ ] Cancel/refund the controlled order if fulfillment is not desired.

## Store policies

- [x] Existing Privacy Policy detected.
- [ ] Add/approve Shipping Policy and Refund Policy. Truth-safe drafts were prepared, but the installed connector lacks `write_legal_policies`, so Shopify rejected the write without modifying the store.
- [ ] Review Terms of Service / other policy requirements before paid traffic.

## Analytics baseline

- [x] Shopify Analytics query executed for the 30-day pre-launch baseline.
- [x] Baseline currently shows traffic but no completed purchases; this is the clean pre-launch reference point.
- [ ] Verify post-release add-to-cart.
- [ ] Verify post-release checkout initiation.
- [ ] Verify first purchase event/sale.
- [ ] Record post-launch conversion rate, AOV, add-to-cart rate and checkout rate after controlled traffic begins.

## Catalog AI residual validation

- [ ] Run the v0.3.1 residual edge matte against the original local feeding-mat source.
- [ ] Approve or reject the residual halo fix from white/mid-gray/dark comparisons.

## Release

Do not label the store `PRODUCTION VALIDATED` until visual preview, payment/controlled checkout and required policy gates are complete.

When those gates pass:

1. Record validated `main` SHA and Shopify RC ID.
2. Publish the validated RC.
3. Smoke-test `nimapets.com` in EN/ES and desktop/mobile.
4. Begin controlled traffic.
5. Confirm first real order fulfillment before paid scaling.
