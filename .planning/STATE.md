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

Progress: [░░░░░░░░░░] 0%

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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Static site on GitHub Pages first; FastAPI + Next.js backend deferred to Phase 2 web app
- [Init]: Videos hosted on GitHub Releases (not Git LFS, not committed to repo tree) to bypass 100 MB Pages file limit
- [Init]: mplsoccer static PNG heatmaps as primary deliverable; D3 interactive heatmap is stretch goal in Phase 5

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: YOLO detection quality on NC State footage is unknown — if detection rate is poor, Roboflow fine-tuning adds 1-2 days
- [Phase 1]: Perspective transform uses estimated pitch vertices (not calibrated keypoints) — speed/distance values are approximate; add visible disclaimer on demo site
- [Phase 2]: Per-frame speed data format in current stats.json is unverified — check whether per-frame export exists before committing to speed timeline chart

## Session Continuity

Last session: 2026-03-16
Stopped at: Roadmap created, STATE.md initialized — ready to plan Phase 1
Resume file: None
