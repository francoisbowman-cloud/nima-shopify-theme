# Nima — Premium Mockup Implementation

## Status

The approved Nima premium mockup has been implemented in source and synchronized to an unpublished Shopify Release Candidate.

- Source branch: `feat/nima-premium-mockup-implementation`
- Merged PR: `#6 — Nima Premium Mockup Implementation`
- Merge commit: `bcb8b861bb79c85216b1b21703772ac88e07c7eb`
- Shopify RC: `Nima — Premium Mockup RC c92500a`
- Shopify theme ID: `199660142673`
- RC role: `UNPUBLISHED`
- Live theme remains: `nima-theme-v3-0-1-editorial`

## Approved visual direction

Nima is a warm editorial pet-lifestyle brand with clean commerce rather than a generic marketplace aesthetic.

Core design language:

- warm ivory / cream foundations
- terracotta primary action accent
- muted olive / taupe supporting tones
- charcoal editorial typography
- generous whitespace and controlled visual rhythm
- serif-led headings with restrained sans-serif UI text
- product photography on clean white / very light commerce backgrounds
- lifestyle photography reserved for hero, storytelling and editorial modules
- uniform media ratios and intentional crops

## Home

The premium Home is ordered as:

1. editorial hero
2. commerce shop window
3. lifestyle brand story
4. Journal / editorial teaser

The Shopify RC was explicitly verified to contain this template structure after the Launch Readiness section dependencies were synchronized.

## Collection

The collection experience now uses:

- editorial collection heading and contextual visual
- restrained filter and sort treatment
- four-column desktop commerce grid
- consistent square white product media frames
- responsive two-column mobile grid
- product imagery contained cleanly without inconsistent card heights

## Product detail page

The PDP now uses:

- large white product gallery
- vertical desktop thumbnails / horizontal mobile thumbnails
- stronger title / price / purchase hierarchy
- quantity control
- terracotta Add to Cart
- Shopify accelerated checkout button underneath
- trust / shipping / returns references using truth-safe copy
- open details section
- editorial cross-sell styling

No payment-method claim is hard-coded. At pre-release checkout the user reported PayPal as the available payment method; payment configuration remains a Shopify Admin / real-checkout gate.

## Localization

UI copy was consolidated in:

- `theme/locales/en.json`
- `theme/locales/es.default.json`

A new regression test, `tests/test_locale_contract.py`, scans literal Liquid `| t` usages and fails when:

- a used translation key is absent from EN or ES; or
- the EN and ES locale key structures diverge.

This turns prior `translation missing` defects into a CI regression rather than a manual-only check.

## Validation

Premium branch validation passed before merge:

- Shopify Theme Check
- JSON parsing
- launch contract
- EN/ES locale contract

Main CI is required to remain green after the merge.

The Shopify Premium RC is healthy (`processingFailed=false`) and remains unpublished.

## Shopify synchronization note

The live Shopify theme predates the GitHub Launch Readiness layer. Therefore the Premium RC was built by:

1. duplicating the current live theme to preserve store settings and assets;
2. applying the premium source files;
3. detecting that `editorial-shop-window` was missing from the live baseline;
4. synchronizing the required Launch Readiness dependencies from GitHub `main`;
5. applying the premium `templates/index.json` again;
6. verifying the resulting Home template body directly through Shopify Admin GraphQL.

This prevented an incomplete hybrid RC.

## Remaining gates before publishing

The source implementation is complete. The theme must not be called `PRODUCTION VALIDATED` until the unpublished RC is visually reviewed in the actual Shopify renderer.

Required final checks:

- Home desktop / mobile against approved mockup
- Collection desktop / mobile
- PDP desktop / mobile
- product image fit and crop behavior across representative products
- EN / ES switch with zero visible `translation missing`
- announcement bar
- cart / checkout path
- PayPal production checkout / available payment methods
- required Shopify policies

Only after those pass should the Premium RC replace the live theme.
