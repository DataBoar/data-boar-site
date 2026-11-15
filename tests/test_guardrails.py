"""
Guardrail suite — data-boar-site.  **This is NOT a toy project.**

Inviolable gates (see docs/adr/ADR-0001). Run in CI and by the local gates
(scripts/pre-commit = fast subset · scripts/check-all.sh = full). NEVER weaken
or remove a guardrail — add, never subtract.

Categories:
  anti_regression  — the live form must post to HubSpot; bilingual intact; robots/sitemap; CNAME.
  security         — no committed secrets; external links carry rel=noopener; no dangerous JS sinks.
  supply_chain (3) — (1) GitHub Actions pinned to a full SHA; (2) external-resource allowlist;
                     (3) form submits only to the HubSpot endpoint allowlist.
  anti_overclaim   — forbidden absolute/legal-conclusion claims (evidence, not legal conclusion).
  anti_llm_decision— no LLM/generative model "decides" findings; keep the deterministic/no-LLM posture.
  hitl             — commits carry NO tool co-authorship (`Co-Authored-By: <tool>`) nor session
                     trailers; the HITL is the sole author (SSH-signed, enforced by the ruleset).
"""
import glob
import os
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import ClassVar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = sorted(
    glob.glob(os.path.join(ROOT, "*.html"))
    + glob.glob(os.path.join(ROOT, "casos", "*.html"))
)


EN_FILES = sorted(
    glob.glob(os.path.join(ROOT, "en", "*.html"))
    + glob.glob(os.path.join(ROOT, "en", "casos", "*.html"))
)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _html(include_en=False):
    """Keys are paths relative to repo root (forward slashes).

    The generated English pages (en/) are left out by default: the structural tests
    (chrome sync, bilingual parity) are about the PT source pages. The content tests
    (overclaim, LLM, external links) ask for them with include_en=True.
    """
    out = {}
    for p in HTML_FILES + (EN_FILES if include_en else []):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        out[rel] = _read(p)
    return out


def _git(*args):
    return subprocess.run(
        ["git", "-C", ROOT, *args], capture_output=True, text=True, check=False
    ).stdout


class AntiRegression(unittest.TestCase):
    def test_form_config_has_real_hubspot_values(self):
        """Regression guard for the empty-form-config bug (#22): the form must post to HubSpot."""
        cfg = _read(os.path.join(ROOT, "js", "form-config.js"))
        self.assertRegex(cfg, r"portalId:\s*['\"]\d{6,}['\"]", "portalId vazio/ausente")
        self.assertRegex(
            cfg, r"demoFormGuid:\s*['\"][0-9a-f-]{20,}['\"]", "demoFormGuid vazio/ausente"
        )

    def test_pages_deploy_queues_and_avoids_unquoted_secret_heredoc(self):
        """#22 race + #68 JS injection: never cancel mid-inject; never <<EOF with secrets."""
        wf = _read(os.path.join(ROOT, ".github", "workflows", "pages-deploy.yml"))
        self.assertRegex(
            wf,
            r"cancel-in-progress:\s*false",
            "pages concurrency must queue (#22) — cancel mid-inject published empty form-config",
        )
        self.assertNotRegex(
            wf,
            r"<<EOF\b",
            "unquoted heredoc expands secrets into JS (#68) — use json.dumps / <<'PY'",
        )
        self.assertIn("json.dumps", wf)
        self.assertIn("refusing deploy", wf)

    def test_security_yml_osv_scanner_job_is_sha256_pinned(self):
        """#91: osv-scanner v2.6.0 checksum pin (keen-platypus / issue comment)."""
        wf = _read(os.path.join(ROOT, ".github", "workflows", "security.yml"))
        self.assertIn("osv-scanner:", wf)
        self.assertIn("2.6.0", wf)
        self.assertIn(
            "ca69b3d3cd08f889a49dc0a383122f71cc528b83803671df5fd874d97485b108",
            wf,
        )
        self.assertIn("--allow-no-lockfiles", wf)
        chk = _read(os.path.join(ROOT, "scripts", "check-all.sh"))
        self.assertIn("--skip-osv-scanner", chk)
        self.assertIn("--allow-no-lockfiles", chk)

    def test_ensure_osv_scanner_does_not_promote_binary_on_bad_sha256(self):
        """PR #94: checksum fail must return 1 before mv into scripts/.cache/osv-scanner."""
        src = _read(os.path.join(ROOT, "scripts", "check-all.sh"))
        ver = re.search(r'^OSV_VER="([^"]+)"', src, flags=re.MULTILINE)
        sha = re.search(r'^OSV_SHA256="([^"]+)"', src, flags=re.MULTILINE)
        self.assertTrue(ver and sha)
        start = src.index("ensure_osv_scanner() {")
        end = src.index('\nif [ "$SKIP_OSV"', start)
        fn = src[start:end]
        body = fn[fn.index("{") + 1 :].rstrip().removesuffix("}")
        idx_if = body.rfind("if ! echo")
        idx_sum = body.rfind("sha256sum -c -")
        idx_mv = body.find('mv "$OSV_CACHE/osv-scanner.download"')
        self.assertGreater(idx_if, -1)
        self.assertGreater(idx_sum, idx_if)
        self.assertGreater(idx_mv, idx_sum)
        between = body[idx_if:idx_mv]
        self.assertIn("return 1", between)
        self.assertRegex(between, r"if !")

        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "cache"
            bindir = Path(td) / "bin"
            cache.mkdir()
            bindir.mkdir()
            curl = bindir / "curl"
            curl.write_text(
                "#!/bin/sh\n"
                "out=\n"
                "while [ $# -gt 0 ]; do\n"
                '  if [ "$1" = "-o" ]; then shift; out=$1; fi\n'
                "  shift\n"
                "done\n"
                'printf "tampered-not-osv\\n" > "$out"\n',
                encoding="utf-8",
            )
            curl.chmod(0o755)
            # Must shadow a real /usr/bin/osv-scanner so we actually hit curl+sha256.
            fake_osv = bindir / "osv-scanner"
            fake_osv.write_text(
                '#!/bin/sh\necho "osv-scanner version: 0.0.0-not-pinned"\n',
                encoding="utf-8",
            )
            fake_osv.chmod(0o755)
            wrapper = Path(td) / "run.sh"
            wrapper.write_text(
                "#!/usr/bin/env bash\n"
                "set -uo pipefail\n"
                f"OSV_VER={ver.group(1)!r}\n"
                f"OSV_SHA256={sha.group(1)!r}\n"
                f"OSV_CACHE={str(cache)!r}\n"
                "ensure_osv_scanner() {\n"
                f"{body}\n"
                "}\n"
                "ensure_osv_scanner\n"
                "exit $?\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PATH"] = f"{bindir}{os.pathsep}/usr/bin{os.pathsep}/bin"
            proc = subprocess.run(
                ["bash", str(wrapper)],
                cwd=td,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((cache / "osv-scanner").exists())
            self.assertFalse((cache / "osv-scanner").is_file())

    def test_pages_deploy_rejects_unpinned_upload_pages_artifact_v3(self):
        """Keep Pages SHA-pin regression next to the concurrency test above."""
        wf = _read(os.path.join(ROOT, ".github", "workflows", "pages-deploy.yml"))
        # Transitive pin: v3.0.1 composite used upload-artifact@v4 (org policy fail).
        self.assertNotIn(
            "56afc609e74202658d3ffba0e8f6dda462b719fa",
            wf,
            "upload-pages-artifact v3.0.1 calls unpinned upload-artifact@v4",
        )
        self.assertIn("fc324d3547104276b827a68afc52ff2a11cc49c9", wf)
        self.assertIn("include-hidden-files: true", wf)
        self.assertIn("bbbca2ddaa5d8feaa63e36b76fdaad77386f024f", wf)

    def test_wheelhouse_docs_use_exclusive_index_url(self):
        """#69: never recommend --extra-index-url (dependency confusion with PyPI)."""
        src = _read(os.path.join(ROOT, "scripts", "build-wheelhouse-index.py"))
        self.assertNotRegex(
            src,
            r"pip\s+install\s+[^\n]*--extra-index-url",
            "install examples must not use --extra-index-url (merges PyPI)",
        )
        self.assertRegex(
            src,
            r"pip\s+install\s+--index-url\s+https://databoar\.com\.br/simple/",
        )
        self.assertIn("dependency confusion", src.lower())

    def test_wheelhouse_install_pages_use_exclusive_index_url(self):
        """#69 applies to the per-OS install notes too, not only to the script."""
        for rel in ("opensource.html", os.path.join("docs", "WHEELHOUSE_BSD_HAIKU.md")):
            txt = _read(os.path.join(ROOT, rel))
            self.assertNotRegex(
                txt,
                r"pip\s+install\s+[^\n]*--extra-index-url",
                f"{rel}: install examples must not use --extra-index-url",
            )
            self.assertRegex(
                txt,
                r"pip\s+install\s+--index-url\s+https://databoar\.com\.br/simple/",
                f"{rel}: expected the exclusive --index-url install example",
            )

    def test_bilingual_panels_present(self):
        for name, txt in _html().items():
            if name in ("privacidade.html", "opensource.html", "login.html",
                        "solucao.html", "agende-demonstracao.html", "index.html",
                        "praticas-de-engenharia.html"):
                self.assertIn('data-lang-panel="pt-BR"', txt, f"{name}: sem painel pt-BR")
                self.assertIn('data-lang-panel="en"', txt, f"{name}: sem painel en")

    def test_robots_and_sitemap_exist(self):
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "robots.txt")))
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "sitemap.xml")))

    def test_cname_is_canonical(self):
        cname = _read(os.path.join(ROOT, "CNAME")).strip()
        self.assertEqual(cname, "databoar.com.br")

    def _normalize_chrome(self, rel: str, block: str) -> str:
        """Strip casos/ ``../`` prefix so nested pages compare equal to root."""
        if rel.startswith("casos/"):
            block = block.replace('href="../', 'href="').replace('src="../', 'src="')
        return block

    def test_footer_block_identical_across_pages(self):
        """Single canonical <footer> — fails on structural drift (no build pipeline).

        Nested pages (casos/) may use a ``../`` prefix on relative href/src; that is
        stripped before comparison. Absolute URLs and panel markup must match.
        Source of truth: partials/site-chrome/footer.html (+ sync-site-chrome.py).
        """
        footer_re = re.compile(r"<footer\b[^>]*>.*?</footer>", re.DOTALL | re.IGNORECASE)

        pages = _html()
        self.assertIn("index.html", pages)
        m = footer_re.search(pages["index.html"])
        self.assertIsNotNone(m, "index.html: sem <footer>")
        canon = self._normalize_chrome("index.html", m.group(0))
        self.assertIn("docs/MAP.pt_BR.md", canon, "Documentação pt-BR deve apontar para MAP.pt_BR.md")
        self.assertIn("docs/MAP.md", canon, "Docs en deve apontar para MAP.md")
        self.assertNotIn("docs/README.md", canon)
        self.assertIn("footer-brand", canon, "canônico inclui coluna logo/blurb")
        self.assertIn("casos-de-uso", canon)
        self.assertIn('href="verticais.html"', canon, "footer Recursos deve apontar Verticais")

        for rel, html in sorted(pages.items()):
            if "<footer" not in html.lower():
                continue
            fm = footer_re.search(html)
            self.assertIsNotNone(fm, f"{rel}: sem <footer>")
            got = self._normalize_chrome(rel, fm.group(0))
            self.assertEqual(
                got,
                canon,
                f"{rel}: <footer> diverge do canônico (index.html / partials)",
            )

    def test_nav_links_identical_across_pages(self):
        """Single canonical #site-nav — sector pages under Verticais, not one-off links."""
        nav_re = re.compile(
            r'<nav\s+class="links"\s+id="site-nav"\s*>.*?</nav>',
            re.DOTALL | re.IGNORECASE,
        )
        pages = _html()
        self.assertIn("index.html", pages)
        m = nav_re.search(pages["index.html"])
        self.assertIsNotNone(m, "index.html: sem #site-nav")
        canon = self._normalize_chrome("index.html", m.group(0))
        self.assertNotIn("verticais.html", canon, "Verticais fica no footer Recursos, não no #site-nav")
        self.assertIn("faq.html", canon)
        self.assertIn("casos-de-uso-en", canon)

        for rel, html in sorted(pages.items()):
            nm = nav_re.search(html)
            self.assertIsNotNone(nm, f"{rel}: sem #site-nav")
            got = self._normalize_chrome(rel, nm.group(0))
            self.assertEqual(
                got,
                canon,
                f"{rel}: #site-nav diverge do canônico (rode sync-site-chrome.py)",
            )

    def test_announce_and_nav_cta_contract(self):
        """Brown .announce on every page; Agendar only there; .nav-cta = Login + lang."""
        pages = _html()
        self.assertIn("index.html", pages)

        def class_block(html: str, class_name: str) -> str | None:
            open_re = re.compile(
                r'<div\b[^>]*\bclass=(["\'])([^"\']*)\1[^>]*>',
                re.IGNORECASE,
            )
            start = pos = None
            for m in open_re.finditer(html):
                if class_name in m.group(2).split():
                    start, pos = m.start(), m.end()
                    break
            if start is None:
                return None
            depth = 1
            token_re = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
            for tm in token_re.finditer(html, pos):
                tok = tm.group(0)
                if tok.startswith("</"):
                    depth -= 1
                    if depth == 0:
                        return html[start : tm.end()]
                elif not tok.rstrip().endswith("/>"):
                    depth += 1
            return None

        ann_canon = self._normalize_chrome(
            "index.html", class_block(pages["index.html"], "announce")
        )
        cta_canon = self._normalize_chrome(
            "index.html", class_block(pages["index.html"], "nav-cta")
        )
        self.assertIsNotNone(ann_canon)
        self.assertIsNotNone(cta_canon)
        self.assertIn("mini-btn", ann_canon)
        self.assertNotIn("mini-btn", cta_canon)
        self.assertIn("lang-switch", cta_canon)

        for rel, html in sorted(pages.items()):
            ann = class_block(html, "announce")
            cta = class_block(html, "nav-cta")
            self.assertIsNotNone(ann, f"{rel}: sem .announce")
            self.assertIsNotNone(cta, f"{rel}: sem .nav-cta")
            self.assertEqual(
                self._normalize_chrome(rel, ann),
                ann_canon,
                f"{rel}: .announce diverge do canônico",
            )
            self.assertEqual(
                self._normalize_chrome(rel, cta),
                cta_canon,
                f"{rel}: .nav-cta diverge do canônico",
            )
            header = re.search(
                r"<header\b.*?>(.*?)</header>", html, re.DOTALL | re.IGNORECASE
            )
            self.assertIsNotNone(header, f"{rel}: sem <header>")
            self.assertNotIn(
                "mini-btn",
                header.group(1),
                f"{rel}: Agendar vazou para o <header>",
            )

    def test_site_chrome_sync_check(self):
        """Wrapper must report clean — partials are the only chrome source of truth."""
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "sync-site-chrome.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            proc.returncode,
            0,
            f"site-chrome drift:\n{proc.stdout}\n{proc.stderr}",
        )

    def test_legal_section_btn_primary_keeps_readable_color(self):
        """`.legal a` must not paint `.btn-primary` gold-on-gold (specificity trap)."""
        css = _read(os.path.join(ROOT, "css", "style.css"))
        self.assertRegex(
            css,
            r"\.legal\s+a\s*\{[^}]*color:\s*var\(--color-accent\)",
            "expected .legal a accent link style (context for the override)",
        )
        self.assertRegex(
            css,
            r"\.legal\s+a\.btn-primary\s*\{[^}]*color:\s*var\(--color-primary\)",
            "missing .legal a.btn-primary override — CTA text becomes invisible",
        )
        # Pages that ship primary CTAs inside section.legal (regression inventory)
        pages = _html()
        for rel in (
            "casos/menores-lgpd-art-14.html",
            "inventario-dados-pessoais-lgpd.html",
            "descobrir-dados-pessoais.html",
            "data-discovery-contabilidade.html",
            "data-discovery-advocacia.html",
            "data-discovery-condominios.html",
            "verticais.html",
            "faq.html",
        ):
            txt = pages[rel]
            self.assertIn('class="legal"', txt, f"{rel}: expected section.legal")
            self.assertIn("btn-primary", txt, f"{rel}: expected btn-primary CTA")


class Security(unittest.TestCase):
    # Public, non-secret identifiers that are allowed to appear in source.
    PUBLIC_OK = ("51690011", "76d53fe2", "3065320542")
    SECRET_PATTERNS: ClassVar[list[str]] = [
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"\bAKIA[0-9A-Z]{16}\b",             # AWS access key id
        r"\bghp_[0-9A-Za-z]{30,}\b",         # GitHub PAT
        r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b", # Slack token
        r"\bsk-[0-9A-Za-z]{20,}\b",          # generic secret key
    ]

    def _tracked_text_files(self):
        out = _git("ls-files")
        for rel in out.splitlines():
            if rel.split(".")[-1] in ("html", "js", "css", "json", "yml", "yaml", "txt", "md", "xml"):
                yield rel

    def test_no_committed_secrets(self):
        for rel in self._tracked_text_files():
            txt = _read(os.path.join(ROOT, rel))
            for pat in self.SECRET_PATTERNS:
                m = re.search(pat, txt)
                self.assertIsNone(m, f"possível segredo em {rel}: {pat}")

    def test_security_txt_rfc9116_paths_match(self):
        """RFC 9116: /.well-known/security.txt plus optional root copy for Pages."""
        root = _read(os.path.join(ROOT, "security.txt"))
        well = _read(os.path.join(ROOT, ".well-known", "security.txt"))
        self.assertEqual(root, well)
        self.assertRegex(root, r"(?m)^Contact:\s+mailto:security@databoar\.com\.br\s*$")
        self.assertRegex(root, r"(?m)^Expires:\s+\d{4}-\d{2}-\d{2}T")
        self.assertIn("Canonical: https://databoar.com.br/.well-known/security.txt", root)

    def test_external_links_have_noopener(self):
        for name, txt in _html(include_en=True).items():
            self.assertEqual(
                _blank_without_noopener(txt), [], f"{name}: target=_blank sem rel=noopener"
            )

    def test_no_dangerous_js_sinks(self):
        for js in glob.glob(os.path.join(ROOT, "js", "*.js")):
            txt = _read(js)
            for bad in ("eval(", "new Function(", "document.write(", ".innerHTML ="):
                self.assertNotIn(bad, txt, f"{os.path.basename(js)}: sink perigoso {bad}")


class SupplyChain(unittest.TestCase):
    # (2) hosts allowed to be contacted by the visitor's browser. Google Fonts is a
    # KNOWN, documented exception pending self-hosting (see ADR-0001 / backlog #C).
    ALLOWED_EXTERNAL_HOSTS: ClassVar[set[str]] = {"fonts.googleapis.com", "fonts.gstatic.com"}
    # (3) endpoints the form JS is allowed to POST to.
    ALLOWED_FORM_HOSTS: ClassVar[set[str]] = {"api.hsforms.com"}

    def test_1_actions_pinned_to_sha(self):
        for wf in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")):
            for line in _read(wf).splitlines():
                m = re.search(r"uses:\s*([^\s@]+)@([^\s#]+)", line)
                if not m:
                    continue
                ref = m.group(2)
                self.assertRegex(
                    ref, r"^[0-9a-f]{40}$",
                    f"{os.path.basename(wf)}: action {m.group(1)} não pinada em SHA (ref={ref})",
                )

    def test_2_external_resources_allowlisted(self):
        # LOADED resources only: src=, and <link rel=stylesheet|preconnect|… href=>.
        # Navigation (<a href=…>) and metadata (<link rel=canonical|alternate>) are out of scope —
        # the browser does not fetch those as third-party assets the way stylesheets/fonts are.
        _loaded_link_rels = (
            "stylesheet", "preconnect", "preload", "prefetch", "dns-prefetch",
            "icon", "apple-touch-icon", "mask-icon",
        )
        for name, txt in _html(include_en=True).items():
            loaded = re.findall(r'\bsrc="(https?://[^"]+)"', txt)
            for tag in re.findall(r"<link\b[^>]*>", txt, flags=re.IGNORECASE):
                href_m = re.search(r'\bhref="(https?://[^"]+)"', tag, flags=re.IGNORECASE)
                rel_m = re.search(r'\brel="([^"]+)"', tag, flags=re.IGNORECASE)
                if not href_m or not rel_m:
                    continue
                rels = {r.strip().lower() for r in rel_m.group(1).split()}
                if rels.isdisjoint(_loaded_link_rels):
                    continue  # e.g. rel=canonical — SEO metadata, not a loaded asset
                loaded.append(href_m.group(1))
            for url in loaded:
                host = re.sub(r"^https?://", "", url).split("/")[0].lower()
                self.assertIn(
                    host, self.ALLOWED_EXTERNAL_HOSTS,
                    f"{name}: recurso externo CARREGADO fora do allowlist: {host} ({url[:60]})",
                )

    def test_3_form_endpoint_allowlisted(self):
        forms = _read(os.path.join(ROOT, "js", "forms.js"))
        for url in re.findall(r"https?://([^/\"'\s]+)", forms):
            host = url.lower()
            # ignore fallback mailto/domain mentions; only real POST hosts matter
            if host.endswith("hsforms.com") or host in self.ALLOWED_FORM_HOSTS:
                continue
            # allow our own domain / docs references, but never a generic exfil endpoint
            self.assertTrue(
                host.endswith(("databoar.com.br", "hubspot.com")),
                f"forms.js contata host inesperado: {host}",
            )


class BestiaryCopy(unittest.TestCase):
    """Order of 2026-11-14: the beasts section says only what the repos' docs prove.

    The source repos are private: no link to them, no internal detail, nothing simulated
    presented as product, and no legal wording in this section.
    """

    SECTIONS: ClassVar[tuple[str, ...]] = ("bestiais", "beasts")
    FORBIDDEN: ClassVar[list[str]] = [
        r"github\.com/DataBoar/(faithful-ferret|sage-remora|stealthy-stoat|keen-platypus)",
        r"ttl[_-]seconds",
        r"\bL3\b",
        r"futurex",
        r"ADR-\d{4}",
        r"\b(LGPD|RGPD|GDPR|DPO|encarregad|titular)\w*",
        r"conclus(ão|ao)\s+jur(í|i)dica",
        r"legal\s+(conclusion|ruling)",
        r"CAVP[- ]validated\b",
        r"FIPS[- ]140",
    ]

    def _sections(self):
        txt = _read(os.path.join(ROOT, "opensource.html"))
        out = []
        for sid in self.SECTIONS:
            m = re.search(
                rf'<section class="diff-section" id="{sid}">(.*?)</section>', txt, re.DOTALL
            )
            self.assertIsNotNone(m, f"opensource.html: section #{sid} missing")
            out.append((sid, m.group(1)))
        return out

    def test_beasts_section_has_no_internal_or_legal_detail(self):
        for sid, body in self._sections():
            for pat in self.FORBIDDEN:
                m = re.search(pat, body, re.IGNORECASE)
                self.assertIsNone(m, f"#{sid}: forbidden /{pat}/ -> {m.group(0) if m else ''}")

    def test_beasts_section_labels_what_is_simulated(self):
        for sid, body in self._sections():
            low = body.lower()
            self.assertTrue(
                "simulad" in low or "simulated" in low, f"#{sid}: HSM must be labeled simulated"
            )
            self.assertTrue(
                "sint" in low or "synthetic" in low, f"#{sid}: demo data must be labeled synthetic"
            )
            self.assertTrue(
                "versão publicada" in low or "published release" in low,
                f"#{sid}: must say no release is published",
            )

    def test_pointers_from_home_and_solution_reach_the_section(self):
        for rel in ("index.html", "solucao.html"):
            txt = _read(os.path.join(ROOT, rel))
            self.assertIn('href="opensource.html#bestiais"', txt, rel)
            self.assertIn('href="opensource.html#beasts"', txt, rel)


_VOID = frozenset({"br", "img", "input", "meta", "link", "hr", "source", "col", "area",
                   "base", "embed", "track", "wbr"})
_SKIP = frozenset({"script", "style", "svg", "noscript", "head"})
_CHROME = frozenset({"header", "footer", "nav"})


class _PanelScan(HTMLParser):
    """Collects the PT/EN language panels of a page and the visible text outside them."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []     # (tag, lang, element id)
        self.records = []   # one dict per language panel, in document order
        self.loose = []     # visible content text that sits outside every panel
        self._open = []     # (stack depth, record) of the panels still open
        self._seq = 0

    def handle_starttag(self, tag, attrs):
        if tag in _VOID:
            return
        lang = dict(attrs).get("data-lang-panel")
        parent = self.stack[-1][2] if self.stack else 0
        self._seq += 1
        self.stack.append((tag, lang, self._seq))
        if lang:
            rec = {"lang": lang, "tag": tag, "parent": parent, "words": []}
            self.records.append(rec)
            self._open.append((len(self.stack), rec))

    def handle_endtag(self, tag):
        if tag in _VOID or tag not in [s[0] for s in self.stack]:
            return
        while self.stack:
            depth = len(self.stack)
            popped = self.stack.pop()
            if self._open and self._open[-1][0] == depth:
                self._open.pop()
            if popped[0] == tag:
                break

    def handle_data(self, data):
        words = data.split()
        if not words:
            return
        tags = [s[0] for s in self.stack]
        if any(tag in _SKIP for tag in tags):
            return
        if self._open:
            for _, rec in self._open:
                rec["words"].extend(words)
            return
        if any(tag in _CHROME for tag in tags):
            return
        if re.search(r"[^\W\d_]", data):  # ignore separators and punctuation
            self.loose.append(" ".join(words))


def _scan_panels(txt):
    scan = _PanelScan()
    scan.feed(txt)
    return scan


def _parity_problems(name, txt):
    """Every way a page can leave one language without its counterpart."""
    scan = _scan_panels(txt)
    problems = [
        f"{name}: texto de conteudo fora de painel de idioma: {text[:70]!r}"
        for text in scan.loose
    ]
    by_parent = {}
    for rec in scan.records:
        by_parent.setdefault(rec["parent"], []).append(rec)
    total_pt = total_en = 0
    for recs in by_parent.values():
        for i, rec in enumerate(recs):
            sample = " ".join(rec["words"][:6])
            if rec["lang"] not in ("pt-BR", "en"):
                problems.append(f"{name}: idioma de painel desconhecido {rec['lang']!r}")
            elif rec["lang"] == "pt-BR":
                twin = recs[i + 1] if i + 1 < len(recs) else None
                if twin is None or twin["lang"] != "en" or twin["tag"] != rec["tag"]:
                    problems.append(f"{name}: painel PT sem irmao EN logo apos: {sample!r}")
                    continue
                if not twin["words"]:
                    problems.append(f"{name}: painel EN vazio para o PT {sample!r}")
                    continue
                total_pt += len(rec["words"])
                total_en += len(twin["words"])
                if len(rec["words"]) >= 15:
                    ratio = len(twin["words"]) / len(rec["words"])
                    if not 0.6 <= ratio <= 1.5:
                        problems.append(
                            f"{name}: razao de palavras EN/PT {ratio:.2f} fora de 0,6-1,5: {sample!r}"
                        )
            elif i == 0 or recs[i - 1]["lang"] != "pt-BR":
                problems.append(f"{name}: painel EN sem PT antes: {sample!r}")
    if total_pt and not 0.6 <= total_en / total_pt <= 1.5:
        problems.append(f"{name}: razao de palavras da pagina {total_en / total_pt:.2f} fora de 0,6-1,5")
    return problems


class BilingualParity(unittest.TestCase):
    """Every PT content block has a non-empty EN twin (text, not only nav). Faithful
    translation is a human review; this gate only blocks a page that leaves a language out."""

    def test_every_page_has_en_for_every_pt_block(self):
        problems = []
        for name, txt in _html().items():
            problems.extend(_parity_problems(name, txt))
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_scanner_catches_a_missing_translation(self):
        base = '<body><div data-lang-panel="pt-BR"><p>{}</p></div>{}</body>'
        long_pt = " ".join(["palavra"] * 20)
        long_en = " ".join(["word"] * 20)
        ok = base.format(long_pt, f'<div data-lang-panel="en" hidden><p>{long_en}</p></div>')
        self.assertEqual(_parity_problems("ok.html", ok), [])
        no_twin = base.format(long_pt, "")
        self.assertTrue(any("sem irmao EN" in p for p in _parity_problems("a.html", no_twin)))
        empty = base.format(long_pt, '<div data-lang-panel="en" hidden></div>')
        self.assertTrue(any("EN vazio" in p for p in _parity_problems("b.html", empty)))
        short = base.format(long_pt, '<div data-lang-panel="en" hidden><p>word</p></div>')
        self.assertTrue(any("razao" in p for p in _parity_problems("c.html", short)))
        loose = ok.replace("<body>", "<body><p>Texto solto em portugues</p>")
        self.assertTrue(any("fora de painel" in p for p in _parity_problems("d.html", loose)))


def _build_en():
    """The generator module (scripts/build-en.py), loaded by path."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_en", os.path.join(ROOT, "scripts", "build-en.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Extract(HTMLParser):
    """Reads a page with a real HTML parser, never with a regex over tags.

    Regexes that "filter" HTML (``<script.*?</script>``) miss ``<SCRIPT>``, ``</script >``
    and friends — CodeQL py/bad-tag-filter. The parser knows them all.
    ``rest`` is the page without script/style elements; ``scripts`` holds (type, body).
    """

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.rest = []
        self.scripts = []
        self.tags = []  # (tag, {attr: value}) of every start tag, scripts included
        self._open = None

    def handle_starttag(self, tag, attrs):
        attr = {k.lower(): (v or "") for k, v in attrs}
        self.tags.append((tag, attr))
        if tag in ("script", "style"):
            self._open = (tag, attr.get("type", "").lower(), [])
        else:
            self.rest.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self._open and tag == self._open[0]:
            self.scripts.append((self._open[0], self._open[1], "".join(self._open[2])))
            self._open = None
        else:
            self.rest.append(f"</{tag}>")

    def handle_data(self, data):
        (self._open[2] if self._open else self.rest).append(data)

    def handle_entityref(self, name):
        self.rest.append(f"&{name};")

    def handle_charref(self, name):
        self.rest.append(f"&#{name};")

    def handle_comment(self, data):
        self.rest.append(f"<!--{data}-->")


def _extract(txt):
    parser = _Extract()
    parser.feed(txt)
    parser.close()
    return parser


def _ids(txt):
    return {a[k] for _t, a in _extract(txt).tags for k in ("id", "name") if a.get(k)}


def _links(txt):
    return [a[k] for _t, a in _extract(txt).tags for k in ("href", "src") if k in a]


def _ld_blocks(txt):
    import json

    return [json.loads(body) for _t, kind, body in _extract(txt).scripts if kind == "application/ld+json"]


def _blank_without_noopener(txt):
    """href of every target=_blank anchor that lacks rel=noopener (any case, any quoting)."""
    return [
        attr.get("href", "")
        for tag, attr in _extract(txt).tags
        if tag == "a"
        and attr.get("target", "").lower() == "_blank"
        and "noopener" not in attr.get("rel", "").lower().split()
    ]


def _shape(obj, key=""):
    """Structure of a JSON-LD value: keys, list lengths, @type/position kept, text erased."""
    if isinstance(obj, dict):
        return {k: _shape(v, k) for k, v in obj.items() if k not in ("inLanguage", "dateModified")}
    if isinstance(obj, list):
        return [_shape(v, key) for v in obj]
    return obj if key in ("@context", "@type", "position") else "text"


class EnglishSite(unittest.TestCase):
    """/en/ is generated (scripts/build-en.py) and committed; hreflang, JSON-LD and dates agree."""

    PAIRS: ClassVar[list[str]] = []
    SINGLE: ClassVar[set[str]] = {"login.html", "agende-demonstracao.html"}

    @classmethod
    def setUpClass(cls):
        cls.b = _build_en()
        cls.PAIRS = cls.b.pair_pages()
        cls.pt = {rel: _read(os.path.join(ROOT, rel)) for rel in cls.b.all_pages()}
        cls.en = {rel: _read(os.path.join(ROOT, "en", rel)) for rel in cls.PAIRS}

    def test_generator_check_is_clean(self):
        """The committed /en/, head blocks, stamps and sitemap are what the script writes."""
        if self.b.is_shallow():
            self.skipTest("shallow clone: the page dates come from the full git log")
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "build-en.py"), "--check"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(r.returncode, 0, f"drift em /en/ — rode scripts/build-en.py:\n{r.stdout}{r.stderr}")

    def test_parser_rebuild_is_lossless(self):
        """The generator rewrites pages with an HTML parser: with no rule applied it must change nothing."""
        for rel, txt in self.pt.items():
            self.assertEqual(self.b.rebuild(txt, None, set()), txt, f"{rel}: rebuild altera o HTML")

    def test_en_pages_match_the_pairs_exactly(self):
        found = {os.path.relpath(p, os.path.join(ROOT, "en")).replace("\\", "/") for p in EN_FILES}
        self.assertEqual(found, set(self.PAIRS))
        for rel in self.SINGLE:
            self.assertNotIn(rel, found, f"{rel} é URL única e não tem par em /en/")

    def test_en_pages_are_only_english(self):
        accent = re.compile(r"[ãõçáéíóúâêôà]", re.IGNORECASE)
        for rel, txt in self.en.items():
            self.assertIn('<html lang="en">', txt, rel)
            self.assertNotIn('data-lang-panel="pt-BR"', txt, f"en/{rel}: painel PT sobrou")
            self.assertNotRegex(txt, r"<[^<>]*\shidden(?=[\s>/])", f"en/{rel}: elemento oculto sobrou")
            self.assertEqual([t for t, _a in _extract(txt).tags].count("h1"), 1, f"en/{rel}: um h1 só")
            body = "".join(_extract(txt).rest)
            for line in body.splitlines():
                if "Português (Brasil)" in line:  # the PT name of the language, in the selector
                    continue
                self.assertIsNone(accent.search(line), f"en/{rel}: texto em PT: {line.strip()[:100]}")

    def test_every_page_has_one_main_and_articles_where_expected(self):
        for rel, txt in self.pt.items():
            self.assertEqual([t for t, _a in _extract(txt).tags].count("main"), 1, f"{rel}: um <main> só")
            self.assertLess(txt.index("</header>"), txt.index("<main"), rel)
            self.assertLess(txt.index("</main>"), txt.index("<footer"), rel)
        for rel in self.PAIRS:
            if 'property="og:type" content="article"' in self.pt[rel]:
                self.assertIn("<article", self.pt[rel], f"{rel}: página de artigo sem <article>")
                self.assertIn("<article", self.en[rel], f"en/{rel}: página de artigo sem <article>")

    def test_hreflang_is_complete_and_reciprocal(self):
        alt = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')
        for rel in self.PAIRS:
            want = {
                "pt-BR": self.b.url(rel, "pt"),
                "en": self.b.url(rel, "en"),
                "x-default": self.b.url(rel, "pt"),
            }
            for label, txt, own in (("", self.pt[rel], "pt"), ("en/", self.en[rel], "en")):
                self.assertEqual(dict(alt.findall(txt)), want, f"{label}{rel}: hreflang")
                canon = re.findall(r'<link rel="canonical" href="([^"]+)">', txt)
                self.assertEqual(canon, [self.b.url(rel, own)], f"{label}{rel}: canonical próprio")
                if 'property="og:url"' in txt:
                    self.assertIn(f'property="og:url" content="{self.b.url(rel, own)}"', txt)
                    loc = "pt_BR" if own == "pt" else "en_US"
                    self.assertIn(f'property="og:locale" content="{loc}"', txt, f"{label}{rel}")
        for rel in self.SINGLE:
            self.assertNotIn("hreflang", self.pt[rel], f"{rel}: URL única fica fora do hreflang")

    def test_sitemap_lists_both_languages_with_alternates_and_real_dates(self):
        import xml.etree.ElementTree as ET

        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
        root = ET.parse(os.path.join(ROOT, "sitemap.xml")).getroot()
        entries = {}
        for u in root.findall("s:url", ns):
            loc = u.find("s:loc", ns).text
            entries[loc] = (
                u.find("s:lastmod", ns).text,
                {a.get("hreflang"): a.get("href") for a in u.findall("x:link", ns)},
            )
        for rel in self.PAIRS:
            want = {
                "pt-BR": self.b.url(rel, "pt"),
                "en": self.b.url(rel, "en"),
                "x-default": self.b.url(rel, "pt"),
            }
            day = re.search(r'<time datetime="([^"]+)"', self.pt.get(rel, "")) if rel != "index.html" else None
            for lang in ("pt", "en"):
                loc = self.b.url(rel, lang)
                self.assertIn(loc, entries, f"sitemap sem {loc}")
                self.assertEqual(entries[loc][1], want, f"sitemap: alternates de {loc}")
                if day:
                    self.assertEqual(entries[loc][0], day.group(1), f"sitemap: lastmod de {loc}")
        locs = set(entries)
        self.assertNotIn(f"{self.b.BASE}/login.html", locs)
        self.assertNotIn(f"{self.b.BASE}/en/agende-demonstracao.html", locs)
        for loc in locs:  # nothing in the sitemap points to a file that does not exist
            path = loc.replace(self.b.BASE + "/", "") or "index.html"
            path = (path + "index.html") if path.endswith("/") else path
            self.assertTrue(os.path.exists(os.path.join(ROOT, path)), f"sitemap: {loc} não existe")

    def test_jsonld_has_the_same_shape_in_both_languages_and_the_same_date(self):
        for rel in self.PAIRS:
            pt, en = _ld_blocks(self.pt[rel]), _ld_blocks(self.en[rel])
            self.assertEqual(len(pt), len(en), f"{rel}: nº de blocos JSON-LD")
            for a, b in zip(pt, en, strict=True):
                self.assertEqual(_shape(a), _shape(b), f"{rel}: estrutura do JSON-LD")
                self.assertEqual(a["inLanguage"], "pt-BR", rel)
                self.assertEqual(b["inLanguage"], "en", f"en/{rel}")
                self.assertRegex(a["dateModified"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertEqual(a["dateModified"], b["dateModified"], rel)
                if rel != "index.html":
                    self.assertIn(f'datetime="{a["dateModified"]}"', self.pt[rel], f"{rel}: data visível")
                    self.assertIn(f'datetime="{a["dateModified"]}"', self.en[rel], f"en/{rel}: data visível")

    def test_page_dates_are_not_in_the_future(self):
        today = __import__("datetime").date.today().isoformat()
        for rel in self.PAIRS:
            for m in re.findall(r'<time datetime="([^"]+)"', self.pt[rel]):
                self.assertLessEqual(m, today, f"{rel}: data no futuro")

    def test_en_links_resolve_to_files_and_anchors(self):
        for rel, txt in self.en.items():
            base = os.path.dirname(os.path.join(ROOT, "en", rel))
            for link in _links(txt):
                if re.match(r"^(https?:|mailto:|tel:|//)", link):
                    continue
                path, _, frag = link.partition("#")
                if not path:
                    target = txt
                else:
                    full = os.path.normpath(os.path.join(base, path))
                    if full.endswith(os.sep) or os.path.isdir(full):
                        full = os.path.join(full, "index.html")
                    self.assertTrue(os.path.exists(full), f"en/{rel}: link quebrado {link}")
                    target = _read(full) if full.endswith(".html") else ""
                if frag and target:
                    self.assertIn(frag, _ids(target), f"en/{rel}: âncora inexistente {link}")

    def test_en_pages_link_single_url_pages_at_the_root(self):
        for rel, txt in self.en.items():
            for single in self.SINGLE:
                for link in _links(txt):
                    if link.endswith(single):
                        self.assertNotIn("en/", link)
                        self.assertTrue(link.startswith("../"), f"en/{rel}: {link} deve apontar para a raiz")

    def test_language_switch_navigates_and_never_redirects_by_browser(self):
        js = _read(os.path.join(ROOT, "js", "site.js"))
        self.assertNotRegex(js, r"navigator\.(languages?|userLanguage)", "sem detecção de idioma pelo navegador")
        self.assertNotRegex(js, r"location\.(replace|assign)\(", "sem redirect automático")
        self.assertIn('rel="alternate"][hreflang=', js, "o seletor navega pelo hreflang da página")

    def test_hreflang_pairs_have_no_orphan_en_files(self):
        self.assertEqual(self.b.pair_pages(), self.PAIRS)
        self.assertFalse(
            [p for p in EN_FILES if os.path.relpath(p, os.path.join(ROOT, "en")).replace("\\", "/") not in self.PAIRS]
        )


class HtmlParsingGuard(unittest.TestCase):
    """The guardrails read HTML with a parser; these pages are the ones a regex gets wrong."""

    def test_script_and_style_variants_are_not_page_content(self):
        page = (
            '<p>ok</p><SCRIPT>var a = "<a href=no>";</SCRIPT ><script type="application/LD+JSON">'
            '{"a": 1}</script ><Style>a{}</STYLE><!-- <script>x</script> -->'
            '<A HREF="yes.html" TARGET="_blank" REL="noopener">x</A>'
        )
        got = _extract(page)
        self.assertEqual(_links(page), ["yes.html"])
        self.assertEqual([k for _t, k, _b in got.scripts], ["", "application/ld+json", ""])
        self.assertEqual(_ld_blocks(page), [{"a": 1}])
        self.assertNotIn("var a", "".join(got.rest))

    def test_noopener_check_sees_uppercase_and_single_quoted_anchors(self):
        bad = "<A TARGET='_blank' HREF='https://x.example'>x</A>"
        good = '<a target="_blank" href="https://x.example" rel="noopener noreferrer">x</a>'
        self.assertEqual(_blank_without_noopener(bad), ["https://x.example"])
        self.assertEqual(_blank_without_noopener(good), [])

    def test_no_regex_filters_script_or_style_tags_in_tests_and_scripts(self):
        """py/bad-tag-filter: no re.* over <script>/<style>; the parser does it."""
        bad = re.compile(r"re\.\w+\(.*<\(?(script|style)", re.IGNORECASE)
        for path in glob.glob(os.path.join(ROOT, "tests", "*.py")) + glob.glob(
            os.path.join(ROOT, "scripts", "*.py")
        ):
            for n, line in enumerate(_read(path).splitlines(), 1):
                if os.path.basename(path) == "test_guardrails.py" and "bad = re.compile" in line:
                    continue
                self.assertIsNone(bad.search(line), f"{os.path.basename(path)}:{n}: regex sobre <script>/<style>")


class AntiOverclaim(unittest.TestCase):
    FORBIDDEN: ClassVar[list[str]] = [
        r"garante[m]?\s+(a\s+)?conformidade",
        r"guarantees?\s+compliance",
        r"ensures?\s+compliance",
        r"\bcertifica(mos)?\b(?!\w)",
        r"\bcertifies\b",
        r"100%\s+de\s+(conformidade|precis|detec)",
        r"RIPD\s*\(Art\.?\s*30\)",          # the exact normative bug (RIPD is not LGPD Art.30)
        r"DPIA\s*\(Art\.?\s*30\)",          # DPIA is GDPR Art.35, not 30 (Art.30 = ROPA)
        r"byte\s+a\s+byte",                 # absolute reproducibility claim for ML/DL
        r"byte\s+for\s+byte",
        r"conclus(ão|ao)\s+jur(í|i)dica\b(?!.{0,40}n(ã|a)o)",  # must be "evidence, NOT legal conclusion"
    ]

    def test_no_forbidden_overclaims(self):
        for name, txt in _html(include_en=True).items():
            for pat in self.FORBIDDEN:
                m = re.search(pat, txt, re.IGNORECASE)
                self.assertIsNone(
                    m, f"{name}: overclaim proibido /{pat}/ -> {m.group(0) if m else ''}"
                )


class AntiLlmDecision(unittest.TestCase):
    # Only clearly AFFIRMATIVE "we use an LLM / generative model" claims are forbidden.
    # The site's correct posture ("nenhum LLM decide" / "sem LLM") must NOT be flagged.
    FORBIDDEN: ClassVar[list[str]] = [
        r"powered\s+by\s+(gpt|chatgpt|an?\s+llm|generative)",
        r"\b(gpt-4|gpt-5|chatgpt)\b",
        r"\bllm-powered\b",
    ]

    def test_no_llm_decides_findings(self):
        for name, txt in _html(include_en=True).items():
            for pat in self.FORBIDDEN:
                m = re.search(pat, txt, re.IGNORECASE)
                self.assertIsNone(m, f"{name}: claim de LLM-decisor /{pat}/")

    def test_no_llm_posture_present_somewhere(self):
        blob = " ".join(_html().values()).lower()
        self.assertTrue(
            ("sem llm" in blob) or ("no llm" in blob) or ("determin" in blob),
            "o site deve declarar a postura determinística / sem-LLM em algum lugar",
        )


class Hitl(unittest.TestCase):
    """The HITL is the sole author. No tool co-authorship / session trailers in commit messages."""

    FORBIDDEN_TRAILERS: ClassVar[list[str]] = [
        r"(?im)^\s*co-authored-by:\s*claude",
        r"(?im)^\s*co-authored-by:\s*(cursor|copilot|gpt|chatgpt|gemini|grok)",
        r"(?im)^\s*claude-session:",
        r"(?im)^\s*generated with \[?claude",
    ]

    def test_new_commits_have_no_tool_coauthorship(self):
        # Enforce going FORWARD from the guardrails baseline tag. Commits BEFORE the baseline
        # carry the 2026-08-05 incident trailers and are frozen (the branch ruleset blocks
        # history rewrite). Every commit AFTER the baseline MUST be clean.
        base = _git("rev-parse", "-q", "--verify", "refs/tags/guardrails-baseline^{commit}").strip()
        rng = f"{base}..HEAD" if base else "-1"
        log = _git("log", rng, "--format=%B%n==GRD==")
        for pat in self.FORBIDDEN_TRAILERS:
            m = re.search(pat, log)
            self.assertIsNone(
                m,
                f"commit novo com co-autoria/sessão de ferramenta proibida: {m.group(0) if m else ''}",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
