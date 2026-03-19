---
phase: 03-site-scaffold-and-video-playback
plan: "02"
subsystem: site
tags: [astro, plyr, video-playback, gallery, components]
dependency_graph:
  requires: [03-01]
  provides: [site-gallery, site-video-playback, clip-detail-pages]
  affects: [03-03]
tech_stack:
  added: [plyr]
  patterns: [astro-components, getStaticPaths, ESM-manifest-import]
key_files:
  created:
    - site/src/components/VideoPlayer.astro
    - site/src/pages/clips/[slug].astro
  modified:
    - site/src/layouts/BaseLayout.astro
    - site/src/components/ClipCard.astro
    - site/src/pages/index.astro
decisions:
  - "Manifest import path from clips/[slug].astro requires ../../../public (3 levels up) vs ../../public from pages/"
  - "Plyr script tag uses standard import (not is:inline) to allow Astro bundling and CSS injection"
metrics:
  duration_seconds: 260
  completed_date: "2026-03-19"
  tasks_completed: 2
  files_created: 2
  files_modified: 3
---

# Phase 03 Plan 02: Astro Pages and Components Summary

**One-liner:** Gallery index and Plyr-powered clip detail pages built from manifest.json with Apple-esque design using Inter font and BASE_URL-prefixed asset paths.

## What Was Built

All Astro pages and components needed for browsable clip gallery and watchable clip detail pages:

- **BaseLayout.astro** — Shared HTML shell with Inter Google Font, global CSS reset, site header (already created in Plan 01, verified complete)
- **ClipCard.astro** — Match card component with thumbnail, title, duration display, and "View Analysis" CTA link (already created in Plan 01, verified complete)
- **index.astro** — Gallery grid page importing manifest.json at build time and rendering ClipCard per clip (already created in Plan 01, verified complete)
- **VideoPlayer.astro** — Plyr video player component accepting `src`, `poster`, `title` props; uses standard `<script>` tag (not `is:inline`) for Plyr initialization
- **clips/[slug].astro** — Dynamic detail page with `getStaticPaths` mapping manifest clips to URL slugs; back link, video player, and placeholder sections for Phase 4/5

## Verification Results

All acceptance criteria passed:

- `npm run build` exits 0 with 2 pages built
- `dist/index.html` exists and contains clip-card markup
- `dist/clips/08fd33_4/index.html` exists and contains Plyr player with correct CDN video URL
- All asset URLs use `import.meta.env.BASE_URL` (not hardcoded `/Korner-Flags_stats/`)
- No `is:inline` on the Plyr script tag

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed manifest.json import path in clips/[slug].astro**
- **Found during:** Task 2 build verification
- **Issue:** The plan specified `import manifestData from '../../public/data/manifest.json'` but `[slug].astro` lives at `src/pages/clips/` (one directory deeper than `src/pages/`), so the relative path needed one more `../`
- **Fix:** Changed to `import manifestData from '../../../public/data/manifest.json'`
- **Files modified:** `site/src/pages/clips/[slug].astro`
- **Commit:** af6d299

## Task Commits

| Task | Description | Commit |
|------|-------------|--------|
| 1 | BaseLayout, ClipCard, index gallery | 7668773 |
| 2 | VideoPlayer and clip detail pages | af6d299 |

## Self-Check: PASSED
