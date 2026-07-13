# Governanca de Branch & Assinatura — org DataBoar

## Principio
Todo commit que entra em `main` e **assinado (SSHSIG)** e chega via **PR**.
Bypass **nao existe** — por design, nao por confianca.

## Enforcement
- **Repos publicos** (`data-boar`, `data-boar-site`): ruleset `main-branch-protection` (active) impoe pelo GitHub.
- **Repos privados** (bestiais): free tier **nao permite** ruleset (403) -> mesmo rigor por **disciplina**
  (assinar + PR por convencao). O rigor nao baixa; so nao e imposto pela plataforma.

## Regras do ruleset (main)
| regra | efeito |
|---|---|
| `required_signatures` | todo commit assinado |
| `pull_request` (reviews=0) | via PR, sem travar em reviewer (2 pessoas + agentes) |
| `non_fast_forward` | sem force-push |
| `deletion` | nao deletar main |
| **`bypass_actors: []`** | **ninguem bypassa — nem admin, nem agente. Assinatura inviolavel.** |

## Por que sem bypass
Bypass isentaria o actor de TODAS as regras (incl. a assinatura). Sem bypass nao ha capability a abusar —
nem por humano, nem por LLM/agente. Emergencia passa pelo processo normal (PR + assinar); num site nao e gargalo.
Se um dia precisar de valvula: **2 rulesets** (assinatura sem bypass + fluxo com bypass admin) — nunca um bypass
unico que cubra a assinatura.

## Identidade do agente (Cursor/Claude)
- Agentes usam **PAT fine-grained SEM `administration`** e **fora de qualquer bypass**
  -> **tecnicamente incapazes** de mexer em protecao ou burlar assinatura, mesmo nos privados sem ruleset.
- Claude Code = READ-ONLY no codigo (so `gh issue create/comment`). Cursor = executor sob os mesmos gates.

## Config obrigatoria (todo contribuidor)
`git config --global gpg.format ssh` - `user.signingkey <chave>` - `commit.gpgsign true` +
registrar a chave como **Signing Key** no GitHub. Commit nao-assinado no push = **config errada do autor**, nao do gate.

## Historico
Commits pre-doutrina (jun->jul-02) podem estar nao-assinados — **nao re-assinamos** (rebase reescreve SHAs).
Daqui pra frente, todo commit assina.
