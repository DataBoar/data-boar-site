#!/usr/bin/env python3
"""Sync canonical site chrome into every HTML page.

Source of truth (partials/site-chrome/):
  announce.html   — brown top bar; sole home of Agendar CTA
  nav-links.html  — links inside #site-nav
  nav-cta.html    — Login + lang-switch only (no Agendar)
  footer.html     — full <footer>…</footer>

Nested pages under casos/ get a ``../`` prefix on relative href/src.

Usage:
  python3 scripts/sync-site-chrome.py          # write pages
  python3 scripts/sync-site-chrome.py --check  # exit 1 on drift (CI / check-all)

No build pipeline — static HTML copies the chrome; this script is the wrapper
that keeps copies identical. See .cursor/rules/01-site-chrome.mdc.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIALS = os.path.join(ROOT, "partials", "site-chrome")
ANNOUNCE_FILE = os.path.join(PARTIALS, "announce.html")
NAV_FILE = os.path.join(PARTIALS, "nav-links.html")
NAV_CTA_FILE = os.path.join(PARTIALS, "nav-cta.html")
FOOTER_FILE = os.path.join(PARTIALS, "footer.html")

NAV_RE = re.compile(
    r"<nav\s+class=\"links\"\s+id=\"site-nav\"\s*>.*?</nav>",
    re.DOTALL | re.IGNORECASE,
)
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.DOTALL | re.IGNORECASE)
FOOTER_PLACEHOLDER_RE = re.compile(r"<!--\s*FOOTER_PLACEHOLDER\s*-->", re.IGNORECASE)
HEADER_RE = re.compile(r"<header\b", re.IGNORECASE)

SKIP_ABS = re.compile(r"^(https?:|mailto:|tel:|#|//)", re.IGNORECASE)

REQUIRED_PARTIALS = (ANNOUNCE_FILE, NAV_FILE, NAV_CTA_FILE, FOOTER_FILE)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read().strip() + "\n"


def _prefix_attr(match: re.Match[str], prefix: str) -> str:
    attr, quote, url = match.group(1), match.group(2), match.group(3)
    if SKIP_ABS.match(url) or url.startswith(prefix):
        return match.group(0)
    return f"{attr}={quote}{prefix}{url}{quote}"


def with_nested_prefix(fragment: str, nested: bool) -> str:
    if not nested:
        return fragment
    prefix = "../"
    return re.sub(
        r'\b(href|src)=(["\'])([^"\']+)\2',
        lambda m: _prefix_attr(m, prefix),
        fragment,
    )


def html_pages() -> list[tuple[str, bool]]:
    """Return (absolute_path, nested) for site HTML pages."""
    out: list[tuple[str, bool]] = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        out.append((p, False))
    for p in sorted(glob.glob(os.path.join(ROOT, "casos", "*.html"))):
        out.append((p, True))
    return out


def find_class_element(html: str, tag: str, class_name: str) -> tuple[int, int] | None:
    """Return [start, end) of the outer <tag class="…class_name…">…</tag>."""
    open_re = re.compile(
        rf"<{tag}\b[^>]*\bclass=(['\"])([^'\"]*)\1[^>]*>",
        re.IGNORECASE,
    )
    start = None
    for m in open_re.finditer(html):
        classes = m.group(2).split()
        if class_name in classes:
            start = m.start()
            pos = m.end()
            break
    if start is None:
        return None

    depth = 1
    token_re = re.compile(rf"</?{tag}\b[^>]*>", re.IGNORECASE)
    for tm in token_re.finditer(html, pos):
        token = tm.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return start, tm.end()
        elif token.rstrip().endswith("/>"):
            continue
        else:
            depth += 1
    return None


def render_announce(nested: bool) -> str:
    return with_nested_prefix(_read(ANNOUNCE_FILE).rstrip() + "\n", nested)


def render_nav(nested: bool) -> str:
    inner = with_nested_prefix(_read(NAV_FILE).rstrip() + "\n", nested)
    indented = "\n".join(
        ("      " + line if line.strip() else line) for line in inner.splitlines()
    )
    return f'<nav class="links" id="site-nav">\n{indented}\n    </nav>'


def render_nav_cta(nested: bool) -> str:
    raw = with_nested_prefix(_read(NAV_CTA_FILE).rstrip() + "\n", nested)
    # Partial is authored at the indent level used inside `.wrap.nav` (4 spaces).
    lines = raw.splitlines()
    if lines and not lines[0].startswith(" "):
        lines[0] = "    " + lines[0]
    return "\n".join(lines) + "\n"


def render_footer(nested: bool) -> str:
    return with_nested_prefix(_read(FOOTER_FILE).rstrip() + "\n", nested).rstrip() + "\n"


def _line_start(html: str, pos: int) -> int:
    """Expand left past spaces/tabs so replacement owns the line indent."""
    while pos > 0 and html[pos - 1] in " \t":
        pos -= 1
    return pos


def apply_announce(html: str, nested: bool) -> str:
    frag = render_announce(nested).rstrip() + "\n"
    span = find_class_element(html, "div", "announce")
    if span:
        start = _line_start(html, span[0])
        return html[:start] + frag + html[span[1] :].lstrip("\n")
    hm = HEADER_RE.search(html)
    if not hm:
        raise ValueError('missing <header> (needed to place .announce)')
    before = html[: hm.start()].rstrip() + "\n\n"
    return before + frag + "\n" + html[hm.start() :]


def apply_nav_cta(html: str, nested: bool) -> str:
    frag = render_nav_cta(nested).rstrip() + "\n"
    span = find_class_element(html, "div", "nav-cta")
    if not span:
        raise ValueError('missing <div class="nav-cta">')
    start = _line_start(html, span[0])
    return html[:start] + frag + html[span[1] :].lstrip("\n")

def apply_chrome(html: str, nested: bool) -> str:
    html = apply_announce(html, nested)
    nav = render_nav(nested)
    if not NAV_RE.search(html):
        raise ValueError('missing <nav class="links" id="site-nav">')
    html = NAV_RE.sub(nav, html, count=1)
    html = apply_nav_cta(html, nested)
    footer = render_footer(nested)
    if FOOTER_RE.search(html):
        html = FOOTER_RE.sub(footer.rstrip(), html, count=1)
    elif FOOTER_PLACEHOLDER_RE.search(html):
        html = FOOTER_PLACEHOLDER_RE.sub(footer.rstrip(), html, count=1)
    else:
        raise ValueError("missing <footer> and FOOTER_PLACEHOLDER")
    return html


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if any page drifts from partials",
    )
    args = ap.parse_args()

    missing = [p for p in REQUIRED_PARTIALS if not os.path.isfile(p)]
    if missing:
        print(f"❌ partials ausentes: {missing}", file=sys.stderr)
        return 2

    dirty: list[str] = []
    for path, nested in html_pages():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        raw = open(path, encoding="utf-8").read()
        try:
            new = apply_chrome(raw, nested)
        except ValueError as exc:
            print(f"❌ {rel}: {exc}", file=sys.stderr)
            return 2
        if new != raw:
            dirty.append(rel)
            if not args.check:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)

    if args.check:
        if dirty:
            print("❌ site-chrome drift (rode: python3 scripts/sync-site-chrome.py):")
            for rel in dirty:
                print(f"  - {rel}")
            return 1
        print("✅ site-chrome sync — announce + nav + nav-cta + footer alinhados aos partials")
        return 0

    if dirty:
        print("site-chrome synced:")
        for rel in dirty:
            print(f"  ✓ {rel}")
    else:
        print("site-chrome já sincronizado (nada a escrever)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
