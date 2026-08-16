/**
 * Grafana Faro loader for databoar.com.br (site#70).
 *
 * Privacy bar (aligned with analytics.js / PLAN_SITE_ANALYTICS):
 *   - pathname only (never location.search / hash query)
 *   - scrub URLs, referrers, and error payloads before export
 *   - no form fields, cookies, Authorization headers, raw user ids, session replay,
 *     or keystroke/input capture
 *   - production send only on allowedHosts (databoar.com.br)
 *   - explicit disable + localStorage / ?faro=0 opt-out (?faro=0 persists the flag)
 *   - CSP violation instrumentation OFF by default (no inline sample export)
 *   - local mode: ConsoleTransport only (no collector send)
 *   - non-invasive diag: window.__DATABOAR_FARO_DIAG__ (+ optional ?faro=diag)
 *
 * Vendored SDK (js/vendor/) — no third-party CDN dependency.
 */
(function () {
  "use strict";

  var OPT_OUT_KEY = "databoar_faro_opt_out";
  var cfg = window.DATABOAR_FARO || {};

  function warn(msg) {
    if (typeof console !== "undefined" && console.warn) {
      console.warn("[databoar-faro] " + msg);
    }
  }

  function diagRequested() {
    if (cfg.diag === true) {
      return true;
    }
    try {
      return /[?&]faro=diag(?:&|$)/.test(location.search || "");
    } catch (_e) {
      return false;
    }
  }

  function collectorHostOnly(raw) {
    var u = String(raw || "").trim();
    if (!u || u.indexOf("REPLACE-WITH-") === 0) {
      return "";
    }
    try {
      return new URL(u).host || "";
    } catch (_e) {
      return "";
    }
  }

  function setDiag(patch) {
    var prev = window.__DATABOAR_FARO_DIAG__ || {};
    var next = {};
    var k;
    for (k in prev) {
      if (Object.prototype.hasOwnProperty.call(prev, k)) {
        next[k] = prev[k];
      }
    }
    for (k in patch) {
      if (Object.prototype.hasOwnProperty.call(patch, k)) {
        next[k] = patch[k];
      }
    }
    // Never put full collector URL / tokens in the diag object (screenshot-safe)
    if ("collectorUrl" in next) {
      delete next.collectorUrl;
    }
    window.__DATABOAR_FARO_DIAG__ = next;
    if (diagRequested() && typeof console !== "undefined" && console.info) {
      console.info(
        "[databoar-faro] diag",
        "skipReason=" + (next.skipReason || "none"),
        "initialized=" + !!next.initialized,
        "sessionSampled=" + String(next.sessionSampled),
        "expectNetworkSend=" + !!next.expectNetworkSend,
        "collectorHost=" + (next.collectorHost || ""),
        "samplingRate=" + String(next.samplingRate)
      );
    }
  }

  function readSessionSampled(faro) {
    try {
      var metas = faro && faro.metas && faro.metas.value;
      var session = metas && metas.session;
      if (!session) {
        return null;
      }
      if (typeof session.isSampled === "boolean") {
        return session.isSampled;
      }
      var attrs = session.attributes || {};
      if (typeof attrs.isSampled === "boolean") {
        return attrs.isSampled;
      }
      if (typeof attrs.isSampled === "string") {
        return attrs.isSampled === "true";
      }
      return null;
    } catch (_e) {
      return null;
    }
  }

  function safePathname() {
    try {
      return location.pathname || "/";
    } catch (_e) {
      return "/";
    }
  }

  function stripUrl(raw) {
    if (!raw || typeof raw !== "string") {
      return "";
    }
    try {
      var u = new URL(raw, location.origin);
      return u.origin + (u.pathname || "/");
    } catch (_e) {
      return raw.split("?")[0].split("#")[0];
    }
  }

  function scrubString(value) {
    if (typeof value !== "string") {
      return value;
    }
    var out = value;
    // Drop query/hash fragments that may carry tokens or PII
    out = out.replace(/([?&#][^\s"'<>]*)/g, "");
    // Authorization / bearer / cookie-like material if it ever appears in messages
    out = out.replace(/authorization\s*[:=]\s*bearer\s+[^\s"'<>]+/gi, "authorization:[redacted]");
    out = out.replace(/bearer\s+[a-z0-9._\-]+/gi, "bearer [redacted]");
    out = out.replace(/cookie\s*[:=]\s*[^\s"'<>]+/gi, "cookie:[redacted]");
    return out;
  }

  function scrubDeep(value, depth) {
    if (depth > 6 || value == null) {
      return value;
    }
    if (typeof value === "string") {
      // Never stripUrl() here — relative tokens like "true" (session isSampled)
      // become https://origin/true and Faro's session hook drops every event.
      return scrubString(value);
    }
    if (Array.isArray(value)) {
      return value.map(function (v) {
        return scrubDeep(v, depth + 1);
      });
    }
    if (typeof value === "object") {
      var out = {};
      Object.keys(value).forEach(function (k) {
        var lk = k.toLowerCase();
        // Drop CSP violation "sample" (may contain inline script / DOM excerpts)
        if (lk === "sample") {
          out[k] = "[redacted]";
          return;
        }
        // URL-shaped fields only — do not treat arbitrary strings as URLs
        if (
          lk === "href" ||
          lk === "url" ||
          lk === "page_url" ||
          lk === "document_uri" ||
          lk === "blockeduri" ||
          lk === "sourcefile"
        ) {
          var uv = value[k];
          if (typeof uv === "string") {
            out[k] = scrubString(stripUrl(uv));
          } else {
            out[k] = "[redacted]";
          }
          return;
        }
        if (
          lk === "cookie" ||
          lk === "cookies" ||
          lk === "authorization" ||
          lk === "password" ||
          lk === "email" ||
          lk === "username" ||
          lk.indexOf("query") !== -1 ||
          lk === "search"
        ) {
          var v = value[k];
          if (typeof v === "string") {
            out[k] = scrubString(v);
          } else {
            out[k] = "[redacted]";
          }
          return;
        }
        out[k] = scrubDeep(value[k], depth + 1);
      });
      return out;
    }
    return value;
  }

  function beforeSend(item) {
    if (!item) {
      return item;
    }
    try {
      return scrubDeep(item, 0);
    } catch (_e) {
      return null;
    }
  }

  function persistOptOut() {
    try {
      localStorage.setItem(OPT_OUT_KEY, "1");
    } catch (_e) {
      /* private mode / quota — query gate still applies this navigation */
    }
  }

  function isOptedOut() {
    try {
      if (/[?&]faro=0(?:&|$)/.test(location.search || "")) {
        persistOptOut();
        return true;
      }
    } catch (_e) {
      /* ignore */
    }
    try {
      return localStorage.getItem(OPT_OUT_KEY) === "1";
    } catch (_e2) {
      return false;
    }
  }

  function hostAllowed(hosts) {
    var host = "";
    try {
      host = (location.hostname || "").toLowerCase();
    } catch (_e) {
      return false;
    }
    if (!host) {
      return false;
    }
    for (var i = 0; i < hosts.length; i++) {
      if (host === String(hosts[i]).toLowerCase()) {
        return true;
      }
    }
    return false;
  }

  function resolveScriptBase() {
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      if (src.indexOf("faro.js") !== -1) {
        return src.replace(/[^/]+$/, "");
      }
    }
    return "js/";
  }

  function loadScript(src, onload, onerror) {
    var s = document.createElement("script");
    s.src = src;
    s.async = false;
    s.onload = onload;
    s.onerror = onerror || function () {
      warn("failed to load " + src);
    };
    document.head.appendChild(s);
  }

  function samplingRate() {
    var n = Number(cfg.samplingRate);
    if (!(n >= 0 && n <= 1)) {
      return 1;
    }
    return n;
  }

  function initFaro(mode) {
    var sdk = window.GrafanaFaroWebSdk;
    var rate = samplingRate();
    var host = collectorHostOnly(cfg.collectorUrl);

    setDiag({
      enabled: !!cfg.enabled,
      mode: mode,
      samplingRate: rate,
      collectorConfigured: !!host,
      collectorHost: host,
      sdkLoaded: !!(sdk && typeof sdk.initializeFaro === "function"),
      initialized: false,
      sessionSampled: null,
      expectNetworkSend: false,
      skipReason: "",
    });

    if (!sdk || typeof sdk.initializeFaro !== "function") {
      setDiag({ skipReason: "sdk_missing" });
      warn("SDK global missing after load");
      return;
    }

    var instrumentations = sdk.getWebInstrumentations
      ? sdk.getWebInstrumentations({
          captureConsole: true,
          // OFF: CSP violation "sample" can carry inline script / page excerpts
          enableContentSecurityPolicyInstrumentation: false,
          // Performance / Web Vitals included by default instrumentations
        })
      : [];

    var app = {
      name: cfg.appName || "databoar-com-br",
      version: cfg.appVersion || "site",
      environment: cfg.environment || (mode === "local" ? "local" : "production"),
    };

    var faroOptions = {
      app: app,
      instrumentations: instrumentations,
      sessionTracking: {
        samplingRate: rate,
        // Anonymous session id only; we never call setUser with PII
        persistent: false,
      },
      ignoreUrls: [
        /api\.hsforms\.com/i,
        /forms\.hsforms\.com/i,
        /hubspot\.com/i,
        /google-analytics\.com/i,
        /googletagmanager\.com/i,
      ],
      beforeSend: beforeSend,
      // Track page as pathname only via metas after init
    };

    if (mode === "local") {
      faroOptions.transports = [new sdk.ConsoleTransport()];
      // Explicitly no collector URL / FetchTransport
    } else {
      var url = String(cfg.collectorUrl || "").trim();
      if (!url || url.indexOf("REPLACE-WITH-") === 0) {
        setDiag({ skipReason: "collector_unconfigured" });
        warn("production mode requires collectorUrl — skipping (operator blocker)");
        return;
      }
      // Public collect URL only — never set apiKey / Authorization from site config
      faroOptions.url = url;
    }

    var faro = sdk.initializeFaro(faroOptions);

    try {
      if (faro && faro.api && typeof faro.api.setView === "function") {
        faro.api.setView({ name: safePathname() });
      }
      // Prefer page meta without query if the API is present
      if (faro && faro.api && faro.metas && typeof faro.metas.add === "function") {
        faro.metas.add({
          page: {
            url: stripUrl(location.href),
          },
        });
      }
    } catch (_e) {
      /* never break the page */
    }

    window.__DATABOAR_FARO__ = faro;

    var sampled = readSessionSampled(faro);
    var expectSend = mode === "production" && sampled !== false;
    setDiag({
      initialized: true,
      sessionSampled: sampled,
      expectNetworkSend: expectSend,
      skipReason: sampled === false ? "session_not_sampled" : "",
    });

    if (cfg.tracingEnabled) {
      loadTracing(faro);
    }
  }

  function loadTracing() {
    var tracingSrc = cfg.tracingSrc || resolveScriptBase() + "vendor/faro-web-tracing.iife.js";

    loadScript(
      tracingSrc,
      function () {
        try {
          var Tracing = window.GrafanaFaroWebTracing;
          var sdk = window.GrafanaFaroWebSdk;
          if (!Tracing || !Tracing.TracingInstrumentation || !sdk || !sdk.faro) {
            warn("tracing bundle loaded but TracingInstrumentation unavailable");
            return;
          }
          sdk.faro.instrumentations.add(new Tracing.TracingInstrumentation());
        } catch (_e) {
          warn("tracing init failed");
        }
      },
      function () {
        warn("tracing bundle failed to load");
      }
    );
  }

  // --- gate ---
  setDiag({
    enabled: !!cfg.enabled,
    mode: String(cfg.mode || "off"),
    samplingRate: samplingRate(),
    hostname: (function () {
      try {
        return location.hostname || "";
      } catch (_e) {
        return "";
      }
    })(),
    hostAllowed: false,
    optedOut: false,
    collectorConfigured: !!collectorHostOnly(cfg.collectorUrl),
    collectorHost: collectorHostOnly(cfg.collectorUrl),
    sdkLoaded: false,
    initialized: false,
    sessionSampled: null,
    expectNetworkSend: false,
    skipReason: "",
  });

  if (!cfg.enabled || cfg.mode === "off") {
    setDiag({ skipReason: "disabled" });
    return;
  }

  if (isOptedOut()) {
    setDiag({ optedOut: true, skipReason: "opt_out" });
    warn("opt-out active (localStorage or ?faro=0) — not initializing");
    return;
  }

  var mode = String(cfg.mode || "off").toLowerCase();
  if (mode !== "local" && mode !== "production") {
    setDiag({ skipReason: "unknown_mode" });
    warn("unknown mode '" + mode + "' — skipping");
    return;
  }

  if (mode === "production") {
    var hosts = cfg.allowedHosts || ["databoar.com.br", "www.databoar.com.br"];
    var allowed = hostAllowed(hosts);
    setDiag({ hostAllowed: allowed, mode: mode });
    if (!allowed) {
      // Local file / preview hosts never send production telemetry
      setDiag({ skipReason: "host_not_allowed" });
      return;
    }
  } else {
    setDiag({ hostAllowed: true, mode: mode });
  }

  var sdkSrc = cfg.sdkSrc || resolveScriptBase() + "vendor/faro-web-sdk.iife.js";
  loadScript(
    sdkSrc,
    function () {
      initFaro(mode);
    },
    function () {
      setDiag({ skipReason: "sdk_load_failed", sdkLoaded: false });
      warn("SDK bundle failed to load");
    }
  );
})();
