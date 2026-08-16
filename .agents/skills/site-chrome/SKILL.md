---
name: site-chrome
description: When editing site header navigation, announce bar, footer links, or adding a new HTML page — keep announce, nav, nav-cta, and footer synchronized via partials and scripts/sync-site-chrome.py. Use when the user mentions footer drift, header menu, brown top bar, Agendar CTA placement, Verticais nav, or "sync chrome".
---

# Site chrome sync (announce + nav + nav-cta + footer)

## Why
GitHub Pages static HTML has **no build**. Chrome must stay byte-identical across pages or the surface/guardrail tests fail.

## Do this
1. Change chrome only in:
   - `partials/site-chrome/announce.html` (brown bar; **only** place for Agendar)
   - `partials/site-chrome/nav-links.html`
   - `partials/site-chrome/nav-cta.html` (Login + lang — **no** Agendar)
   - `partials/site-chrome/footer.html`
2. Apply: `python3 scripts/sync-site-chrome.py`
3. Verify: `python3 scripts/sync-site-chrome.py --check`
4. New page: include `.announce`, `<nav class="links" id="site-nav">`, `.nav-cta`, and either a `<footer>` or `<!-- FOOTER_PLACEHOLDER -->`, then run the sync script.
5. Nested under `casos/`: sync adds `../` automatically — never hand-maintain divergent chrome.
6. **Verticais** lives in footer Recursos only — do **not** put it in top `#site-nav` (logo breathing room).

## Do not
- Hand-edit announce/nav/nav-cta/footer on one page “just for this PR”
- Put `mini-btn` / Agendar inside `<header>` (belongs only in `.announce`)
- Re-add Contabilidade / Menores as top-level footer siblings (use **Verticais**)
- Skip `--check` when check-all is expected green

## Related
- Rule: `.cursor/rules/01-site-chrome.mdc`
- Tests: `tests/test_site_surface.py` (announce + nav-cta + Agendar placement) · `tests/test_guardrails.py`
