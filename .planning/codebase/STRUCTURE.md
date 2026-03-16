# Codebase Structure

**Analysis Date:** 2026-03-16

## Directory Layout

```
Korner flag/                          # Project root
├── main.py                           # CLI entry point — sequences the full pipeline
├── requirements.txt                  # Python dependencies
├── CLAUDE.md                         # Project documentation for AI assistant
│
├── trackers/                         # YOLO detection + ByteTrack + annotation drawing
│   ├── __init__.py
│   └── tracker.py
│
├── team_assigner/                    # KMeans jersey color clustering
│   ├── __init__.py
│   └── team_assigner.py
│
├── player_ball_assigner/             # Nearest-player ball possession assignment
│   ├── __init__.py
│   └── player_ball_assigner.py
│
├── camera_movement_estimator/        # Optical flow camera pan estimation
│   ├── __init__.py
│   └── camera_movement_estimator.py
│
├── view_transformer/                 # Perspective transform to real-world meters
│   ├── __init__.py
│   └── view_transformer.py
│
├── speed_and_distnace_estimator/     # Speed (km/h) and distance (m) per player
│   ├── __init__.py
│   └── speed_and_distance_estimator.py
│
├── utils/                            # Shared pure helpers
│   ├── __init__.py
│   ├── video_utils.py                # read_video, save_video, get_video_info
│   └── bbox_utils.py                 # Geometry: center, width, distance, foot position
│
├── Models/                           # YOLO model weights (not source code)
│   ├── best.pt                       # Primary model used by default
│   └── last.pt                       # Last checkpoint from training
│
├── stubs/                            # Pickle cache for expensive computation steps
│   ├── tracks_stubs.pkl              # Cached YOLO+ByteTrack output
│   └── camera_movement_stubs.pkl     # Cached optical flow output
│
├── Input video/                      # Sample/test input videos
│   └── 08fd33_4.mp4
│
├── output_videos/                    # Generated outputs (annotated video + stats JSON)
│   ├── 08fd33_4_annotated.avi
│   ├── 08fd33_4_annotated_stats.json
│   └── output_video.avi
│
├── training/                         # YOLO training data and notebook
│   ├── football_training_yolo_v5.ipynb
│   ├── yolov5lu.pt
│   ├── yolov5xu.pt
│   └── football-players-detection-1/ # Labelled dataset (train/valid/test splits)
│
├── development_and_analysis/         # Exploratory notebooks
│   └── color_assignment.ipynb
│
├── Stat tracker/                     # Standalone ad-hoc inference script (dev only)
│   └── yolo_inference.py
│
├── runs/                             # YOLO auto-generated detection output (not committed intent)
│   └── detect/
│
├── docs/                             # Product documentation
│   └── Korner-Flags-PRD.docx
│
└── .venv/                            # Python virtual environment (not committed)
```

## Directory Purposes

**`trackers/`:**
- Purpose: Core detection and tracking — the heaviest module in the pipeline
- Contains: YOLO model wrapper, supervision ByteTrack integration, all drawing primitives (ellipse, triangle, possession overlay)
- Key files: `trackers/tracker.py`

**`team_assigner/`:**
- Purpose: Unsupervised jersey color clustering to separate two teams without hardcoded IDs
- Contains: KMeans fitting on first frame; per-frame team prediction with caching
- Key files: `team_assigner/team_assigner.py`

**`player_ball_assigner/`:**
- Purpose: Determine which player controls the ball each frame using foot-point proximity
- Contains: Single class, single method — `assign_ball_to_player(players, ball_bbox)`
- Key files: `player_ball_assigner/player_ball_assigner.py`

**`camera_movement_estimator/`:**
- Purpose: Compensate for camera panning so player positions are relative to the pitch, not the camera
- Contains: Lucas-Kanade optical flow using narrow left/right edge masks; draws camera movement overlay
- Key files: `camera_movement_estimator/camera_movement_estimator.py`

**`view_transformer/`:**
- Purpose: Map pixel coordinates to real-world pitch meters via homographic transform
- Contains: Auto-derives 4 pitch corner vertices from frame dimensions using calibrated ratios; supports manual override
- Key files: `view_transformer/view_transformer.py`

**`speed_and_distnace_estimator/`:**
- Purpose: Calculate player speed and cumulative distance using transformed (real-world) coordinates
- Contains: 5-frame sliding window calculation; draws speed/distance labels on frames
- Key files: `speed_and_distnace_estimator/speed_and_distance_estimator.py`
- Note: Directory name contains a typo (`distnace`) — matches the package import in `main.py`

**`utils/`:**
- Purpose: Pure functions shared across all modules; no business logic
- Contains: Video I/O (`read_video`, `save_video`, `get_video_info`) and geometry helpers (`get_center_of_bbox`, `measure_distance`, `get_foot_position`, etc.)
- Key files: `utils/video_utils.py`, `utils/bbox_utils.py`

**`Models/`:**
- Purpose: Storage for trained YOLO weights
- Contains: `.pt` files; not Python packages
- Key files: `Models/best.pt` (used by default unless overridden with `--model`)

**`stubs/`:**
- Purpose: Development speed — cache expensive YOLO and optical flow results to pickle files
- Contains: `.pkl` binaries; loaded only when `--use-stubs` flag is passed
- Generated: Yes, by the pipeline itself on first run with stub path set

**`output_videos/`:**
- Purpose: Default output directory for annotated video and stats JSON
- Generated: Yes, created automatically by `main.py` if absent
- Committed: Sample outputs are committed; routine run outputs should be gitignored

**`training/`:**
- Purpose: YOLO fine-tuning materials — labelled dataset and training notebook
- Contains: Roboflow-format dataset with train/valid/test splits, Jupyter notebook
- Generated: No (source data)

**`development_and_analysis/`:**
- Purpose: Exploratory analysis notebooks, not part of the production pipeline
- Key files: `development_and_analysis/color_assignment.ipynb`

**`Stat tracker/`:**
- Purpose: Ad-hoc standalone YOLO inference script for development/debugging
- Contains: `yolo_inference.py` with hardcoded absolute paths — not for production use

## Key File Locations

**Entry Points:**
- `main.py`: Primary CLI entry point for the full pipeline

**Configuration:**
- `requirements.txt`: All Python dependencies
- `CLAUDE.md`: Project conventions and run instructions

**Core Logic:**
- `trackers/tracker.py`: YOLO inference, ByteTrack, all frame drawing
- `team_assigner/team_assigner.py`: Team classification via KMeans
- `camera_movement_estimator/camera_movement_estimator.py`: Optical flow camera compensation
- `view_transformer/view_transformer.py`: Perspective transform calibration and application
- `speed_and_distnace_estimator/speed_and_distance_estimator.py`: Speed/distance computation
- `player_ball_assigner/player_ball_assigner.py`: Ball possession assignment

**Shared Utilities:**
- `utils/video_utils.py`: Video read/write/metadata
- `utils/bbox_utils.py`: Bounding box geometry helpers

**Model Weights:**
- `Models/best.pt`: Primary YOLO weights (default when running `python main.py`)

**Development Cache:**
- `stubs/tracks_stubs.pkl`: Cached detection/tracking output
- `stubs/camera_movement_stubs.pkl`: Cached optical flow output

## Naming Conventions

**Files:**
- Module source files use `snake_case.py` (e.g., `team_assigner.py`, `video_utils.py`)
- One class per file; filename matches the class name in snake_case

**Directories:**
- Module packages use `snake_case` and match the class they contain (e.g., `team_assigner/`, `trackers/`)
- Exception: `Stat tracker/` uses a space and capital — legacy/ad-hoc directory
- Exception: `Models/`, `Input video/`, `output_videos/` — non-code asset directories

**Classes:**
- `PascalCase` (e.g., `Tracker`, `TeamAssigner`, `PlayerBallAssigner`, `ViewTransformer`, `SpeedAndDistanceEstimator`)

**Methods:**
- `snake_case`; pipeline stage methods follow the pattern `add_*_to_tracks()` or `get_*()` or `draw_*()`

**Package `__init__.py`:**
- Each module package exports its primary class directly: `from .tracker import Tracker`

## Where to Add New Code

**New pipeline stage (e.g., offside detection):**
- Create a new directory: `offside_detector/`
- Add `__init__.py` exporting the class
- Add implementation: `offside_detector/offside_detector.py`
- Integrate in `main.py` following the existing instantiate → `add_*_to_tracks()` pattern

**New utility function (geometry or I/O):**
- Add to `utils/bbox_utils.py` (geometry) or `utils/video_utils.py` (I/O)
- Export from `utils/__init__.py`

**New annotation / drawing:**
- Add a `draw_*()` method to `trackers/tracker.py` (player/ball annotations) or to the relevant estimator class (overlay text)
- Call the new draw method in the annotation sequence at the bottom of `main()`

**New CLI argument:**
- Add `parser.add_argument(...)` in `parse_args()` in `main.py`
- Pass via `args` into the relevant component at instantiation or call time

**New stats output field:**
- Add to the dict returned by `generate_stats()` in `main.py`

## Special Directories

**`.venv/`:**
- Purpose: Python virtual environment
- Generated: Yes
- Committed: No (`.venv/.gitignore` excludes it)

**`runs/`:**
- Purpose: Auto-generated by YOLO `predict(..., save=True)` when using `Stat tracker/yolo_inference.py`
- Generated: Yes
- Committed: No (should be gitignored; currently present as artifact)

**`.planning/`:**
- Purpose: GSD planning and codebase analysis documents
- Generated: Yes, by AI analysis tools
- Committed: Yes

---

*Structure analysis: 2026-03-16*
