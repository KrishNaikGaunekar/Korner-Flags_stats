# Phase 1: Pipeline Fixes and Validation - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix two confirmed bugs (camera movement feature refresh, view transformer reading wrong position key), switch video output from AVI to browser-compatible H.264 MP4, and validate YOLO detection quality on an available soccer clip before any full-clip processing begins. No new features. No site work.

</domain>

<decisions>
## Implementation Decisions

### MP4 encoding toolchain (PIPE-03)
- Install ffmpeg as a system dependency (one-time setup, winget install ffmpeg on Windows)
- `save_video` writes a temp file via OpenCV, then calls ffmpeg subprocess to re-encode to H.264 MP4 with `-movflags +faststart`
- Final output extension changes from `.avi` to `.mp4` everywhere
- Rationale: coaching demo audience needs video that loads instantly in browser; OpenCV alone cannot produce faststart MP4

### Bug fix: view transformer reads wrong position key (PIPE-01)
- `view_transformer.py` line 54: change `track_info.get('position')` to `track_info.get('position_adjusted')`
- This is a one-line fix — no redesign needed
- After fix, camera pan corrections will actually flow into speed/distance calculations

### Bug fix: camera movement feature refresh typo (PIPE-02)
- `camera_movement_estimator.py` line 65: change `old_feature =` to `old_features =`
- This is a one-line fix — no redesign needed
- After fix, optical flow feature points are correctly refreshed on panning frames, preventing drift on long clips

### Camera mask hardcoding — fix bundled with PIPE-02
- Current mask hardcodes pixel columns 900–1050, calibrated only for 1920px-wide video
- Fix: compute mask columns proportionally from actual frame width (e.g. `int(0.469 * w)` to `int(0.547 * w)`)
- Fix while already in that file for PIPE-02

### Stats output path bug — fix bundled with PIPE-03
- Current: `args.output.replace('.avi', '_stats.json')` — produces broken filename once output is `.mp4`
- Fix: use `os.path.splitext(args.output)[0] + '_stats.json'`
- Bundled with the PIPE-03 output path changes

### `__innit__.py` typo cleanup — bundled in Phase 1
- Remove misspelled `__innit__.py` from `view_transformer/` and `speed_and_distnace_estimator/`
- Remove `_init.py` from `team_assigner/`
- Keep only correctly named `__init__.py` in each module
- These are not actively breaking anything now but will cause confusion during Phase 2+ work

### YOLO validation approach (PIPE-04)
- Use any available soccer clip on the machine — not blocked on NC State footage
- NC State footage will be sourced/downloaded before Phase 2 begins
- Validation is manual visual inspection by user: watch the output annotated video and confirm 80%+ of visible players are tracked with persistent IDs across frames
- No automated tracking metric needed
- PIPE-04 is complete when user signs off on detection quality

### Claude's Discretion
- Exact ffmpeg subprocess call flags (beyond H.264 + faststart)
- Whether to write temp file to `output_videos/` or system temp dir before ffmpeg conversion
- How to handle ffmpeg not being installed (error message copy)
- Proportional mask column values (derived from 1920px calibration ratios)

</decisions>

<specifics>
## Specific Ideas

- Demo will be sent as a recorded video walkthrough to coaching staff (not a live upload) — so pipeline reliability matters more than speed
- User will visually inspect annotated output video to validate PIPE-04 — no automated scoring needed

</specifics>

<canonical_refs>
## Canonical References

No external specs beyond what's captured in planning files.

### Requirements
- `.planning/REQUIREMENTS.md` §Pipeline Fixes — PIPE-01 through PIPE-04 definitions and acceptance criteria

### Known bugs and concerns
- `.planning/codebase/CONCERNS.md` §Known Bugs — exact line numbers for the two confirmed bugs
- `.planning/codebase/CONCERNS.md` §Fragile Areas — camera mask hardcoding details (columns 900–1050, frame width assumption)
- `.planning/codebase/CONCERNS.md` §Tech Debt — `__innit__.py` typo file details

### Source files to modify
- `camera_movement_estimator/camera_movement_estimator.py` — line 65 (old_feature typo), lines 17–19 (mask hardcoding)
- `view_transformer/view_transformer.py` — line 54 (position vs position_adjusted)
- `utils/video_utils.py` — `save_video` function (XVID→H.264 MP4 via ffmpeg)
- `main.py` — line 45 (output path default), line 164 (stats path derivation), line 13 (speed_and_distnace_estimator import typo)
- `view_transformer/__innit__.py` — delete
- `speed_and_distnace_estimator/__innit__.py` — delete
- `team_assigner/_init.py` — delete

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `utils/video_utils.py:save_video` — existing function to modify in-place (add ffmpeg subprocess call after OpenCV write)
- `utils/video_utils.py:get_video_info` — already reads frame width/height; pass these to CameraMovementEstimator constructor to drive proportional mask

### Established Patterns
- All CLI paths come from `argparse` in `main.py` — no hardcoded paths to introduce
- `CameraMovementEstimator.__init__` already receives the first frame — frame dimensions are available there for proportional mask calculation
- `ViewTransformer` already accepts `frame_width`/`frame_height` as constructor args (proportional vertices pattern already established) — same pattern should be applied to the mask

### Integration Points
- `main.py:160` — `save_video` call is the insertion point for the ffmpeg encoding step
- `main.py:164` — stats path derivation is the one-line fix location
- `main.py:86` — `add_adjust_position_to_tracks` writes `position_adjusted`; `view_transformer.py:54` must read it — these are the two ends of the PIPE-01 fix

</code_context>

<deferred>
## Deferred Ideas

- Streaming/frame-by-frame pipeline (avoid loading all frames into RAM) — performance concern, not a Phase 1 blocker
- Rename `speed_and_distnace_estimator/` directory to fix the "distnace" typo — requires coordinated import updates across main.py and all consumers; defer to a cleanup phase to avoid scope creep
- `Stat tracker/yolo_inference.py` hardcoded paths — legacy dev script, not part of the pipeline; delete or defer
- Stub write condition bug in CameraMovementEstimator — inverted logic means stubs only written with `--use-stubs`; low priority since stubs are dev-only; defer

</deferred>

---

*Phase: 01-pipeline-fixes-and-validation*
*Context gathered: 2026-03-16*
