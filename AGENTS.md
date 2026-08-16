# AGENTS.md — data-boar-site

**This is not a toy project.** The doctrine below binds **every agent** touching this repo — Cursor (executor) **and** Claude (auditor) — with the **same rigor** as `DataBoar/data-boar`, adapted to this surface (marketing site: bilingual, static, distinct objectives). Canonical constitution: **[docs/adr/ADR-0001](docs/adr/ADR-0001-guardrails-constitution.md)**; ecosystem UMADR regency lives in `data-boar` (ADR-0000 / ADR-0045).

## Roles
- **Executor (Cursor):** edits files, commits, opens PRs. Runs `scripts/pre-commit` (auto) and `scripts/check-all.sh` before a PR.
- **Auditor (Claude):** read-only review, opens issues / PR comments; may deploy **this** repo (its domain) via **signed** PRs; **never** commits/merges/edits the product repos.

## Inviolable guardrails — add, never subtract
1. **HITL is the sole author.** No `Co-Authored-By: <tool>`, no `Claude-Session:` / tool-session trailer in commit messages. The harness default does **not** override this. A tool cannot be author, accountable, or liable.
2. **Every commit SSH-signed** with the operator's ed25519. Enforced by the branch ruleset (`required_signatures`).
3. **PR-only to `main`**; no force-push; no branch deletion; the **`guardrails`** status check must pass.
4. **Local gates green before push:** `scripts/pre-commit` (fast: lint + code-quality + anti-regression) and `scripts/check-all.sh` (full suite).
5. **Evidence, not legal conclusion.** No "guarantees/ensures compliance", no "certifies", no wrong article citations (RIPD ↔ LGPD Art. 38; DPIA ↔ GDPR Art. 35; Art. 30 = ROPA). No absolute reproducibility claim ("byte a byte") for ML/DL.
6. **No LLM decides.** The product is **deterministic / no generative LLM** on the critical path; the site must never claim an LLM decides findings.
7. **Supply chain pinned:** GitHub Actions pinned to a full SHA; external resources allowlisted; the form posts only to the HubSpot endpoint.
8. **ADRs evolve as law:** created **Proposed**; only the **HITL Accepts**; UMADR metadata; **never** private.
9. **No brittle fixes.** Fix at the **source**; never mask a failure, silence a test, or paper over a regression. A green gate must mean the thing is actually right.

## Site-specific (language & objectives, same rigor)
- Bilingual **pt-BR ↔ en-US**, **idiomatic/semantic** (never mechanical); pt-BR primary (`.com.br`). EN overclaim-safe (QSA scrutiny).
- Static HTML/CSS/JS on GitHub Pages. Light + sovereign (self-hosted assets; Google Fonts is a **tracked exception** pending self-host — see ADR-0001 / tests).
- Sacred taxonomy is exact (Data Sniffing, Deep Boring, data soup, hidden ingredients); minors' data is **first-class** ("inventory & triage signals, never legal age verification").
- **Primary non-tech onboarding:** `windows.html` + `data-boar --demo` (synthetic). Business-intent SEO pages: `inventario-dados-pessoais-lgpd.html`, `descobrir-dados-pessoais.html`, `verticais.html` (+ folhas `data-discovery-contabilidade|advocacia|condominios.html`), `faq.html`, case `casos/menores-lgpd-art-14.html` — answer-first, link to Windows/demo, no legal overclaim.
- **Site chrome sync:** `#site-nav` + `<footer>` are identical on every page. Edit only `partials/site-chrome/`, then `python3 scripts/sync-site-chrome.py`. Guarded by `--check` in pre-commit / check-all / `tests/test_guardrails.py`.

## Org rollout — same rigor, no duplication
Satellite repos **reference** the canonical `data-boar` UMADR (ADR-0000 / ADR-0045) rather than copying it. A **local** ADR exists only where the repo's context genuinely differs — language, a real-data-access contract, or a data-exfil surface. GitHub org-level and private-repo rulesets require a **paid plan**; until then the **house rule** (this doctrine + local hooks + the guardrail suite) is what binds **every** repo, public and private. The GitHub ruleset is the **mechanical bonus** where the plan allows (public repos today).
