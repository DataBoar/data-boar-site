/**
 * Grafana Faro — production config for databoar.com.br (issue #70).
 * Public collector URL only (Grafana Cloud Frontend Observability app "DataBoar Site").
 * Never put Grafana write API tokens, Cloudflare tokens, or private lab endpoints here.
 * Kill switch: set enabled:false and mode:"off".
 * Diag (optional): open with ?faro=diag and inspect window.__DATABOAR_FARO_DIAG__.
 */
window.DATABOAR_FARO = {
  enabled: true,
  mode: "production",
  collectorUrl:
    "https://faro-collector-prod-sa-east-1.grafana.net/collect/825e0cc859d9ba030a892ac7f8894511",
  appName: "databoar-com-br",
  appVersion: "site",
  environment: "production",
  // 100% while traffic is low (stealth/ops visibility); lower later if volume grows
  samplingRate: 1.0,
  tracingEnabled: false,
  allowedHosts: ["databoar.com.br", "www.databoar.com.br"],
};
