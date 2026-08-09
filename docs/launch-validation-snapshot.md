# Nima — Launch Validation Snapshot

Branch: `feat/nima-production-readiness-launch`

## Static validation added

- Shopify Theme Check workflow (`.github/workflows/theme-validation.yml`).
- Launch contract tests (`tests/test_launch_theme_contract.py`).
- Launch contract workflow (`.github/workflows/launch-contract.yml`).

## Contracts covered

- Home and product templates reference section files that exist.
- EN/ES launch keys exist and remain in parity.
- Translation keys used by new launch sections resolve in both locales.
- `launch.css` loads after `base.css`.
- Home shop window appears before editorial discovery blocks.
- PDP routine cross-sell remains the last product-template section.

## Not yet claimed as validated

- Theme Check execution result.
- Browser visual validation on desktop/mobile.
- Real Shopify preview rendering.
- End-to-end checkout.
- Admin-only shipping/payment/market configuration.

No merge to `main` is authorized by this snapshot.
