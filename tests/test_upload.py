import pytest
from upload_release import build_release_command, get_cdn_url


class TestUploadRelease:
    def test_upload_command(self):
        cmd = build_release_command('08fd33_4', 'output_videos')
        assert cmd[0] == 'gh'
        assert cmd[1] == 'release'
        assert cmd[2] == 'create'
        assert cmd[3] == 'clip-08fd33_4'
        # MP4 path must be in the command
        assert 'output_videos/08fd33_4_annotated.mp4' in cmd

    def test_cdn_url_format(self):
        url = get_cdn_url('08fd33_4')
        expected = 'https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4'
        assert url == expected

    def test_upload_command_has_title(self):
        cmd = build_release_command('08fd33_4')
        assert '--title' in cmd

    def test_upload_command_has_clobber(self):
        cmd = build_release_command('08fd33_4')
        assert '--clobber' in cmd

    def test_cdn_url_different_stem(self):
        url = get_cdn_url('ncstate_clip2')
        assert 'clip-ncstate_clip2' in url
        assert 'ncstate_clip2_annotated.mp4' in url
