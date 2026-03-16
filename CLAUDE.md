# Korner Flags - Soccer Video Analysis

## Project Overview
AI-powered soccer/football video analysis tool. Takes ANY uploaded match video, runs YOLO object detection + ByteTrack tracking, classifies teams by jersey color, estimates speed/distance, and outputs an annotated video with stats overlay.

## How to Run
```bash
# Basic usage — process any video
python main.py --input path/to/match.mp4

# With custom output path
python main.py --input match.mp4 --output results/annotated.avi

# With custom model and confidence
python main.py --input match.mp4 --model models/best.pt --confidence 0.15

# Development mode (use cached stubs from previous runs)
python main.py --input match.mp4 --use-stubs
```

## Output
- Annotated video with player ellipses, ball triangle, team colors, possession overlay
- JSON stats file with possession %, player speeds, distances, video metadata

## Architecture
```
main.py                          — CLI entry point (argparse-based)
trackers/tracker.py              — YOLO detection + supervision ByteTrack + annotation drawing
team_assigner/team_assigner.py   — KMeans jersey color clustering for team classification
player_ball_assigner/            — Ball-to-nearest-player assignment
camera_movement_estimator/       — Optical flow camera pan estimation
view_transformer/                — Perspective transform → real-world coordinates
speed_and_distnace_estimator/    — Player speed (km/h) and distance (m) from transformed coords
utils/video_utils.py             — read_video, save_video, get_video_info
utils/bbox_utils.py              — Geometry helpers (center, width, distance, foot position)
models/                          — YOLO weights (best.pt)
training/                        — Training data and notebook
```

## Key Design Decisions
- **No hardcoded video paths** — all paths come from CLI arguments
- **No hardcoded resolutions** — UI overlays scale to any frame size
- **No hardcoded player IDs** — team assignment is purely color-based
- **FPS read from input video** — speed/distance calculations use actual frame rate
- **View transformer estimates pitch vertices proportionally** from frame dimensions
- **Stats JSON output** — machine-readable alongside the annotated video

## Dependencies
```
ultralytics, supervision, opencv-python-headless, numpy, pandas, scikit-learn
```
Install: `pip install -r requirements.txt`

## Pipeline Flow
1. Read video frames + extract fps/resolution metadata
2. YOLO detect players, referees, ball (batch inference, configurable confidence)
3. ByteTrack assign persistent IDs across frames
4. Optical flow estimate camera pan movement
5. Perspective transform positions to real-world meters
6. Interpolate missing ball positions
7. KMeans cluster jersey colors → team assignment
8. Assign ball possession with 15-frame smoothing threshold
9. Calculate speed (km/h) and distance (m) per player
10. Draw annotations: ellipses, triangles, possession overlay, speed/distance labels
11. Save annotated video + stats JSON

## Product Documentation
- PRD: docs/Korner-Flags-PRD.docx (full product requirements)
