# Phase 2: Data Export and Video Processing - Research

**Researched:** 2026-03-17
**Domain:** Python data export, mplsoccer heatmaps, GitHub Releases hosting
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Heatmap visual style:**
- Pitch background: green grass (classic) — mplsoccer `VerticalPitch` or `Pitch` with default green style
- Team 1 = blue heatmap, Team 2 = red heatmap — standard soccer analytics convention, both legible on green
- Output PNG size: 1200x800 px at web-ready DPI — suitable for demo site without heavy load times
- Label: include a plain title on each PNG — "Team 1" and "Team 2" respectively

**positions.json schema (DATA-01):**
- Downsampled to 1 Hz (every N-th frame where N = fps, e.g. frame 0, 25, 50… for 25 fps video)
- Each record includes: `player_id`, `x`, `y`, `team` — minimal but complete
- ByteTrack ephemeral player IDs are acceptable — IDs only need to be consistent within one clip run
- Output location: alongside stats JSON, e.g. `output_videos/<stem>_positions.json`

Schema:
```json
{
  "fps": 25.0,
  "sample_rate_hz": 1,
  "positions": [
    { "second": 0, "player_id": 3, "x": 34.2, "y": 18.7, "team": 1 },
    { "second": 0, "player_id": 7, "x": 52.1, "y": 31.4, "team": 2 }
  ]
}
```

**Stats JSON schema (DATA-03):**
- Restructure to nested per-player object
- Per-player fields: `team` (int), `distance_m` (float), `max_speed_kmh` (float), `avg_speed_kmh` (float)
- Top-level `possession` and `video` sections unchanged
- Global `max_speed_kmh` removed from top level

Schema:
```json
{
  "video": { "fps": 25.0, "resolution": "1920x1080", "total_frames": 750, "duration_seconds": 30.0 },
  "possession": { "team_1_percent": 37.9, "team_2_percent": 62.1 },
  "players": {
    "1": { "team": 1, "distance_m": 74.2, "max_speed_kmh": 22.1, "avg_speed_kmh": 8.3 }
  }
}
```

**Heatmap generation (DATA-02):**
- Separate script: `generate_heatmaps.py` reads `positions.json` and outputs two PNGs — one per team
- Output: `output_videos/<stem>_heatmap_team1.png` and `output_videos/<stem>_heatmap_team2.png`

### Claude's Discretion

- GitHub Releases upload workflow (DATA-04, HOST-01, HOST-02): Claude picks approach — likely a helper script `upload_release.py` using `gh release create` CLI; release named by clip stem; user runs manually per clip
- manifest.json schema and location (DATA-04): Claude designs schema with at minimum `clip_id`, `video_url`, `stats_url`, `heatmap_team1_url`, `heatmap_team2_url`, `duration_seconds` — committed to repo root or `data/`
- mplsoccer exact API calls (Pitch dimensions, KDE bandwidth, colormap intensity)
- Exact `gh` CLI flags for release creation

### Deferred Ideas (OUT OF SCOPE)

- Time-based heatmap filtering (first half / second half) — would need `frame_number` and `timestamp_s` in positions.json; may be added in Phase 5 (interactive heatmaps)
- Stable player IDs across clips (player re-identification) — significant scope; deferred to v2
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | Pipeline exports `positions.json` with per-player (x,y) at 1 Hz | `position_transformed` key confirmed in tracks after full pipeline; x range 0–23.32m, y range 0–68m |
| DATA-02 | Pipeline generates team heatmap PNGs via mplsoccer | mplsoccer 1.6.1 `Pitch` + `bin_statistic` + `heatmap` API confirmed; separate `generate_heatmaps.py` script decided |
| DATA-03 | Stats JSON includes possession %, per-player max/avg speed, per-player distance, team assignment | `team`, `speed`, `distance` keys all confirmed in tracks; `generate_stats()` identified as the function to restructure |
| DATA-04 | `manifest.json` committed to repo listing all clips with video URL, stats URL, heatmap URLs, metadata | JSON schema designed; location `data/manifest.json` recommended |
| HOST-01 | Annotated MP4s uploaded to GitHub Releases | `gh release create` CLI confirmed; CDN URL pattern confirmed |
| HOST-02 | Video URLs in manifest.json point to stable GitHub Release CDN URLs | URL pattern: `https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/<tag>/<filename>` |
</phase_requirements>

---

## Summary

Phase 2 produces all static data artifacts needed by the demo site. The pipeline already computes every piece of data required — `position_transformed` (real-world meter coordinates), `speed`, `distance`, and `team` are all live in the `tracks` dict after the full pipeline runs. The work is purely about extracting and reshaping this data into the agreed schemas, generating heatmap images from the extracted positions, and establishing the hosting workflow.

The coordinate system output by `ViewTransformer` is confirmed from live inspection: x spans 0–23.32 meters (visible pitch length) and y spans 0–68 meters (standard pitch width). These are the coordinates to write into `positions.json` and pass to mplsoccer. mplsoccer's `Pitch(pitch_type='custom', pitch_length=23.32, pitch_width=68)` accepts these directly; no coordinate transformation is needed.

The GitHub Releases hosting path is straightforward using the `gh` CLI. The CDN URL format is deterministic and stable: `https://github.com/{owner}/{repo}/releases/download/{tag}/{filename}`. This is the URL format for `manifest.json`. `gh` is not currently installed on this machine — the plan must include installing it via `winget install GitHub.cli` before the upload step.

**Primary recommendation:** Write `export_positions()` in `main.py` alongside `generate_stats()`, create `generate_heatmaps.py` as a standalone script, restructure `generate_stats()` in-place, and write `upload_release.py` as a thin wrapper around `gh release create`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mplsoccer | 1.6.1 (latest on PyPI) | Soccer pitch drawing + heatmap plotting | Purpose-built for football analytics; wraps matplotlib with pitch-aware coordinate system |
| matplotlib | 3.10.8 (already installed) | Figure creation, PNG export | mplsoccer dependency; already in environment |
| scipy | 1.17.1 (already installed) | Gaussian filter for heatmap smoothing | Standard for `gaussian_filter` on binned statistics |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| gh CLI | latest (not yet installed) | Upload MP4 assets to GitHub Releases | Manual release workflow; `winget install GitHub.cli` |
| json (stdlib) | N/A | Read/write positions.json, manifest.json | Already used in main.py |
| os (stdlib) | N/A | Path derivation | Already used in main.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Pitch.bin_statistic` + `Pitch.heatmap` | `Pitch.kdeplot` | `kdeplot` gives smooth continuous contours; `bin_statistic`+`heatmap` gives discrete grid cells. Both work — `heatmap` with `gaussian_filter` smoothing is simpler to control and produces a cleaner density map for position data |
| `gh release create` | GitHub API via `requests` | `requests` approach requires a PAT in env var and is more code; `gh` CLI handles auth interactively and is the standard tool |

**Installation (new dependency only):**
```bash
pip install mplsoccer
# gh CLI — Windows only, run in PowerShell or cmd:
winget install GitHub.cli
```

**Version verification (confirmed 2026-03-17):**
- `mplsoccer`: 1.6.1 (latest) confirmed via `pip index versions mplsoccer`
- `matplotlib`: 3.10.8 already installed
- `scipy`: 1.17.1 already installed

---

## Architecture Patterns

### Recommended Project Structure (additions only)
```
generate_heatmaps.py        # new standalone script — reads positions.json, writes 2 PNGs
upload_release.py           # new standalone script — wraps gh release create for one clip
data/
└── manifest.json           # committed to repo — lists all clips with stable URLs
output_videos/
├── <stem>_positions.json   # new — per-player 1Hz coordinates
├── <stem>_heatmap_team1.png  # new — generated by generate_heatmaps.py
└── <stem>_heatmap_team2.png  # new — generated by generate_heatmaps.py
```

### Pattern 1: positions.json Export in main.py

**What:** After `generate_stats()` is called, call a new `export_positions()` function with the same `tracks` and `video_info` arguments.

**When to use:** Immediately after speed/distance estimation and team assignment are complete (all required keys are populated).

**Key detail:** Sample interval = `round(video_info['fps'])` frames. At frame 0, 25, 50... for 25fps. Record `second = frame_num // fps`.

**Only include frames where `position_transformed` is not None and `team` is set.** Frames where the player was not visible produce `None` transformed positions — skip those silently.

```python
# Source: direct code inspection of main.py + view_transformer.py
def export_positions(tracks, video_info, output_path):
    fps = video_info['fps']
    sample_interval = round(fps)  # 1 Hz downsampling
    records = []
    for frame_num, player_track in enumerate(tracks['players']):
        if frame_num % sample_interval != 0:
            continue
        second = int(frame_num / fps)
        for player_id, info in player_track.items():
            pos = info.get('position_transformed')
            team = info.get('team')
            if pos is None or team is None:
                continue
            records.append({
                'second': second,
                'player_id': int(player_id),
                'x': round(float(pos[0]), 2),
                'y': round(float(pos[1]), 2),
                'team': int(team),
            })
    data = {
        'fps': fps,
        'sample_rate_hz': 1,
        'positions': records,
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
```

### Pattern 2: Stats JSON Restructure in generate_stats()

**What:** Rebuild `generate_stats()` to emit the new nested per-player format. The existing function collects `distance` per player from the last frame they appear. Extend it to also collect per-player max and average speed, and team assignment.

**Key detail:** `speed` is written to every frame in the 5-frame window where the player was visible. To get max and avg, iterate all frames per player, collect all non-None speed values, compute `max()` and `mean()`.

**Schema delta from current:**
- Remove: `players.total_detected`, `players.max_speed_kmh`, `players.distances`
- Add: `players` becomes a dict keyed by player_id string, each with `team`, `distance_m`, `max_speed_kmh`, `avg_speed_kmh`

```python
# Source: direct code inspection of generate_stats() + speed_and_distance_estimator.py
# Collect per-player speed lists across all frames:
player_speeds = {}   # {pid: [speed1, speed2, ...]}
player_team = {}     # {pid: team_int}
player_distance = {} # {pid: latest_distance}
for frame_tracks in tracks['players']:
    for pid, info in frame_tracks.items():
        if 'speed' in info and info['speed'] is not None:
            player_speeds.setdefault(pid, []).append(info['speed'])
        if 'distance' in info and info['distance'] is not None:
            player_distance[pid] = info['distance']
        if 'team' in info:
            player_team[pid] = info['team']
```

### Pattern 3: mplsoccer Heatmap Generation

**What:** `generate_heatmaps.py` reads `positions.json`, splits by team, creates one PNG per team using `Pitch` + `bin_statistic` + `gaussian_filter` + `heatmap`.

**Coordinate system:** ViewTransformer outputs x in [0, 23.32] and y in [0, 68]. Use `pitch_type='custom'`, `pitch_length=23.32`, `pitch_width=68` to match. This means the visible segment of pitch is plotted, not a full 105m pitch.

**Pitch orientation decision:** Use `Pitch` (horizontal) with x as the length axis and y as the width axis, consistent with how ViewTransformer defines target vertices (`[0, court_width]` = top-left corner of the visible section).

```python
# Source: mplsoccer official docs + verified via WebSearch 2026-03-17
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use('Agg')  # headless — no display server needed
import matplotlib.pyplot as plt
import json, numpy as np

def generate_heatmap(x_coords, y_coords, team_label, color, output_path):
    pitch = Pitch(
        pitch_type='custom',
        pitch_length=23.32,
        pitch_width=68,
        pitch_color='grass',
        line_color='white',
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=(12, 8))  # 12x8 inches @ 100 dpi = 1200x800 px
    fig.patch.set_facecolor('green')

    if len(x_coords) > 0:
        bin_statistic = pitch.bin_statistic(
            x_coords, y_coords, statistic='count', bins=(25, 25)
        )
        bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
        pitch.heatmap(bin_statistic, ax=ax, cmap=color, edgecolors='none', alpha=0.7)

    ax.set_title(team_label, fontsize=16, color='white', pad=10)
    fig.savefig(output_path, dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
```

**Colormap choices:**
- Team 1 (blue): `cmap='Blues'`
- Team 2 (red): `cmap='Reds'`

Both are perceptually legible on a green grass background. (HIGH confidence — standard matplotlib colormaps, verified.)

### Pattern 4: GitHub Releases Upload Workflow

**What:** `upload_release.py` takes a clip stem as argument, creates a release tag from the stem, uploads the MP4 and returns the stable download URL.

**CDN URL format (HIGH confidence, verified from GitHub docs):**
```
https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/<tag>/<filename>
```

**gh CLI not installed on this machine.** Must install before this pattern is usable:
```bash
# Windows — run in PowerShell or cmd (not bash)
winget install GitHub.cli
# After install, authenticate:
gh auth login
```

**gh release create flags:**
```bash
gh release create <tag> \
  --title "<title>" \
  --notes "Auto-generated release for clip <stem>" \
  output_videos/<stem>_annotated.mp4
```

**upload_release.py pattern:**
```python
import argparse, subprocess, os, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stem', required=True, help='Clip stem, e.g. 08fd33_4')
    parser.add_argument('--output-dir', default='output_videos')
    args = parser.parse_args()

    mp4_path = os.path.join(args.output_dir, f'{args.stem}_annotated.mp4')
    tag = f'clip-{args.stem}'
    title = f'Clip: {args.stem}'

    cmd = [
        'gh', 'release', 'create', tag,
        mp4_path,
        '--title', title,
        '--notes', f'Annotated clip {args.stem}',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'ERROR: {result.stderr}')
        sys.exit(1)

    url = f'https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/{tag}/{args.stem}_annotated.mp4'
    print(f'Video URL: {url}')
```

### Pattern 5: manifest.json Schema

**What:** A JSON file committed to `data/manifest.json` that the Phase 3 site consumes.

**Recommended location:** `data/manifest.json` (keeps data artifacts separate from source code).

**Schema:**
```json
{
  "clips": [
    {
      "clip_id": "08fd33_4",
      "title": "NC State Match Clip 1",
      "duration_seconds": 30.0,
      "video_url": "https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4",
      "stats_url": "output_videos/08fd33_4_annotated_stats.json",
      "heatmap_team1_url": "output_videos/08fd33_4_heatmap_team1.png",
      "heatmap_team2_url": "output_videos/08fd33_4_heatmap_team2.png",
      "positions_url": "output_videos/08fd33_4_positions.json"
    }
  ]
}
```

**stats_url and heatmap_urls:** These reference paths within the repo (relative to repo root), since they are committed alongside the code. The site (Phase 3) will use GitHub raw URLs or relative paths to fetch them.

### Anti-Patterns to Avoid

- **Hardcoding FPS as 25:** Always use `video_info['fps']` for sample interval — per project rules and skill doc.
- **Running `generate_heatmaps.py` from within the pipeline:** It is a separate script by design. Do not call it from `main.py`.
- **Using `kdeplot` instead of `bin_statistic` + `heatmap`:** `kdeplot` requires scipy kernel bandwidth tuning and clips at pitch edges in ways that can produce sparse-looking plots when data is limited to 23.32m of pitch. The `bin_statistic` + `gaussian_filter` approach is more controllable.
- **Importing matplotlib without `matplotlib.use('Agg')`:** On Windows without a display, the default backend may raise a GUI error. Always set Agg backend before importing pyplot in `generate_heatmaps.py`.
- **Using `tracks['players'][frame_num][player_id]['team']`:** Team assignment happens in the loop after the pipeline step. For the positions export, team must be read from the same frame being exported — don't assume team is set in frame 0 for all players.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Soccer pitch drawing | Custom matplotlib rectangles/arcs | `mplsoccer.Pitch` | Pitch geometry is complex (arc radii, penalty box proportions, center circle); mplsoccer handles all of it correctly |
| Density visualization | Custom 2D histogram plotting | `bin_statistic` + `gaussian_filter` + `heatmap` | Edge clamping, colormap normalization, aspect ratio are all handled |
| GitHub asset upload | `requests`-based GitHub API client | `gh release create` | Auth handling, rate limiting, multipart upload — gh CLI handles all of this |
| Coordinate rescaling | Manual pitch unit conversion | `pitch_type='custom'` with `pitch_length` + `pitch_width` | mplsoccer accepts your actual meter coordinates directly |

**Key insight:** mplsoccer's coordinate-agnostic design means you pass your actual meter values and specify the pitch dimensions — no normalization to 0-100 or StatsBomb coordinates needed.

---

## Common Pitfalls

### Pitfall 1: position_transformed Available Too Late
**What goes wrong:** Code tries to read `position_transformed` from tracks but it is None or the key is missing because the positions export runs before `ViewTransformer.add_transformered_position_to_tracks()` completes.
**Why it happens:** The pipeline has a strict ordering; `position_transformed` is only populated after step 5 in the pipeline order.
**How to avoid:** Call `export_positions()` only after both `speed_and_distance_estimator.add_speed_and_distance_to_tracks()` AND the team assignment loop have completed — i.e., insert the call at line 163+ in main.py alongside `generate_stats()`.
**Warning signs:** `positions.json` contains zero records, or all entries have `team: null`.

### Pitfall 2: Team Key Missing for Some Players
**What goes wrong:** Some player entries in `positions.json` have no `team` field, causing heatmap generation to fail when splitting by team.
**Why it happens:** Team assignment in `main.py` iterates all frames and calls `get_player_team` per frame — but a player visible only briefly in early frames may not have team assigned at the 1Hz sample frames.
**How to avoid:** Skip records where `team is None` silently (already in the pattern above). Also consider a two-pass approach: collect team per player_id across all frames, then use that dict when exporting positions.
**Warning signs:** Fewer positions entries than expected; `heatmap_team1.png` is nearly blank.

### Pitfall 3: mplsoccer Displays Empty Pitch (No Heatmap Overlay)
**What goes wrong:** The heatmap PNG shows only the green pitch with no density overlay.
**Why it happens:** All position data is filtered out (all `None` or wrong team) — `bin_statistic` is called with empty arrays.
**How to avoid:** Add a guard: `if len(x_coords) == 0: # write pitch-only placeholder PNG and log warning`.
**Warning signs:** File size of PNG is suspiciously small (< 50KB typically means just the pitch background).

### Pitfall 4: gh CLI Not in PATH After winget Install
**What goes wrong:** `subprocess.run(['gh', ...])` raises `FileNotFoundError`.
**Why it happens:** `winget install GitHub.cli` installs gh but the PATH update requires a new shell session on Windows.
**How to avoid:** After installing, open a new terminal before running `upload_release.py`. Or use the full path `C:\Program Files\GitHub CLI\gh.exe`.
**Warning signs:** `FileNotFoundError: [WinError 2] The system cannot find the file specified`.

### Pitfall 5: Release Already Exists for Tag
**What goes wrong:** `gh release create` fails with "release already exists" when re-running for a clip.
**Why it happens:** The tag `clip-<stem>` was already created in a previous upload attempt.
**How to avoid:** Add `--clobber` flag to `gh release create` to overwrite, or check `gh release view <tag>` first and use `gh release upload <tag>` for subsequent uploads.
**Warning signs:** `gh release create` exits with non-zero code and error message "already_exists".

### Pitfall 6: matplotlib Backend Error on Windows
**What goes wrong:** `generate_heatmaps.py` crashes with `cannot connect to X server` or `no display name and no $DISPLAY environment variable`.
**Why it happens:** Default matplotlib backend tries to open a GUI window.
**How to avoid:** `import matplotlib; matplotlib.use('Agg')` BEFORE `import matplotlib.pyplot as plt`. This must be the very first matplotlib call.
**Warning signs:** Import error or backend-related RuntimeError at startup.

---

## Code Examples

### Reading positions.json in generate_heatmaps.py
```python
# Verified pattern from code inspection
import json, sys

def load_positions(path):
    with open(path) as f:
        data = json.load(f)
    team1_x, team1_y = [], []
    team2_x, team2_y = [], []
    for record in data['positions']:
        if record['team'] == 1:
            team1_x.append(record['x'])
            team1_y.append(record['y'])
        elif record['team'] == 2:
            team2_x.append(record['x'])
            team2_y.append(record['y'])
    return team1_x, team1_y, team2_x, team2_y
```

### Deriving output paths from stem (consistent with existing pattern)
```python
# Source: main.py line 44 — os.path.splitext pattern
import os
stem = os.path.splitext(os.path.basename(args.output))[0]
# e.g. "output_videos/08fd33_4_annotated"
positions_path = os.path.splitext(args.output)[0].replace('_annotated', '') + '_positions.json'
# Alternative: derive directly from input stem:
input_stem = os.path.splitext(os.path.basename(args.input))[0]
positions_path = f'output_videos/{input_stem}_positions.json'
```

The second approach (from input stem, not output stem) is cleaner and consistent with how `args.output` is currently derived.

### Calling generate_heatmaps.py from the command line
```bash
python generate_heatmaps.py --positions output_videos/08fd33_4_positions.json
# Outputs: output_videos/08fd33_4_heatmap_team1.png
#          output_videos/08fd33_4_heatmap_team2.png
```

### Uploading a release and getting the stable URL
```bash
# One-time: winget install GitHub.cli && gh auth login
python upload_release.py --stem 08fd33_4
# Prints: Video URL: https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual matplotlib pitch drawing | mplsoccer `Pitch` class | ~2020 | Eliminates custom pitch geometry code entirely |
| Committing videos to Git repo | GitHub Releases for binary assets | GitHub best practice | Avoids repo bloat and GitHub's 100 MB file size limit |
| Flat stats JSON with top-level player aggregate | Nested per-player dict | This phase | Enables per-player team, speed, and distance access without joins |

**Deprecated/outdated:**
- Old stats schema: `players.distances` (flat dict) and `players.max_speed_kmh` (global scalar) — replaced by nested per-player objects.
- Storing binary video files in Git tree — not appropriate for files over ~50 MB.

---

## Open Questions

1. **gh CLI installation path on this machine**
   - What we know: `gh` is not currently in PATH; `winget` is available
   - What's unclear: Whether a system-level `winget install` will require admin rights in this environment
   - Recommendation: The plan should include a task to verify `gh` is installed and authenticated before the upload task; if winget fails, the GitHub Releases web UI is a fallback for manual upload

2. **positions.json path derivation convention**
   - What we know: Current code uses `os.path.splitext(args.output)[0] + '_stats.json'` for stats
   - What's unclear: Whether positions path should be derived from `args.output` (annotated video stem) or `args.input` (original video stem)
   - Recommendation: Derive from input stem for cleaner naming — `output_videos/<input_stem>_positions.json` — consistent with how `generate_heatmaps.py` will reference it by stem

3. **stats_url and heatmap_url format in manifest.json**
   - What we know: Stats JSON and heatmap PNGs are committed to the repo in `output_videos/`; the demo site (Phase 3) needs to load them
   - What's unclear: Whether Phase 3 will use relative paths, GitHub raw URLs, or GitHub Pages paths for these assets
   - Recommendation: In Phase 2, use relative repo paths (`output_videos/<stem>_stats.json`) in manifest.json — Phase 3 can convert to absolute URLs once the Pages URL is known

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (to be installed — not yet present) |
| Config file | none — Wave 0 creates `pytest.ini` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | `export_positions()` produces valid positions.json with correct schema | unit | `pytest tests/test_export.py::test_positions_schema -x` | Wave 0 |
| DATA-01 | Positions downsampled to 1 Hz (frame interval = fps) | unit | `pytest tests/test_export.py::test_positions_sample_rate -x` | Wave 0 |
| DATA-01 | Records with None `position_transformed` are excluded | unit | `pytest tests/test_export.py::test_positions_skips_none -x` | Wave 0 |
| DATA-02 | `generate_heatmaps.py` produces two PNG files | integration | `pytest tests/test_heatmaps.py::test_heatmap_files_created -x` | Wave 0 |
| DATA-02 | PNG dimensions are 1200x800 (or close to target DPI) | unit | `pytest tests/test_heatmaps.py::test_heatmap_dimensions -x` | Wave 0 |
| DATA-03 | `generate_stats()` emits per-player nested dict with required fields | unit | `pytest tests/test_stats.py::test_stats_schema -x` | Wave 0 |
| DATA-03 | Per-player max_speed_kmh is derived correctly | unit | `pytest tests/test_stats.py::test_stats_speed_calculation -x` | Wave 0 |
| DATA-04 | `manifest.json` is valid JSON with required top-level keys | unit | `pytest tests/test_manifest.py::test_manifest_schema -x` | Wave 0 |
| HOST-01 | `upload_release.py` calls `gh release create` with correct args (mock subprocess) | unit | `pytest tests/test_upload.py::test_upload_command -x` | Wave 0 |
| HOST-02 | Constructed CDN URL matches expected pattern | unit | `pytest tests/test_upload.py::test_cdn_url_format -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/__init__.py` — package marker
- [ ] `tests/test_export.py` — covers DATA-01
- [ ] `tests/test_heatmaps.py` — covers DATA-02
- [ ] `tests/test_stats.py` — covers DATA-03
- [ ] `tests/test_manifest.py` — covers DATA-04
- [ ] `tests/test_upload.py` — covers HOST-01, HOST-02
- [ ] `pytest.ini` — minimal config pointing to `tests/`
- [ ] Framework install: `pip install pytest` — not yet in requirements.txt

---

## Sources

### Primary (HIGH confidence)
- Live codebase inspection (`main.py`, `view_transformer.py`, `speed_and_distance_estimator.py`) — confirmed all tracks keys and coordinate ranges
- Live Python inspection — `position_transformed` values confirmed at x=[0–23.32], y=[0–68] meters
- `pip index versions mplsoccer` — confirmed 1.6.1 is latest as of 2026-03-17
- https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_heatmap.html — bin_statistic + gaussian_filter + heatmap pattern
- https://cli.github.com/manual/gh_release_create — gh release create flags

### Secondary (MEDIUM confidence)
- https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases — CDN URL format `releases/download/<tag>/<filename>` confirmed
- WebSearch result (multiple sources agree) — `pitch_color='grass'` is a valid mplsoccer parameter

### Tertiary (LOW confidence — needs validation)
- mplsoccer `pitch_type='custom'` with `pitch_length=23.32` accepting meter values directly — inferred from docs, not directly tested; verify in Wave 0 heatmap test

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all versions verified against PyPI registry; matplotlib and scipy already installed
- Architecture: HIGH — patterns derived from direct codebase inspection; tracks data structure confirmed live
- mplsoccer API calls: MEDIUM — official docs consulted, exact `pitch_type='custom'` with sub-105m pitch_length not directly tested yet
- GitHub Releases URL format: HIGH — confirmed from official GitHub docs
- gh CLI installation: MEDIUM — winget approach is standard but not tested in this environment

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stable libraries; mplsoccer releases infrequently)
