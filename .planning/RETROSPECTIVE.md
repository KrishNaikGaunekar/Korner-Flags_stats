# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

---

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-20
**Phases:** 6 | **Plans:** 14 | **Timeline:** 4 days (2026-03-15 → 2026-03-20)

### What Was Built

- Fixed pipeline bugs (view transformer, camera movement, H.264 output) — made annotated video browser-compatible
- Data export layer: positions.json (1Hz), team heatmap PNGs via mplsoccer, per-player stats JSON schema, GitHub Releases upload helper
- Astro static site on GitHub Pages — manifest-driven gallery, Plyr video player, GitHub Actions CI/CD
- Stats visualizations: possession bar with AI disclaimer, speed/distance tables in coaching language, coming-soon cards
- Team heatmap display — two-column layout, team-colored headings, AI disclaimer
- Demo-ready polish: 2-clip NC State gallery, coaching-audience intro, plain-English "How It Works" section

### What Worked

- **Risk-first phase ordering** — fixing pipeline bugs (Phase 1) before touching the site prevented rework downstream
- **Static-first decision** — GitHub Pages with pre-processed data was the right call for a 4-day demo build; no backend complexity
- **GitHub Releases for video** — cleanly solved the 100 MB Pages file size limit; stable CDN URLs that won't change
- **GSD wave-based parallel execution** — executor subagents ran cleanly and atomically per task
- **No ML jargon rule** — enforcing plain English at the plan level meant zero cleanup needed at the end

### What Was Inefficient

- **Heatmap PNG approach** — static PNGs are fine for v1 but require re-running the Python pipeline to update; interactive heatmaps deferred to v1.1
- **Duplicate clip 2 data** — clip 2 is a placeholder duplicate of clip 1 stats/video; real second clip data still needs to be sourced
- **No pipeline test suite** — YOLO inference and ByteTrack integration have no automated tests; regression risk if pipeline changes

### Patterns Established

- `manifest.json` as single source of truth for all clip URLs — site pages are pure consumers
- Astro `getStaticPaths` + dynamic import pattern for clip detail pages — scales cleanly to N clips
- HTML entities for emoji in Astro static pages (no encoding issues across browsers)
- GSD planning structure (CONTEXT → RESEARCH → PLAN → SUMMARY → VERIFICATION) proved effective for a project of this scope

### Key Lessons

1. **Validate data artifacts before building UI** — Phase 2 integration checkpoint (17/17 tests) caught schema issues before the site consumed them
2. **Commit data files to repo for static site** — positions.json, heatmap PNGs, and stats JSON in `site/public/data/` keeps the build deterministic
3. **Plain-language constraint must be in the plan** — including "zero ML jargon" in acceptance criteria is what enforces it; leaving it to judgment doesn't work

### Cost Observations

- Model mix: all sonnet (executor + verifier agents)
- Sessions: ~6-8 sessions across 4 days
- Notable: subagent-based execution kept orchestrator context lean; no context overflow across 6 phases

---

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Days | 4 |
| Phases | 6 |
| Plans | 14 |
| Rework cycles | 0 major |
| Verification gaps | 0 (all passed) |
