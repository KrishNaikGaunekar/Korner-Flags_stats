import json
import os
import pytest

MANIFEST_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'manifest.json')

REQUIRED_CLIP_KEYS = [
    'clip_id', 'title', 'duration_seconds', 'video_url',
    'stats_url', 'heatmap_team1_url', 'heatmap_team2_url', 'positions_url',
]


class TestManifest:
    def test_manifest_schema(self):
        with open(MANIFEST_PATH) as f:
            data = json.load(f)
        assert 'clips' in data
        assert isinstance(data['clips'], list)
        assert len(data['clips']) >= 1

    def test_manifest_clip_keys(self):
        with open(MANIFEST_PATH) as f:
            data = json.load(f)
        for clip in data['clips']:
            for key in REQUIRED_CLIP_KEYS:
                assert key in clip, f'Missing key {key} in clip {clip.get("clip_id", "unknown")}'

    def test_manifest_video_url_format(self):
        with open(MANIFEST_PATH) as f:
            data = json.load(f)
        for clip in data['clips']:
            assert clip['video_url'].startswith('https://github.com/'), \
                f'video_url must be a GitHub URL, got: {clip["video_url"]}'
            assert '/releases/download/' in clip['video_url'], \
                f'video_url must use releases/download path, got: {clip["video_url"]}'

    def test_manifest_valid_json(self):
        """Ensure manifest.json is parseable without errors."""
        with open(MANIFEST_PATH) as f:
            data = json.load(f)  # will raise ValueError if invalid
        assert data is not None
