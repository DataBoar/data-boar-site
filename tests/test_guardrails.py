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
import unittest
from typing import ClassVar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILES = sorted(
    glob.glob(os.path.join(ROOT, "*.html"))
    + glob.glob(os.path.join(ROOT, "casos", "*.html"))
)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _html():
    """Keys are paths relative to repo root (forward slashes)."""
    out = {}
    for p in HTML_FILES:
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

    def test_bilingual_panels_present(self):
        for name, txt in _html().items():
            if name in ("privacidade.html", "opensource.html", "login.html",
                        "solucao.html", "agende-demonstracao.html", "index.html"):
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
        self.assertIn("verticais.html", canon)
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

    def test_external_links_have_noopener(self):
        for name, txt in _html().items():
            for tag in re.findall(r"<a\b[^>]*target=\"_blank\"[^>]*>", txt):
                self.assertIn("noopener", tag, f"{name}: target=_blank sem rel=noopener: {tag[:80]}")

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
        for name, txt in _html().items():
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
        for name, txt in _html().items():
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
        for name, txt in _html().items():
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
