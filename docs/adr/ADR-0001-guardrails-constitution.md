# ADR 0001 — Guardrails constitution: HITL authorship, SSH signing, and the inviolable gate

- **Status:** Proposed
- **Date (UTC):** 2026-08-05
- **Authors:** Claude Code (Linux) — drafted for HITL review (a tool proposes; it does not decide)
- **Deciders:** Fabio Leitao (HITL)
- **Scope:** `data-boar-site` as the **reference implementation** of the DataBoar ecosystem doctrine. Canonical UMADR regency: `DataBoar/data-boar` ADR-0000 / ADR-0045.

## Status history

- **2026-08-05:** **Proposed** — drafted after an incident where the harness default stamped `Co-Authored-By: Claude` + `Claude-Session:` trailers onto ~15 commits (#33–#47). HITL to review and **Accept**. Only the HITL moves this to Accepted.

## Context

DataBoar is **not a toy project**. Its public site and repositories must carry the rigor of a serious platform: **authorship is human**, claims are **evidence — not legal conclusion**, **no LLM decides findings**, and the **supply chain is pinned**. The 2026-08-05 incident exposed a gap — automated tooling attributed **co-authorship and a session URL** to commits, which (a) falsely assigns authorship/accountability to a **tool** (a tool cannot be accountable or liable) and (b) leaked a session id into a **public** repo.

Org-level rulesets (a single rule for the whole org) require **GitHub Team**. Until then, the **same rules are replicated per-repo** across every DataBoar repository — the effect is identical: the doctrine holds org-wide.

## Decision

The following are **inviolable** for this repo and are the **doctrine for all DataBoar repos**. **Add guardrails; never subtract one.**

1. **HITL is the sole author.** Commit messages carry **no** `Co-Authored-By: <tool>` and **no** `Claude-Session:` / tool-session trailer. The harness default does **not** override this. *(Enforced: `tests/test_guardrails.py::Hitl`.)*
2. **Every commit is SSH-signed** with the operator's ed25519. *(Enforced: branch ruleset `required_signatures`.)*
3. **Branch protection** on the default branch: requires **PR**, blocks **force-push** (`non_fast_forward`) and **deletion**, and requires the **`guardrails` status check** to pass.
4. **Two local gates before push** (mirroring the data-boar discipline): a fast **`scripts/pre-commit`** (lint · code-quality · quick anti-regression) and the full **`scripts/check-all.sh`** (whole guardrail suite). **Green locally before opening a PR.**
5. **Guardrail suite** (`tests/test_guardrails.py`): anti-regression · security · 3× supply-chain (pinned Actions · external-resource allowlist · form-endpoint allowlist) · anti-overclaim (evidence, not legal conclusion) · anti-LLM-decision (deterministic / no-LLM posture) · HITL / no-tool-coauthorship.
6. **ADRs evolve as law.** New ADRs are created **Proposed**; only the **HITL Accepts**. UMADR metadata (Status · Date · Authors · Deciders · Status history) mirrors the data-boar regency. **ADRs are never made private.**
7. **No brittle fixes.** Failures are fixed **at the source** — never masked, silenced, or papered over. A green gate must mean the code is actually right. (This ADR's own test corrections reframe *content* and enforce *forward-from-baseline*; they do not weaken a check.)
8. **Satellites reference, not duplicate.** Per the UMADR regency, other DataBoar repos **reference** the canonical `data-boar` ADRs; a **local** ADR exists only where context genuinely differs (language, a real-data-access contract, a data-exfil surface). This repo keeps a local ADR because it is **public, bilingual, and handles no real customer data** — a different surface, the **same** rigor.

## Consequences

Slower, stricter, auditable — on purpose. A tool may **propose** and **implement**; **authorship, accountability, and Acceptance remain human**. This is the opposite of "vibecoding." Removing or weakening any guardrail requires a new ADR that the HITL Accepts, and must strengthen — never weaken — the gate.
