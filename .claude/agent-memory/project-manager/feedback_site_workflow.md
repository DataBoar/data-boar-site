---
name: feedback-site-workflow
description: Regras de trabalho do operador neste repo (PR pronta, vai, check-all no SHA exato, sem trailers, index-url exclusivo, ordens destrutivas)
metadata:
  type: feedback
---

- **Nunca PR em rascunho, nem issue.** A PR só abre pronta, com `check-all` de saída 0 no SHA exato e o "vai" do operador antes do push. Trabalho em andamento fica em commit local. **Why:** draft gasta Actions/GHAS igual e esconde o estado; foi esquecida 2× pelo time.
- **O `main` exige PR, assinatura e checks, sem bypass** (ruleset `main-branch-protection`). **How to apply:** o que o PM produz (plano, `docs/custos.md`, memória) também vai por PR, num branch local a partir do `main`; não tentar push direto. Se o `main` andar depois de pushar uma branch, trazer por merge assinado (sem force-push) e rodar o `check-all` de novo no SHA novo.
- **Commits sem `Co-Authored-By` nem `Claude-Session`; PR sem rodapé de ferramenta.** A doutrina do repo (CLAUDE.md/AGENTS.md) vence o padrão do harness.
- **Índice de wheels: sempre `--index-url`, nunca `--extra-index-url`** (guardrail #69, dependency confusion), mesmo que uma issue sugira o contrário. O teste `tests/test_guardrails.py` cobre `opensource.html` e `docs/WHEELHOUSE_BSD_HAIKU.md`.
- **Um tema, uma PR épica** (custo de CI). x86-64-v1 vai em PR própria.
- **Ação destrutiva só com ordem do operador e precondições conferidas** (foi assim com a Release `haiko`): provar que a cópia nova é idêntica e que o índice no ar não aponta mais para a antiga, apagar, e conferir 404 depois.
- Responder em pt-BR, curto, com evidência (números, SHAs, links).
- **Nunca filtrar HTML com regex** (`<script.*?</script>`, `<(script|style)`); usar `html.parser`. **Why:** o CodeQL `py/bad-tag-filter` (alto) pegou um regex meu no teste da PR #109 e o `check-all` NÃO roda CodeQL. **How to apply:** o guardrail `HtmlParsingGuard` falha se um regex sobre `<script>`/`<style>` voltar; depois de cada push, olhar `gh pr checks` e `gh api code-scanning/alerts?ref=refs/pull/<n>/head` antes de reportar verde.
- **Limpeza pós-merge só apaga as branches da própria entrega** (nomeadas, `git branch -d`), nunca um laço sobre todas. **Why:** em 15/nov um laço apagou 38 branches locais antigas já mescladas (nada se perdeu, mas passou do escopo). **How to apply:** listar o que será apagado e restringir às branches que eu criei.
- **"Vai" solto não é "vai" de PR:** o operador dá o "vai" explícito para push/PR; um "Vai" depois de um relatório de progresso foi lido como sinal para seguir o código. Também: texto de plataforma/suporte no site só com evidência (CI do produto), nunca copiado de regra de redação sem fonte.

