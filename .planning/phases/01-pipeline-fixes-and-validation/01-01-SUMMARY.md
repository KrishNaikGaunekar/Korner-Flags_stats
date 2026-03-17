---
phase: 01-pipeline-fixes-and-validation
plan: 01
subsystem: pipeline
tags: [opencv, optical-flow, perspective-transform, camera-movement, view-transformer]

# Dependency graph
requires: []
provides:
  - Camera-corrected perspective transform (view_transformer reads position_adjusted)
  - Fixed optical flow feature refresh (camera_movement_estimator correctly resets old_features)
  - Proportional camera mask (adapts to any frame width, not hardcoded 1920px)
  - Clean module init files (no typo __innit__.py or _init.py duplicates)
affects: [02-pipeline-fixes-and-validation, speed-distance-estimation, view-transformation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Proportional mask values derived from frame dimensions, not hardcoded pixel columns"
    - "position_adjusted key is the camera-corrected coordinate consumed downstream by ViewTransformer"

key-files:
  created: []
  modified:
    - view_transformer/view_transformer.py
    - camera_movement_estimator/camera_movement_estimator.py

key-decisions:
  - "Use proportional mask ratios (0.010*w, 0.469*w:0.547*w) derived from original 1920px calibration to support any frame width"
  - "position_adjusted (not position) is the correct key linking camera movement correction to perspective transform"

patterns-established:
  - "Pipeline data flow: position -> add_adjust_position_to_tracks writes position_adjusted -> add_transformered_position_to_tracks reads position_adjusted -> position_transformed"

requirements-completed: [PIPE-01, PIPE-02]

# Metrics
duration: 3min
completed: 2026-03-17
---

# Phase 1 Plan 01: Pipeline Bug Fixes (View Transformer + Camera Movement Estimator) Summary

**Fixed three confirmed pipeline bugs: camera-corrected position ignored by ViewTransformer, optical flow feature refresh silently broken by typo, camera mask hardcoded to 1920px width.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-17T20:25:07Z
- **Completed:** 2026-03-17T20:28:23Z
- **Tasks:** 2
- **Files modified:** 2 modified, 3 deleted

## Accomplishments
- ViewTransformer now reads `position_adjusted` (camera-corrected) instead of `position` (raw), so camera pan compensation actually propagates to speed/distance calculations
- CameraMovementEstimator.get_camera_movement now correctly reassigns `old_features` (was `old_feature`) so optical flow tracking refreshes on movement frames instead of silently accumulating drift
- Camera feature detection mask columns replaced with proportional values (0.010*w, 0.469*w:0.547*w) derived from original 1920px calibration, making the estimator resolution-independent
- Deleted three misspelled init duplicates (`__innit__.py` in view_transformer and speed_and_distnace_estimator, `_init.py` in team_assigner) that could shadow the correct `__init__.py` on case-insensitive filesystems

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix view transformer position key and camera movement estimator typo + mask** - `56e9846` (fix)
2. **Task 2: Delete misspelled init files** - `40f2df3` (chore)

## Files Created/Modified
- `view_transformer/view_transformer.py` - Line 54: changed `position` to `position_adjusted` lookup key
- `camera_movement_estimator/camera_movement_estimator.py` - Fixed `old_feature` typo to `old_features`; replaced hardcoded mask with proportional values; added `h, w = first_frame_grayscale.shape[:2]`
- `view_transformer/__innit__.py` - Deleted (typo duplicate)
- `speed_and_distnace_estimator/__innit__.py` - Deleted (typo duplicate)
- `team_assigner/_init.py` - Deleted (typo duplicate)

## Decisions Made
- Proportional mask ratios (0.010, 0.469, 0.547) were back-calculated from the original hardcoded pixel values (0, 20, 900, 1050) on a 1920px frame; this preserves calibration intent while adapting to any resolution.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Import verification initially failed because numpy/opencv were not installed in the execution environment. Installed dependencies (`pip install numpy opencv-python-headless scikit-learn`) to complete verification. All four module imports passed after installation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- PIPE-01 and PIPE-02 bugs are resolved; pipeline can now correctly propagate camera movement corrections through to speed/distance output
- Ready for plan 01-02 (next pipeline fixes or validation run)
- No blockers introduced by this plan

---
*Phase: 01-pipeline-fixes-and-validation*
*Completed: 2026-03-17*
