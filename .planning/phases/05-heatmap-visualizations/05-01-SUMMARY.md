---
phase: 05-heatmap-visualizations
plan: 01
subsystem: ui
tags: [astro, heatmap, mplsoccer, static-site, github-pages]

# Dependency graph
requires:
  - phase: 04-site-stats-display
    provides: clip detail page [slug].astro with possession bar and player stats table
  - phase: 02-data-export-and-video-processing
    provides: heatmap PNG files in site/public/data/ and manifest.json heatmap URL fields
provides:
  - Two-column team heatmap section on every clip detail page
  - Responsive grid collapsing to single column at 640px
  - AI disclaimer text below heatmaps
affects: [06-stretch-goals, future-ui-phases]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BASE_URL prefix pattern: `${base}${url.replace(/^\\//, '')}` for public/ assets on GitHub Pages subpath"
    - "Static heatmap images served from public/data/ directory — no Vite import, URL-referenced only"

key-files:
  created: []
  modified:
    - site/src/pages/clips/[slug].astro

key-decisions:
  - "Heatmap images use identical BASE_URL stripping pattern as ClipCard.astro thumbnails — no new patterns introduced"
  - "Section is purely static: no client-side JS, no client:* directives, no Vite asset imports"

patterns-established:
  - "Phase 4 team colors (#0071e3 blue, #e8732a orange) used consistently for Team 1/Team 2 labels across all sections"
  - "AI disclaimer color #86868b matches PossessionBar.astro for visual consistency"

requirements-completed: [SITE-05]

# Metrics
duration: 5min
completed: 2026-03-19
---

# Phase 5 Plan 01: Heatmap Visualizations Summary

**Two-column static team heatmap section with colored headings, responsive grid, and AI disclaimer replaces the "Coming in the next update" placeholder on clip detail pages**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-19T20:05:00Z
- **Completed:** 2026-03-19T20:10:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Replaced `.heatmaps-placeholder` stub with a fully functional `.heatmaps-section` rendering two PNG heatmaps from manifest URLs
- Applied correct `${base}${url.replace(/^\//, '')}` pattern ensuring images load on GitHub Pages subpath without 404
- Team 1 heading in #0071e3 (Apple blue), Team 2 in #e8732a (warm orange) — consistent with Phase 4 palette
- Responsive CSS grid collapses from two columns to one at max-width 640px
- AI disclaimer "AI-estimated from video — values are approximate" in #86868b below heatmap images
- Astro build exits 0 with no errors or warnings related to the change

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace heatmaps placeholder with two-column PNG layout** - `845060a` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `site/src/pages/clips/[slug].astro` - Replaced heatmaps-placeholder section and CSS with full heatmaps-section two-column grid layout

## Decisions Made
- No new patterns needed — reused the existing `${base}${url.replace(/^\//, '')}` pattern established in Phase 3 ClipCard.astro
- Section kept fully static (no JS, no Vite imports) per plan constraint

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Clip detail pages now show real heatmap images in a polished two-column layout
- If Phase 6 adds interactive D3 heatmaps, they can replace the `<img>` tags inside `.heatmap-col` without restructuring the section shell
- No blockers

---
*Phase: 05-heatmap-visualizations*
*Completed: 2026-03-19*
