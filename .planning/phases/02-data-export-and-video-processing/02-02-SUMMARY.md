---
phase: 02-data-export-and-video-processing
plan: "02"
subsystem: data
tags: [mplsoccer, heatmap, matplotlib, scipy, python, visualization]

# Dependency graph
requires:
  - phase: 02-01
    provides: positions.json schema with per-player (x,y,team) at 1Hz
provides:
  - generate_heatmaps.py standalone script: reads positions.json, outputs two team heatmap PNGs
  - tests/test_heatmaps.py: 3 passing tests covering file creation, dimensions, empty-team handling
affects:
  - 02-03 (stats restructure)
  - 02-04 (manifest.json)
  - phase-3 (demo site consuming heatmap PNGs)

# Tech tracking
tech-stack:
  added: [mplsoccer>=1.6.0]
  patterns:
    - "matplotlib.use('Agg') before any pyplot import for headless PNG generation"
    - "Pitch(pitch_type='custom', pitch_length=23.32, pitch_width=68) for ViewTransformer coordinate range"
    - "bin_statistic + gaussian_filter + heatmap pattern for soccer density visualization"
    - "Save without bbox_inches='tight' to preserve target 1200x800 figure dimensions"

key-files:
  created:
    - generate_heatmaps.py
    - tests/test_heatmaps.py
  modified:
    - requirements.txt

key-decisions:
  - "Removed bbox_inches='tight' from fig.savefig() to preserve 1200x800px output — extreme pitch aspect ratio (23.32m x 68m) caused tight crop to compress width to ~325px"
  - "Team 1 = Blues colormap, Team 2 = Reds colormap (locked from Phase 2 context)"
  - "mplsoccer Pitch (horizontal) with custom dimensions matches ViewTransformer x/y coordinate ranges directly — no normalization needed"

patterns-established:
  - "Pattern: standalone heatmap script separate from main.py pipeline — allows regeneration without re-running YOLO"
  - "Pattern: guard len(x_coords) > 0 before bin_statistic call — produces pitch-only PNG for empty teams"

requirements-completed: [DATA-02]

# Metrics
duration: 7min
completed: "2026-03-17"
---

# Phase 02 Plan 02: Heatmap Generation Summary

**mplsoccer team heatmap PNGs from positions.json using bin_statistic + gaussian_filter on custom 23.32x68m pitch, Blues/Reds colormaps, 1200x800px output**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-17T21:52:50Z
- **Completed:** 2026-03-17T21:59:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 3

## Accomplishments
- generate_heatmaps.py reads positions.json and produces two heatmap PNGs (one per team) with correct colormaps on a green pitch background
- mplsoccer Pitch with pitch_type='custom' accepts ViewTransformer meter coordinates directly (no rescaling needed)
- All 3 heatmap tests pass: file creation, dimensions (1200x800), and empty-team graceful handling

## Task Commits

Each task was committed atomically:

1. **Task 1: Create generate_heatmaps.py with tests** - `9e2857e` (feat)

## Files Created/Modified
- `generate_heatmaps.py` - Standalone heatmap script: load_positions(), generate_heatmap(), argparse CLI
- `tests/test_heatmaps.py` - 3 tests: test_heatmap_files_created, test_heatmap_dimensions, test_heatmap_empty_team
- `requirements.txt` - Added mplsoccer>=1.6.0

## Decisions Made
- Removed `bbox_inches='tight'` from savefig call — the extreme pitch aspect ratio (23.32m wide vs 68m tall) caused matplotlib's tight crop to compress the PNG to ~325px wide, far below the 1200x800 target. Without tight crop, figsize=(12,8) at 100 DPI produces the correct 1200x800 output.
- Used `Pitch` (horizontal) rather than `VerticalPitch` so x is the pitch-length axis (0-23.32m) and y is the width axis (0-68m), consistent with ViewTransformer vertex definitions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed bbox_inches='tight' to fix PNG width compression**
- **Found during:** Task 1 (TDD GREEN — test_heatmap_dimensions failure)
- **Issue:** Plan specified `bbox_inches='tight'` in savefig call. With the custom pitch aspect ratio (23.32:68 = 0.343), matplotlib's tight bounding box cropped the 12-inch figure to ~3.25 inches, producing a 325px-wide PNG instead of the expected 1200px.
- **Fix:** Removed `bbox_inches='tight'` parameter. figsize=(12,8) at dpi=100 now saves exactly 1200x800px.
- **Files modified:** generate_heatmaps.py
- **Verification:** test_heatmap_dimensions passes with w=1200, h=800
- **Committed in:** 9e2857e (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Fix necessary to meet the "approximately 1200x800 pixels" acceptance criterion. No scope creep.

## Issues Encountered
- mplsoccer not previously installed — installed via `pip install mplsoccer` (1.6.1) during task execution, added to requirements.txt.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- generate_heatmaps.py is ready to run on any positions.json produced by Plan 01 (export_positions)
- Command: `python generate_heatmaps.py --positions output_videos/<stem>_positions.json`
- Phase 3 demo site can consume the output PNGs directly from output_videos/

---
*Phase: 02-data-export-and-video-processing*
*Completed: 2026-03-17*
