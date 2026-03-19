---
phase: 04-stats-visualizations
plan: 01
subsystem: site/components
tags: [astro, css, stats-visualization, possession-bar, player-table, coming-soon]
dependency_graph:
  requires: []
  provides:
    - site/src/components/PossessionBar.astro
    - site/src/components/PlayerStatsTable.astro
    - site/src/components/ComingSoonCards.astro
  affects:
    - site/src/pages/clips/[slug].astro (Plan 02 will wire these in)
tech_stack:
  added: []
  patterns:
    - Astro scoped CSS components with prop interfaces
    - CSS flexbox possession bar (no charting library)
    - HTML table with two stacked team sections (no client-side JS)
key_files:
  created:
    - site/src/components/PossessionBar.astro
    - site/src/components/PlayerStatsTable.astro
    - site/src/components/ComingSoonCards.astro
  modified: []
decisions:
  - Two stacked team sections chosen over tabs for PlayerStatsTable (no client-side JS required)
  - Team 1 = #0071e3 (Apple blue), Team 2 = #e8732a (warm orange) — both pass 4.5:1 contrast
  - SVG padlock chosen over emoji for ComingSoonCards (monochrome, consistent with Apple-esque palette)
  - Ghost player filtering deferred to caller ([slug].astro in Plan 02) per plan spec
metrics:
  duration: 4 minutes
  completed_date: "2026-03-19"
  tasks_completed: 2
  files_created: 3
  files_modified: 0
---

# Phase 04 Plan 01: Stats Visualization Components Summary

**One-liner:** Three Astro components — CSS flexbox possession bar, two-team player speed/distance table, and four Coming Soon teaser cards — using the Apple-esque palette with scoped CSS and no charting libraries.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create PossessionBar and ComingSoonCards | 9890512 | site/src/components/PossessionBar.astro, site/src/components/ComingSoonCards.astro |
| 2 | Create PlayerStatsTable | d28af35 | site/src/components/PlayerStatsTable.astro |

## What Was Built

### PossessionBar.astro
Accepts `{ team1Pct: number, team2Pct: number }` props. Renders a horizontal flex bar split into two colored segments (Team 1 blue `#0071e3`, Team 2 orange `#e8732a`). Percentage labels appear outside the bar as block elements. Accessibility: `role="img"` with `aria-label` on the bar element. Exact disclaimer text "AI-estimated ±5%" appears below in grey caption style.

### ComingSoonCards.astro
No props (static content). Renders four muted cards (opacity 0.55, grey `#f5f5f7` background) in a responsive auto-fill grid (minmax 160px). Each card: monochrome SVG padlock icon, stat name, "Coming Soon" badge. Stats covered: Pass Counts, Shots, Shots on Target, Assists. No emoji anywhere.

### PlayerStatsTable.astro
Accepts `{ team1Players: Player[], team2Players: Player[] }` props. Renders two stacked table sections with color-coded left-border headings (Team 1 = blue, Team 2 = orange). Columns: Player, Top Speed, Avg Speed, Distance. All numeric values formatted to 1 decimal place. `scope="col"` on every `th`. Horizontal scroll wrapper (`overflow-x: auto`) for narrow viewports. Exact disclaimer "AI-estimated from video — values are approximate" appears below both tables.

## Decisions Made

1. **Two stacked sections over tabs** — PlayerStatsTable uses two static HTML sections rather than a JS-toggled tab interface. Removes client-side JavaScript dependency entirely and coaches scan by team naturally anyway.

2. **Color palette** — Team 1 `#0071e3` (slightly adjusted from palette `#0066cc` to match plan spec), Team 2 `#e8732a`. Both pass 4.5:1 contrast ratio against white text. These colors are consistent between PossessionBar and PlayerStatsTable headings.

3. **SVG padlock over emoji** — Inline monochrome SVG padlock used in ComingSoonCards for consistent rendering across platforms (emoji rendering varies per OS/browser).

4. **Ghost player filtering deferred to caller** — The plan spec states "ghost rows are expected to be pre-filtered by the caller." PlayerStatsTable renders whatever players it receives. [slug].astro (Plan 02) will filter `distance_m > 0 || max_speed_kmh > 0` before passing arrays.

## Verification

- All three component files exist in `site/src/components/`
- `npm run build` passes cleanly (2 pages built)
- 23/23 acceptance criteria checks pass
- No charting library imports
- No emoji characters in any component file

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

- [x] site/src/components/PossessionBar.astro — FOUND
- [x] site/src/components/PlayerStatsTable.astro — FOUND
- [x] site/src/components/ComingSoonCards.astro — FOUND
- [x] Commit 9890512 — FOUND
- [x] Commit d28af35 — FOUND

## Self-Check: PASSED
