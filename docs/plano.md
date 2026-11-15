# Plano de gestão — data-boar-site

Site público https://databoar.com.br (GitHub Pages): site comercial, `images/` (logo, favicons, mascote) e o índice de wheels em `simple/` (PEP 503, wheelhouse para musl, CPUs sem AVX e, de laboratório, Haiku, FreeBSD, NetBSD e OpenBSD). Operação e regras em [operacao.md](operacao.md); PLANs técnicos em [plans/PLANS_TODO.md](plans/PLANS_TODO.md).

## Entregáveis

| ID | Entregável | Issue / PR | Status |
| --- | --- | --- | --- |
| 1 | Alinhar o site ao data-boar 1.8.0 GA (flag do Windows, claims, novidades) | [#96](https://github.com/DataBoar/data-boar-site/issues/96), PRs #99 e #100 | Concluído (plano em `plans/completed/`) |
| 2 | Refresh do wheelhouse x86-64-v1 para os pins do 1.8.0 (numpy 2.5.4 e demais) | [data-boar#2218](https://github.com/DataBoar/data-boar/issues/2218), PR própria (a abrir quando as células existirem) | Em andamento (wheels perdidos no reboot de 11/nov; recompilação); ver [ops/WHEELHOUSE_REFRESH_2026-11.md](ops/WHEELHOUSE_REFRESH_2026-11.md) |
| 3 | Regra de leitura completa de thread no `AGENTS.md` | [#95](https://github.com/DataBoar/data-boar-site/issues/95) | Aberto |
| 4 | Wheelhouses de laboratório Haiku, FreeBSD, NetBSD e OpenBSD no `simple/`, com instalação por SO | [#104](https://github.com/DataBoar/data-boar-site/issues/104), PR #101 (mesclada em 13/nov) | Concluído, exceto a 4.7 (illumos); inventário em [WHEELHOUSE_BSD_HAIKU.md](WHEELHOUSE_BSD_HAIKU.md) |
| 5 | Bestiais no site (Sage Remora, Faithful Ferret, Stealthy Stoat, Keen Platypus): o que faz hoje × o que vem, pt/en, só o que a doc dos repos prova | [#106](https://github.com/DataBoar/data-boar-site/issues/106), PR única | Concluído (PR #107 mesclada em 14/nov); falta só a 5.5 |
| 6 | Site bilíngue de verdade: corpo EN nas 3 páginas, `/en/` gerado, hreflang e AI-SEO básico | [#108](https://github.com/DataBoar/data-boar-site/issues/108), PR épica única (junto com o fechamento da rodada 2) | Pronto no branch local (`check-all` 0); falta a leitura do EN da `menores` e o "vai"; merge só depois da demo de quarta 18/nov |

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

- Citar satélites privados, parceiros, clientes, preços ou planos comerciais. Exceção por ordem do operador (14/nov/2026): os quatro bestiais do entregável 5, sem link para os repos privados e sem detalhe interno.
- `llms.txt` (adiado por ordem do operador, 14/nov; entra depois do entregável 6).
- Qualquer número de desempenho 1.7.4 contra 1.8.0 (não medido). O único número citável é o do filtro Rust isolado (4,69×).

## Tarefas do entregável 5

| ID | Tarefa | Dono | Status |
| --- | --- | --- | --- |
| 5.1 | Conferir cada afirmação no `origin/main` dos 4 repos (nada de memória); o que não tem prova vai para a lista "sem prova" | PM | Feito (14/nov) |
| 5.2 | Seção "Os bestiais" em `opensource.html` (pt/en) e ponteiro em `index.html` e `solucao.html` | PM | Feito (PR #107) |
| 5.3 | Guardrail `BestiaryCopy`: sem link para repo privado, sem termo interno ou jurídico, com rótulo de simulado/sintético | PM | Feito (PR #107) |
| 5.4 | `check-all` 0 no SHA exato, diff ao operador, "vai" e PR única | PM / Operador | Feito (14/nov): `check-all` 0 no SHA `b5ba22a`, PR #107 mesclada, seção conferida no ar |
| 5.5 | Decidir os itens da lista "sem prova" (o que entra depois da conferência do dono de cada repo) | Operador | Pendente |

## Tarefas do entregável 6

Ordem do operador (14/nov): a 6.1 e a 6.2 vêm antes da 6.3 em diante. Uma PR épica, merge só depois da demo de quarta 18/nov. `llms.txt` fica para depois.

| ID | Tarefa | Dono | Status |
| --- | --- | --- | --- |
| 6.1 | Corpo EN de `descobrir-dados-pessoais`, `inventario-dados-pessoais-lgpd` e `casos/menores-lgpd-art-14` (fiel ao PT, sem afirmação nova) e 2 links de rodapé em EN, pelo partial `footer.html` | PM | Feito (local); **o operador lê o EN da `menores-lgpd-art-14` antes do merge** |
| 6.2 | Guardrail `BilingualParity` (texto de conteúdo dentro de painel, painel PT com irmão EN não vazio, razão EN/PT entre 0,6 e 1,5) | PM | Feito (local) |
| 6.3 | `scripts/build-en.py`: gera `/en/` dos painéis EN (`html lang="en"`, canonical próprio, links internos e assets reescritos), commitado, com guardrail de drift | PM | Feito (local): `--check` no `check-all`; parser com teste de reescrita sem perdas |
| 6.4 | Metadados por idioma: title, description, `og:*`, `og:locale` e JSON-LD (com `inLanguage`) em PT e EN | PM | Feito (local): `partials/i18n/head.en.json` (15 páginas, 8 blocos JSON-LD); o item em inglês que estava no JSON-LD PT da `faq.html` saiu (o EN tem o seu) |
| 6.5 | hreflang `pt-BR`/`en`/`x-default` em cada par e sitemap com `xhtml:link`, com guardrail de consistência; `login.html` e `agende-demonstracao.html` ficam de fora | PM | Feito (local): canonical próprio nas 15 páginas (5 não tinham); sitemap com 30 URLs de par + `agende` |
| 6.6 | Seletor de idioma navega para a URL do par; sai a detecção automática por navegador; sem redirect | PM | Feito (local): conferido em navegador (PT→EN→PT, e `agende` abre no idioma lembrado); guardrail proíbe `navigator.language` e redirect |
| 6.7 | AI-SEO de baixo esforço: `<main>`/`<article>`, `dateModified` e "Atualizado em" com a data real do `git log` | PM | Feito (local): `<main>` nas 17 páginas, `<article>` nas 6 de artigo; datas do `git log` ignorando as linhas gerenciadas |
| 6.8 | Fechamento da rodada 2 na mesma PR (custos, plano, memória; commit `fadf823`) | PM | Feito (local) |
| 6.9 | Leitura do EN da `menores-lgpd-art-14` e "vai" do operador; merge depois de 18/nov | Operador | Pendente |
