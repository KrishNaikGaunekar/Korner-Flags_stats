import json
import os
import tempfile
import pytest

# Import will fail until Task 2 creates export_positions — that's the RED phase
from main import export_positions

def _make_tracks(num_frames=75, fps=25.0):
    """Create minimal tracks dict with 2 players across num_frames frames."""
    players = []
    for f in range(num_frames):
        frame = {}
        # Player 1: always visible with valid position
        frame[1] = {
            'position_transformed': (10.0 + f * 0.1, 30.0),
            'team': 1,
            'speed': 5.0 + f * 0.01,
            'distance': f * 0.5,
        }
        # Player 2: visible only on even frames
        if f % 2 == 0:
            frame[2] = {
                'position_transformed': (15.0, 40.0 + f * 0.05),
                'team': 2,
                'speed': 3.0,
                'distance': f * 0.3,
            }
        else:
            frame[2] = {
                'position_transformed': None,
                'team': None,
                'speed': None,
                'distance': None,
            }
        players.append(frame)
    return {'players': players, 'ball': [{} for _ in range(num_frames)]}

def _make_video_info(fps=25.0):
    return {'fps': fps, 'width': 1920, 'height': 1080, 'total_frames': 75}

class TestPositionsSchema:
    def test_positions_schema(self):
        tracks = _make_tracks(75, 25.0)
        video_info = _make_video_info(25.0)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            tmp = f.name
        try:
            export_positions(tracks, video_info, tmp)
            with open(tmp) as f:
                data = json.load(f)
            assert 'fps' in data
            assert 'sample_rate_hz' in data
            assert data['sample_rate_hz'] == 1
            assert 'positions' in data
            assert isinstance(data['positions'], list)
            assert len(data['positions']) > 0
            record = data['positions'][0]
            assert 'second' in record
            assert 'player_id' in record
            assert 'x' in record
            assert 'y' in record
            assert 'team' in record
        finally:
            os.unlink(tmp)

    def test_positions_sample_rate(self):
        tracks = _make_tracks(75, 25.0)
        video_info = _make_video_info(25.0)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            tmp = f.name
        try:
            export_positions(tracks, video_info, tmp)
            with open(tmp) as f:
                data = json.load(f)
            # 75 frames at 25fps = 3 seconds, sample at 0, 25, 50 = seconds 0, 1, 2
            seconds = sorted(set(r['second'] for r in data['positions']))
            assert seconds == [0, 1, 2]
        finally:
            os.unlink(tmp)

    def test_positions_skips_none(self):
        tracks = _make_tracks(75, 25.0)
        video_info = _make_video_info(25.0)
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            tmp = f.name
        try:
            export_positions(tracks, video_info, tmp)
            with open(tmp) as f:
                data = json.load(f)
            # Player 2 has None position_transformed on odd frames
            # Frame 25 is odd -> player 2 excluded at second=1
            second_1_players = [r['player_id'] for r in data['positions'] if r['second'] == 1]
            assert 2 not in second_1_players
            # Frame 0 is even -> player 2 included at second=0
            second_0_players = [r['player_id'] for r in data['positions'] if r['second'] == 0]
            assert 2 in second_0_players
        finally:
            os.unlink(tmp)
