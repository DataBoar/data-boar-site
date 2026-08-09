/**
 * Copy to analytics-config.js and set enabled + real Umami/Plausible values.
 * Never commit third-party secrets; websiteId is not a password but treat URLs as operator-owned.
 */
window.DATABOAR_ANALYTICS = {
  enabled: true,
  provider: "umami", // or "plausible"
  src: "https://analytics.example.com/script.js",
  websiteId: "REPLACE-WITH-WEBSITE-ID-OR-DOMAIN",
  // Optional: local smoke only — POST pageview JSON to a mock receiver
  // beaconUrl: "http://127.0.0.1:8791/beacon",
};
