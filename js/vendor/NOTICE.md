# Vendored Grafana Faro Web SDK

Pinned third-party browser bundles for GitHub Pages (no CDN load at runtime).

| Package | Version | File | SHA-256 |
| ------- | ------- | ---- | ------- |
| `@grafana/faro-web-sdk` | 2.9.0 | `faro-web-sdk.iife.js` | `0a9dc4836fadc63ad0b10a2b76d698f28bb9c2c846204690aa4c2ead61cad2ac` |
| `@grafana/faro-web-tracing` | 2.9.0 | `faro-web-tracing.iife.js` | `a173fb4bf6e9d1ed5505a6018e4e829855586c9a64b2273166b313c8eeab7f4a` |

- **License:** Apache-2.0 (upstream Grafana Faro)
- **Source:** npm registry tarballs for the versions above
- **Refresh:** re-download the pinned tarballs, replace the IIFE files, update hashes here, and bump the pin in `docs/ops/FARO_FRONTEND_OBSERVABILITY.md`

These files are loaded only by `js/faro.js` when Faro is enabled. They are **not** loaded from unpkg/jsDelivr.
