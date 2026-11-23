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
python3 - "$SITE" "${SITE_LIVE_RETRIES:-8}" "${SITE_LIVE_SLEEP:-15}" <<'PY'
import hashlib, re, subprocess, sys, time

site = sys.argv[1].rstrip("/")
retries = int(sys.argv[2])
sleep_s = int(sys.argv[3])

def footer(text):
    m = re.search(r"<footer\b.*?</footer>", text, re.S | re.I)
    return m.group(0) if m else ""

def fingerprint(text):
    return hashlib.sha256(re.sub(r"\s+", " ", footer(text)).encode("utf-8")).hexdigest()

expected = fingerprint(open("faq.html", encoding="utf-8").read())
for attempt in range(1, retries + 1):
    url = f"{site}/faq.html?cb={int(time.time() * 1000)}"
    # curl, nao urllib: o Cloudflare devolve 403 para o User-Agent padrao do Python.
    res = subprocess.run(
        ["curl", "-fsSL", "--max-time", "20", "-H", "Cache-Control: no-cache", url],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        print(f"site-live-check: NAO consegui buscar {url}: {res.stderr.strip()[:200]}", file=sys.stderr)
        sys.exit(2)

    actual = fingerprint(res.stdout)
    if expected == actual:
        print(f"site-live-check: OK — ar == main ({expected[:12]}) — tentativa {attempt}/{retries} — {url}")
        sys.exit(0)

    if attempt < retries:
        print(
            f"site-live-check: ar ainda nao bateu ({actual[:12]} != {expected[:12]}) "
            f"— tentativa {attempt}/{retries}, aguardando {sleep_s}s (deploy assincrono do Pages)...",
            file=sys.stderr,
        )
        time.sleep(sleep_s)

print(
    f"site-live-check: DRIFT — main footer={expected[:12]} ar footer={actual[:12]}\n"
    f"  O ar nao reflete o main apos {retries} tentativas. "
    f"Deploy pendente, cache ou merge sem publicar.",
    file=sys.stderr,
)
sys.exit(1)
PY
