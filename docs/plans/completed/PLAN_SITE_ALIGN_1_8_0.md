# Site — align public copy with data-boar 1.8.0 GA

**Status:** Done (shipped on `main` via #99 and #100, 2026-11-11)
**Date:** 2026-11-10
**Authors:** Fabio Leitao (HITL); drafted with Claude (toolkit)
**Priority:** P2
**Issue:** [DataBoar/data-boar-site#96](https://github.com/DataBoar/data-boar-site/issues/96)

## Goal

Make every product claim and instruction on the public site match what `DataBoar/data-boar` **1.8.0** publicly documents. The site cites no product version, so there is no version bump: the work is correcting stale **claims and instructions**, and adding a few verifiable 1.8.0 facts. **Evidence, not legal conclusion; no platform claim without public evidence.**

## Evidence checked (2026-11-10, via `gh api` on `DataBoar/data-boar@main`, not the local clone)

- `docs/QUICKSTART_WINDOWS.md` line 108 and `main.py` use `--allow-insecure-http`. The site's `windows.html` uses `--allow-insecure` (4 occurrences: 102, 103, 156, 157).
- Public tree has **0 `.clj` files**; the open-core ships no sidecar implementation.
- `main.py` (line ~526) exposes an **L1 `metadata_manifest` output meant for sidecars** (`--l1-output`; no raw values) — a code-backed integration point.
- [ADR-0086](https://github.com/DataBoar/data-boar/blob/main/docs/adr/ADR-0086-plugin-sdk-language-neutral-contract.md): "Open-core does not ship L2/L3 partner drivers"; `docs/PLUGIN_SDK.md` calls L2/L3 "future evolution, not APIs you can load today".
- `docs/plans/PLAN_CLOJURE_AUGMENTATION.md` was amended 2026-10-12: the Clojure runtime lives outside the host (not an in-tree sidecar).

## Scope — one epic PR (`Closes #96`)

### P1 — correct (claim/instruction diverges from product)

| # | File(s) | Change |
| - | ------- | ------ |
| 1 | `windows.html` (pt + en) | `--allow-insecure` → `--allow-insecure-http` (4 places) |
| 2 | `index.html`, `solucao.html`, `opensource.html` (pt + en) | Sidecar mention: the HITL ordered the original Clojure wording kept (restored via #100); `opensource.html` also carries the generic, code-backed sentence about the metadata manifest for external sidecar modules |
| 3 | `praticas-de-engenharia.html` | the site stops citing the signed manifest and cites the build digest and the SBOMs instead |

### P3 — platform / evidence hygiene (no new platform claim)

| # | File(s) | Change |
| - | ------- | ------ |
| 7a | `opensource.html` ("runs where heavy platforms will not") | soften to "designed for"; no "runs everywhere" |
| 7b | `solucao.html` ("min-spec to datacenter, air-gapped") | soften to "designed for" until the 1.8.0 full run is green |
| 7c | wheelhouse copy | state only the fact (wheels for musl / older hardware exist in `simple/`) |
| 8 | `sitemap.xml` | update `lastmod` only for pages touched |

Platform wording rule for any touched copy: **only Linux is supported**; Haiku/BSDs are lab-validated (VM); Windows native (MSI, agent) and macOS are **in progress**; Homebrew is **not mentioned** while data-boar#2156 is open. The existing "MSI, in progress" in `windows.html` stays.

### P2 — add (1-line, verifiable, no superclaim) — **scope blocked on D3**

- `praticas-de-engenharia.html`: hybrid **Ed25519 + ML-DSA-65** license signature (say "hybrid", never "post-quantum / quantum-safe"); minimal `GET /health`; 429 after 5 failed API-key attempts / 60 s, audited without the key; 12 h `SameSite=Strict` session cookie; CycloneDX SBOM per release. **Exclude** the credential host gate (#2103) and the integrity trust-root item (#2168, still open on `data-boar`).
- Install channels (`faq.html` or `opensource.html`): `pip` / `pipx` / `uvx data-boar --demo`, Docker Hub, native packages (deb/rpm/apk/pacman). **No Homebrew.** `pipx` stays the main Windows path.

### Out of scope

- Wheelhouse version refresh (item 9) — **dependency: [DataBoar/data-boar#2218](https://github.com/DataBoar/data-boar/issues/2218)** (open). The hosted wheelhouse lags the 1.8.0 `requirements.txt` (numpy 2.5.1 on the Release vs 2.5.4 pinned; the full delta is still to be measured there). `simple/` is generated from Release assets, so it is **not** edited until the new Release exists; then regenerate with `scripts/build-wheelhouse-index.py --tag <new-tag>`, in a separate PR.
- Naming non-public apps/integrations (site must stay clean of private satellites, partners, clients, prices).
- Any 1.7.4 vs 1.8.0 performance statement (not measured). Only citable figure remains the isolated Rust filter **4.69x**.
- Item 10 ("current version" badge): static text only if the HITL wants it; no external badge hosts without an ADR-0001 allowlist entry.

## Decisions pending (HITL)

- **D1 — DECIDED (a), generic wording. REVISED 2026-11-11 by the HITL: the original Clojure sidecar mention was restored on `index.html`, `solucao.html` and `opensource.html`.** Original discussion:  naming one language is inaccurate (HITL: there are several sidecars) and has no public source (0 `.clj` in the public tree). Options: (a) generic wording backed by the code above, e.g. "emits a metadata manifest (no raw values) for external sidecar modules, which are separate from the open-core", naming no language, component or count — **recommended**; (b) remove the mention; (c) keep a specific claim only with a verifiable public reference. Whatever is chosen, no sidecar is described as part of the open-core scanner unless the public docs say so.
- **D2 — DECIDED:** one epic PR (`Closes #96`).
- **D3 — DECIDED:** P2 goes in the same PR as P1 and P3.

## Constraints

- Bilingual pt-BR ↔ en-US, idiomatic, mirrored on the same page; EN overclaim-safe.
- Chrome only via `partials/site-chrome/` + `python3 scripts/sync-site-chrome.py` (not expected to be touched).
- Gates: `scripts/pre-commit` and `scripts/check-all.sh` green before PR; signed commits, no tool trailers; HITL merges.

## Acceptance criteria

- [x] No `--allow-insecure` without `-http` in `*.html`.
- [x] D1 applied consistently in pt and en on all three pages.
- [x] No sentence implies support beyond Linux; no Homebrew mention.
- [x] `praticas-de-engenharia.html` no longer claims a signed release manifest.
- [x] Anti-overclaim tests and `scripts/check-all.sh` green.
- [x] `PLANS_TODO.md` updated; plan moved to `completed/` when #96 closes.
