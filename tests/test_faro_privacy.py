"""
Faro RUM privacy / config guards — data-boar-site issue #70.

Static checks so we never ship bearer tokens, form/query exfil hooks, or
accidental production send without an explicit, host-gated config.
"""
import glob
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


class FaroConfigSafe(unittest.TestCase):
    def test_production_config_enabled_for_databoar(self):
        cfg = _read(os.path.join(ROOT, "js", "faro-config.js"))
        self.assertRegex(cfg, r"enabled:\s*true")
        self.assertRegex(cfg, r'mode:\s*"production"')
        self.assertRegex(
            cfg,
            r'collectorUrl:\s*\n?\s*"https://faro-collector-prod-sa-east-1\.grafana\.net/collect/[0-9a-f]{32}"',
        )
        self.assertRegex(cfg, r"samplingRate:\s*0\.2")
        self.assertRegex(cfg, r"tracingEnabled:\s*false")
        # Public collect path only — no write tokens / bearer headers
        self.assertIsNone(re.search(r"(?i)\bglc_[A-Za-z0-9]+", cfg))
        self.assertIsNone(re.search(r"(?i)authorization\s*[:=]\s*['\"][^'\"]+['\"]", cfg))
        self.assertIsNone(re.search(r"(?i)bearer\s+[a-z0-9_\-.]{8,}", cfg))

    def test_stub_hosts_are_databoar_com_br_only(self):
        cfg = _read(os.path.join(ROOT, "js", "faro-config.js"))
        self.assertIn('"databoar.com.br"', cfg)
        self.assertIn('"www.databoar.com.br"', cfg)
        self.assertNotIn("data-boar.com", cfg)
        self.assertNotIn("dashboard.net.br", cfg)

    def test_example_is_parameterized_not_secret(self):
        ex = _read(os.path.join(ROOT, "js", "faro-config.example.js"))
        self.assertIn("REPLACE-WITH-GRAFANA-CLOUD-FARO-COLLECTOR-URL", ex)
        self.assertIn("tracingEnabled: false", ex)
        # No live credentials / bearer material (mentions of "Cloudflare tokens" in comments are OK)
        self.assertIsNone(re.search(r"(?i)authorization\s*[:=]\s*['\"][^'\"]+['\"]", ex))
        self.assertIsNone(re.search(r"(?i)bearer\s+[a-z0-9_\-.]{8,}", ex))
        self.assertIsNone(re.search(r"(?i)\bglc_[A-Za-z0-9]+", ex))
        self.assertIsNone(re.search(r"(?i)api[_-]?token\s*[:=]\s*['\"][^'\"]+['\"]", ex))
        self.assertNotRegex(ex, r"https://faro-collector-[^\"']+grafana\.net/collect/[A-Za-z0-9]+")


class FaroLoaderPrivacy(unittest.TestCase):
    def setUp(self):
        self.src = _read(os.path.join(ROOT, "js", "faro.js"))

    def test_no_form_cookie_or_replay_capture(self):
        self.assertNotIn("FormData", self.src)
        self.assertNotIn("document.cookie", self.src)
        self.assertNotIn("ReplayInstrumentation", self.src)
        self.assertNotRegex(self.src, r"addEventListener\(\s*['\"]key")
        # Opt-out may read location.search; must not export it as telemetry path
        self.assertIn("faro=0", self.src)
        self.assertNotIn("location.search,", self.src)
        self.assertNotIn("location.href,", self.src)

    def test_scrub_and_opt_out_present(self):
        self.assertIn("beforeSend", self.src)
        self.assertIn("databoar_faro_opt_out", self.src)
        self.assertIn("safePathname", self.src)
        self.assertIn("ConsoleTransport", self.src)
        self.assertIn("allowedHosts", self.src)

    def test_no_api_key_assignment_from_config(self):
        # Public collect URL only — never wire cfg.apiKey / Authorization request headers
        self.assertNotIn("cfg.apiKey", self.src)
        self.assertNotRegex(self.src, r"\bapiKey\s*:")
        self.assertNotRegex(self.src, r"headers\s*:\s*\{[^}]*Authorization")
        self.assertNotRegex(self.src, r"setRequestHeader\s*\(\s*['\"]Authorization")

    def test_tracing_off_unless_flag(self):
        self.assertIn("tracingEnabled", self.src)
        self.assertIn("faro-web-tracing.iife.js", self.src)


class FaroVendorPinned(unittest.TestCase):
    def test_vendor_files_and_notice(self):
        sdk = os.path.join(ROOT, "js", "vendor", "faro-web-sdk.iife.js")
        tr = os.path.join(ROOT, "js", "vendor", "faro-web-tracing.iife.js")
        notice = os.path.join(ROOT, "js", "vendor", "NOTICE.md")
        self.assertTrue(os.path.isfile(sdk), "missing vendored Faro SDK")
        self.assertTrue(os.path.isfile(tr), "missing vendored Faro tracing")
        self.assertTrue(os.path.isfile(notice))
        n = _read(notice)
        self.assertIn("2.9.0", n)
        self.assertIn("0a9dc4836fadc63ad0b10a2b76d698f28bb9c2c846204690aa4c2ead61cad2ac", n)

    def test_vendor_not_loaded_from_cdn_in_html(self):
        html_files = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(
            os.path.join(ROOT, "casos", "*.html")
        )
        for path in html_files:
            txt = _read(path)
            self.assertNotIn("unpkg.com/@grafana/faro", txt)
            self.assertNotIn("jsdelivr.net/@grafana/faro", txt)
            self.assertNotIn("cdn.jsdelivr.net/npm/@grafana/faro", txt)


class FaroWiredIntoPages(unittest.TestCase):
    def test_public_pages_load_faro_before_site_js(self):
        html_files = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(
            os.path.join(ROOT, "casos", "*.html")
        )
        self.assertGreaterEqual(len(html_files), 10)
        for path in html_files:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            txt = _read(path)
            self.assertIn("faro-config.js", txt, f"{rel}: missing faro-config")
            self.assertIn("faro.js", txt, f"{rel}: missing faro.js")
            # Ordering: config, faro, then site.js
            i_cfg = txt.find("faro-config.js")
            i_faro = txt.find("faro.js")
            i_site = txt.find("site.js")
            self.assertGreater(i_faro, i_cfg, f"{rel}: faro.js before config")
            self.assertGreater(i_site, i_faro, f"{rel}: site.js should follow faro.js")


class FaroDocsAndPrivacyCopy(unittest.TestCase):
    def test_ops_doc_exists(self):
        path = os.path.join(ROOT, "docs", "ops", "FARO_FRONTEND_OBSERVABILITY.md")
        self.assertTrue(os.path.isfile(path))
        txt = _read(path)
        self.assertIn("collectorUrl", txt)
        self.assertIn("connect-src", txt)
        self.assertIn("faro-collector-prod-sa-east-1.grafana.net", txt)
        self.assertIn("verified", txt.lower())
        self.assertNotIn("activation risk", txt.lower())
        self.assertNotIn("does **not** yet include", txt)
        ex = _read(os.path.join(ROOT, "js", "faro-config.example.js"))
        self.assertIn("BLOCKER", ex)

    def test_privacy_page_mentions_rum_and_opt_out(self):
        txt = _read(os.path.join(ROOT, "privacidade.html"))
        self.assertIn("databoar_faro_opt_out", txt)
        self.assertIn("Grafana Faro", txt)
        self.assertIn("session replay", txt.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
