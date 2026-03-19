---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: in_progress
stopped_at: "Completed 04-01-PLAN.md"
last_updated: "2026-03-19T22:00:00.000Z"
progress:
  total_phases: 6
  completed_phases: 3
  total_plans: 12
  completed_plans: 11
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-16)

**Core value:** A coach can drop in any match video and immediately see annotated footage with player tracking, possession %, and speed/distance stats — no setup, no expertise required.
**Current focus:** Phase 04 — stats-visualizations

## Current Position

Phase: 04 (stats-visualizations) — EXECUTING
Plan: 2 of 2

## Performance Metrics

**Velocity:**

- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**

- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
| Phase 01 P02 | 1 | 2 tasks | 2 files |
| Phase 01-pipeline-fixes-and-validation P01 | 3 | 2 tasks | 5 files |
| Phase 01 P03 | 15 | 2 tasks | 0 files |
| Phase 02 P01 | 18 | 2 tasks | 6 files |
| Phase 02 P02 | 7 | 1 tasks | 3 files |
| Phase 03 P01 | 3 | 3 tasks | 11 files |
| Phase 03 P02 | 260 | 2 tasks | 5 files |
| Phase 03 P03 | 15 | 3 tasks | 2 files |
| Phase 04 P01 | 4 | 2 tasks | 3 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Static site on GitHub Pages first; FastAPI + Next.js backend deferred to Phase 2 web app
- [Init]: Videos hosted on GitHub Releases (not Git LFS, not committed to repo tree) to bypass 100 MB Pages file limit
- [Init]: mplsoccer static PNG heatmaps as primary deliverable; D3 interactive heatmap is stretch goal in Phase 5
- [Phase 01]: Write frames to temp AVI via OpenCV then re-encode to H.264 MP4 via ffmpeg subprocess — avoids OpenCV's lack of native H.264 support
- [Phase 01]: Use -movflags +faststart so browser video playback starts immediately without full download
- [Phase 01]: Use os.path.splitext for stats JSON path derivation so it works regardless of video extension
- [Phase 01-pipeline-fixes-and-validation]: Proportional mask ratios (0.010, 0.469, 0.547) back-calculated from original 1920px calibration to support any frame width
- [Phase 01-pipeline-fixes-and-validation]: position_adjusted is the correct key linking camera movement correction to ViewTransformer perspective transform
- [Phase 01-pipeline-fixes-and-validation]: ffmpeg installed via winget Gyan.FFmpeg (system-level, not Python dependency) to enable H.264 MP4 output
- [Phase 01-03]: PIPE-04 satisfied: user confirmed all 5 detection quality criteria (player ellipses, persistent IDs, ball triangle, two team colors, possession overlay)
- [Phase 01-03]: Speed values unrealistically high (268 km/h max) — known limitation of estimated pitch vertices; add disclaimer on demo site in Phase 6
- [Phase 01-03]: Possession accuracy slightly off — 15-frame smoothing + estimated vertices are approximate by design; acceptable for Phase 2
- [Phase 02-01]: generate_stats() players dict keyed by str(player_id) for JSON string-key convention
- [Phase 02-01]: export_positions() uses round(fps) as sample interval for exact 1 Hz; positions_path strips _annotated suffix for clean filename
- [Phase 03-01]: Manual Astro scaffold used instead of npm create astro due to interactive TTY requirement
- [Phase 03-01]: trailingSlash: always set in astro.config.mjs to guarantee clean BASE_URL trailing slash for public asset paths
- [Phase 03-02]: Manifest import path from clips/[slug].astro requires ../../../public (3 levels up) vs ../../public from root pages/ directory
- [Phase 03-02]: Plyr script tag uses standard import (not is:inline) to allow Astro bundling and CSS injection
- [Phase 03]: Committed site/package-lock.json so withastro/action@v5 can detect npm as the package manager
- [Phase 03]: site/.gitignore added to exclude node_modules/, dist/, .astro/ from git in monorepo structure
- [Phase 04-01]: PlayerStatsTable uses two stacked static sections (no tabs, no client-side JS) — coaches scan by team naturally
- [Phase 04-01]: Team 1 = #0071e3 (Apple blue), Team 2 = #e8732a (warm orange) — consistent across PossessionBar and PlayerStatsTable
- [Phase 04-01]: Ghost player filtering (distance_m > 0 || max_speed_kmh > 0) deferred to [slug].astro caller (Plan 02)
- [Phase 04-01]: SVG padlock used in ComingSoonCards instead of emoji — consistent monochrome rendering across platforms

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: YOLO detection quality on NC State footage is unknown — if detection rate is poor, Roboflow fine-tuning adds 1-2 days
- [Phase 1]: Perspective transform uses estimated pitch vertices (not calibrated keypoints) — speed/distance values are approximate; add visible disclaimer on demo site
- [Phase 2]: Per-frame speed data format in current stats.json is unverified — check whether per-frame export exists before committing to speed timeline chart

## Session Continuity

Last session: 2026-03-19T22:00:00.000Z
Stopped at: Completed 04-01-PLAN.md
Resume file: .planning/phases/04-stats-visualizations/04-01-SUMMARY.md
