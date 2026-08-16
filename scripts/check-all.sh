#!/usr/bin/env bash
# check-all — FULL local gate for data-boar-site (run before opening a PR / before merge).
# Mirrors the data-boar `check-all` discipline: green locally BEFORE push (ADR-0080 spirit).
# NOT a toy project — this gate is inviolable (docs/adr/ADR-0001). Add checks, never remove.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
fail=0

run() { echo; echo "── $1 ──"; shift; if "$@"; then echo "  ✅ ok"; else echo "  ❌ FALHOU"; fail=1; fi; }

# 0) Site chrome (nav + footer) must match partials/site-chrome — no silent drift
run "site-chrome sync --check" python3 scripts/sync-site-chrome.py --check

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

echo
if [ "$fail" = "0" ]; then echo "✅ check-all VERDE — pode abrir PR."; else echo "❌ check-all VERMELHO — NÃO abra PR."; fi
exit "$fail"
