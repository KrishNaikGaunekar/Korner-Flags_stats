import json
import os
import tempfile
import pytest

from generate_heatmaps import generate_heatmap, load_positions


def _write_positions_json(path, positions):
    data = {
        'fps': 25.0,
        'sample_rate_hz': 1,
        'positions': positions,
    }
    with open(path, 'w') as f:
        json.dump(data, f)


class TestHeatmapGeneration:
    def test_heatmap_files_created(self, tmp_path):
        pos_path = str(tmp_path / 'test_positions.json')
        _write_positions_json(pos_path, [
            {'second': 0, 'player_id': 1, 'x': 10.0, 'y': 30.0, 'team': 1},
            {'second': 0, 'player_id': 2, 'x': 15.0, 'y': 40.0, 'team': 2},
            {'second': 1, 'player_id': 1, 'x': 11.0, 'y': 31.0, 'team': 1},
            {'second': 1, 'player_id': 2, 'x': 16.0, 'y': 41.0, 'team': 2},
        ])
        t1_x, t1_y, t2_x, t2_y = load_positions(pos_path)
        out1 = str(tmp_path / 'test_heatmap_team1.png')
        out2 = str(tmp_path / 'test_heatmap_team2.png')
        generate_heatmap(t1_x, t1_y, 'Team 1', 'Blues', out1)
        generate_heatmap(t2_x, t2_y, 'Team 2', 'Reds', out2)
        assert os.path.exists(out1)
        assert os.path.exists(out2)
        assert os.path.getsize(out1) > 10000  # non-trivial PNG
        assert os.path.getsize(out2) > 10000

    def test_heatmap_dimensions(self, tmp_path):
        import cv2
        out = str(tmp_path / 'dim_test.png')
        import numpy as np
        x = np.array([5.0, 10.0, 15.0, 20.0])
        y = np.array([10.0, 30.0, 50.0, 60.0])
        generate_heatmap(x, y, 'Test', 'Blues', out)
        img = cv2.imread(out)
        h, w = img.shape[:2]
        # 12x8 inches at 100dpi = 1200x800, bbox_inches='tight' may adjust
        assert 600 < w < 1600, f'Width {w} out of expected range'
        assert 400 < h < 1200, f'Height {h} out of expected range'

    def test_heatmap_empty_team(self, tmp_path):
        import numpy as np
        out = str(tmp_path / 'empty_test.png')
        # Empty arrays — should produce pitch-only PNG without error
        generate_heatmap(np.array([]), np.array([]), 'Empty Team', 'Blues', out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 5000  # at least a pitch background
