# Site — Grafana Faro frontend RUM (databoar.com.br)

**Status:** Implemented (production config enabled; edge CSP + collector CORS verified 2026-08-16)
**Date:** 2026-08-16
**Authors:** Fabio Leitao (HITL) — executor patch for review
**Priority:** P2
**Issue:** [DataBoar/data-boar-site#70](https://github.com/DataBoar/data-boar-site/issues/70)

**Sibling (product APM, different repo):** not this issue — do not duplicate Prometheus/Loki/Tempo/Pyroscope datasources or dashboards.

## Decision

Instrument **databoar.com.br** only with the **Grafana Faro Web SDK** (vendored IIFE), privacy-preserving, sampled, disableable. Keep the existing Umami/Plausible-class analytics loader (`js/analytics.js`, #58/#59) as a separate opt-in path — Faro is RUM/errors/Web Vitals for Grafana Cloud Frontend Observability, not a replacement analytics product.

| Option | Verdict | Why |
| ------ | ------- | --- |
| **Vendored Faro IIFE + config stub** | **Selected** | Matches static Pages / no bundler; respects external-resource allowlist (no CDN); same enable/disable pattern as analytics. |
| Faro via unpkg/jsDelivr | Rejected | Third-party CDN load violates supply-chain allowlist posture. |
| Google Analytics / session replay | Rejected | Out of scope; conflicts with privacy bar. |
| Instrument `data-boar.com` / `dashboard.net.br` | Rejected | Explicit non-goals (#70). |

## Constraints

- No Grafana write tokens / Cloudflare tokens / private lab endpoints in the browser or git.
- Collector URL + public app id are public client config in `js/faro-config.js` (kill switch remains `enabled: false`).
- Pathname-only URLs; scrub query/hash, auth, cookies; no form contents; no replay/keystrokes.
- Tracing off until operator confirms sampling policy for traces.
- No Cloudflare / OCI / DNS / Grafana server edits from this repo (CSP updated by operator outside git).

## Implementation map

| File | Role |
| ---- | ---- |
| `js/faro-config.js` | Production enablement for DataBoar Site collector |
| `js/faro-config.example.js` | Operator template (placeholders) |
| `js/faro.js` | Loader: gates, sampling, scrub, local no-send, optional tracing |
| `js/vendor/faro-web-sdk.iife.js` | Pinned Faro 2.9.0 |
| `js/vendor/faro-web-tracing.iife.js` | Pinned tracing 2.9.0 (loaded only if `tracingEnabled`) |
| `js/vendor/NOTICE.md` | Pin + SHA-256 |
| `docs/ops/FARO_FRONTEND_OBSERVABILITY.md` | Enablement, CSP/CORS (verified), rollback, verification |
| `privacidade.html` | Honest RUM disclosure + opt-out |

## Roll-out / rollback

See `docs/ops/FARO_FRONTEND_OBSERVABILITY.md`. Rollback = set `enabled: false` / `mode: "off"` and redeploy Pages.
