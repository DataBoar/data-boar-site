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
        self.assertRegex(cfg, r"samplingRate:\s*1(?:\.0)?")
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

    def test_faro0_persists_opt_out_flag(self):
        self.assertIn("persistOptOut", self.src)
        self.assertRegex(
            self.src,
            r"faro=0[\s\S]{0,200}persistOptOut\(\)|persistOptOut[\s\S]{0,200}setItem\(\s*OPT_OUT_KEY",
        )
        self.assertIn('setItem(OPT_OUT_KEY, "1")', self.src)

    def test_csp_instrumentation_disabled_and_sample_scrubbed(self):
        self.assertIn("enableContentSecurityPolicyInstrumentation: false", self.src)
        self.assertIn('lk === "sample"', self.src)
        self.assertIn('out[k] = "[redacted]"', self.src)

    def test_no_api_key_assignment_from_config(self):
        # Public collect URL only — never wire cfg.apiKey / Authorization request headers
        self.assertNotIn("cfg.apiKey", self.src)
        self.assertNotRegex(self.src, r"\bapiKey\s*:")
        self.assertNotRegex(self.src, r"headers\s*:\s*\{[^}]*Authorization")
        self.assertNotRegex(self.src, r"setRequestHeader\s*\(\s*['\"]Authorization")

    def test_tracing_off_unless_flag(self):
        self.assertIn("tracingEnabled", self.src)
        self.assertIn("faro-web-tracing.iife.js", self.src)

    def test_diag_surface_distinguishes_sampling_from_send(self):
        self.assertIn("__DATABOAR_FARO_DIAG__", self.src)
        self.assertIn("expectNetworkSend", self.src)
        self.assertIn("session_not_sampled", self.src)
        self.assertIn("sessionSampled", self.src)
        self.assertIn("collectorHost", self.src)
        self.assertIn("faro=diag", self.src)
        # Must not stash full collector URL on the diag object
        self.assertIn('delete next.collectorUrl', self.src)
        self.assertNotRegex(self.src, r"__DATABOAR_FARO_DIAG__[^=]*=[\s\S]{0,80}collectorUrl\s*:")


def _published_html_pages():
    """Site HTML served on GitHub Pages (marketing + casos + wheelhouse index).

    Nested ``simple/<pkg>/index.html`` PEP 503 package stubs are machine link
    lists regenerated by the wheelhouse builder and are out of Faro scope;
    the human/public distribution entry is ``simple/index.html`` only.
    """
    pages = (
        glob.glob(os.path.join(ROOT, "*.html"))
        + glob.glob(os.path.join(ROOT, "casos", "*.html"))
        + [os.path.join(ROOT, "simple", "index.html")]
    )
    return sorted({os.path.abspath(p) for p in pages if os.path.isfile(p)})


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
        for path in _published_html_pages():
            txt = _read(path)
            self.assertNotIn("unpkg.com/@grafana/faro", txt)
            self.assertNotIn("jsdelivr.net/@grafana/faro", txt)
            self.assertNotIn("cdn.jsdelivr.net/npm/@grafana/faro", txt)


class FaroWiredIntoPages(unittest.TestCase):
    def test_published_pages_load_faro(self):
        html_files = _published_html_pages()
        self.assertGreaterEqual(len(html_files), 11)
        self.assertTrue(
            any(p.endswith(os.path.join("simple", "index.html")) for p in html_files),
            "simple/index.html must be in the published Faro coverage set",
        )
        for path in html_files:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            txt = _read(path)
            self.assertIn("faro-config.js", txt, f"{rel}: missing faro-config")
            self.assertIn("faro.js", txt, f"{rel}: missing faro.js")
            i_cfg = txt.find("faro-config.js")
            i_faro = txt.find("faro.js")
            self.assertGreater(i_faro, i_cfg, f"{rel}: faro.js before config")
            # Marketing pages load site.js after Faro; wheelhouse index has no site.js
            i_site = txt.find("site.js")
            if i_site != -1:
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
        self.assertIn("localStorage", txt)
        # ?faro=0 must be described as persisting the flag (Bugbot #71)
        self.assertRegex(txt, r"faro=0[\s\S]{0,120}localStorage|grava o mesmo flag|persists the same flag")

    def test_ops_doc_mentions_csp_off_and_persistent_opt_out(self):
        txt = _read(os.path.join(ROOT, "docs", "ops", "FARO_FRONTEND_OBSERVABILITY.md"))
        self.assertIn("enableContentSecurityPolicyInstrumentation: false", txt)
        self.assertIn("persists", txt.lower())


class WheelhouseFaroGeneration(unittest.TestCase):
    """Faro must survive wheelhouse regen on root only (Bugbot #72)."""

    def test_write_html_root_includes_faro_package_does_not(self):
        import importlib.util
        import tempfile
        from pathlib import Path

        spec = importlib.util.spec_from_file_location(
            "build_wheelhouse_index",
            os.path.join(ROOT, "scripts", "build-wheelhouse-index.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "index.html"
            pkg = Path(tmp) / "numpy" / "index.html"
            mod.write_html(
                root,
                "data BOAR wheelhouse — PEP 503 index",
                ['<a href="numpy/">numpy</a><br>'],
                include_faro=True,
            )
            mod.write_html(
                pkg,
                "Links for numpy",
                ['<a href="https://example.com/numpy.whl">numpy.whl</a><br>'],
            )
            root_txt = root.read_text(encoding="utf-8")
            pkg_txt = pkg.read_text(encoding="utf-8")

        self.assertIn('src="../js/faro-config.js"', root_txt)
        self.assertIn('src="../js/faro.js"', root_txt)
        self.assertIn('meta name="pypi:repository-version"', root_txt)
        self.assertIn(mod.FARO_ROOT_SCRIPTS.strip(), root_txt)
        self.assertNotIn("faro", pkg_txt.lower())
        self.assertNotIn("<script", pkg_txt.lower())
        self.assertIn('meta name="pypi:repository-version"', pkg_txt)

    def test_committed_simple_tree_matches_faro_policy(self):
        root = _read(os.path.join(ROOT, "simple", "index.html"))
        self.assertIn("../js/faro-config.js", root)
        self.assertIn("../js/faro.js", root)
        # Package stubs must stay JS-free for pip/pipx
        for path in glob.glob(os.path.join(ROOT, "simple", "*", "index.html")):
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            txt = _read(path)
            self.assertNotIn("<script", txt.lower(), f"{rel}: unexpected script tag")
            self.assertNotIn("faro", txt.lower(), f"{rel}: unexpected faro reference")


if __name__ == "__main__":
    unittest.main(verbosity=2)
