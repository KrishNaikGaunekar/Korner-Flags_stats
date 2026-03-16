# Architecture

**Analysis Date:** 2026-03-16

## Pattern Overview

**Overall:** Sequential Pipeline (ETL-style)

**Key Characteristics:**
- All processing happens in a single `main()` function in `main.py` — no web server, no async, no event loop
- Each module is a class that encapsulates one stage of the pipeline and mutates a shared `tracks` dict
- The `tracks` dict is the central data structure passed through every stage; each stage enriches it with new keys
- No inter-module dependencies — all modules import only from `utils/`, not from each other
- Stateless output: results are written to disk (annotated video + JSON stats file)

## Layers

**Entry / CLI Layer:**
- Purpose: Parse arguments, validate input, sequence all pipeline stages, write outputs
- Location: `main.py`
- Contains: `parse_args()`, `main()`, `generate_stats()`
- Depends on: All modules
- Used by: Terminal / shell only

**Detection & Tracking Layer:**
- Purpose: YOLO inference + ByteTrack persistent ID assignment; also handles all drawing/annotation
- Location: `trackers/tracker.py`
- Contains: `Tracker` class with `detect_frames()`, `get_object_tracks()`, `add_position_to_track()`, `interpolate_ball_positions()`, `draw_annotations()`, `draw_ellipse()`, `draw_triangle()`, `draw_team_ball_control()`
- Depends on: `ultralytics`, `supervision`, `utils/bbox_utils.py`
- Used by: `main.py`

**Camera Compensation Layer:**
- Purpose: Lucas-Kanade optical flow to estimate frame-to-frame camera pan; adjusts player positions accordingly
- Location: `camera_movement_estimator/camera_movement_estimator.py`
- Contains: `CameraMovementEstimator` class
- Depends on: `cv2`, `utils/bbox_utils.py`
- Used by: `main.py`

**Coordinate Transformation Layer:**
- Purpose: Homographic perspective transform from pixel space to real-world meters (pitch coordinates)
- Location: `view_transformer/view_transformer.py`
- Contains: `ViewTransformer` class
- Depends on: `numpy`, `cv2`
- Used by: `main.py`

**Team Classification Layer:**
- Purpose: KMeans clustering on jersey pixel colors to assign each player to one of two teams
- Location: `team_assigner/team_assigner.py`
- Contains: `TeamAssigner` class with `assign_teams()`, `get_player_team()`, `get_player_color()`
- Depends on: `sklearn.cluster.KMeans`
- Used by: `main.py`

**Ball Possession Layer:**
- Purpose: Nearest-player assignment with 15-frame smoothing threshold to determine ball possession
- Location: `player_ball_assigner/player_ball_assigner.py`
- Contains: `PlayerBallAssigner` class with `assign_ball_to_player()`
- Depends on: `utils/bbox_utils.py`
- Used by: `main.py`

**Speed & Distance Layer:**
- Purpose: Sliding 5-frame window over transformed coordinates; calculates km/h and cumulative meters per player
- Location: `speed_and_distnace_estimator/speed_and_distance_estimator.py`
- Contains: `SpeedAndDistanceEstimator` class
- Depends on: `utils/bbox_utils.py`
- Used by: `main.py`

**Utility Layer:**
- Purpose: Shared pure functions (video I/O and bbox geometry)
- Location: `utils/video_utils.py`, `utils/bbox_utils.py`
- Contains: `read_video`, `save_video`, `get_video_info`, `get_center_of_bbox`, `get_bbox_width`, `measure_distance`, `measure_xy_distance`, `get_foot_position`
- Depends on: `cv2`, stdlib only
- Used by: All other modules

## Data Flow

**Main Pipeline:**

1. `get_video_info(input)` → `video_info` dict with fps, width, height, total_frames
2. `read_video(input)` → `video_frames` list of numpy arrays (BGR)
3. `Tracker.get_object_tracks(video_frames)` → `tracks` dict: `{"players": [...], "referees": [...], "ball": [...]}`
4. `Tracker.add_position_to_track(tracks)` → adds `position` key (pixel center) to each track entry
5. `CameraMovementEstimator.get_camera_movement(video_frames)` → `camera_movement_per_frame` list
6. `CameraMovementEstimator.add_adjust_position_to_tracks(tracks, ...)` → adds `position_adjusted` key
7. `ViewTransformer.add_transformered_position_to_tracks(tracks)` → adds `position_transformed` key (meters)
8. `Tracker.interpolate_ball_positions(tracks['ball'])` → fills gaps in ball position using pandas interpolation
9. `SpeedAndDistanceEstimator.add_speed_and_distance_to_tracks(tracks)` → adds `speed` (km/h) and `distance` (m) keys
10. `TeamAssigner.assign_teams(frame_0, players_0)` → fits KMeans; `get_player_team()` per frame → adds `team` and `team_color` keys
11. `PlayerBallAssigner.assign_ball_to_player()` per frame → adds `has_ball` key; builds `team_ball_control` array
12. `Tracker.draw_annotations(video_frames, tracks, team_ball_control)` → annotated frames list
13. `CameraMovementEstimator.draw_camera_movement(...)` → adds camera overlay to frames
14. `SpeedAndDistanceEstimator.draw_speed_and_distance(...)` → adds speed/distance labels to frames
15. `save_video(output_frames, output_path, fps)` → writes AVI file
16. `generate_stats(tracks, team_ball_control, video_info)` → writes JSON stats file

**Tracks Data Structure (central state):**
```python
tracks = {
    "players": [
        # one dict per frame
        {
            track_id: {
                "bbox": [x1, y1, x2, y2],
                "position": (cx, cy),              # added by add_position_to_track
                "position_adjusted": (cx, cy),     # added by camera estimator
                "position_transformed": [mx, my],  # added by view transformer (meters)
                "speed": float,                    # km/h, added by speed estimator
                "distance": float,                 # cumulative meters
                "team": int,                       # 1 or 2
                "team_color": ndarray,             # BGR color
                "has_ball": bool,                  # set when player possesses ball
            }
        },
        ...
    ],
    "referees": [...],  # same structure, team/has_ball not set
    "ball": [
        {1: {"bbox": [...]}},  # ball always uses key=1
        ...
    ]
}
```

**State Management:**
- All state lives in `tracks` (mutated in-place by each pipeline stage) and `team_ball_control` (numpy array)
- No global state; all objects are instantiated per-run in `main()`
- Stub files (`stubs/*.pkl`) provide optional caching for slow detection/camera steps during development

## Key Abstractions

**Tracks Dict:**
- Purpose: Central carrier of all per-frame, per-object data throughout the pipeline
- Pattern: List of dicts (one per frame) where each inner dict maps `track_id → attribute dict`; stages add new keys

**Stub / Cache System:**
- Purpose: Skip expensive YOLO inference and optical flow during development
- Files: `stubs/tracks_stubs.pkl`, `stubs/camera_movement_stubs.pkl`
- Pattern: Each expensive method checks `read_from_stub` flag; loads from pickle if stub exists, otherwise computes and optionally saves

**Module-as-Stage Pattern:**
- Each pipeline stage is a class with an `add_*_to_tracks()` method that mutates the tracks dict
- Example: `add_position_to_track`, `add_adjust_position_to_tracks`, `add_transformered_position_to_tracks`, `add_speed_and_distance_to_tracks`

## Entry Points

**CLI Entry Point:**
- Location: `main.py`
- Triggers: `python main.py --input <video>` via argparse
- Responsibilities: Parse args, validate inputs, instantiate all components, sequence pipeline, write video + JSON output

**Ad-hoc Inference Script:**
- Location: `Stat tracker/yolo_inference.py`
- Triggers: Standalone script with hardcoded paths (development/testing only)
- Responsibilities: Run raw YOLO prediction and save detection video to `runs/detect/`

**Development Notebook:**
- Location: `development_and_analysis/color_assignment.ipynb`
- Triggers: Jupyter manually
- Responsibilities: Exploratory analysis of color clustering for team assignment

## Error Handling

**Strategy:** Minimal — mostly print-and-return at the entry point level

**Patterns:**
- `main.py` checks if input file exists and if frames were read; prints error and returns early
- `get_video_info()` falls back to `fps=25.0` if OpenCV returns 0
- `save_video()` prints a warning if no frames are provided
- No try/except blocks in pipeline modules; errors propagate as Python exceptions
- Missing ball positions handled via pandas `interpolate()` + `bfill()` (data-level, not exception-level)

## Cross-Cutting Concerns

**Logging:** `print()` statements in `main.py` only; no logging framework
**Validation:** Input file existence checked in `main.py`; no schema validation on tracks dict
**Authentication:** Not applicable (local CLI tool)
**Resolution Independence:** Frame dimensions read from video metadata and passed to `ViewTransformer` and `draw_team_ball_control` — no hardcoded pixel values in rendering

---

*Architecture analysis: 2026-03-16*
