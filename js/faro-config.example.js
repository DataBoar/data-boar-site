/**
 * Copy to faro-config.js when the operator supplies the Grafana Cloud Faro collector URL.
 *
 * Public-safe client config only:
 *   - collectorUrl = Grafana Cloud Frontend Observability collect URL
 *     (often https://faro-collector-….grafana.net/collect/<public-app-id>)
 *   - Do NOT put Grafana Cloud API tokens, service-account tokens, Cloudflare tokens,
 *     Authorization headers, or private lab collectors in this file.
 *
 * Modes:
 *   - "off"         — no SDK load (same as enabled:false)
 *   - "local"       — load SDK, ConsoleTransport only (no network send)
 *   - "production"  — send only from allowedHosts to collectorUrl
 *
 * BLOCKER until operator supplies collectorUrl: keep enabled:false / mode:"off".
 */
window.DATABOAR_FARO = {
  enabled: true,
  mode: "production", // "off" | "local" | "production"
  collectorUrl: "REPLACE-WITH-GRAFANA-CLOUD-FARO-COLLECTOR-URL",
  appName: "databoar-com-br",
  appVersion: "site",
  environment: "production",
  // Conservative default; raise only after privacy + volume review
  samplingRate: 0.2,
  // Keep false until Grafana Cloud app + sampling policy are confirmed
  tracingEnabled: false,
  // databoar.com.br only — never data-boar.com / dashboard.net.br
  allowedHosts: ["databoar.com.br", "www.databoar.com.br"],
  // Optional: override vendored script paths (defaults under js/vendor/)
  // sdkSrc: "js/vendor/faro-web-sdk.iife.js",
  // tracingSrc: "js/vendor/faro-web-tracing.iife.js",
};
