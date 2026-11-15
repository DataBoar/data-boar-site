#!/usr/bin/env python3
"""Build the English site (/en/), hreflang, "updated" stamps and the sitemap.

Source of truth: the Portuguese pages at the repo root and in casos/. Each of
them carries its English body in a hidden ``data-lang-panel="en"`` panel
(see tests/test_guardrails.py::BilingualParity). This script derives from them:

  en/<page>.html            the English page (html lang="en", own canonical,
                            only the EN panels, links and assets rewritten).
                            Committed: GitHub Pages runs no build step.
  head block in PT pages    canonical + hreflang pt-BR/en/x-default (+ og:locale:alternate),
                            between the i18n-head markers.
  "updated" stamp           visible date + JSON-LD dateModified/inLanguage, from the git log.
  sitemap.xml               lastmod from the git log, xhtml:link alternates, /en/ entries.

EN head metadata (title, description, og:*, JSON-LD) is the translated copy kept in
partials/i18n/head.en.json. login.html and agende-demonstracao.html stay single-URL
(no EN twin, outside hreflang) and are never touched here.

The date of a page is the date of the last commit that changed it in a way other
than the lines this script manages (the managed lines are ignored, otherwise
writing the stamp would move the date it records).

Usage:
  python3 scripts/build-en.py           # write everything
  python3 scripts/build-en.py --check   # exit 1 on drift (check-all / CI)
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import posixpath
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://databoar.com.br"
HEAD_DATA = os.path.join(ROOT, "partials", "i18n", "head.en.json")
SITEMAP = os.path.join(ROOT, "sitemap.xml")

# Single-URL pages: no EN twin, outside hreflang.
EXCLUDED = {"login.html", "agende-demonstracao.html"}
# No visible "updated" stamp on the landing page.
NO_STAMP = {"index.html"}

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
SKIP_ABS = re.compile(r"^(https?:|mailto:|tel:|#|//|/)", re.IGNORECASE)
# Lines this script writes: ignored when dating a page by its git history.
MANAGED = re.compile(
    r'i18n-head|page-updated|dateModified|inLanguage|hreflang|rel="canonical"|og:locale'
)

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]


# ── pages and URLs ──────────────────────────────────────────────────────────

def all_pages() -> list[str]:
    root = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    nested = sorted(
        "casos/" + os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "casos", "*.html"))
    )
    return root + nested


def pair_pages() -> list[str]:
    return [p for p in all_pages() if p not in EXCLUDED]


def url(rel: str, lang: str) -> str:
    """Absolute URL of a page in a language ('pt' or 'en')."""
    path = "" if rel == "index.html" else rel
    return f"{BASE}/{path}" if lang == "pt" else f"{BASE}/en/{path}"


def read(path: str) -> str:
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ── git dates ───────────────────────────────────────────────────────────────

def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", ROOT, *args], capture_output=True, text=True, check=False
    ).stdout


def is_shallow() -> bool:
    return _git("rev-parse", "--is-shallow-repository").strip() == "true"


def content_date(rel: str) -> str:
    """ISO date of the last real change to the page (managed lines ignored)."""
    dirty = _git("diff", "HEAD", "-U0", "--", rel)
    for line in dirty.splitlines():
        if line[:1] in "+-" and not line.startswith(("+++", "---")):
            body = line[1:].strip()
            if body and not MANAGED.search(body):
                return dt.date.today().isoformat()
    for entry in _git("log", "--no-merges", "--format=%H %cs", "--", rel).splitlines():
        sha, day = entry.split()
        diff = _git("show", "--format=", "-U0", sha, "--", rel)
        for line in diff.splitlines():
            if line[:1] in "+-" and not line.startswith(("+++", "---")):
                body = line[1:].strip()
                if body and not MANAGED.search(body):
                    return day
    return dt.date.today().isoformat()


def pt_date(day: str) -> str:
    y, m, d = day.split("-")
    return f"{d}/{m}/{y}"


def en_date(day: str) -> str:
    y, m, d = day.split("-")
    return f"{MONTHS_EN[int(m) - 1]} {int(d)}, {y}"


# ── PT pages: managed head block, stamp, JSON-LD ────────────────────────────

HEAD_BEGIN = "<!-- i18n-head:begin -->"
HEAD_END = "<!-- i18n-head:end -->"
STAMP_BEGIN = "<!-- page-updated:begin -->"
STAMP_END = "<!-- page-updated:end -->"
HEAD_RE = re.compile(re.escape(HEAD_BEGIN) + r".*?" + re.escape(HEAD_END) + r"\n", re.DOTALL)
STAMP_RE = re.compile(re.escape(STAMP_BEGIN) + r".*?" + re.escape(STAMP_END) + r"\n", re.DOTALL)
CANON_RE = re.compile(r'<link rel="canonical"[^>]*>\n', re.IGNORECASE)


class _LdSpans(HTMLParser):
    """Where the JSON-LD script bodies are (character offsets), found by the parser.

    A regex over <script>...</script> is the classic bad tag filter (case, </script >,
    comments); the parser reports the real elements.
    """

    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.starts = [0]
        for line in text.split("\n")[:-1]:
            self.starts.append(self.starts[-1] + len(line) + 1)
        self.spans: list[tuple[int, int]] = []
        self._open: int | None = None

    def _here(self) -> int:
        line, col = self.getpos()
        return self.starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag == "script" and (dict(attrs).get("type") or "").lower() == "application/ld+json":
            self._open = self._here() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "script" and self._open is not None:
            self.spans.append((self._open, self._here()))
            self._open = None


def ld_spans(text: str) -> list[tuple[int, int]]:
    parser = _LdSpans(text)
    parser.feed(text)
    parser.close()
    return parser.spans


def map_ld(text: str, fn) -> str:
    """Rewrite every JSON-LD body with fn(inner); the newline around it is kept."""
    for start, end in reversed(ld_spans(text)):
        body = text[start:end]
        if not (body.startswith("\n") and body.endswith("\n")):
            raise SystemExit("JSON-LD script body must sit on its own lines")
        text = text[:start] + "\n" + fn(body[1:-1]) + "\n" + text[end:]
    return text


def head_block(rel: str, text: str, lang: str) -> str:
    own = url(rel, lang)
    lines = [
        HEAD_BEGIN,
        f'<link rel="canonical" href="{own}">',
        f'<link rel="alternate" hreflang="pt-BR" href="{url(rel, "pt")}">',
        f'<link rel="alternate" hreflang="en" href="{url(rel, "en")}">',
        f'<link rel="alternate" hreflang="x-default" href="{url(rel, "pt")}">',
    ]
    if 'property="og:locale"' in text:
        other = "en_US" if lang == "pt" else "pt_BR"
        lines.append(f'<meta property="og:locale:alternate" content="{other}">')
    lines.append(HEAD_END)
    return "\n".join(lines) + "\n"


def stamp_block(day: str) -> str:
    return (
        f"{STAMP_BEGIN}\n"
        f'<div class="wrap page-updated" data-lang-panel="pt-BR">Atualizado em '
        f'<time datetime="{day}">{pt_date(day)}</time></div>\n'
        f'<div class="wrap page-updated" data-lang-panel="en" hidden>Last updated '
        f'<time datetime="{day}">{en_date(day)}</time></div>\n'
        f"{STAMP_END}\n"
    )


def set_ld_meta(text: str, lang: str, day: str) -> str:
    def fix(inner: str) -> str:
        body = re.sub(r'^\s*"(inLanguage|dateModified)":.*\n', "", inner + "\n", flags=re.M)
        body = re.sub(
            r'^(  "@type": "[^"]+",\n)',
            lambda t: f'{t.group(1)}  "inLanguage": "{lang}",\n  "dateModified": "{day}",\n',
            body, count=1, flags=re.M,
        )
        return body.rstrip("\n")

    return map_ld(text, fix)


def managed_pt(rel: str, text: str, day: str) -> str:
    """The PT page with its managed blocks (head, stamp, JSON-LD) up to date."""
    text = HEAD_RE.sub("", text)
    text = CANON_RE.sub("", text)
    anchor = re.search(r'<meta name="description"[^>]*>\n', text, re.IGNORECASE)
    if not anchor:
        raise SystemExit(f"{rel}: no <meta name=description> line to anchor the head block")
    text = text[: anchor.end()] + head_block(rel, text, "pt") + text[anchor.end():]
    if rel not in NO_STAMP:
        text = STAMP_RE.sub("", text)
        if "</main>\n" not in text:
            raise SystemExit(f"{rel}: no </main> line to anchor the updated stamp")
        text = text.replace("</main>\n", stamp_block(day) + "</main>\n", 1)
    return set_ld_meta(text, "pt-BR", day)


# ── EN pages ────────────────────────────────────────────────────────────────

def rewrite_url(value: str, src_rel: str, en_set: set[str]) -> str:
    """Relative URL written for the PT page at src_rel, rewritten for en/<src_rel>."""
    if SKIP_ABS.match(value):
        return value
    frag = ""
    path = value
    if "#" in path:
        path, frag = path.split("#", 1)
        frag = "#" + frag
    if not path:
        return value
    trailing = path.endswith("/")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), path))
    if target in en_set:
        target = "en/" + target
    out = posixpath.relpath(target, posixpath.dirname("en/" + src_rel))
    return out + ("/" if trailing else "") + frag


class _Rebuild(HTMLParser):
    """Rebuilds the page text exactly; optionally keeps only the EN panels."""

    def __init__(self, src_rel: str | None, en_set: set[str]):
        super().__init__(convert_charrefs=False)
        self.src_rel = src_rel  # None: identity transform
        self.en_set = en_set
        self.out: list[str] = []
        self.stack: list[str] = []
        self.skip: int | None = None
        self.eat_nl = False
        self.line_drop = False
        self.case: dict[str, str] = {}  # html.parser lower-cases tags; SVG needs the original

    # tokens
    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, self.get_starttag_text(), False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, self.get_starttag_text(), True)

    def _start(self, tag, attrs, raw, selfclose):
        void = selfclose or tag in VOID
        panel = dict(attrs).get("data-lang-panel")
        self.case[tag] = raw[1 : 1 + len(tag)]
        if self.skip is not None:
            if not void:
                self.stack.append(tag)
            return
        self.eat_nl = False
        if self.src_rel is not None and panel == "pt-BR":
            self.line_drop = self._strip_indent()
            if void:
                self.eat_nl = self.line_drop
            else:
                self.stack.append(tag)
                self.skip = len(self.stack)
            return
        if self.src_rel is not None:
            raw = self._rewrite(raw, panel)
        self.out.append(raw)
        if not void:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[idx:]
        if self.skip is not None:
            if len(self.stack) < self.skip:
                self.skip = None
                self.eat_nl = self.line_drop
            return
        self.eat_nl = False
        self.out.append(f"</{self.case.get(tag, tag)}>")

    def handle_data(self, data):
        if self.skip is not None:
            return
        if self.eat_nl:
            self.eat_nl = False
            data = data[2:] if data.startswith("\r\n") else data[1:] if data.startswith("\n") else data
        self.out.append(data)

    def handle_entityref(self, name):
        if self.skip is None:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if self.skip is None:
            self.out.append(f"&#{name};")

    def handle_comment(self, data):
        if self.skip is None:
            self.eat_nl = False
            self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        if self.skip is None:
            self.out.append(f"<!{decl}>")

    def unknown_decl(self, data):
        if self.skip is None:
            self.out.append(f"<![{data}]>")

    def handle_pi(self, data):
        if self.skip is None:
            self.out.append(f"<?{data}>")

    # helpers
    def _strip_indent(self) -> bool:
        """Drop the indent of a dropped element that starts its own line."""
        if self.out and isinstance(self.out[-1], str):
            m = re.search(r"\n[ \t]*$", self.out[-1])
            if m:
                self.out[-1] = self.out[-1][: m.start() + 1]
                return True
        return False

    def _rewrite(self, raw: str, panel: str | None) -> str:
        if panel == "en":
            raw = re.sub(r'\s+data-lang-panel=(["\'])en\1', "", raw)
            raw = re.sub(r"\s+hidden(?=[\s/>])", "", raw)
        return re.sub(
            r'\b(href|src)=(["\'])([^"\']*)\2',
            lambda m: f"{m.group(1)}={m.group(2)}{rewrite_url(m.group(3), self.src_rel, self.en_set)}{m.group(2)}",
            raw,
        )


def rebuild(text: str, src_rel: str | None, en_set: set[str]) -> str:
    parser = _Rebuild(src_rel, en_set)
    parser.feed(text)
    parser.close()
    return "".join(parser.out)


def _sub_once(text: str, pattern: str, repl: str, what: str, rel: str, flags: int = 0) -> str:
    new, n = re.subn(pattern, lambda _m: repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"en/{rel}: {what} not found")
    return new


def _meta(text: str, kind: str, key: str, value: str, rel: str) -> str:
    new, n = re.subn(
        rf'(<meta {kind}="{re.escape(key)}" content=")[^"]*("\s*/?>)',
        lambda m: f"{m.group(1)}{esc(value)}{m.group(2)}",
        text, count=1,
    )
    if n != 1:
        raise SystemExit(f"en/{rel}: meta {key} not found")
    return new


def to_en(rel: str, pt_text: str, head: dict, day: str, en_set: set[str]) -> str:
    text = rebuild(pt_text, rel, en_set)
    text = _sub_once(text, r'<html lang="pt-BR">', '<html lang="en">', "html lang", rel)
    text = _sub_once(
        text, r"<title>.*?</title>", f"<title>{esc(head['title'])}</title>", "title", rel, re.S
    )
    text = _meta(text, "name", "description", head["description"], rel)
    has_og = 'property="og:title"' in pt_text
    if has_og != ("og:title" in head):
        raise SystemExit(f"en/{rel}: og tags in the page and in head.en.json disagree")
    if has_og:
        text = _meta(text, "property", "og:title", head["og:title"], rel)
        text = _meta(text, "property", "og:description", head["og:description"], rel)
        text = _meta(text, "property", "og:url", url(rel, "en"), rel)
        text = _meta(text, "property", "og:locale", "en_US", rel)
    text = HEAD_RE.sub(lambda _m: head_block(rel, pt_text, "en"), text, count=1)
    # JSON-LD: the translated blocks, with the same structure as the PT ones.
    blocks = head.get("jsonld", [])
    found = len(ld_spans(text))
    if found != len(blocks):
        raise SystemExit(f"en/{rel}: {found} JSON-LD blocks in the page, {len(blocks)} in head.en.json")
    it = iter(reversed(blocks))  # map_ld rewrites from the last block to the first

    def ld(_inner: str) -> str:
        block = next(it)
        ordered = {"@context": block["@context"], "@type": block["@type"],
                   "inLanguage": "en", "dateModified": day}
        ordered.update({k: v for k, v in block.items() if k not in ordered})
        return json.dumps(ordered, indent=2, ensure_ascii=False)

    text = map_ld(text, ld)
    # chrome: the selector and the menu label say English
    for old, new in (
        ('<span class="lang-flag">🇧🇷</span>', '<span class="lang-flag">🇺🇸</span>'),
        ('<span class="lang-code">PT-BR</span>', '<span class="lang-code">EN</span>'),
        ('class="lang-option selected" data-lang="pt-BR"', 'class="lang-option" data-lang="pt-BR"'),
        ('class="lang-option" data-lang="en"', 'class="lang-option selected" data-lang="en"'),
        ('aria-label="Abrir menu de navegação"', 'aria-label="Open navigation menu"'),
    ):
        if text.count(old) != 1:
            raise SystemExit(f"en/{rel}: chrome snippet not found exactly once: {old}")
        text = text.replace(old, new)
    return text


# ── sitemap ─────────────────────────────────────────────────────────────────

def build_sitemap(dates: dict[str, str], current: str) -> str:
    meta: dict[str, tuple[str, str]] = {}
    order: list[str] = []
    for m in re.finditer(  # one-line entries (hand-written) and multi-line ones (generated)
        r"<url>\s*<loc>([^<]+)</loc>.*?<changefreq>([^<]+)</changefreq>\s*<priority>([^<]+)</priority>",
        current,
        re.DOTALL,
    ):
        loc = m.group(1)
        if loc.startswith(f"{BASE}/en/"):
            continue
        meta[loc] = (m.group(2), m.group(3))
        order.append(loc)
    by_url = {url(rel, "pt"): rel for rel in all_pages()}
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for loc in order:
        rel = by_url.get(loc)
        if rel is None:
            raise SystemExit(f"sitemap.xml: {loc} is not a page of the site")
        freq, prio = meta[loc]
        day = dates[rel]
        if rel in EXCLUDED:
            lines.append(
                f"  <url><loc>{loc}</loc><lastmod>{day}</lastmod>"
                f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
            )
            continue
        alternates = (
            f'    <xhtml:link rel="alternate" hreflang="pt-BR" href="{url(rel, "pt")}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{url(rel, "en")}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{url(rel, "pt")}"/>'
        )
        for lang in ("pt", "en"):
            lines.append(
                f"  <url>\n    <loc>{url(rel, lang)}</loc>\n{alternates}\n"
                f"    <lastmod>{day}</lastmod><changefreq>{freq}</changefreq>"
                f"<priority>{prio}</priority>\n  </url>"
            )
    missing = [p for p in pair_pages() if url(p, "pt") not in meta]
    if missing:
        raise SystemExit(f"sitemap.xml has no entry for: {', '.join(missing)}")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ── driver ──────────────────────────────────────────────────────────────────

def desired() -> dict[str, str]:
    """Path (relative to the repo root) -> wanted content, for every managed file."""
    with open(HEAD_DATA, encoding="utf-8") as fh:
        heads = json.load(fh)
    pairs = pair_pages()
    en_set = set(pairs)
    unknown = set(heads) - en_set
    if unknown:
        raise SystemExit(f"head.en.json has entries for non-pair pages: {sorted(unknown)}")
    dates = {rel: content_date(rel) for rel in all_pages()}
    out: dict[str, str] = {}
    for rel in pairs:
        if rel not in heads:
            raise SystemExit(f"head.en.json has no entry for {rel}")
        pt = managed_pt(rel, read(os.path.join(ROOT, rel)), dates[rel])
        out[rel] = pt
        out["en/" + rel] = to_en(rel, pt, heads[rel], dates[rel], en_set)
    out["sitemap.xml"] = build_sitemap(dates, read(SITEMAP))
    return out


def existing_en() -> set[str]:
    found = set()
    for dirpath, _dirs, files in os.walk(os.path.join(ROOT, "en")):
        for name in files:
            found.add(os.path.relpath(os.path.join(dirpath, name), ROOT).replace(os.sep, "/"))
    return found


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 on drift instead of writing")
    args = ap.parse_args(argv)
    want = desired()
    stale = sorted(existing_en() - set(want))
    drift = []
    for rel, text in want.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path) or read(path) != text:
            drift.append(rel)
    if args.check:
        for rel in drift:
            print(f"drift: {rel} (run python3 scripts/build-en.py)")
        for rel in stale:
            print(f"stale: {rel} is not generated any more (run python3 scripts/build-en.py)")
        return 1 if drift or stale else 0
    for rel in drift:
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(want[rel])
        print(f"wrote {rel}")
    for rel in stale:
        os.remove(os.path.join(ROOT, rel))
        print(f"removed {rel}")
    print(f"build-en: {len(drift)} written, {len(stale)} removed, {len(want) - len(drift)} unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
