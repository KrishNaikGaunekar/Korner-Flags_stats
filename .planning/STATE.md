---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: planning
stopped_at: Completed 02-02-PLAN.md
last_updated: "2026-03-17T21:56:58.766Z"
last_activity: 2026-03-16 — Roadmap created
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 7
  completed_plans: 6
  percent: 33
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-16)

**Core value:** A coach can drop in any match video and immediately see annotated footage with player tracking, possession %, and speed/distance stats — no setup, no expertise required.
**Current focus:** Phase 1 — Pipeline Fixes and Validation

## Current Position

Phase: 1 of 6 (Pipeline Fixes and Validation)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-16 — Roadmap created

Progress: [███░░░░░░░] 33%

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

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: YOLO detection quality on NC State footage is unknown — if detection rate is poor, Roboflow fine-tuning adds 1-2 days
- [Phase 1]: Perspective transform uses estimated pitch vertices (not calibrated keypoints) — speed/distance values are approximate; add visible disclaimer on demo site
- [Phase 2]: Per-frame speed data format in current stats.json is unverified — check whether per-frame export exists before committing to speed timeline chart

## Session Continuity

Last session: 2026-03-17T21:56:58.762Z
Stopped at: Completed 02-02-PLAN.md
Resume file: None
