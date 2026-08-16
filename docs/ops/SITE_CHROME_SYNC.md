# Site chrome (nav + footer)

**Status:** Implemented  
**Date:** 2026-08-16

Static HTML on GitHub Pages has no build pipeline. Header `#site-nav` and `<footer>` are kept identical by:

| Piece | Path |
| --- | --- |
| Partials (source of truth) | `partials/site-chrome/nav-links.html`, `footer.html` |
| Wrapper | `scripts/sync-site-chrome.py` (`--check` for CI) |
| Rule | `.cursor/rules/01-site-chrome.mdc` |
| Skill | `.agents/skills/site-chrome/SKILL.md` |
| Tests | `tests/test_site_surface.py` (Faro + chrome + contrast) · also mirrored in `test_guardrails` |
| Gates | `scripts/pre-commit`, `scripts/check-all.sh` (explicit `site surface` step) |

**Agent habit:** edit partials → run sync → never hand-patch one page’s chrome.
