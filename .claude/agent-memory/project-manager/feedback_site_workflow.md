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
