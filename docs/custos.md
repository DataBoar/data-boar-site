# Custos do projeto

Estimativas pelos preços da API, medidas por `~/.claude/skills/auditar-projeto/scripts/custos.py` a partir das sessões do Claude Code deste projeto. Num plano por assinatura, leia os valores como proporção do limite de uso. Cada rodada também tem um evento `custo` na issue [`[registro] Eventos do projeto`](https://github.com/DataBoar/data-boar-site/issues/103).

## Resumo

| Rodada | Início (UTC) | Total (US$) | Mesclado na rodada |
| --- | --- | --- | --- |
| 1 | 2026-11-13T18:08 | 4,54 | #104 (PR #101, mesclada pelo operador) |
| **Acumulado** | | **4,54** | |

## Rodada 1, desde 2026-11-13T18:08

- **Total:** US$ 4,54 (evento publicado em [#103](https://github.com/DataBoar/data-boar-site/issues/103#issuecomment-6862963148)).
- **Por agente:** project-manager 4,52 · sessão sem agente 0,02.
- **Por tarefa:** coordenação 4,52 · sem tarefa identificada 0,02.
- **Entregas:** #104 inteira (PR #101): `simple/` com Haiku, FreeBSD, NetBSD e OpenBSD (46 projetos, 120 links); instalação por SO em `opensource.html` (pt/en); inventário `WHEELHOUSE_BSD_HAIKU.md`; gerador sem nome de wheel duplicado; Release `wheelhouse-haiku-2026-11-04` criada e a antiga (`haiko`) removida depois de o índice no ar ser conferido.
- **Chamou a atenção:**
  - Rodada só do project-manager, sem outros agentes; os US$ 0,02 de "sessão sem agente" são de outra sessão no mesmo intervalo.
  - A #104 não tem ID `[x.y]` no título (veio como pedido do operador), por isso o custo sai em "coordenação"; no plano é a 4.x.
  - O `check-all` rodou duas vezes (SHA `1a740aa` e `91daedd`) porque o `main` ganhou o #102 com o mesmo `docs/operacao.md` (conflito add/add), o que exigiu um merge assinado e novo CI.
