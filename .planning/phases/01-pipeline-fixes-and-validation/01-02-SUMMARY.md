---
phase: 01-pipeline-fixes-and-validation
plan: 02
subsystem: video-output
tags: [ffmpeg, opencv, h264, mp4, subprocess]

# Dependency graph
requires: []
provides:
  - H.264 MP4 video output with faststart flag via ffmpeg subprocess
  - Browser-compatible annotated video (Chrome, Firefox, Safari without transcoding)
  - Correct stats JSON path derivation via os.path.splitext (extension-agnostic)
affects: [phase-2-web-app, demo-site]

# Tech tracking
tech-stack:
  added: [ffmpeg (system dependency, called via subprocess)]
  patterns: [temp-avi-then-reencode, ffmpeg-subprocess-with-fallback]

key-files:
  created: []
  modified:
    - utils/video_utils.py
    - main.py

key-decisions:
  - "Write frames to temp AVI via OpenCV then re-encode to H.264 MP4 via ffmpeg subprocess — avoids OpenCV's lack of native H.264 support"
  - "Use -movflags +faststart so browser video playback starts immediately without full download"
  - "Normalize output extension to .mp4 inside save_video to guard against callers passing .avi paths"
  - "Use os.path.splitext for stats JSON path derivation so it works regardless of video extension"

patterns-established:
  - "ffmpeg-subprocess-with-fallback: wrap ffmpeg calls in FileNotFoundError + CalledProcessError with actionable install instructions"
  - "temp-file-cleanup: always attempt os.remove on temp files after successful encode, swallow OSError"

requirements-completed: [PIPE-03]

# Metrics
duration: 1min
completed: 2026-03-17
---

# Phase 1 Plan 02: H.264 MP4 Output via ffmpeg Summary

**save_video rewritten to produce browser-compatible H.264 MP4 with faststart via ffmpeg subprocess, replacing XVID/AVI output**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-03-17T20:25:07Z
- **Completed:** 2026-03-17T20:26:05Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- save_video now writes a temp XVID AVI via OpenCV then re-encodes to H.264 MP4 via ffmpeg with -movflags +faststart
- ffmpeg not-found error gives clear install instructions (winget on Windows, brew on macOS) with temp AVI fallback preserved
- Default output extension changed from .avi to .mp4 in main.py argument default and help text
- Stats JSON path derived via os.path.splitext so it works correctly with any video extension, not just .avi

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite save_video to produce H.264 MP4 via ffmpeg** - `5f08a84` (feat)
2. **Task 2: Update main.py default output to .mp4 and fix stats path** - `ff08356` (feat)

## Files Created/Modified
- `utils/video_utils.py` - save_video rewritten with ffmpeg subprocess, temp-AVI-then-reencode pattern, error handling
- `main.py` - default output path changed to .mp4, help text updated, stats path uses os.path.splitext

## Decisions Made
- Used temp AVI + ffmpeg re-encode approach because OpenCV's VideoWriter does not support libx264 directly on all platforms
- -crf 23 and -preset medium chosen as good quality/speed balance for demo output
- -pix_fmt yuv420p included for maximum browser compatibility (Safari requires this)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

ffmpeg must be installed on the system where the pipeline runs. It is called as a subprocess at video save time. If not installed, the pipeline will print a clear error with install instructions and preserve the temp AVI file.

Install commands:
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` or `dnf install ffmpeg`

## Next Phase Readiness
- Pipeline now produces H.264 MP4 files suitable for direct embedding in the demo site
- The -movflags +faststart flag ensures playback starts immediately in browser without full download
- ffmpeg is a new system dependency — must be documented in project setup instructions

---
*Phase: 01-pipeline-fixes-and-validation*
*Completed: 2026-03-17*
