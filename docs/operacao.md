# Operação — data-boar-site

Modo: supervisionado
Duelo: não
Dev externo: não
Pausa: não

## Regras vigentes

- **Só o operador mescla** (`gh pr merge <n> --merge`, nunca squash). Agentes abrem a PR e entregam o veredito.
- **Mostrar o escopo antes de abrir a PR**; uma PR epic por tema, com `Closes #N` só quando a PR realmente fecha a issue.
- **Commits assinados (SSH)**, sem `Co-Authored-By` nem trailer de sessão de ferramenta; PR-only para o `main`; `scripts/check-all.sh` verde antes de abrir PR (doutrina em `AGENTS.md` e `docs/adr/ADR-0001`).
- **Honestidade comercial**: evidência, não conclusão jurídica; nenhuma capacidade ou plataforma afirmada sem evidência pública; o site é público (sem nomes de satélites privados, parceiros, clientes, preços ou planos comerciais).
- **Custo de CI**: cada PR reroda o pipeline inteiro; agrupar o trabalho de um tema numa PR só.
- **Implantação**: o site publica pelo GitHub Pages ao mesclar no `main`; a publicação de Releases de wheels (upload de assets) é ato do operador.

## Decisões pendentes do operador

| Assunto | Situação |
| --- | --- |
| "Só Linux é suportado" em `solucao.html` e `faq.html` (visível e JSON-LD) | Fala de nível de suporte, não de onde roda. Manter ou trocar por "suporte oficial: Linux; validado em laboratório (VM): …" |
| "SaaS nosso" em `opensource.html` | Está no roadmap, em construção. Manter ou escrever "em construção" |
| Regra do Cursor `execution-priority-and-pr-batching.mdc` | Commit assinado local, nunca publicado. Publicar por PR ou descartar |

Ver o plano de gestão em [plano.md](plano.md).
