# Site — lightweight privacy-first analytics / RUM

**Status:** Active (opt-in POC)
**Date:** 2026-08-09
**Authors:** Fabio Leitao
**Priority:** P3
**Issue:** [DataBoar/data-boar-site#58](https://github.com/DataBoar/data-boar-site/issues/58)

**Sibling (product APM, different repo):** [DataBoar/data-boar#1500](https://github.com/DataBoar/data-boar/issues/1500) — FastAPI OTel; **not** this issue.

## Decision

**Choose privacy-first self-hosted analytics (Umami or Plausible class) for production GitHub Pages.**

| Option | Verdict | Why |
| ------ | ------- | --- |
| **Umami / Plausible (self-hosted)** | **Selected** | One `<script>` tag, no third-party cookies, no PII by design, aligns with LGPD positioning; works on static Pages without a bundler. |
| **OpenTelemetry Web SDK via CDN → lab OTLP** | Rejected as **default** | Public Pages cannot reach private lab collectors (`127.0.0.1` / homelan). A public OTLP sink would need auth and careful CORS; heavier client payload. Keep as optional lab experiment only if a **public, authenticated** collector exists later. |
| **Google Analytics / similar SaaS** | Rejected | Third-party cookies / consent burden conflicts with product narrative. |

## Constraints

- **No build pipeline** — plain HTML + one loader script.
- **No-op by default** — until the operator sets `window.DATABOAR_ANALYTICS` (via `js/analytics-config.js`).
- **Zero PII** — do not send form field values. First-party beacon (when used): `path` = `location.pathname` only (**never** `location.search`); `referrer` = **origin only** (`new URL(document.referrer).origin`), never the full referrer URL (path/query). Full-referrer allowlist is a future explicit opt-in, not default. Provider scripts (Umami/Plausible) should be configured for the same privacy bar when possible.
- **Consent** — when enabling a live endpoint, keep `privacidade.html` honest about what is measured (operator follow-up if legal copy must change).

## Implementation

| File | Role |
| ---- | ---- |
| `js/analytics.js` | Loader: injects provider script only when config is enabled |
| `js/analytics-config.example.js` | Copy → `analytics-config.js` with real `src` + `websiteId` |
| `js/analytics-config.js` | Tracked stub with `enabled: false` (safe for Pages) |
| `index.html`, `agende-demonstracao.html` | Load config + analytics (conversion + home) |

Config shape:

```js
window.DATABOAR_ANALYTICS = {
  enabled: false,
  provider: "umami", // or "plausible"
  src: "https://analytics.example.com/script.js",
  websiteId: "REPLACE-ME"
};
```

## Roll-out

1. Operator deploys Umami/Plausible on a host they control.
2. Copy example → set `enabled: true` + real URL/id (or keep secrets in a private overlay if preferred).
3. Confirm events in the provider UI; attach screenshot/export on the PR.

## Evidence (this PR)

Local smoke uses a tiny first-party mock receiver (`scripts/analytics-mock-receiver.py`) so the loader’s wire path is proven without waiting for a production Umami URL. Production still uses the real provider when `enabled: true`.

Evidence file: `docs/ops/evidence/site_analytics_58_smoke_2026-08-09.json` (beacon pageview for `/agende-demonstracao.html`).
