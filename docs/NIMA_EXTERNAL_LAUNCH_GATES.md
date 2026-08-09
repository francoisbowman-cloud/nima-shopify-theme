# Nima — External Launch Gates

This file tracks release checks that require Shopify/runtime evidence rather than GitHub source alone.

Current storefront source: `main`

Current cutover state: launch source merged; Shopify Release Candidate prepared; source/theme validation and most commerce-runtime gates have passed; live theme not yet replaced.

## Shopify Release Candidate

- [x] Release Candidate created as unpublished theme: `Nima — Release Candidate 86a6b4b` (`199658373201`).
- [x] 16/16 launch theme files materialized successfully in Shopify.
- [x] Shopify schema rejection for the cross-sell section name found and fixed in GitHub (`41e53ab`) and the RC.
- [x] RC reports `processing=false` and `processingFailed=false`.
- [x] Launch contract CI PASS — GitHub Actions run `31291026621`; `pytest -q tests/test_launch_theme_contract.py` succeeded.
- [x] Theme Check + JSON validation PASS — GitHub Actions run `31291026619`; Theme Check and JSON parse steps both succeeded.
- [x] Deprecated Theme Check 1.x `MissingRequiredTemplateFiles` was explicitly disabled because Shopify reports the store uses `NEW_CUSTOMER_ACCOUNTS`; Shopify documents this legacy check as safe to disable. All other Theme Check rules remain active.
- [ ] Perform visual Home / Collection / PDP review on desktop and mobile. The current assistant runtime cannot resolve/open the Shopify preview URL even though the RC exists.

## Localization

- [x] English published as primary locale.
- [x] Spanish enabled and published in Shopify.
- [x] Announcement/UI locale keys present in the RC.
- [x] 23/23 ACTIVE products have native Spanish `title` and `body_html` translations.
- [x] Translation audit reports no `outdated:true` entries for the active products.
- [x] Spanish SEO title/description translations registered wherever the English source fields exist.
- [x] Existing Privacy Policy already has a full Spanish translation and reports `outdated:false`.
- [x] U.S. market has no separate MarketWebPresence; localized storefront traffic therefore uses the primary shop domain/locales rather than a market-specific domain.

## Catalog / brand hygiene

- [x] 23/23 ACTIVE products are published to Online Store.
- [x] ACTIVE `vendor:PetDrop` count reduced to zero; active supplier vendor leakage replaced with `Nima` without changing SKU, price, inventory or fulfillment.
- [x] Seven clearly supplier-style product titles normalized while preserving their existing handles/URLs.
- [x] No ACTIVE product has `inventory_total <= 0`.
- [x] No ACTIVE product has a variant price `<= 0`.
- [x] Products returned by the partial-stock-location audit retain positive sellable inventory and featured media; the zero-stock signal comes from the unused manual location while AutoDS remains stocked.

## U.S. commerce runtime

- [x] United States market is ACTIVE.
- [x] `shipsToCountries` currently contains only `US`.
- [x] 23 ACTIVE products belong to `AutoDS Free Shipping`; 0 ACTIVE products belong to the default $18.99 shipping profile.
- [x] Draft-order calculation using an ACTIVE feeding-mat variant and a representative U.S. address returns `Free Shipping` at `$0.00`, no alerts/errors, and does not create an order.
- [x] Feeding-mat inventory verified at AutoDS location: sellable inventory is held at the active AutoDS fulfillment location, not the manual location.
- [x] AutoDS fulfillment service and location are active and configured to fulfill online orders.
- [x] Store uses `NEW_CUSTOMER_ACCOUNTS`; login links are enabled but login is not required at checkout.
- [ ] Verify enabled payment gateway in a real checkout. Admin GraphQL does not expose the configured gateway list; Shopify documents it under the REST PaymentGateway resource with a separate `payment_gateways` scope not exposed by the installed connector.
- [ ] Complete one controlled purchase.
- [ ] Verify order in Shopify Admin.
- [ ] Verify Shopify → AutoDS synchronization on that order.
- [ ] Verify confirmation email/order-status page.
- [ ] Cancel/refund the controlled order if fulfillment is not desired.

## Store policies

- [x] Existing Privacy Policy detected with current Spanish translation.
- [x] Truth-safe EN/ES Shipping and Refund policy drafts are versioned in `docs/NIMA_SHOPIFY_POLICY_DRAFTS.md`.
- [ ] Add/approve Shipping Policy and Refund Policy in Shopify Admin. The installed connector lacks `write_legal_policies`, so Shopify rejected the API write without modifying the store.
- [ ] Review/publish Shopify Terms of Service template and remaining legal-policy requirements before paid traffic.

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
