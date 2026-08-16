# Site chrome (announce + nav + nav-cta + footer)

**Status:** Implemented  
**Date:** 2026-08-16

Static HTML on GitHub Pages has no build pipeline. Site chrome is kept identical by:

| Piece | Path |
| --- | --- |
| Partials (source of truth) | `partials/site-chrome/announce.html`, `nav-links.html`, `nav-cta.html`, `footer.html` |
| Wrapper | `scripts/sync-site-chrome.py` (`--check` for CI) |
| Rule | `.cursor/rules/01-site-chrome.mdc` |
| Skill | `.agents/skills/site-chrome/SKILL.md` |
| Tests | `tests/test_site_surface.py` (Faro + chrome + Agendar placement + contrast) · also mirrored in `test_guardrails` |
| Gates | `scripts/pre-commit`, `scripts/check-all.sh` (explicit `site surface` step) |

**Layout contract:** brown `.announce` on every page; **Agendar** only there; white header `.nav-cta` = Login + lang-switch.

**Agent habit:** edit partials → run sync → never hand-patch one page’s chrome.
