---
phase: 04-stats-visualizations
plan: 02
subsystem: ui
tags: [astro, static-site, stats-visualization, possession-bar, player-tables]

# Dependency graph
requires:
  - phase: 04-01
    provides: PossessionBar, PlayerStatsTable, ComingSoonCards Astro components with verified prop interfaces
  - phase: 03-02
    provides: "[slug].astro clip detail page with manifest import pattern"
provides:
  - Clip detail page with live stats visualizations built from real JSON data at build time
  - Possession bar showing Team 1/Team 2 split with real percentages from stats JSON
  - Per-team player speed/distance tables with ghost player filtering
  - Four Coming Soon teaser cards for future stats features
affects:
  - 05-heatmaps (will add to the same clip detail page below heatmaps-placeholder)

# Tech tracking
tech-stack:
  added: []
  patterns: [Vite dynamic import of public JSON at Astro build time with clip_id template literal, ghost player filtering via OR condition on distance_m and max_speed_kmh]

key-files:
  created: []
  modified:
    - site/src/pages/clips/[slug].astro

key-decisions:
  - "Dynamic JSON import uses template literal with literal prefix so Vite can resolve it at build time: await import(`../../../public/data/${clip.clip_id}_annotated_stats.json`)"
  - "Ghost player filter uses OR condition (distance_m > 0 || max_speed_kmh > 0) to retain partial-data players while excluding all-zero ghost entries"
  - "stats-section replaces stats-placeholder with identical card layout (same margin, padding, background, border-radius, box-shadow) for visual continuity"
  - "heatmaps-placeholder section left completely untouched with its own explicit CSS rule — no shared selector with stats-section"

patterns-established:
  - "Build-time data loading: Vite template literal dynamic import from public/data/ — same pattern as manifest import, works for per-clip JSON"
  - "Ghost filtering in caller ([slug].astro) not in component (PlayerStatsTable) — components remain pure, filtering logic stays with data assembly"

requirements-completed: [SITE-04, SITE-06, SITE-07, SITE-08]

# Metrics
duration: 15min
completed: 2026-03-19
---

# Phase 04 Plan 02: Stats Visualizations Integration Summary

**PossessionBar, PlayerStatsTable, and ComingSoonCards wired into [slug].astro with build-time stats JSON import, ghost player filtering, and ID-sorted team tables**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-19T17:43:00Z
- **Completed:** 2026-03-19T17:58:00Z
- **Tasks:** 1 of 2 complete (Task 2 is human-verify checkpoint — awaiting visual sign-off)
- **Files modified:** 1

## Accomplishments
- Stats JSON imported at Astro build time via Vite dynamic import with clip_id template literal
- Ghost players (all-zero stats entries) filtered before passing to PlayerStatsTable
- Players sorted by numeric ID ascending for stable, coach-readable order
- Three components (PossessionBar, PlayerStatsTable, ComingSoonCards) rendered in one stats-section card
- Heatmaps placeholder preserved unchanged for Phase 5
- Astro build exits 0; dist HTML contains Top Speed, AI-estimated, Coming Soon, Pass Counts, heatmaps-placeholder

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire stats components into clip detail page** - `bd8f7d5` (feat)
2. **Task 2: Visual verification of stats layout** - pending human checkpoint

**Plan metadata:** pending final commit

## Files Created/Modified
- `site/src/pages/clips/[slug].astro` - Added 3 component imports, build-time stats JSON import, ghost filtering, player partitioning by team, replaced stats-placeholder section with stats-section rendering real data

## Decisions Made
- Dynamic import uses template literal `../../../public/data/${clip.clip_id}_annotated_stats.json` — Vite resolves this at build time given the literal path prefix, same pattern proven by manifest import
- Ghost filter applied in [slug].astro frontmatter rather than inside PlayerStatsTable — keeps components pure and data assembly concerns in the page layer
- stats-section CSS rule explicitly declared (not shared selector with heatmaps-placeholder) to avoid any risk of breakage when heatmaps-placeholder is replaced in Phase 5

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- Task 2 (visual verification) is a human checkpoint — user must confirm the layout at http://localhost:4321/Korner-Flags_stats/
- Once confirmed, plan 04-02 is complete and Phase 04 is done
- Phase 05 (heatmaps) can add content below the heatmaps-placeholder section without touching the stats-section

---
*Phase: 04-stats-visualizations*
*Completed: 2026-03-19*
