---
phase: 2
slug: data-export-and-video-processing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (to be installed — not yet present) |
| **Config file** | none — Wave 0 creates `pytest.ini` |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 0 | DATA-01 | unit | `pytest tests/test_export.py::test_positions_schema -x` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 0 | DATA-01 | unit | `pytest tests/test_export.py::test_positions_sample_rate -x` | ❌ W0 | ⬜ pending |
| 2-01-03 | 01 | 0 | DATA-01 | unit | `pytest tests/test_export.py::test_positions_skips_none -x` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02 | 0 | DATA-03 | unit | `pytest tests/test_stats.py::test_stats_schema -x` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02 | 0 | DATA-03 | unit | `pytest tests/test_stats.py::test_stats_speed_calculation -x` | ❌ W0 | ⬜ pending |
| 2-03-01 | 03 | 0 | DATA-02 | integration | `pytest tests/test_heatmaps.py::test_heatmap_files_created -x` | ❌ W0 | ⬜ pending |
| 2-03-02 | 03 | 0 | DATA-02 | unit | `pytest tests/test_heatmaps.py::test_heatmap_dimensions -x` | ❌ W0 | ⬜ pending |
| 2-04-01 | 04 | 0 | HOST-01 | unit | `pytest tests/test_upload.py::test_upload_command -x` | ❌ W0 | ⬜ pending |
| 2-04-02 | 04 | 0 | HOST-02 | unit | `pytest tests/test_upload.py::test_cdn_url_format -x` | ❌ W0 | ⬜ pending |
| 2-05-01 | 05 | 0 | DATA-04 | unit | `pytest tests/test_manifest.py::test_manifest_schema -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — package marker
- [ ] `tests/test_export.py` — stubs for DATA-01
- [ ] `tests/test_stats.py` — stubs for DATA-03
- [ ] `tests/test_heatmaps.py` — stubs for DATA-02
- [ ] `tests/test_upload.py` — stubs for HOST-01, HOST-02
- [ ] `tests/test_manifest.py` — stubs for DATA-04
- [ ] `pytest.ini` — minimal config pointing to `tests/`
- [ ] `pip install pytest` added to requirements.txt — framework not yet installed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Heatmap PNG is visually legible on green pitch background | DATA-02 | Visual quality cannot be verified by automated test | Open `output_videos/<stem>_heatmap_team1.png` and `_team2.png`; confirm blue/red density overlay is visible on green pitch background |
| gh CLI authentication works | HOST-01 | Auth state is per-machine, not testable in CI | Run `gh auth status` — must show "Logged in to github.com" |
| Annotated MP4 is accessible at the GitHub Releases CDN URL | HOST-01, HOST-02 | Requires live GitHub upload | Open the URL from `manifest.json` `video_url` in a browser — video must load |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
