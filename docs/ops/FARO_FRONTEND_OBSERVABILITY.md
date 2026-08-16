# Grafana Faro — frontend observability (databoar.com.br)

**Issue:** [#70](https://github.com/DataBoar/data-boar-site/issues/70)  
**Scope:** institutional site RUM only. Does **not** configure Grafana Cloud datasources, dashboards, Alloy, Cloudflare, OCI, DNS, `data-boar.com`, or `dashboard.net.br`.

## What ships in git

| Piece | Default |
| ----- | ------- |
| `js/faro-config.js` | `enabled: true`, `mode: "production"`, Grafana Cloud collect URL for app **DataBoar Site** |
| `js/faro.js` | Host allowlist + privacy scrub + opt-out; loads vendored SDK when enabled |
| `js/vendor/faro-*.iife.js` | Faro **2.9.0** vendored (see `NOTICE.md`) |
| Site HTML | Loads config + `faro.js` (root, `casos/`, and `simple/index.html` wheelhouse entry) |

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
  URL stripping applies only to explicit URL fields (`url`/`href`/…)—never to arbitrary strings
  such as Faro `session.attributes.isSampled` (`"true"` must stay `"true"` or the SDK drops all events).
- CSP violation instrumentation **off** (`enableContentSecurityPolicyInstrumentation: false`); scrubber also redacts any residual `sample` field.
- Ignore HubSpot / common analytics hosts for resource noise.
- Never call `setUser` with email/name; no session replay instrumentation.
- Sampling via `sessionTracking.samplingRate` (**1.0** / 100% while traffic is low).
- Visitor opt-out: `localStorage.setItem('databoar_faro_opt_out','1')` or `?faro=0` (the query param **persists** the same localStorage flag).
- Kill switch: `enabled: false` / `mode: "off"` in `faro-config.js`.
- **Diag (no PII):** after load, inspect `window.__DATABOAR_FARO_DIAG__` (or open with `?faro=diag` for one console line). Fields distinguish skip reasons (`disabled`, `opt_out`, `host_not_allowed`, `session_not_sampled`, `collector_unconfigured`, `sdk_load_failed`) from `expectNetworkSend: true` (POST `/collect` should appear in Network).

Disclosed on `privacidade.html` (pt-BR + en-US).

## CSP / CORS (operator edge — not edited in this repo)

This repository does **not** change Cloudflare. Edge CSP and Grafana Cloud CORS are operator-owned; the site only ships first-party Faro scripts + `connect` to the public collector URL.

### Verified live CSP (databoar.com.br, 2026-08-16)

External check confirms `connect-src` includes the Faro collector origin, for example:

```
connect-src 'self' https://api.hsforms.com https://forms.hsforms.com https://forms.hscollectedforms.net https://faro-collector-prod-sa-east-1.grafana.net;
script-src 'self' 'unsafe-inline' https://js.hsforms.net;
```

| Directive | Faro posture |
| --------- | ------------ |
| `script-src` | Vendored Faro under `/js/**` — covered by `'self'` |
| `connect-src` | Includes `https://faro-collector-prod-sa-east-1.grafana.net` (verified) |

Grafana Cloud Frontend Observability CORS for app **DataBoar Site** allows origins `https://databoar.com.br` and `https://www.databoar.com.br` (not `data-boar.com` / `dashboard.net.br`) — verified via collector OPTIONS preflight.

## Verification

1. **Local no-send:** set `enabled: true`, `mode: "local"`; open a page; confirm console Faro output and **no** requests to `grafana.net` / collector hosts (browser Network panel).
2. **Production (after Pages deploy of this branch):** visit `https://databoar.com.br/` once; confirm Web Vitals / errors appear in Grafana Cloud Frontend Observability.
3. **Opt-out:** `?faro=0` persists `databoar_faro_opt_out=1` → no init on later pages; clear the key to re-enable.
4. **Diag / no POST in F12:** open `https://databoar.com.br/?faro=diag`, then in console check `window.__DATABOAR_FARO_DIAG__`:
   - `skipReason: "session_not_sampled"` → sampling dropped the session (not a CSP/CORS failure).
   - `expectNetworkSend: true` but no POST → transport/CSP/CORS/network failure (filter Network by `faro-collector`).
   - `skipReason: "host_not_allowed"` / `opt_out` / `disabled` → loader never sent (expected).
5. **Gates:** `scripts/check-all.sh` green (includes Faro privacy static checks).

## Rollback

1. Set `window.DATABOAR_FARO.enabled = false` and `mode: "off"` in `js/faro-config.js`.
2. Merge/deploy. Optional: remove script tags later; disabled config is sufficient.

## Non-goals (do not do from this repo)

- Cloudflare Workers/rules, DNS, OCI, Grafana datasource/dashboard creation
- Instrumenting redirect alias `data-boar.com` or `dashboard.net.br`
- Google Analytics, session replay, keystroke capture
