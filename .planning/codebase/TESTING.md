# Testing Patterns

**Analysis Date:** 2026-03-16

## Test Framework

**Runner:**
- None — no test framework is installed or configured
- No `pytest`, `unittest`, `nose`, or any test runner present in `requirements.txt`
- No `pytest.ini`, `setup.cfg`, `tox.ini`, or `pyproject.toml` test configuration found

**Assertion Library:**
- None

**Run Commands:**
```bash
# No test commands exist. There are no tests to run.
```

## Test File Organization

**Location:**
- No test files exist anywhere in the project
- No `tests/` directory
- No `test_*.py` or `*_test.py` files
- No test fixtures or factories

**Naming:**
- No naming convention established — no tests to observe

## Test Structure

No test structure exists. The project has zero automated tests.

## Mocking

**Framework:** None

No mocking infrastructure exists. The codebase has no test doubles, stubs (in the testing sense — the `stubs/` directory contains pickle caches of inference results for development speed, not test mocks), or fixtures.

## Fixtures and Factories

**Test Data:**
- None for testing purposes
- `stubs/tracks_stubs.pkl` and `stubs/camera_movement_stubs.pkl` are pickle-serialized inference outputs used as development caches via `--use-stubs` CLI flag, not test fixtures

**Location:**
- `stubs/` — development caches only, not a test fixture directory

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# Coverage tooling not configured. Install and configure pytest-cov to begin:
# pip install pytest pytest-cov
# pytest --cov=. --cov-report=html
```

## Test Types

**Unit Tests:**
- Not present. Candidates for unit testing include:
  - `utils/bbox_utils.py` — pure functions with no dependencies (`get_center_of_bbox`, `measure_distance`, `get_foot_position`)
  - `utils/video_utils.py` — `get_video_info`, `save_video`
  - `team_assigner/team_assigner.py` — `get_player_team` team ID logic
  - `main.py::generate_stats` — pure function, easily testable with mock track data

**Integration Tests:**
- Not present. End-to-end pipeline in `main.py` is only validated by manual execution.

**E2E Tests:**
- Not used

## Manual Validation Approach

The project uses manual inspection and development caches as its sole validation mechanism:

1. **Stub caching** (`--use-stubs` flag): Re-runs the annotation and stats pipeline on cached YOLO detections without re-running inference. Located at `stubs/tracks_stubs.pkl` and `stubs/camera_movement_stubs.pkl`.

2. **Visual inspection**: Annotated output video is reviewed manually.

3. **Stats JSON**: Output JSON at `<output>_stats.json` is inspected manually for sanity checking possession percentages, speed values, and player counts.

4. **Exploratory notebooks**: `development_and_analysis/color_assignment.ipynb` and `training/football_training_yolo_v5.ipynb` are Jupyter notebooks used for interactive development, not automated validation.

5. **Standalone inference script**: `Stat tracker/yolo_inference.py` runs YOLO directly with hardcoded absolute paths — a one-off development script, not a test.

## Adding Tests (Recommended Starting Point)

To introduce testing, the following setup is recommended:

```bash
pip install pytest pytest-cov
```

Place tests in a `tests/` directory at project root. Start with pure utility functions:

```python
# tests/test_bbox_utils.py
from utils.bbox_utils import get_center_of_bbox, measure_distance, get_foot_position

def test_get_center_of_bbox():
    assert get_center_of_bbox([10, 20, 30, 40]) == (20, 30)

def test_measure_distance():
    assert measure_distance((0, 0), (3, 4)) == 5.0

def test_get_foot_position():
    assert get_foot_position([10, 20, 30, 40]) == (20, 40)
```

Then test `generate_stats` in `main.py` with synthetic track data before moving to component-level tests requiring mocked YOLO/supervision dependencies.

---

*Testing analysis: 2026-03-16*
