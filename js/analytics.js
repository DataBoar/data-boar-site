/**
 * Privacy-first analytics loader (site#58).
 * No-op unless window.DATABOAR_ANALYTICS.enabled is true and src/websiteId are set.
 * Does not introduce a bundler; injects at most one provider <script>.
 *
 * First-party beacon (optional): path = pathname only (no query); referrer =
 * origin only (no path/query). Full referrer URL requires a future explicit allowlist.
 */
(function () {
  "use strict";

  function safePathname() {
    try {
      return location.pathname || "/";
    } catch (_e) {
      return "/";
    }
  }

  function safeReferrerOrigin(raw) {
    if (!raw) {
      return "";
    }
    try {
      return new URL(raw).origin || "";
    } catch (_e) {
      return "";
    }
  }

  var cfg = window.DATABOAR_ANALYTICS || {};
  if (!cfg.enabled) {
    return;
  }

  var src = (cfg.src || "").trim();
  var websiteId = (cfg.websiteId || "").trim();
  if (!src || !websiteId) {
    if (typeof console !== "undefined" && console.warn) {
      console.warn(
        "[databoar-analytics] enabled but missing src or websiteId — skipping"
      );
    }
    return;
  }

  var provider = (cfg.provider || "umami").toLowerCase();
  var s = document.createElement("script");
  s.defer = true;
  s.src = src;
  s.setAttribute("data-website-id", websiteId);

  if (provider === "plausible") {
    s.setAttribute("data-domain", websiteId);
    s.removeAttribute("data-website-id");
  }

  /* Optional first-party beacon for local smoke / mock receiver (no third party). */
  if (cfg.beaconUrl) {
    try {
      var payload = {
        type: "pageview",
        path: safePathname(),
        referrer: safeReferrerOrigin(document.referrer),
        title: document.title || "",
        ts: new Date().toISOString(),
        websiteId: websiteId,
        provider: provider,
      };
      if (navigator.sendBeacon) {
        navigator.sendBeacon(
          cfg.beaconUrl,
          new Blob([JSON.stringify(payload)], { type: "application/json" })
        );
      } else {
        fetch(cfg.beaconUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          keepalive: true,
          mode: "cors",
        }).catch(function () {});
      }
    } catch (_e) {
      /* never break the page */
    }
  }

  document.head.appendChild(s);
})();
