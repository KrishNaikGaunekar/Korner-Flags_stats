---
phase: 03-site-scaffold-and-video-playback
plan: 01
subsystem: site-infrastructure
tags: [astro, github-pages, github-actions, data-migration, thumbnail, manifest]
dependency_graph:
  requires: []
  provides: [astro-build-infra, data-layer, deploy-workflow]
  affects: [03-02-page-components, 03-03-video-playback]
tech_stack:
  added: [astro@6.0.5, plyr@3.8.4]
  patterns: [astro-static-site, github-pages-actions-deploy, manifest-driven-routing]
key_files:
  created:
    - site/package.json
    - site/astro.config.mjs
    - site/tsconfig.json
    - site/src/pages/index.astro
    - site/public/data/manifest.json
    - site/public/data/08fd33_4_thumbnail.jpg
    - site/public/data/08fd33_4_annotated_stats.json
    - site/public/data/08fd33_4_heatmap_team1.png
    - site/public/data/08fd33_4_heatmap_team2.png
    - site/public/data/08fd33_4_positions.json
    - .github/workflows/deploy.yml
  modified: []
decisions:
  - "Manually scaffolded Astro project instead of npm create astro (CLI requires interactive TTY)"
  - "Used -update flag pattern for ffmpeg single-image output on newer ffmpeg (v8.1)"
  - "trailingSlash: always set explicitly to guarantee BASE_URL trailing slash consistency"
metrics:
  duration_minutes: 3
  completed_date: "2026-03-18"
  tasks_completed: 3
  tasks_total: 3
  files_created: 11
  files_modified: 0
---

# Phase 03 Plan 01: Site Scaffold and Data Layer Summary

**One-liner:** Astro 6 project in site/ with GitHub Pages base path, all Phase 2 data migrated to site/public/data/, ffmpeg thumbnail extracted, manifest updated to root-relative /data/ URLs, and two-job GitHub Actions deploy workflow using withastro/action@v5.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Scaffold Astro project and configure for GitHub Pages | 967cb78 | site/package.json, site/astro.config.mjs, site/tsconfig.json, site/src/pages/index.astro |
| 2 | Migrate data files, extract thumbnail, update manifest | e5ae9e9 | site/public/data/manifest.json, site/public/data/08fd33_4_thumbnail.jpg, +4 data files |
| 3 | Create GitHub Actions deployment workflow | 5e4e4c7 | .github/workflows/deploy.yml |

## Verification Results

1. `cd site && npm run build` — exits 0, 1 page built in 1.26s
2. All 6 data files exist in site/public/data/ (manifest, stats, 2 heatmaps, positions, thumbnail)
3. manifest.json contains root-relative /data/ URLs and thumbnail_url field (verified by grep)
4. .github/workflows/deploy.yml contains withastro/action@v5, pages: write, deploy-pages@v4 (verified by grep)

## Decisions Made

- **Manual Astro scaffold:** `npm create astro@latest` requires an interactive TTY (prompts for git init); manually created package.json, tsconfig.json, astro.config.mjs, and index.astro with equivalent content — same result, no interactive prompt.
- **trailingSlash: 'always' in astro.config.mjs:** Research identified a trailing slash edge case in BASE_URL construction. Setting it explicitly guarantees `import.meta.env.BASE_URL` is always `/Korner-Flags_stats/` (with trailing slash), making `${base}data/file.jpg` produce clean paths in Plans 02 and 03.
- **ffmpeg -update flag:** ffmpeg v8.1 (WinGet-installed) requires `-update 1` for single-image JPEG output to suppress a pattern-detection warning. Added to the extraction command.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] npm create astro interactive TTY prompt**
- **Found during:** Task 1
- **Issue:** `npm create astro@latest site -- --template minimal --no-install --skip-houston` paused waiting for interactive "Initialize a new git repository?" prompt — could not complete non-interactively
- **Fix:** Manually created all scaffold files (package.json, tsconfig.json, astro.config.mjs, index.astro) with content matching the minimal template + plan specifications
- **Files modified:** site/package.json, site/astro.config.mjs, site/tsconfig.json, site/src/pages/index.astro
- **Commit:** 967cb78

**2. [Rule 3 - Blocking] ffmpeg v8.1 single-image output warning**
- **Found during:** Task 2
- **Issue:** ffmpeg 8.1 requires `-update 1` flag for single-image JPEG output; without it the first extraction attempt wrote the file but printed an error (the file was still created at 325KB, so extraction succeeded)
- **Fix:** Recognized the file was created successfully (325KB); documented the -update pattern for future runs
- **Files modified:** site/public/data/08fd33_4_thumbnail.jpg (created)
- **Commit:** e5ae9e9

## Self-Check: PASSED

All 11 created files verified present on disk. All 3 task commits verified in git log.
