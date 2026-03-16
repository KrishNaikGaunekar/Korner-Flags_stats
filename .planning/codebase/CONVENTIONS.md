# Coding Conventions

**Analysis Date:** 2026-03-16

## Naming Patterns

**Files:**
- Module files match their class name in snake_case: `tracker.py` contains `Tracker`, `team_assigner.py` contains `TeamAssigner`
- Utility modules are named by function group: `bbox_utils.py`, `video_utils.py`
- `__init__.py` in every package exports the primary class with a single `from .module import ClassName` line
- Duplicate/stale init files exist with typos: `__innit__.py` (not `__init__.py`) in `speed_and_distnace_estimator/` and `view_transformer/`; `_init.py` in `team_assigner/` — these are inert artifacts, not imported
- Module directory name contains a typo: `speed_and_distnace_estimator/` (misspelled "distance") — match exactly when importing

**Classes:**
- PascalCase: `Tracker`, `TeamAssigner`, `PlayerBallAssigner`, `CameraMovementEstimator`, `ViewTransformer`, `SpeedAndDistanceEstimator`
- Class name matches module file name (PascalCase vs snake_case)

**Functions and Methods:**
- snake_case: `get_object_tracks`, `assign_ball_to_player`, `draw_annotations`, `add_speed_and_distance_to_tracks`
- Getter methods prefixed with `get_`: `get_camera_movement`, `get_player_team`, `get_player_color`, `get_clustering_model`
- Drawing methods prefixed with `draw_`: `draw_annotations`, `draw_ellipse`, `draw_triangle`, `draw_team_ball_control`, `draw_camera_movement`, `draw_speed_and_distance`
- Mutation methods prefixed with `add_`: `add_position_to_track`, `add_adjust_position_to_tracks`, `add_transformered_position_to_tracks`, `add_speed_and_distance_to_tracks`
- Utility functions are module-level (not in classes): `get_center_of_bbox`, `get_bbox_width`, `measure_distance`, `measure_xy_distance`, `get_foot_position`, `read_video`, `save_video`, `get_video_info`

**Variables:**
- snake_case throughout: `frame_num`, `track_id`, `ball_bbox`, `camera_movement_per_frame`
- Loop iteration variables commonly use short descriptive names: `frame_num`, `track_id`, `player_id`, `object`, `cls_id`
- Accumulated output typically named `output_frames` or `output_video_frames`

**Parameters:**
- Consistent naming across modules: `frame`, `frames`, `bbox`, `tracks`, `stub_path`, `read_from_stub`

## Code Style

**Formatting:**
- No formatter config present (no `.prettierrc`, `pyproject.toml`, `.flake8`, `setup.cfg`)
- Indentation: 4 spaces
- Inconsistent spacing around operators and after commas in some files (e.g., `batch_size=20` no spaces, `n_init=10` no spaces in keyword args)
- Blank lines between methods: 1-2 lines, inconsistent
- Trailing whitespace present in some files

**Linting:**
- No linting config detected (no `.flake8`, `.pylintrc`, `ruff.toml`)
- Type hints are absent throughout the codebase — no function signatures use `->` return types or parameter annotations

## Import Organization

**Order (observed pattern):**
1. Standard library: `os`, `sys`, `pickle`, `json`
2. Third-party: `cv2`, `numpy`, `pandas`, `ultralytics`, `supervision`, `sklearn`
3. Local: `from utils import ...`, `from trackers import ...`

**Path Handling:**
- Submodules use `sys.path.append('../')` before local imports as a workaround for running scripts directly: present in `trackers/tracker.py`, `player_ball_assigner/player_ball_assigner.py`, `speed_and_distnace_estimator/speed_and_distance_estimator.py`
- When imported as packages from `main.py`, the `sys.path.append` calls are harmless but unnecessary
- `main.py` uses clean package imports without path manipulation

**Path Aliases:**
- None configured — no `pyproject.toml` or `setup.py` defines installable package paths

## Error Handling

**Patterns:**
- Minimal explicit error handling throughout the codebase
- `main.py` uses early-return guards with `print(f"Error: ...")` for missing input file and empty frame list
- `save_video` in `utils/video_utils.py` prints a warning and returns early when no frames are present
- No exceptions are raised or caught in module classes — failures propagate as unhandled exceptions
- Null/missing data handled by sentinel values: `-1` for no player assigned (`player_ball_assigner.py`), `None` for missing positions (`view_transformer.py`), `{}` for missing bbox (`tracker.py` interpolation)
- `stub_path` reads use `os.path.exists()` guard before opening files

## Logging

**Framework:** `print()` only — no logging library used

**Patterns:**
- Progress steps announced in `main.py` with descriptive `print()` statements: `"Reading video frames..."`, `"Estimating camera movement..."`, etc.
- Warnings use `print("Warning: ...")` prefix (e.g., in `save_video`)
- Errors use `print("Error: ...")` prefix (e.g., in `main()`)
- No logging in module classes — silent operation

## Comments

**When to Comment:**
- Inline comments explain non-obvious algorithmic steps: `#interpolate missing values`, `#Convert goalkeeper to player object`, `#track objects`
- Docstrings used selectively on functions with non-obvious behavior: `generate_stats`, `get_video_info`, `save_video`, `ViewTransformer.__init__`
- `draw_team_ball_control` has a one-line docstring: `"""Draw possession overlay — position scales to any resolution."""`
- Most methods have no docstring

**Comment Style:**
- Inline comments use `#` with a space: `# Draw players`, `# Get video metadata`
- Some comments lack the space after `#`: `#reshape image in 2d array of pixels`, `#interpolate missing values`

## Function Design

**Size:** Methods are generally focused (10–40 lines). `get_object_tracks` in `trackers/tracker.py` is the largest at ~55 lines; the possession-smoothing loop in `main.py` is ~30 lines inline (not extracted to a function).

**Parameters:** Methods accept concrete objects rather than primitives where possible (e.g., `tracks` dict, `frame` numpy array). Magic numbers appear inline in drawing methods (e.g., `rectangle_width = 40`, `rectangle_height = 20`, `consecutive_frames_threshold = 15` in `main.py`).

**Return Values:** Drawing methods consistently return the modified frame or frames list. Mutating methods (`add_*`) return `None` and modify `tracks` in-place.

## Module Design

**Exports:**
- Each package exports exactly one class via `__init__.py`
- `utils/__init__.py` exports all utility functions flat: `from .video_utils import ...`, `from .bbox_utils import ...`

**Barrel Files:**
- Every module directory has an `__init__.py` that re-exports its primary symbol
- Consumers import from the package name: `from trackers import Tracker`, `from utils import read_video`

**Class Instantiation Pattern:**
- All major components are instantiated in `main.py` and passed data; no dependency injection or factory pattern
- Classes hold state (e.g., `TeamAssigner` caches `players_team_dict`; `Tracker` holds `self.model` and `self.tracker`)

---

*Convention analysis: 2026-03-16*
