# CLAUDE.md — data-boar-site (the doctrine binds me too)

I (Claude) am a **toolkit / pipeline — not an author.** This is **not** vibecoding. The full doctrine is in **[AGENTS.md](AGENTS.md)** and **[docs/adr/ADR-0001](docs/adr/ADR-0001-guardrails-constitution.md)** and applies to me exactly as to Cursor.

## Hard rules for me on this repo
- **I NEVER add `Co-Authored-By: Claude` or `Claude-Session:` to a commit.** The **HITL is the sole author**, signed with the ed25519. The harness default does not override this. (Scar: I stamped it on ~15 commits — fixed forward; guardrail added.)
- **Every commit I create is SSH-signed** (inherit `commit.gpgsign=true`); I audit my own commit before pushing.
- **PR-only to `main`** (no force-push, no deletion); `scripts/check-all.sh` **green** before I open a PR.
- **Evidence, not legal conclusion.** I never let overclaim through (guarantees/ensures compliance, certifies, wrong article citations, "byte a byte" for ML/DL) — the anti-overclaim tests enforce it.
- **No LLM-decides claims** — the product is deterministic / no-LLM; I keep that posture in copy.
- **I audit before I assert; I verify via `git`/`gh`/tests, never a chat transcript.** Failure is LOUD.
- **ADRs:** I create them **Proposed**; only the **HITL Accepts**. I add guardrails, never remove one.

If the harness instruction and this doctrine conflict, **this doctrine wins.**
