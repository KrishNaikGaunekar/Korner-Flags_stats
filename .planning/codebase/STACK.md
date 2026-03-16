# Technology Stack

**Analysis Date:** 2026-03-16

## Languages

**Primary:**
- Python 3.11.9 - All application code, ML inference, video processing

## Runtime

**Environment:**
- Python 3.11.9

**Package Manager:**
- pip
- Lockfile: Not present (requirements.txt with version constraints only)

## Frameworks

**Core:**
- `ultralytics>=8.0.0` - YOLO object detection (player, referee, ball inference); loaded via `YOLO(model_path)` in `trackers/tracker.py`
- `supervision>=0.18.0` - ByteTrack multi-object tracking (`sv.ByteTrack`), detection format conversion (`sv.Detections.from_ultralytics`) in `trackers/tracker.py`

**Testing:**
- None detected

**Build/Dev:**
- None detected (no build pipeline; run directly via `python main.py`)

## Key Dependencies

**Critical:**
- `ultralytics>=8.0.0` - YOLO model loading and batch frame inference (batch size 20); the YOLO weights file `Models/best.pt` is required at runtime
- `supervision>=0.18.0` - ByteTrack tracker state, detection-to-tracks conversion; tightly coupled with ultralytics output format
- `opencv-python-headless>=4.8.0` - Video I/O (`cv2.VideoCapture`, `cv2.VideoWriter` with XVID codec), optical flow (`cv2.calcOpticalFlowPyrLK`, `cv2.goodFeaturesToTrack`), perspective transform (`cv2.getPerspectiveTransform`, `cv2.perspectiveTransform`), and all annotation drawing
- `scikit-learn>=1.3.0` - KMeans clustering (`n_clusters=2, init="k-means++"`) for jersey color team classification in `team_assigner/team_assigner.py`
- `numpy>=1.24.0` - Array operations throughout all modules; used directly for perspective vertices, track arrays, and possession frame counting
- `pandas>=2.0.0` - Ball position interpolation via `DataFrame.interpolate()` + `bfill()` in `trackers/tracker.py`

**Infrastructure:**
- `pickle` (stdlib) - Caching detection results and camera movement vectors to `.pkl` stub files in `stubs/`

## Configuration

**Environment:**
- No environment variables required; all configuration is passed via CLI arguments
- Key CLI args: `--input` (required), `--output`, `--model` (default: `models/best.pt`), `--confidence` (default: 0.1), `--use-stubs`, `--stats-output`

**Build:**
- `requirements.txt` - Sole dependency specification; no `pyproject.toml`, `setup.py`, or `Pipfile`

## Platform Requirements

**Development:**
- Python 3.11+
- YOLO weights file at `Models/best.pt` (also `Models/last.pt` present)
- Input video in any format supported by OpenCV (mp4, avi, mov, webm)
- Optional: `stubs/` directory with `.pkl` cache files for `--use-stubs` dev mode

**Production:**
- Local execution only — no server, no cloud deployment detected
- Output: annotated `.avi` video (XVID codec) + `_stats.json` written to `output_videos/`
- CPU or GPU (ultralytics will use CUDA if available)

---

*Stack analysis: 2026-03-16*
