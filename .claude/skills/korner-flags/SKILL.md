# Korner Flags — Project Knowledge Skill

## Pipeline Order (must follow this sequence)
1. `read_video()` → frames + fps/resolution via `get_video_info()`
2. `Tracker.get_object_tracks()` → detections with persistent IDs
3. `CameraMovementEstimator.get_camera_movement()` → per-frame pan delta
4. `CameraMovementEstimator.add_adjust_position_to_tracks()` → camera-corrected positions
5. `ViewTransformer.add_transformed_position_to_tracks()` → real-world meter coordinates
6. `Tracker.interpolate_ball_positions()` → fill missing ball frames
7. `TeamAssigner.assign_team_color()` + `assign_player_team()` → jersey clustering
8. `PlayerBallAssigner.assign_ball_to_player()` → per-frame possession
9. `SpeedAndDistanceEstimator.add_speed_and_distance_to_tracks()` → km/h + meters
10. Drawing: `draw_annotations()`, `draw_camera_movement()`, `draw_speed_and_distance()`, `draw_team_ball_control()`
11. `save_video()` + write `_stats.json`

## Critical Rules
- **Never hardcode video paths** — always use `args.input` / `args.output`
- **Never hardcode resolution** — scale all overlays using `frame.shape`
- **Never hardcode FPS** — use `get_video_info()` result
- **Team 1 = brighter (white) team** — enforced in `team_assigner.py` via HSV value sort
- **Possession smoothing = 15 frames** — `consecutive_frames_threshold = 15` in `main.py`
- **Stubs** — use `--use-stubs` flag during dev to skip rerunning YOLO inference

## Key Libraries
- `ultralytics` — YOLO inference (`YOLO(model_path).track()`)
- `supervision` — ByteTrack (`sv.ByteTrack`), annotation drawers
- `opencv-python-headless` — video I/O, optical flow (`cv2.calcOpticalFlowPyrLK`)
- `scikit-learn` — KMeans for jersey color clustering
- `numpy`, `pandas` — array ops and track dataframes

## Folder Name Quirks
- Speed estimator folder is `speed_and_distnace_estimator/` (typo — "distnace") — do not rename
- Init files: some packages had `__innit__.py` (typo) — all fixed to `__init__.py`

## Debug Checklist
- `KeyError` on tracks dict → check key is `'referees'` not `'referee'`
- Possession flickers → increase `consecutive_frames_threshold`
- Players missing stats → `ViewTransformer` polygon check was removed; all players should get stats
- Speed = 0 for everyone → check `frame_rate` is passed correctly to `SpeedAndDistanceEstimator`
- Output video black → check `save_video()` return value is captured in `main.py`

## CLI Usage
```bash
python main.py --input path/to/match.mp4
python main.py --input match.mp4 --output out/result.avi --confidence 0.15
python main.py --input match.mp4 --use-stubs
python main.py --input match.mp4 --stats-output results/stats.json
```

## Output Files
- `output_videos/<input_stem>_annotated.avi` — annotated video
- `output_videos/<input_stem>_stats.json` — possession %, speeds, distances, metadata
