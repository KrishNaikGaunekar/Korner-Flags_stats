# External Integrations

**Analysis Date:** 2026-03-16

## APIs & External Services

None detected. The pipeline runs entirely offline. No HTTP clients, API keys, or cloud SDKs are imported anywhere in the codebase.

## Data Storage

**Databases:**
- None. All data is in-memory during a pipeline run.

**File Storage:**
- Local filesystem only
  - Input: any video path via `--input` CLI arg
  - Output video: `output_videos/<name>_annotated.avi` (XVID-encoded via `cv2.VideoWriter`)
  - Output stats: `output_videos/<name>_annotated_stats.json` (plain JSON, written in `main.py`)
  - Dev cache (stubs): `stubs/tracks_stubs.pkl` and `stubs/camera_movement_stubs.pkl` (Python pickle format, read/written in `trackers/tracker.py` and `camera_movement_estimator/camera_movement_estimator.py`)

**Caching:**
- File-based pickle cache via `--use-stubs` flag. Bypasses YOLO inference and optical flow on repeat runs. Not suitable for production use.

## Authentication & Identity

**Auth Provider:**
- None. No user accounts, sessions, or auth of any kind.

## ML Model Files

**YOLO Weights (local):**
- `Models/best.pt` - Primary model loaded at runtime by `Tracker.__init__()` in `trackers/tracker.py`
- `Models/last.pt` - Alternate weights present (not loaded by default)
- `training/yolov5lu.pt`, `training/yolov5xu.pt` - Training-phase base weights
- Model classes detected: `player`, `goalkeeper` (remapped to `player`), `referee`, `ball`

**Training Artifacts:**
- `training/football_training_yolo_v5.ipynb` - Jupyter notebook for model training
- `training/football-players-detection-1/` - Training dataset directory

## Monitoring & Observability

**Error Tracking:**
- None. Errors surface as Python exceptions or `print()` messages to stdout.

**Logs:**
- `print()` statements only, written to stdout during pipeline execution. No structured logging.

## CI/CD & Deployment

**Hosting:**
- Local machine execution only. No deployment target detected.

**CI Pipeline:**
- None detected. No `.github/`, `.gitlab-ci.yml`, or equivalent.

## Environment Configuration

**Required env vars:**
- None

**Secrets location:**
- No secrets required. No `.env` files present.

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-03-16*
