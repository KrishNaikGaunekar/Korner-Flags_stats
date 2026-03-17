---
phase: 01-pipeline-fixes-and-validation
plan: 03
subsystem: infra
tags: [yolo, ffmpeg, h264, mp4, pipeline-validation, bytetrack]

# Dependency graph
requires:
  - phase: 01-pipeline-fixes-and-validation
    provides: "H.264 MP4 output via ffmpeg, view transformer position key fix, camera movement correction"
provides:
  - "End-to-end pipeline validation on real soccer clip (08fd33_4.mp4)"
  - "H.264 MP4 annotated output with browser-playable faststart encoding"
  - "Stats JSON with possession and player speed/distance data"
  - "User sign-off on YOLO detection quality (pending Task 2)"
affects: [phase-02-web-static-site, phase-03-roboflow-finetuning]

# Tech tracking
tech-stack:
  added: [ffmpeg-8.1 (via winget Gyan.FFmpeg)]
  patterns: []

key-files:
  created: []
  modified: []

key-decisions:
  - "Pipeline validated on 08fd33_4.mp4 (750 frames, 1920x1080, 25fps) using cached stubs for speed"
  - "max_speed_kmh of 268.2 is unrealistically high - perspective transform vertex estimation needs calibration disclaimer"

patterns-established: []

requirements-completed: []  # PIPE-04 pending user sign-off in Task 2

# Metrics
duration: 15min
completed: 2026-03-17
---

# Phase 1 Plan 03: Pipeline Validation Summary

**Full pipeline ran end-to-end on 750-frame soccer clip producing H.264 MP4 with possession stats — awaiting user visual sign-off on YOLO tracking quality**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-17T20:30:00Z
- **Completed:** 2026-03-17 (Task 1 complete; Task 2 at checkpoint)
- **Tasks:** 1 of 2 complete (Task 2 is human-verify checkpoint)
- **Files modified:** 0 source files (pipeline executed with existing code)

## Accomplishments
- Installed ffmpeg 8.1 on the machine (was missing, blocking H.264 output)
- Pipeline ran end-to-end without Python exceptions on `Input video/08fd33_4.mp4`
- Output `output_videos/08fd33_4_annotated.mp4` confirmed H.264 via ffprobe
- Stats JSON generated: team_1=37.9%, team_2=62.1% possession, 42 players detected

## Stats JSON Output

```json
{
  "video": { "fps": 25.0, "resolution": "1920x1080", "total_frames": 750, "duration_seconds": 30.0 },
  "possession": { "team_1_percent": 37.9, "team_2_percent": 62.1 },
  "players": { "total_detected": 42, "max_speed_kmh": 268.2 }
}
```

Note: `max_speed_kmh` of 268.2 is unrealistically high. This is expected given that the perspective transform uses estimated (not calibrated) pitch vertices. A disclaimer should be added to the demo site output.

## Task Commits

1. **Task 1: Run pipeline on available soccer clip** - `0a57961` (chore)
2. **Task 2: User validates YOLO detection quality** - PENDING (checkpoint)

## Files Created/Modified
- None (pipeline execution only; output files are gitignored)

## Decisions Made
- Used `--use-stubs` flag to reuse cached YOLO detections from previous runs, avoiding full YOLO inference re-run
- ffmpeg installed via `winget install Gyan.FFmpeg` (system-level, not Python dependency)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing ffmpeg**
- **Found during:** Task 1 (Run pipeline)
- **Issue:** ffmpeg was not installed on the machine. `save_video()` catches `FileNotFoundError` and falls back to saving a temp AVI, but the acceptance criteria requires H.264 MP4 output confirmed by ffprobe.
- **Fix:** Ran `winget install --id Gyan.FFmpeg` — installed ffmpeg 8.1 full build
- **Files modified:** None (system install)
- **Verification:** `ffprobe` confirmed `codec_name=h264` on output MP4
- **Committed in:** `0a57961` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential for acceptance criteria. No scope creep.

## Issues Encountered
- ffmpeg PATH change from winget requires shell restart. Worked around by using full binary path in the `export PATH` prefix for the pipeline run command.

## User Setup Required
None - ffmpeg is now installed system-wide via winget.

## Next Phase Readiness
- Awaiting user visual confirmation of YOLO detection quality (Task 2 checkpoint)
- If approved: PIPE-04 complete, Phase 2 web static site can begin
- If detection quality is poor (< 80% players tracked): may need Roboflow fine-tuning (adds 1-2 days per existing blocker in STATE.md)

---
*Phase: 01-pipeline-fixes-and-validation*
*Completed: 2026-03-17*
