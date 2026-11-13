# Plano de gestão — data-boar-site

Site público https://databoar.com.br (GitHub Pages): site comercial, `images/` (logo, favicons, mascote) e o índice de wheels em `simple/` (PEP 503, wheelhouse para musl, CPUs sem AVX e, de laboratório, Haiku, FreeBSD, NetBSD e OpenBSD). Operação e regras em [operacao.md](operacao.md); PLANs técnicos em [plans/PLANS_TODO.md](plans/PLANS_TODO.md).

## Entregáveis

| ID | Entregável | Issue / PR | Status |
| --- | --- | --- | --- |
| 1 | Alinhar o site ao data-boar 1.8.0 GA (flag do Windows, claims, novidades) | [#96](https://github.com/DataBoar/data-boar-site/issues/96), PRs #99 e #100 | Concluído (plano em `plans/completed/`) |
| 2 | Refresh do wheelhouse x86-64-v1 para os pins do 1.8.0 (numpy 2.5.4 e demais) | [data-boar#2218](https://github.com/DataBoar/data-boar/issues/2218), PR própria (a abrir quando as células existirem) | Em andamento (wheels perdidos no reboot de 11/nov; recompilação); ver [ops/WHEELHOUSE_REFRESH_2026-11.md](ops/WHEELHOUSE_REFRESH_2026-11.md) |
| 3 | Regra de leitura completa de thread no `AGENTS.md` | [#95](https://github.com/DataBoar/data-boar-site/issues/95) | Aberto |
| 4 | Wheelhouses de laboratório Haiku, FreeBSD, NetBSD e OpenBSD no `simple/`, com instalação por SO | [#104](https://github.com/DataBoar/data-boar-site/issues/104), PR #101 (mesclada em 13/nov) | Concluído, exceto a 4.7 (illumos); inventário em [WHEELHOUSE_BSD_HAIKU.md](WHEELHOUSE_BSD_HAIKU.md) |

## Tarefas do entregável 2

| ID | Tarefa | Dono | Status |
| --- | --- | --- | --- |
| 2.1 | Fechar o plano da #96 e apontar o wheelhouse no `opensource.html` | PM | Feito (PR #101, junto com o entregável 4) |
| 2.2 | Compilar numpy, scipy e scikit-learn nas 6 células (glibc e musl × 3.12, 3.13, 3.14) pela receita documentada do produto | PM (build local) | Em andamento |
| 2.3 | Montar o staging completo da nova Release (wheels novos, itens inalterados da Release antiga, `SHA256SUMS`, `README`) | PM | Aguarda 2.2 |
| 2.4 | Publicar o upload da nova Release | Operador | Aguarda 2.3 |
| 2.5 | Regenerar `simple/` com `scripts/build-wheelhouse-index.py --tags …` e atualizar `docs/WHEELHOUSE_X86_64_V1.md` | PM | Só depois de 2.4; nunca antes |
| 2.6 | Apontar o `WHEELHOUSE_TAG` padrão do produto para a nova tag | Executor (repositório do produto) | Aguarda 2.4 |

## Tarefas do entregável 4

| ID | Tarefa | Dono | Status |
| --- | --- | --- | --- |
| 4.1 | Release `wheelhouse-haiku-2026-11-04` (a tag antiga `wheelhouse-haiko-…` tinha typo), mesmos 24 assets e digests | PM | Feito (13/nov) |
| 4.2 | Regenerar `simple/` com as 5 tags (x86-64-v1, Haiku, FreeBSD, NetBSD, OpenBSD), sem perder links; 120 links com 200 e `#sha256=` conferido | PM | Feito |
| 4.3 | Gerador sem nome de wheel duplicado na mesma página (`odfpy`, `red_black_tree_mod`), com teste | PM | Feito |
| 4.4 | Instalação por SO em `opensource.html` (pt e en) e inventário `WHEELHOUSE_BSD_HAIKU.md`, comando testado contra o índice | PM | Feito |
| 4.5 | Remover a Release `wheelhouse-haiko-2026-11-04` | PM | Feito (13/nov): `simple/` no ar com 120 links 200, Haiku 23/23 com hash conferido; Release e tag removidas |
| 4.6 | Haiku: o índice não resolve (o GitHub troca `~` por `.` no nome do asset). Hospedar os wheels em outro lugar (~71 MB no repo) ou manter o passo manual | Operador | Decidido (13/nov): passo manual documentado, sem hospedar wheels no Pages |
| 4.7 | illumos: nenhum wheel foi guardado | PM | Pendente (refazer a célula) |

## Fora do escopo

- Citar satélites privados, parceiros, clientes, preços ou planos comerciais.
- Qualquer número de desempenho 1.7.4 contra 1.8.0 (não medido). O único número citável é o do filtro Rust isolado (4,69×).
