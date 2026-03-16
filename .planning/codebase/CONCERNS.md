# Codebase Concerns

**Analysis Date:** 2026-03-16

## Tech Debt

**`sys.path.append('../')` Hacks in Module Files:**
- Issue: Several modules inject the parent directory into `sys.path` to find `utils`, making them only importable from a specific working directory. This is a path manipulation hack that breaks if modules are imported from a different CWD.
- Files: `trackers/tracker.py` (line 7), `player_ball_assigner/player_ball_assigner.py` (line 2), `speed_and_distnace_estimator/speed_and_distance_estimator.py` (line 2)
- Impact: Running any of these modules directly from their own directories fails. Portable packaging (e.g., as an installable library) is blocked.
- Fix approach: Convert `utils` to a proper package import (e.g., `from utils import ...`) and run everything via `main.py` from the project root, or use relative imports within a top-level package.

**Duplicate `__init__.py` Files with Typos:**
- Issue: Two modules have both a correctly named `__init__.py` and a misspelled `__innit__.py`. The misspelled file is the one Python imports. This is fragile and confusing.
- Files: `speed_and_distnace_estimator/__init__.py` and `speed_and_distnace_estimator/__innit__.py`; `view_transformer/__init__.py` and `view_transformer/__innit__.py`; `team_assigner/__init__.py` and `team_assigner/_init.py`
- Impact: Renaming or removing the typo file would silently break imports. Any new developer adding to `__init__.py` may edit the wrong file.
- Fix approach: Remove the misspelled duplicates, keep only correctly named `__init__.py` in each module.

**Entire `Stat tracker/yolo_inference.py` Contains Hardcoded Absolute Windows Paths:**
- Issue: `yolo_inference.py` contains hardcoded paths (`C:\\Korner flag\\Models\\best.pt`, `C:\\Korner flag\\Input video\\08fd33_4.mp4`) that are machine-specific and reference a specific video file.
- Files: `Stat tracker/yolo_inference.py` (lines 3–9)
- Impact: This script is completely non-portable. It will fail on any machine other than the original developer's. It also hardcodes the input video filename, defeating the CLI generalization in `main.py`.
- Fix approach: Remove or convert this script to use `argparse`-based paths, or delete it as a legacy development artifact.

**Module Directory Named with a Space (`speed_and_distnace_estimator`):**
- Issue: The directory and import name `speed_and_distnace_estimator` contains a typo ("distnace" instead of "distance"). This is embedded in `main.py` imports and the package name.
- Files: `speed_and_distnace_estimator/` directory, `main.py` line 13
- Impact: Every reference to this module carries the typo, making autocomplete and search less reliable. Renaming later will require coordinated changes across all import sites.
- Fix approach: Rename directory to `speed_and_distance_estimator` and update all imports simultaneously.

**KMeans Fit Called Twice in `get_clustering_model`:**
- Issue: `kmeans.fit(image_2d)` is called twice — once via `KMeans(...).fit(image_2d)` and once explicitly on the next line. The second fit restarts clustering from scratch on the same data, wasting CPU time.
- Files: `team_assigner/team_assigner.py` (lines 16–17)
- Impact: Doubles the KMeans computation cost for every player bounding box processed. On a 90-minute video with 22 players, this compounds significantly.
- Fix approach: Remove the redundant `kmeans.fit(image_2d)` call on line 17.

**Stub Write Condition Bug in `CameraMovementEstimator`:**
- Issue: The stub is written only when `read_from_stub=True` (line 70: `if read_from_stub and stub_path is not None`). But `read_from_stub=True` combined with a missing stub (no early return) means the computation runs and then writes — but if `read_from_stub=False`, the stub is never written. This inverts expected behavior where running without stubs should produce stubs for future caching.
- Files: `camera_movement_estimator/camera_movement_estimator.py` (lines 70–72)
- Impact: Stubs for camera movement are only written when `--use-stubs` is passed but the stub file doesn't exist yet. On the second run with `--use-stubs`, the stub is read correctly. But a user who runs once without `--use-stubs`, then re-runs with `--use-stubs`, gets no cached stub. The tracker (`tracker.py` lines 99–101) has the same bug.
- Fix approach: Change the write condition to `if stub_path is not None:` (write whenever a path is provided, regardless of `read_from_stub`).

## Known Bugs

**`old_feature` Variable Silently Unused in Camera Movement Loop:**
- Symptoms: Camera tracking features are re-initialized each frame when movement is detected, but the result is stored in `old_feature` (singular) instead of `old_features` (plural). The loop on the next iteration continues using the original `old_features` from frame 0, ignoring the refresh.
- Files: `camera_movement_estimator/camera_movement_estimator.py` (line 65)
- Trigger: Any video with significant camera panning where feature refresh is intended.
- Workaround: None — the bug means feature points from the first frame are used throughout the entire video, causing camera movement estimation to drift for long clips.

**View Transformer Reads Raw `position`, Not Camera-Adjusted `position_adjusted`:**
- Symptoms: The camera movement correction step writes `position_adjusted` into tracks (line 31 in `camera_movement_estimator.py`), but `ViewTransformer.add_transformered_position_to_tracks` reads `position` (line 54 in `view_transformer.py`). Camera pan corrections are therefore completely ignored in speed/distance calculations.
- Files: `view_transformer/view_transformer.py` (line 54), `camera_movement_estimator/camera_movement_estimator.py` (line 31)
- Trigger: Present in every run. Speed and distance figures are wrong for any video with camera movement.
- Workaround: None currently.

**Team Assignment Uses Only First Frame:**
- Symptoms: `team_assigner.assign_teams(video_frames[0], tracks['players'][0])` trains the KMeans color model on players visible only in frame 0. If few players are visible in frame 0, or if lighting changes drastically between the first frame and the rest of the video, team colors are miscalibrated for the whole video.
- Files: `main.py` (line 107)
- Trigger: Videos that open on a partial view, a close-up, or with fewer than 4–6 players in the first frame.
- Workaround: Manually seek to a frame with full pitch visibility.

**Ball Interpolation Overwrites All Ball Track Data:**
- Symptoms: `interpolate_ball_positions` rebuilds `tracks['ball']` as a list of `{1: {"bbox": x}}` dicts from raw DataFrame rows. Any extra keys stored on ball track entries (future extensions) would be silently dropped.
- Files: `trackers/tracker.py` (lines 18–28)
- Trigger: Present in every run.
- Workaround: Only `bbox` is currently stored on ball entries, so this is latent rather than active.

## Security Considerations

**Unpickling Untrusted Stub Files:**
- Risk: `pickle.load()` is used unconditionally on stub files provided via `--use-stubs`. Pickle deserialization of attacker-controlled files allows arbitrary code execution.
- Files: `trackers/tracker.py` (line 51), `camera_movement_estimator/camera_movement_estimator.py` (line 39)
- Current mitigation: None. Stubs are only used when `--use-stubs` is explicitly passed, which limits exposure to developer workflows.
- Recommendations: Add a warning in help text that stubs should only be loaded from trusted sources. Consider switching to a safer serialization format (JSON, numpy `.npy`) for stubs.

**No Input Video Path Sanitization:**
- Risk: The `--input` path is passed directly to `cv2.VideoCapture`. On systems where ffmpeg URL schemes are supported (e.g., `rtsp://`, `http://`), a user could pass a remote URL rather than a local file, potentially causing unexpected network connections.
- Files: `main.py` (lines 37–38)
- Current mitigation: `os.path.exists(args.input)` check prevents non-existent local paths, but does not block URL-scheme strings which may pass the existence check differently.
- Recommendations: Add a path extension whitelist check or explicitly reject non-local paths.

## Performance Bottlenecks

**Entire Video Loaded into RAM Before Processing:**
- Problem: `read_video()` reads all frames into a Python list before any processing begins. A 90-minute 1080p video at 25fps is approximately 140,000 frames × ~6MB each uncompressed = multi-hundred GB RAM requirement in the worst case. Even short clips can exhaust memory.
- Files: `utils/video_utils.py` (lines 17–26), `main.py` (line 56)
- Cause: Sequential pipeline design requires all frames to be available for detection batching, camera estimation, annotation, and saving.
- Improvement path: Implement frame-by-frame streaming with a sliding window, or at minimum add a `--max-frames` argument to limit processing scope during development.

**KMeans Re-run Per Player Per Frame for Team Classification:**
- Problem: `get_player_team` calls `get_player_color` which runs a full KMeans fit on every invocation for players not yet in `players_team_dict`. For the first occurrence of each player ID, a new KMeans model is trained from the pixel data of their bounding box.
- Files: `team_assigner/team_assigner.py` (lines 11–17, 77–91)
- Cause: No pre-computation of all player colors before team assignment loop.
- Improvement path: Pre-extract all player colors in a batch pass, then call KMeans once for classification. Cache is already in place via `players_team_dict` for subsequent frames.

**Camera Movement Estimation Processes All Frames Serially:**
- Problem: Optical flow is computed frame-by-frame with no parallelism. For long videos, this is a significant sequential bottleneck before any other processing can begin.
- Files: `camera_movement_estimator/camera_movement_estimator.py` (lines 47–68)
- Cause: Sequential loop with no threading or GPU acceleration.
- Improvement path: Use GPU-accelerated optical flow (`cv2.cuda`) or parallelize across frame windows.

## Fragile Areas

**`CameraMovementEstimator` Mask is Hardcoded to Pixel Columns 900–1050:**
- Files: `camera_movement_estimator/camera_movement_estimator.py` (lines 18–19)
- Why fragile: The feature mask `mask_features[:,900:1050] = 1` is hardcoded to a pixel column range calibrated for 1920-wide video. For any video narrower than 1050px (e.g., 720p portrait, 640px wide clips), this slice is out of bounds or covers the wrong region. The left-column mask `[:,0:20]` is similarly calibrated for 1920-wide video.
- Safe modification: Pass mask regions as constructor parameters derived from `frame_width`, similar to how `ViewTransformer` now uses proportional coordinates.
- Test coverage: None.

**Possession Smoothing Threshold is a Magic Number:**
- Files: `main.py` (line 119)
- Why fragile: `consecutive_frames_threshold = 15` is hardcoded and not exposed as a CLI parameter. For videos at 50fps or 60fps, 15 frames is 0.25 seconds; at 24fps it is 0.6 seconds. The effective sensitivity of the possession tracker varies silently with frame rate.
- Safe modification: Derive threshold from video FPS (e.g., `int(fps * 0.5)` for 0.5-second smoothing) or expose as `--possession-threshold` CLI argument.
- Test coverage: None.

**Ball Detection Hardcoded to Track ID 1:**
- Files: `trackers/tracker.py` (line 97), `trackers/tracker.py` (line 19), `main.py` (line 122)
- Why fragile: Ball track entries are always stored under key `1` regardless of what ByteTrack assigns. If multiple ball-class detections occur (e.g., a second ball enters frame), only the last one is kept, silently overwriting. All downstream ball lookups use `.get(1, {})` which will fail silently if ByteTrack assigns any other ID.
- Safe modification: Store the ball by its actual track ID and update downstream consumers accordingly.
- Test coverage: None.

**Output Path Always Appends `.avi` Extension Regardless of Input:**
- Files: `main.py` (line 45), `main.py` (line 164)
- Why fragile: Default output is always `_annotated.avi` and the stats path is derived by `.replace('.avi', '_stats.json')`. If a user specifies `--output result.mp4`, the stats path becomes `result.mp4_stats.json` (no `.avi` to replace), producing an unexpected filename.
- Safe modification: Use `os.path.splitext` for stats path derivation rather than string replacement.
- Test coverage: None.

## Scaling Limits

**Frame-in-RAM Architecture:**
- Current capacity: Dependent on available RAM. A 10-minute 1080p clip at 25fps requires ~15–20GB of RAM for uncompressed frames.
- Limit: Hits OS/Python memory limits well before a full-match video (90 minutes).
- Scaling path: Streaming pipeline with frame batching; process and annotate frames in rolling windows rather than all-at-once.

**Single YOLO Model for All Object Classes:**
- Current capacity: One model (`models/best.pt`) handles players, referees, and ball detection simultaneously.
- Limit: Accuracy is coupled — improving ball detection requires retraining the full model including player/referee classes.
- Scaling path: Separate specialized models per object class, or use a larger backbone for the unified model.

## Dependencies at Risk

**`supervision` Version Floor (`>=0.18.0`) Without Upper Bound:**
- Risk: The `supervision` library has had breaking API changes between minor versions (e.g., `sv.ByteTrack()` constructor signature, `sv.Detections` field names). Unpinned `>=0.18.0` means `pip install` on a new machine may install a newer version that breaks `trackers/tracker.py`.
- Files: `requirements.txt` (line 2)
- Impact: `tracker.py` lines 15, 67, 75 all rely on specific `supervision` API shapes.
- Migration plan: Pin to a tested version range (e.g., `supervision>=0.18.0,<0.25.0`) or lock with `pip freeze` into a `requirements.lock` file.

**`opencv-python-headless` Conflicts with `opencv-python`:**
- Risk: If a user has `opencv-python` (GUI version) installed system-wide, installing `opencv-python-headless` alongside it can cause symbol conflicts. The `requirements.txt` does not document this.
- Files: `requirements.txt` (line 3)
- Impact: Silent runtime errors or import failures depending on which version's shared libraries are loaded.
- Migration plan: Add a comment warning in `requirements.txt` and recommend using the provided `.venv`.

## Missing Critical Features

**No Progress Reporting During Long Processing Steps:**
- Problem: Detection (`detect_frames`), camera movement estimation, and annotation drawing all run silently with no frame-level progress output. On a 5,000-frame video, each step appears hung for minutes.
- Files: `trackers/tracker.py` (lines 38–45), `camera_movement_estimator/camera_movement_estimator.py` (lines 47–68)
- Blocks: User confidence that the process is running; no way to estimate remaining time.

**No Validation That `tracks['players'][0]` Is Non-Empty Before Team Assignment:**
- Problem: `team_assigner.assign_teams(video_frames[0], tracks['players'][0])` calls `KMeans.fit([])` if no players are detected in frame 0, raising a `ValueError` with no helpful error message.
- Files: `main.py` (line 107)
- Blocks: Processing any video where the first frame contains no player detections.

## Test Coverage Gaps

**Zero Automated Tests Exist:**
- What's not tested: Every module — tracking, team assignment, ball assignment, camera movement, perspective transform, speed/distance, video I/O.
- Files: All of `trackers/`, `team_assigner/`, `player_ball_assigner/`, `camera_movement_estimator/`, `view_transformer/`, `speed_and_distnace_estimator/`, `utils/`
- Risk: Any refactor or dependency upgrade can silently break the pipeline with no safety net. The camera movement bug (wrong variable name) and the position pipeline disconnect (raw vs adjusted position) exist precisely because there are no unit tests to catch them.
- Priority: High — `utils/bbox_utils.py` geometry functions and `team_assigner.py` color logic are the easiest starting points for pure-unit tests with no video I/O dependency.

---

*Concerns audit: 2026-03-16*
