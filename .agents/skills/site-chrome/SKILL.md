---
name: site-chrome
description: When editing site header navigation, footer links, or adding a new HTML page — keep nav and footer synchronized via partials and scripts/sync-site-chrome.py. Use when the user mentions footer drift, header menu, Verticais nav, or "sync chrome".
---

# Site chrome sync (nav + footer)

## Why
GitHub Pages static HTML has **no build**. Chrome must stay byte-identical across pages or the footer/nav regression tests fail.

## Do this
1. Change links only in:
   - `partials/site-chrome/nav-links.html`
   - `partials/site-chrome/footer.html`
2. Apply: `python3 scripts/sync-site-chrome.py`
3. Verify: `python3 scripts/sync-site-chrome.py --check`
4. New page: include `<nav class="links" id="site-nav">…</nav>` and either a `<footer>` or `<!-- FOOTER_PLACEHOLDER -->`, then run the sync script.
5. Nested under `casos/`: sync adds `../` automatically — never hand-maintain a divergent footer.

## Do not
- Hand-edit footer/nav on one page “just for this PR”
- Re-add Contabilidade / Menores as top-level footer siblings (use **Verticais**)
- Skip `--check` when check-all is expected green

## Related
- Rule: `.cursor/rules/01-site-chrome.mdc`
- Tests: `tests/test_guardrails.py` (`test_footer_block_identical`, `test_nav_links_identical`, `test_site_chrome_sync_check`)
