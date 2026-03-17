# Phase 2: Data Export and Video Processing - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce all static data artifacts for 2-3 NC State clips: `positions.json` (per-player x,y at 1 Hz), team heatmap PNGs via mplsoccer, enhanced stats JSON (per-player team + speed + distance), upload annotated MP4s to GitHub Releases, and commit `manifest.json` with stable CDN URLs. No site work. No new pipeline features.

</domain>

<decisions>
## Implementation Decisions

### Heatmap visual style
- Pitch background: **green grass (classic)** — mplsoccer `VerticalPitch` or `Pitch` with default green style
- Team 1 = **blue** heatmap, Team 2 = **red** heatmap — standard soccer analytics convention, both legible on green
- Output PNG size: **1200×800 px at web-ready DPI** — suitable for demo site without heavy load times
- Label: include a plain title on each PNG — "Team 1" and "Team 2" respectively (site handles further labeling)

### positions.json schema (DATA-01)
- Downsampled to **1 Hz** (every N-th frame where N = fps, e.g. frame 0, 25, 50… for 25 fps video)
- Each record includes: `player_id`, `x`, `y`, `team` — minimal but complete for heatmap generation without needing to rejoin stats
- ByteTrack ephemeral player IDs are acceptable — IDs only need to be consistent within one clip run
- Output location: alongside stats JSON, e.g. `output_videos/<stem>_positions.json`

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

### Stats JSON schema (DATA-03)
- Restructure to **nested per-player object** — most extensible for future additions (pass count, jersey number, etc.)
- Per-player fields: `team` (int), `distance_m` (float), `max_speed_kmh` (float), `avg_speed_kmh` (float)
- Top-level `possession` and `video` sections stay the same structure
- Global `max_speed_kmh` field removed from top level; it can be derived from per-player data

```json
{
  "video": { "fps": 25.0, "resolution": "1920x1080", "total_frames": 750, "duration_seconds": 30.0 },
  "possession": { "team_1_percent": 37.9, "team_2_percent": 62.1 },
  "players": {
    "1": { "team": 1, "distance_m": 74.2, "max_speed_kmh": 22.1, "avg_speed_kmh": 8.3 },
    "3": { "team": 2, "distance_m": 75.2, "max_speed_kmh": 19.4, "avg_speed_kmh": 7.1 }
  }
}
```

### Heatmap generation (DATA-02)
- **Separate script**: `generate_heatmaps.py` reads `positions.json` and outputs two PNGs — one per team
- Rationale: clean separation allows heatmap regeneration (style changes, color tweaks) without re-running YOLO inference
- Output: `output_videos/<stem>_heatmap_team1.png` and `output_videos/<stem>_heatmap_team2.png`
- mplsoccer `Pitch` with `kdeplot` or `heatmap` for density visualization

### Claude's Discretion
- GitHub Releases upload workflow (DATA-04, HOST-01, HOST-02): Claude picks approach — likely a helper script `upload_release.py` using `gh release create` CLI; release named by clip stem; user runs manually per clip
- manifest.json schema and location (DATA-04): Claude designs schema with at minimum `clip_id`, `video_url`, `stats_url`, `heatmap_team1_url`, `heatmap_team2_url`, `duration_seconds` — committed to repo root or `data/`
- mplsoccer exact API calls (Pitch dimensions, KDE bandwidth, colormap intensity)
- Exact `gh` CLI flags for release creation

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Data Export — DATA-01 through DATA-04 definitions and acceptance criteria
- `.planning/REQUIREMENTS.md` §Video Hosting — HOST-01, HOST-02 definitions

### Source files to modify
- `main.py` — `generate_stats()` function (restructure to nested per-player schema) and add positions.json export call
- `output_videos/08fd33_4_annotated_stats.json` — current stats JSON structure (reference for what schema changes are needed)

### Codebase architecture
- `CLAUDE.md` — pipeline order, critical rules (no hardcoded paths/FPS/resolutions), key libraries
- `.planning/codebase/CONCERNS.md` — known fragile areas (speed values unrealistically high — known limitation, not a Phase 2 bug to fix)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tracks['players'][frame_num][player_id]` — already contains `transformed_position` (real-world meter coords), `speed`, `distance`, `team`, `team_color` per player per frame — all raw data needed for positions.json and enhanced stats is already in memory
- `generate_stats()` in `main.py` — existing function to restructure in-place (extend, don't rewrite from scratch)
- `video_info['fps']` — already available at pipeline run time; needed to compute 1 Hz downsample interval

### Established Patterns
- All output paths derived from `args.output` using `os.path.splitext` — positions.json and heatmap PNGs must follow same pattern
- `--use-stubs` pattern exists for skipping YOLO re-inference — positions.json export should work correctly when stubs are used
- No hardcoded paths, resolutions, or FPS — positions.json export must use `video_info['fps']` for sample interval

### Integration Points
- `main.py:163–167` — stats export block is the insertion point for positions.json export (same `tracks` data, same `video_info`)
- `main.py:171` — `generate_stats()` function signature: `(tracks, team_ball_control, video_info)` — same args needed for positions export function
- `generate_heatmaps.py` (new script) — reads `<stem>_positions.json`, no dependency on main.py pipeline state

</code_context>

<specifics>
## Specific Ideas

- Speed disclaimer is a known issue (268 km/h max observed) — it's an accepted limitation of estimated pitch vertices; Phase 2 does NOT fix this, Phase 6 adds the site disclaimer
- Demo target is NC State soccer coaching staff — "Team 1 / Team 2" labels are fine for Phase 2; actual team name mapping can be added to manifest.json metadata in Phase 3

</specifics>

<deferred>
## Deferred Ideas

- Time-based heatmap filtering (first half / second half) — would need `frame_number` and `timestamp_s` in positions.json; user left as Claude's discretion for now; may be added in Phase 5 (interactive heatmaps)
- Stable player IDs across clips (player re-identification) — significant scope; deferred to v2

</deferred>

---

*Phase: 02-data-export-and-video-processing*
*Context gathered: 2026-03-17*
