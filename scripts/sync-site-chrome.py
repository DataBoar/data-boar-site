#!/usr/bin/env python3
"""Sync canonical site chrome (header nav links + footer) into every HTML page.

Source of truth:
  partials/site-chrome/nav-links.html
  partials/site-chrome/footer.html

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
NAV_FILE = os.path.join(PARTIALS, "nav-links.html")
FOOTER_FILE = os.path.join(PARTIALS, "footer.html")

NAV_RE = re.compile(
    r"<nav\s+class=\"links\"\s+id=\"site-nav\"\s*>.*?</nav>",
    re.DOTALL | re.IGNORECASE,
)
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.DOTALL | re.IGNORECASE)
# Pages that used a placeholder before first sync
FOOTER_PLACEHOLDER_RE = re.compile(
    r"<!--\s*FOOTER_PLACEHOLDER\s*-->", re.IGNORECASE
)

SKIP_ABS = re.compile(
    r'^(https?:|mailto:|tel:|#|//)', re.IGNORECASE
)


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


def render_nav(nested: bool) -> str:
    inner = with_nested_prefix(_read(NAV_FILE).rstrip() + "\n", nested)
    # indent like existing pages (2 spaces inside header wrap)
    indented = "\n".join(
        ("      " + line if line.strip() else line) for line in inner.splitlines()
    )
    return f'<nav class="links" id="site-nav">\n{indented}\n    </nav>'


def render_footer(nested: bool) -> str:
    return with_nested_prefix(_read(FOOTER_FILE).rstrip() + "\n", nested).rstrip() + "\n"


def apply_chrome(html: str, nested: bool) -> str:
    nav = render_nav(nested)
    footer = render_footer(nested)
    if not NAV_RE.search(html):
        raise ValueError("missing <nav class=\"links\" id=\"site-nav\">")
    html = NAV_RE.sub(nav, html, count=1)
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

    if not os.path.isfile(NAV_FILE) or not os.path.isfile(FOOTER_FILE):
        print(f"❌ partials ausentes em {PARTIALS}", file=sys.stderr)
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
        print("✅ site-chrome sync — nav + footer alinhados aos partials")
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
