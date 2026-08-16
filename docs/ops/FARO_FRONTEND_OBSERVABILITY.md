# Grafana Faro — frontend observability (databoar.com.br)

**Issue:** [#70](https://github.com/DataBoar/data-boar-site/issues/70)  
**Scope:** institutional site RUM only. Does **not** configure Grafana Cloud datasources, dashboards, Alloy, Cloudflare, OCI, DNS, `data-boar.com`, or `dashboard.net.br`.

## What ships in git

| Piece | Default |
| ----- | ------- |
| `js/faro-config.js` | `enabled: true`, `mode: "production"`, Grafana Cloud collect URL for app **DataBoar Site** |
| `js/faro.js` | Host allowlist + privacy scrub + opt-out; loads vendored SDK when enabled |
| `js/vendor/faro-*.iife.js` | Faro **2.9.0** vendored (see `NOTICE.md`) |
| Site HTML | Loads config + `faro.js` before `site.js` |

Existing privacy-first pageview analytics (`js/analytics.js`, #58) remain separate and also off by default.

## Operator enablement — collector configuration

Grafana Cloud Frontend Observability app **DataBoar Site** supplies the public collect URL wired in `js/faro-config.js`.

Kill switch / rollback: set `enabled: false` and `mode: "off"` in `js/faro-config.js`, then deploy via PR.

Keep `tracingEnabled: false` until sampling policy for traces is confirmed. Do **not** paste Grafana API tokens, service-account tokens, or Cloudflare credentials into the repo or the browser config.

If `mode: "production"` and `collectorUrl` is missing/placeholder, `faro.js` **skips initialization** and logs a console warning — the site stays up.

## Modes

| `mode` | Behavior |
| ------ | -------- |
| `off` | No SDK load (same as `enabled: false`) |
| `local` | Load vendored SDK; **ConsoleTransport only** — no collector send (safe for `python -m http.server` / local previews) |
| `production` | Send only when `location.hostname` ∈ `allowedHosts` (`databoar.com.br`, `www.databoar.com.br`) |

## Privacy controls

- Scrub query/hash from URLs; redact authorization/cookie-like strings in payloads (`beforeSend`).
- Ignore HubSpot / common analytics hosts for resource noise.
- Never call `setUser` with email/name; no session replay instrumentation.
- Sampling via `sessionTracking.samplingRate` (default **0.2**).
- Visitor opt-out: `localStorage.setItem('databoar_faro_opt_out','1')` or `?faro=0`.
- Kill switch: `enabled: false` / `mode: "off"` in `faro-config.js`.

Disclosed on `privacidade.html` (pt-BR + en-US).

## CSP / CORS (operator edge — not edited in this repo)

This repository does **not** change Cloudflare. Production Faro is enabled in `js/faro-config.js` for the Grafana Cloud app **DataBoar Site**, but the browser will only deliver telemetry after edge CSP and collector CORS allow it.

### Observed live CSP (databoar.com.br, 2026-08-16)

Cloudflare currently serves approximately:

```
connect-src 'self' https://api.hsforms.com https://forms.hsforms.com https://forms.hscollectedforms.net;
script-src 'self' 'unsafe-inline' https://js.hsforms.net;
```

**Activation risk:** `connect-src` does **not** yet include `https://faro-collector-prod-sa-east-1.grafana.net`. Until the operator adds that origin (or the collect URL origin) to the edge CSP, Faro `fetch`/`sendBeacon` calls will be blocked in the browser. No Cloudflare edits are made from this repo.

| Directive | Required for Faro |
| --------- | ----------------- |
| `script-src` | first-party `/js/**` (vendored Faro) — already covered by `'self'` |
| `connect-src` | add `https://faro-collector-prod-sa-east-1.grafana.net` |

Grafana Cloud Frontend Observability CORS for app **DataBoar Site** must allow origins `https://databoar.com.br` and `https://www.databoar.com.br` (not `data-boar.com` / `dashboard.net.br`). Configure that in Grafana Cloud — **outside** this repo.

## Verification

1. **Local no-send:** set `enabled: true`, `mode: "local"`; open a page; confirm console Faro output and **no** requests to `grafana.net` / collector hosts (browser Network panel).
2. **Production (after collector URL):** deploy with real `collectorUrl`; visit `https://databoar.com.br/` once; confirm Web Vitals / errors appear in Grafana Cloud Frontend Observability.
3. **Opt-out:** `?faro=0` or localStorage flag → no init.
4. **Gates:** `scripts/check-all.sh` green (includes Faro privacy static checks).

## Rollback

1. Set `window.DATABOAR_FARO.enabled = false` and `mode: "off"` in `js/faro-config.js`.
2. Merge/deploy. Optional: remove script tags later; disabled config is sufficient.

## Non-goals (do not do from this repo)

- Cloudflare Workers/rules, DNS, OCI, Grafana datasource/dashboard creation
- Instrumenting redirect alias `data-boar.com` or `dashboard.net.br`
- Google Analytics, session replay, keystroke capture
