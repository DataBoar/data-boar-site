---
name: reference-infra-gotchas
description: Armadilhas de infra do índice de wheels e do site (Cloudflare 403, nomes de asset, resolução do pip, issue de registro)
metadata:
  type: reference
---

- **https://databoar.com.br está atrás do Cloudflare:** `urllib` com o User-Agent padrão leva 403 em todas as páginas. Para verificar o ar, usar `curl -A pip/25.1.1` (e comparar com `cmp`), não um script `urllib`.
- **GitHub troca `~` por `.` no nome do asset** (`haiku_r1~beta6` vira `haiku_r1.beta6`). O `SHA256SUMS` guarda o nome original.
- **Nomes de wheel puro-Python repetem entre Releases** (`odfpy`, `red_black_tree_mod`) com hashes diferentes: o gerador `scripts/build-wheelhouse-index.py` mantém um link por nome (a primeira tag passada ganha).
- **Pages publica em ~1 min depois do merge** (`last-modified` do índice 19:32:10Z, merge 19:31:39Z).
- **Issue de registro de eventos:** #103 `[registro] Eventos do projeto` (eventos `custo` e `coordenacao`). Issues de tarefa: #104. A rodada de custo começa no último evento `custo` da #103 (hoje: 2026-11-13T18:08 UTC, que cobriu a rodada 1).
- Medir custo: `python3 ~/.claude/skills/auditar-projeto/scripts/custos.py --desde <UTC> --evento` na pasta do projeto.
- Testar resolução de wheels de outro SO a partir do Linux: `pip download --only-binary=:all: --platform <tag> --python-version <v> --abi <abi> --index-url https://databoar.com.br/simple/ <pacote>`.
