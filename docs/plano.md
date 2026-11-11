# Plano de gestão — data-boar-site

Site público https://databoar.com.br (GitHub Pages): site comercial, `images/` (logo, favicons, mascote) e o índice de wheels em `simple/` (PEP 503, wheelhouse para musl, CPUs sem AVX e Haiku). Operação e regras em [operacao.md](operacao.md); PLANs técnicos em [plans/PLANS_TODO.md](plans/PLANS_TODO.md).

## Entregáveis

| ID | Entregável | Issue / PR | Status |
| --- | --- | --- | --- |
| 1 | Alinhar o site ao data-boar 1.8.0 GA (flag do Windows, claims, novidades) | [#96](https://github.com/DataBoar/data-boar-site/issues/96), PRs #99 e #100 | Concluído (plano em `plans/completed/`) |
| 2 | Refresh do wheelhouse x86-64-v1 para os pins do 1.8.0 (numpy 2.5.4 e demais) | [data-boar#2218](https://github.com/DataBoar/data-boar/issues/2218), PR #101 (rascunho) | Em andamento; ver [ops/WHEELHOUSE_REFRESH_2026-11.md](ops/WHEELHOUSE_REFRESH_2026-11.md) |
| 3 | Regra de leitura completa de thread no `AGENTS.md` | [#95](https://github.com/DataBoar/data-boar-site/issues/95) | Aberto |

## Tarefas do entregável 2

| ID | Tarefa | Dono | Status |
| --- | --- | --- | --- |
| 2.1 | Fechar o plano da #96 e apontar o wheelhouse no `opensource.html` | PM | Na PR #101 |
| 2.2 | Compilar numpy, scipy e scikit-learn nas 6 células (glibc e musl × 3.12, 3.13, 3.14) pela receita documentada do produto | PM (build local) | Em andamento |
| 2.3 | Montar o staging completo da nova Release (wheels novos, itens inalterados da Release antiga, `SHA256SUMS`, `README`) | PM | Aguarda 2.2 |
| 2.4 | Publicar o upload da nova Release | Operador | Aguarda 2.3 |
| 2.5 | Regenerar `simple/` com `scripts/build-wheelhouse-index.py --tags …` e atualizar `docs/WHEELHOUSE_X86_64_V1.md` | PM | Só depois de 2.4; nunca antes |
| 2.6 | Apontar o `WHEELHOUSE_TAG` padrão do produto para a nova tag | Executor (repositório do produto) | Aguarda 2.4 |

## Fora do escopo

- Citar satélites privados, parceiros, clientes, preços ou planos comerciais.
- Qualquer número de desempenho 1.7.4 contra 1.8.0 (não medido). O único número citável é o do filtro Rust isolado (4,69×).
