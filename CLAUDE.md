# Korner Flag - Soccer Video Analysis Project

## Project Overview
Soccer/football video analysis tool using YOLO for object detection. Tracks players, ball, referees, and calculates possession, speed, distance, and camera movement.

## Key Files Structure
- `main.py` - Entry point
- `trackers/tracker.py` - YOLO tracking and drawing annotations
- `camera_movement_estimator/` - Estimates camera pan/movement
- `view_transformer/` - Perspective transformation for real-world coordinates
- `speed_and_distnace_estimator/` - Speed and distance calculations (note: folder name has typo "distnace")
- `utils/` - Helper functions (bbox_utils, video_utils)
- `team_assigner/` - Team color assignment
- `player_ball_assigner/` - Ball possession assignment

## Known Issues / Bugs Fixed in Session

### 1. Misspelled `__init__.py` files
Several packages had `__innit__.py` instead of `__init__.py`:
- `view_transformer/__innit__.py` (created proper `__init__.py`)
- `speed_and_distnace_estimator/__innit__.py` (created proper `__init__.py`)

### 2. tracker.py
- `draw_team_ball_control` was called with wrong argument order on line ~198
- `get_foot_position` was imported but didn't exist - removed from import
- `add_position_to_track` had variable shadowing bug (`track` parameter shadowed by loop variable)

### 3. camera_movement_estimator.py
- `max_corners` should be `maxCorners` (OpenCV parameter)
- List init `[[0,0]] * len(frames)` creates shared references - use list comprehension
- For loop syntax `for i in (new,old) in enumerate(...)` was invalid
- `return output_frames` was inside the loop (draw_camera_movement method)
- Parameter name mismatch in `add_adjust_position_to_tracks`

### 4. view_transformer.py
- **Line 14 bug**: `self.pixel_verticies = self.target_verticies.astype(np.float32)` should be `self.target_verticies = ...` (FIXED)
- **Line 38 bug**: Calls non-existent `self.transform_position()` - should be removed (FIXED)
- **Polygon boundary check**: Removed `pointPolygonTest` check that rejected players outside pitch quadrilateral - now all players get stats (FIXED)

### 5. speed_and_distance_estimator.py
- `__innit__` should be `__init__`
- Inconsistent indentation (mixed 3 and 4 spaces)
- `position - list(position)` should be `position = list(position)`
- Logic bug: `if start_position is not None and end_position is not None: continue` should use `is None or is None`

### 6. utils/bbox_utils.py
- Added missing `get_foot_position(bbox)` function - returns bottom center (x_center, y2)

## Possession Smoothing
`main.py` line ~40: `consecutive_frames_threshold = 15` (increased from 5) to prevent possession flickering during goalkeeper kicks.

## Remaining Fixes Needed
None - all bugs have been fixed.

### Additional Bugs Fixed
- `speed_and_distnace_estimator/speed_and_distance_estimator.py` lines 19 & 59: Changed `'referee'` to `'referees'` (key mismatch with tracker)
- `main.py` line 96: Added return value capture for `draw_speed_and_distance()`
