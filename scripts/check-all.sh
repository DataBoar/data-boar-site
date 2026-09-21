#!/usr/bin/env bash
# check-all — FULL local gate for data-boar-site (run before opening a PR / before merge).
# Mirrors the data-boar `check-all` discipline: green locally BEFORE push (ADR-0080 spirit).
# NOT a toy project — this gate is inviolable (docs/adr/ADR-0001). Add checks, never remove.
#   --skip-osv-scanner  skip OSV dependency scan (same flag as keen-platypus check-all)
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
fail=0
SKIP_OSV=0
for arg in "$@"; do
  case "$arg" in
    --skip-osv-scanner) SKIP_OSV=1 ;;
    -h|--help)
      echo "uso: $0 [--skip-osv-scanner]"
      exit 0
      ;;
    *)
      echo "check-all: argumento desconhecido: $arg" >&2
      echo "uso: $0 [--skip-osv-scanner]" >&2
      exit 2
      ;;
  esac
done

run() { echo; echo "── $1 ──"; shift; if "$@"; then echo "  ✅ ok"; else echo "  ❌ FALHOU"; fail=1; fi; }

# 0) Site chrome (nav + footer) must match partials/site-chrome — no silent drift
run "site-chrome sync --check" python3 scripts/sync-site-chrome.py --check

# 0b) Deterministic surface gates: Faro on every human page · chrome identical · contrast
run "site surface (faro + chrome + contrast)" python3 -m unittest -q tests.test_site_surface

# 1) Guardrail suite (anti-regression · security · supply-chain · anti-overclaim · anti-llm · hitl)
run "guardrails (unittest)" python3 -m unittest -q tests.test_guardrails

# 1b) Faro RUM privacy / config guards (issue #70)
run "faro privacy (unittest)" python3 -m unittest -q tests.test_faro_privacy

# 2) Ruff on tests/ — mirrors CI job py-ruff in .github/workflows/security.yml.
#    Same availability pattern as tidy/node: use the tool when present; if missing,
#    fail loudly (CI always installs ruff — a silent skip here would greenwash).
if command -v ruff >/dev/null 2>&1; then
  run "ruff check tests/" ruff check tests/
elif python3 -m ruff --version >/dev/null 2>&1; then
  run "ruff check tests/ (python3 -m)" python3 -m ruff check tests/
else
  echo
  echo "── ruff check tests/ ──"
  echo "  ❌ FALHOU — ruff ausente (CI security.yml · py-ruff instala e roda \`ruff check tests/\`)"
  echo "     instale: pip install ruff   # ou: uv tool install ruff"
  fail=1
fi

# 3) Lint / code quality (best-effort; skip if tool absent, never silently pass a present tool)
if command -v tidy >/dev/null 2>&1; then
  run "html tidy (errors only)" bash -c 'for f in *.html; do tidy -qe "$f" || exit 1; done'
fi
if command -v node >/dev/null 2>&1; then
  run "js syntax (node --check)" bash -c 'for f in js/*.js; do node --check "$f" || exit 1; done'
else
  run "js syntax (py compile of check)" python3 - <<'PY'
import glob, sys
# minimal sanity: balanced braces/parens per JS file
bad=0
for f in glob.glob("js/*.js"):
    s=open(f, encoding="utf-8").read()
    for a,b in (("{","}"),("(",")"),("[","]")):
        if s.count(a)!=s.count(b):
            print(f"  desbalanceado {a}{b} em {f}"); bad=1
sys.exit(bad)
PY
fi

# 4) OSV dependency scan — mirrors CI job osv-scanner (#91). Pin = keen-platypus 2.6.0.
OSV_VER="2.6.0"
OSV_SHA256="ca69b3d3cd08f889a49dc0a383122f71cc528b83803671df5fd874d97485b108"
OSV_CACHE="$(pwd)/scripts/.cache"
ensure_osv_scanner() {
  mkdir -p "$OSV_CACHE"
  if command -v osv-scanner >/dev/null 2>&1 && osv-scanner --version 2>/dev/null | grep -qF "$OSV_VER"; then
    return 0
  fi
  if [ -x "$OSV_CACHE/osv-scanner" ] && "$OSV_CACHE/osv-scanner" --version 2>/dev/null | grep -qF "$OSV_VER"; then
    PATH="$OSV_CACHE:$PATH"
    export PATH
    return 0
  fi
  echo "check-all: baixando osv-scanner v${OSV_VER} para ${OSV_CACHE}..." >&2
  curl -sSfL "https://github.com/google/osv-scanner/releases/download/v${OSV_VER}/osv-scanner_linux_amd64" \
    -o "$OSV_CACHE/osv-scanner.download"
  echo "${OSV_SHA256}  $OSV_CACHE/osv-scanner.download" | sha256sum -c -
  mv "$OSV_CACHE/osv-scanner.download" "$OSV_CACHE/osv-scanner"
  chmod +x "$OSV_CACHE/osv-scanner"
  PATH="$OSV_CACHE:$PATH"
  export PATH
}

if [ "$SKIP_OSV" = "1" ]; then
  echo
  echo "── osv-scanner ──"
  echo "  ⏭️  skip (--skip-osv-scanner)"
else
  if ensure_osv_scanner && command -v osv-scanner >/dev/null 2>&1; then
    # Static site: no lockfiles today → --allow-no-lockfiles (CI same). Exit 128 without it.
    run "osv-scanner scan source -r ." osv-scanner scan source -r . --allow-no-lockfiles
  else
    echo
    echo "── osv-scanner ──"
    echo "  ❌ FALHOU — osv-scanner v${OSV_VER} ausente (CI security.yml baixa e verifica sha256)"
    fail=1
  fi
fi

echo
if [ "$fail" = "0" ]; then echo "✅ check-all VERDE — pode abrir PR."; else echo "❌ check-all VERMELHO — NÃO abra PR."; fi
exit "$fail"
