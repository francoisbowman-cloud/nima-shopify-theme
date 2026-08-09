# Nima Production Readiness — PR Notes

This branch prepares Nima for controlled production launch without merging automatically to `main`.

## Included

- EN/ES locale audit work, including locale-aware announcement bar.
- Editorial shop window on Home with automatic `all` collection fallback.
- Editorial routine cross-sell on PDP without paid apps or AJAX dependency.
- Additive launch visual layer (`launch.css`) to strengthen hierarchy while preserving Nima's editorial identity.
- Reproducible Theme Check and launch-contract CI definitions.
- Explicit Production Readiness documentation and gate.

## Explicitly excluded

- Shopify admin changes.
- Publishing a theme.
- Checkout/payment configuration changes.
- Catalog AI merge.
- Image-generation API calls.
- Automatic merge to `main`.

## Validation status

Static contracts are encoded in tests. GitHub Actions availability/execution must be confirmed on the PR. Browser/Shopify preview validation remains a release gate.
