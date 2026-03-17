---
phase: 02-data-export-and-video-processing
plan: 01
subsystem: data-export
tags: [pytest, json, positions-export, stats-restructure, tdd]

# Dependency graph
requires:
  - phase: 01-pipeline-fixes-and-validation
    provides: tracks structure with position_transformed, speed, distance, team per player per frame
provides:
  - export_positions() function writing 1 Hz positions.json for heatmap generation (DATA-01)
  - generate_stats() restructured to per-player nested format with team, distance_m, max_speed_kmh, avg_speed_kmh (DATA-03)
  - pytest test suite with 5 tests covering schema and correctness
affects: [02-02-heatmap-generation, phase-3-demo-site]

# Tech tracking
tech-stack:
  added: [pytest>=7.0.0]
  patterns: [TDD red-green, per-player dict keyed by string player_id, 1 Hz downsampling via round(fps)]

key-files:
  created: [tests/test_export.py, tests/test_stats.py, tests/__init__.py, pytest.ini]
  modified: [main.py, requirements.txt]

key-decisions:
  - "generate_stats() players dict keyed by str(player_id) — consistent with JSON string-key convention"
  - "export_positions() uses round(fps) as sample interval for exact 1 Hz regardless of non-integer fps values"
  - "positions_path derived from output path with .replace('_annotated', '') so it reads as <name>_positions.json not <name>_annotated_positions.json"
  - "Records where position_transformed is None OR team is None are both excluded from positions export"

patterns-established:
  - "Per-player stats: dict keyed by str(player_id) with team (int), distance_m (float), max_speed_kmh (float), avg_speed_kmh (float)"
  - "1 Hz sampling: frame_num % round(fps) == 0 as the canonical gating condition"
  - "Speed aggregation: max and mean of all non-None speed values across all frames for each player"

requirements-completed: [DATA-01, DATA-03]

# Metrics
duration: 18min
completed: 2026-03-17
---

# Phase 2 Plan 01: Data Export and Stats Restructure Summary

**positions.json 1 Hz export and per-player stats JSON restructure with pytest TDD — 5 tests green**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-17T21:45:05Z
- **Completed:** 2026-03-17T22:03:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `export_positions(tracks, video_info, output_path)` to main.py that samples player positions at 1 Hz and writes positions.json with fps, sample_rate_hz, and positions array (DATA-01)
- Restructured `generate_stats()` to return per-player nested dict keyed by string player_id, each containing team, distance_m, max_speed_kmh, avg_speed_kmh — replacing the old flat distances/total_detected format (DATA-03)
- Wired `export_positions()` call into `main()` after the stats JSON save, deriving output path automatically from the video output path
- Created pytest test suite (5 tests) covering schema validation, 1 Hz sample rate, None-record skipping, and speed calculation correctness

## Task Commits

Each task was committed atomically:

1. **Task 1: Create test scaffolding and write failing tests (RED phase)** - `6ff20e4` (test)
2. **Task 2: Implement export_positions() and restructure generate_stats() (GREEN phase)** - `2c9eda5` (feat)

## Files Created/Modified

- `main.py` - Added `export_positions()` function; rewrote `generate_stats()` to per-player format; added call to `export_positions()` in `main()`
- `tests/test_export.py` - 3 tests: schema, sample rate at 1 Hz, None-record exclusion
- `tests/test_stats.py` - 2 tests: per-player schema structure, max/avg speed calculation
- `tests/__init__.py` - Empty package marker
- `pytest.ini` - testpaths = tests
- `requirements.txt` - Added pytest>=7.0.0

## Decisions Made

- `generate_stats()` players dict keyed by `str(player_id)` — consistent with JSON string-key convention
- `export_positions()` uses `round(fps)` as sample interval for exact 1 Hz regardless of non-integer fps values
- `positions_path` derived with `.replace('_annotated', '')` so file reads as `<name>_positions.json` not `<name>_annotated_positions.json`
- Records where `position_transformed is None` OR `team is None` are both excluded from positions export — ensures no orphaned records with missing team context

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `positions.json` schema is ready for Plan 02 heatmap generation to consume
- `stats.json` per-player format is ready for Phase 3+ demo site rendering
- Both output files are derived from the output video path automatically — no CLI flag changes needed

---
*Phase: 02-data-export-and-video-processing*
*Completed: 2026-03-17*
