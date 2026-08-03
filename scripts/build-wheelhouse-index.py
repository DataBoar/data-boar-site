#!/usr/bin/env python3
"""Generate a PEP 503 "simple" index for the hosted data BOAR wheelhouse.

The wheels live as assets of a GitHub Release on this same repo
(DataBoar/data-boar-site, tag wheelhouse-x86-64-v1-*). This script reads that
release, groups the .whl by normalized project name, and emits a static
simple/ tree that GitHub Pages can serve so the wheels are pip-installable:

    pip install --extra-index-url https://databoar.com.br/simple/ numpy

Regenerate after every wheelhouse release (or wire into CI). Requires `gh`
authenticated. Deterministic output — no timestamps — so re-runs are no-ops
unless the release changed.

Usage:
    python3 scripts/build-wheelhouse-index.py [--repo OWNER/REPO] [--tag TAG] [--out simple]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "DataBoar/data-boar-site"
# Keep in sync with scripts/docker/apply_wheelhouse_v1.sh in the data-boar repo.
DEFAULT_TAG = "wheelhouse-x86-64-v1-2026-07-29"


def normalize(name: str) -> str:
    """PEP 503 normalized project name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def fetch_assets(repo: str, tag: str) -> list[dict]:
    out = subprocess.check_output(
        [
            "gh", "api", f"repos/{repo}/releases/tags/{tag}",
            "--jq", "[.assets[] | {name, digest, url: .browser_download_url}]",
        ],
        text=True,
    )
    return json.loads(out)


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sha256_fragment(digest: str | None) -> str:
    if digest and digest.startswith("sha256:"):
        return "#sha256=" + digest.split(":", 1)[1]
    return ""


def write_html(path: Path, title: str, links: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(links)
    html = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="pypi:repository-version" content="1.0">\n'
        f"<title>{html_escape(title)}</title>\n</head>\n<body>\n"
        f"<h1>{html_escape(title)}</h1>\n{body}\n</body>\n</html>\n"
    )
    path.write_text(html, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--tag", default=DEFAULT_TAG)
    ap.add_argument("--out", default="simple")
    args = ap.parse_args()

    assets = fetch_assets(args.repo, args.tag)
    wheels = [a for a in assets if a["name"].endswith(".whl")]
    if not wheels:
        print(f"error: no .whl assets on {args.repo}@{args.tag}", file=sys.stderr)
        return 1

    # Group by normalized project name. In a wheel filename the distribution is
    # the first '-'-separated field (PEP 427: internal '-' become '_'), so
    # split('-')[0] is safe.
    packages: dict[str, list[dict]] = {}
    for w in wheels:
        dist = w["name"].split("-")[0]
        packages.setdefault(normalize(dist), []).append(w)

    out = Path(args.out)
    names = sorted(packages)

    # Root index: one link per project.
    root_links = [f'<a href="{n}/">{n}</a><br>' for n in names]
    write_html(out / "index.html", "data BOAR wheelhouse — PEP 503 index", root_links)

    # Per-project index: one link per wheel, with #sha256=.
    for n in names:
        links = []
        for w in sorted(packages[n], key=lambda x: x["name"]):
            href = w["url"] + sha256_fragment(w.get("digest"))
            links.append(f'<a href="{href}">{html_escape(w["name"])}</a><br>')
        write_html(out / n / "index.html", f"Links for {n}", links)

    print(f"OK: {len(names)} projects, {len(wheels)} wheels -> {out}/")
    for n in names:
        print(f"  {n} ({len(packages[n])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
