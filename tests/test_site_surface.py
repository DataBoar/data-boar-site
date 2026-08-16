"""
Deterministic surface gates — Faro wiring, chrome sync, contrast trap.

No browser, no network, no flaky timing: only committed HTML/CSS/scripts.
Run by scripts/check-all.sh (pre-PR) and CI via the same unittest entry.
Add assertions; never weaken or remove a gate.
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _site_html() -> dict[str, str]:
    """Marketing + casos HTML (excludes simple/ package stubs)."""
    paths = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(
        os.path.join(ROOT, "casos", "*.html")
    )
    out: dict[str, str] = {}
    for p in sorted(paths):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        out[rel] = _read(p)
    return out


def _normalize_nested(rel: str, block: str) -> str:
    if rel.startswith("casos/"):
        return block.replace('href="../', 'href="').replace('src="../', 'src="')
    return block


class FaroInstrumentation(unittest.TestCase):
    """Every published human page loads vendored Faro config + loader (order fixed)."""

    def _published_pages(self) -> list[str]:
        pages = list(_site_html().keys())
        simple = "simple/index.html"
        self.assertTrue(
            os.path.isfile(os.path.join(ROOT, simple)),
            "missing simple/index.html wheelhouse entry",
        )
        pages.append(simple)
        return pages

    def test_every_site_page_and_wheelhouse_index_loads_faro(self):
        pages = self._published_pages()
        self.assertGreaterEqual(len(pages), 16, "unexpectedly few published pages")
        for rel in pages:
            txt = _read(os.path.join(ROOT, rel))
            self.assertIn("faro-config.js", txt, f"{rel}: missing faro-config.js")
            self.assertIn("faro.js", txt, f"{rel}: missing faro.js")
            self.assertGreater(
                txt.find("faro.js"),
                txt.find("faro-config.js"),
                f"{rel}: faro.js must follow faro-config.js",
            )
            i_site = txt.find("site.js")
            if i_site != -1:
                self.assertGreater(
                    i_site,
                    txt.find("faro.js"),
                    f"{rel}: site.js must follow faro.js",
                )

    def test_pep503_package_stubs_do_not_load_faro(self):
        """PEP 503 package indexes stay machine-only — Faro only on simple/index.html."""
        stubs = sorted(
            glob.glob(os.path.join(ROOT, "simple", "*", "index.html"))
        )
        self.assertGreater(len(stubs), 0, "expected simple/<pkg>/index.html stubs")
        for path in stubs:
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            txt = _read(path).lower()
            self.assertNotIn("faro", txt, f"{rel}: unexpected Faro reference")


class ChromeSync(unittest.TestCase):
    """#site-nav and <footer> identical across site pages (partials + sync wrapper)."""

    def test_sync_wrapper_check_is_clean(self):
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
            f"site-chrome drift — rode sync-site-chrome.py:\n{proc.stdout}\n{proc.stderr}",
        )

    def test_nav_identical_across_site_pages(self):
        nav_re = re.compile(
            r'<nav\s+class="links"\s+id="site-nav"\s*>.*?</nav>',
            re.DOTALL | re.IGNORECASE,
        )
        pages = _site_html()
        canon = _normalize_nested("index.html", nav_re.search(pages["index.html"]).group(0))
        self.assertNotIn("verticais.html", canon, "Verticais fica no footer, não no #site-nav")
        self.assertIn("faq.html", canon)
        self.assertIn("casos-de-uso-en", canon)
        for rel, html in sorted(pages.items()):
            m = nav_re.search(html)
            self.assertIsNotNone(m, f"{rel}: missing #site-nav")
            self.assertEqual(
                _normalize_nested(rel, m.group(0)),
                canon,
                f"{rel}: #site-nav diverges from canonical",
            )

    def test_footer_identical_across_site_pages(self):
        footer_re = re.compile(r"<footer\b[^>]*>.*?</footer>", re.DOTALL | re.IGNORECASE)
        pages = _site_html()
        canon = _normalize_nested(
            "index.html", footer_re.search(pages["index.html"]).group(0)
        )
        self.assertIn('href="verticais.html"', canon)
        for rel, html in sorted(pages.items()):
            m = footer_re.search(html)
            self.assertIsNotNone(m, f"{rel}: missing <footer>")
            self.assertEqual(
                _normalize_nested(rel, m.group(0)),
                canon,
                f"{rel}: <footer> diverges from canonical",
            )


class ContrastReadable(unittest.TestCase):
    """Deterministic guard against gold-on-gold / invisible CTA text in .legal."""

    def test_css_override_legal_btn_primary(self):
        css = _read(os.path.join(ROOT, "css", "style.css"))
        self.assertRegex(
            css,
            r"\.legal\s+a\s*\{[^}]*color:\s*var\(--color-accent\)",
            "expected .legal a accent link (sets up the specificity trap)",
        )
        self.assertRegex(
            css,
            r"\.legal\s+a\.btn-primary\s*\{[^}]*color:\s*var\(--color-primary\)",
            "missing .legal a.btn-primary override — CTA text becomes invisible",
        )
        self.assertRegex(
            css,
            r"\.legal\s+a\.btn-outline\s*\{[^}]*color:\s*var\(--color-primary\)",
            "missing .legal a.btn-outline override",
        )

    def test_every_legal_page_with_btn_primary_is_guarded(self):
        """Inventory is dynamic: any new .legal + btn-primary page is covered."""
        pages = _site_html()
        legal_with_cta = [
            rel
            for rel, html in pages.items()
            if 'class="legal"' in html and "btn-primary" in html
        ]
        self.assertGreaterEqual(
            len(legal_with_cta),
            8,
            f"expected several .legal CTA pages, got {legal_with_cta}",
        )
        css = _read(os.path.join(ROOT, "css", "style.css"))
        self.assertIn(".legal a.btn-primary", css)
        for rel in legal_with_cta:
            # Page uses the shared stylesheet that carries the override
            self.assertIn(
                "css/style.css",
                pages[rel].replace("../css/style.css", "css/style.css"),
                f"{rel}: must load css/style.css (btn-primary contrast override lives there)",
            )


if __name__ == "__main__":
    unittest.main()
