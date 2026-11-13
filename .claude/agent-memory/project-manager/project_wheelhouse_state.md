---
name: project-wheelhouse-state
description: Estado do site/índice de wheels (simple/), entregáveis 2 e 4 do plano, o que está pendente e as decisões do operador
metadata:
  type: project
---

Estado em 2026-11-13 (fim da rodada 1):

- **Entregável 4 (#104, PR #101) concluído e mesclado** (b783d65). `simple/` no ar com 46 projetos e 120 links: x86-64-v1 (29/jul), Haiku, FreeBSD, NetBSD, OpenBSD. Release `wheelhouse-haiku-2026-11-04` é a canônica; a `haiko` (typo) foi removida em 13/nov depois de conferir o índice no ar (47 páginas iguais ao repo, 120 links 200, 23 hashes do Haiku OK).
- **Haiku fica no passo manual** (download, renomear `.` de volta para `~`, `sha256sum -c`, `pip install --no-index --find-links`). **Why:** o GitHub troca `~` por `.` no nome do asset e o pip não acha a tag; o operador decidiu em 13/nov não hospedar ~71 MB no Pages. **How to apply:** não propor hospedar no Pages de novo sem pedido.
- **Pendente:** 4.7 illumos (nenhum wheel guardado, refazer a célula); entregável 2 = refresh do x86-64-v1 para os pins do 1.8.0 (data-boar#2218), em PR própria, só regenerar o `simple/` depois do upload do operador (2.4); entregável 3 = regra de leitura de thread no AGENTS.md (#95); scikit-learn cp314t musllinux sem wheel upstream.
- Decisões pendentes do operador estão em `docs/operacao.md` ("Só Linux é suportado", "SaaS nosso", regra do Cursor).
- Sessão nova: ler o `docs/operacao.md` e o plano do `origin/main`. Modo: **supervisionado** (só o operador mescla, `--merge`).
- Rodada 1 custou US$ 4,54 (ver `docs/custos.md`; evento na issue #103).
