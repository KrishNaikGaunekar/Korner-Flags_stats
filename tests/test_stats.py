import numpy as np
import pytest

from main import generate_stats

def _make_tracks(num_frames=75):
    players = []
    for f in range(num_frames):
        frame = {}
        frame[1] = {
            'speed': 5.0 + f * 0.1,  # speeds: 5.0, 5.1, ... 12.4
            'distance': f * 0.5,      # last frame distance = 37.0
            'team': 1,
        }
        frame[3] = {
            'speed': 3.0 if f < 50 else None,  # speed None for last 25 frames
            'distance': f * 0.3 if f < 50 else 14.7,
            'team': 2,
        }
        players.append(frame)
    return {'players': players, 'ball': [{} for _ in range(num_frames)]}

def _make_video_info():
    return {'fps': 25.0, 'width': 1920, 'height': 1080, 'total_frames': 75}

class TestStatsSchema:
    def test_stats_schema(self):
        tracks = _make_tracks()
        tbc = np.array([1] * 40 + [2] * 36)  # 76 entries (frames + 1)
        vi = _make_video_info()
        stats = generate_stats(tracks, tbc, vi)
        assert 'video' in stats
        assert 'possession' in stats
        assert 'players' in stats
        # players must be dict keyed by string player_id
        assert isinstance(stats['players'], dict)
        assert '1' in stats['players']
        assert '3' in stats['players']
        p1 = stats['players']['1']
        assert 'team' in p1
        assert 'distance_m' in p1
        assert 'max_speed_kmh' in p1
        assert 'avg_speed_kmh' in p1
        assert isinstance(p1['team'], int)
        assert isinstance(p1['distance_m'], float)
        assert isinstance(p1['max_speed_kmh'], float)
        assert isinstance(p1['avg_speed_kmh'], float)
        # Old keys must NOT exist
        assert 'total_detected' not in stats['players']
        assert 'distances' not in stats['players']

    def test_stats_speed_calculation(self):
        tracks = _make_tracks()
        tbc = np.array([1] * 76)
        vi = _make_video_info()
        stats = generate_stats(tracks, tbc, vi)
        p1 = stats['players']['1']
        # Player 1 speeds: 5.0, 5.1, ... 12.4 — max = 12.4
        assert abs(p1['max_speed_kmh'] - 12.4) < 0.1
        # avg = mean(5.0, 5.1, ..., 12.4) = 8.7
        assert abs(p1['avg_speed_kmh'] - 8.7) < 0.2
        # Player 3 has speed=3.0 for first 50 frames, None for last 25
        p3 = stats['players']['3']
        assert abs(p3['max_speed_kmh'] - 3.0) < 0.1
        assert abs(p3['avg_speed_kmh'] - 3.0) < 0.1
