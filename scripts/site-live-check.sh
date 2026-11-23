#!/usr/bin/env bash
# site-live-check — prova que o site NO AR bate com o main (determinístico, sem cache).
#
# Cicatriz 2026-11-23: o link de comparacao.html ficou como WIP no working tree,
# o merge-green passou, mas o site continuou sem navegação. "Merge verde" NÃO
# significava "publicado". Este check fecha o buraco: falha se o ar divergir do
# main, independentemente de cache do Cloudflare/GitHub Pages.
#
# Uso:
#   bash scripts/site-live-check.sh              # usa SITE_URL ou databoar.com.br
#   SITE_URL=https://... bash scripts/site-live-check.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SITE="${SITE_URL:-https://databoar.com.br}"

# 1) Gate local: o main tem que estar com chrome e /en/ sincronizados.
#    Se houve drift, a falha é no repo — não no ar.
python3 scripts/sync-site-chrome.py --check
python3 scripts/build-en.py --check

# 2) Marker determinístico = hash do <footer> renderizado de faq.html.
#    O footer é injetado pelo mesmo partial em todas as páginas; compará-lo
#    prova que o ar contém o chrome do commit atual do main.
python3 - "$SITE" <<'PY'
import hashlib, re, subprocess, sys, time

site = sys.argv[1].rstrip("/")

def footer(text):
    m = re.search(r"<footer\b.*?</footer>", text, re.S | re.I)
    return m.group(0) if m else ""

def fingerprint(text):
    return hashlib.sha256(re.sub(r"\s+", " ", footer(text)).encode("utf-8")).hexdigest()

expected = fingerprint(open("faq.html", encoding="utf-8").read())
url = f"{site}/faq.html?cb={int(time.time())}"
# curl, nao urllib: o Cloudflare devolve 403 para o User-Agent padrao do Python.
res = subprocess.run(
    ["curl", "-fsSL", "--max-time", "20", "-H", "Cache-Control: no-cache", url],
    capture_output=True, text=True,
)
if res.returncode != 0:
    print(f"site-live-check: NAO consegui buscar {url}: {res.stderr.strip()[:200]}", file=sys.stderr)
    sys.exit(2)

live = res.stdout
actual = fingerprint(live)
if expected != actual:
    print(
        f"site-live-check: DRIFT — main footer={expected[:12]} ar footer={actual[:12]}\n"
        f"  O ar ainda nao reflete o main (deploy pendente, cache ou merge sem publicar).",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"site-live-check: OK — ar == main ({expected[:12]}) — {url}")
PY
