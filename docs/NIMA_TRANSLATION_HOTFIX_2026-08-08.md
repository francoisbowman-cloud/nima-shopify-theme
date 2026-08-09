# Nima — Footer + Magazine locale hotfix

Date: 2026-08-08

## Trigger

Visual review of the unpublished Premium RC exposed visible Shopify `Translation missing` strings in the premium Footer and Magazine.

## Root cause

The Premium RC contained newer localized `footer.liquid`, `magazine-hero.liquid`, and `magazine-grid.liquid` implementations than GitHub `main`. Several Magazine story keys are assembled dynamically at runtime, so the previous locale regression test — which only detected literal `| t` keys — could not see them.

## Fix

- Added complete EN/ES locale coverage for `sections.footer.*`.
- Added complete EN/ES locale coverage for `sections.magazine.*`, including feature and story 1–3 keys.
- Added explicit dynamic-key regression coverage in `tests/test_locale_contract.py`.
- Synchronized `footer.liquid`, `magazine-hero.liquid`, and `magazine-grid.liquid` from the Premium RC back into GitHub `main` to remove source/deployment drift.
- Synchronized both corrected locale files to Shopify Premium RC `199660142673`.

## Validation

Shopify Admin confirmed both locale files were updated in the unpublished RC and contain the new Footer + Magazine key groups.

Post-fix GitHub CI on commit `25453fb9cd1bdb55542788c3cc5cf41add762a20`:

- Launch contract: SUCCESS — run `31293456055`
- Theme validation: SUCCESS — run `31293456079`

The live Shopify theme was not modified or published.
