#!/usr/bin/env bash
# install-hooks — wire the local guardrail gates for data-boar-site (idempotent).
# Points core.hooksPath at scripts/ so scripts/pre-commit runs before EVERY commit.
# Run once per clone:  ./scripts/install-hooks.sh
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
chmod +x scripts/pre-commit scripts/check-all.sh 2>/dev/null || true
git config core.hooksPath scripts
echo "✅ gates locais ativos:"
echo "   • pre-commit  -> scripts/pre-commit  (roda a cada commit: lint + code-quality + anti-regression rápido)"
echo "   • full gate   -> scripts/check-all.sh (rode ANTES de abrir PR: suíte completa)"
echo "   core.hooksPath = scripts"
