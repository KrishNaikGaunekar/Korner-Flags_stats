# Architecture Research

**Domain:** Static sports video analysis demo site (GitHub Pages)
**Researched:** 2026-03-16
**Confidence:** HIGH (GitHub Pages constraints verified from official docs; video hosting pattern verified from multiple sources; heatmap library verified from official repo)

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    OFFLINE (Local Machine)                        │
│                                                                   │
│  ┌─────────────┐    ┌────────────────┐    ┌────────────────────┐ │
│  │  Raw Match  │───▶│  Python CLI    │───▶│  Pipeline Output   │ │
│  │  Video.mp4  │    │  main.py       │    │  annotated.mp4     │ │
│  └─────────────┘    │  (YOLO+Track)  │    │  stats.json        │ │
│                     └────────────────┘    │  positions.json    │ │
│                                           └────────┬───────────┘ │
└────────────────────────────────────────────────────┼─────────────┘
                                                     │ manual upload
                         ┌───────────────────────────▼─────────────┐
                         │           GitHub (two stores)            │
                         │                                          │
                         │  ┌──────────────┐  ┌──────────────────┐ │
                         │  │ Repo (Pages) │  │ Releases Assets  │ │
                         │  │ HTML/CSS/JS  │  │ annotated.mp4    │ │
                         │  │ stats JSONs  │  │ (<2GB per file)  │ │
                         │  │ manifest.json│  └──────────────────┘ │
                         │  └──────┬───────┘                       │
                         └─────────┼─────────────────────────────--┘
                                   │ serves
                    ┌──────────────▼────────────────────────────────┐
                    │              GitHub Pages (Browser)            │
                    │                                                │
                    │  ┌─────────────┐  ┌──────────┐  ┌──────────┐ │
                    │  │ Match Index │  │  Match   │  │ Heatmap  │ │
                    │  │  Browser    │  │  Viewer  │  │ Canvas   │ │
                    │  │ (index.html)│  │(match.js)│  │(d3.js)   │ │
                    │  └─────────────┘  └──────────┘  └──────────┘ │
                    └────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Python CLI pipeline | Detect, track, annotate video; output stats JSON | Existing `main.py` + modules |
| Heatmap exporter | New pipeline stage: write per-player position arrays to JSON | New Python module in pipeline |
| Video converter | Convert AVI output to browser-compatible H.264 MP4 | `ffmpeg -i annotated.avi -c:v libx264 annotated.mp4` |
| `manifest.json` | Registry of all matches: title, video URL, stats URL, heatmap URL | Hand-edited or script-generated JSON |
| Match index page | Browsable gallery of processed matches | `index.html` + vanilla JS reading `manifest.json` |
| Match viewer page | Single-match view: video player + stats panel side by side | `match.html` + `match.js` |
| Heatmap canvas | Render player position density on pitch SVG | D3.js + d3-soccer library |
| GitHub Releases | Host annotated MP4 files outside repo tree (bypasses 100MB limit) | GitHub web UI upload under a release tag |

## Recommended Project Structure

```
(repo root)/
├── index.html                # Match browser — reads manifest.json, renders gallery
├── match.html                # Single match viewer — video + stats + heatmap tabs
├── assets/
│   ├── css/
│   │   └── styles.css        # Shared styles (pitch colors, layout, typography)
│   └── js/
│       ├── manifest.js       # Loads + parses manifest.json, exports match list
│       ├── gallery.js        # Renders match cards on index.html
│       ├── player.js         # Controls HTML5 video element on match.html
│       ├── stats.js          # Reads stats JSON, renders possession/speed/distance
│       └── heatmap.js        # D3 + d3-soccer pitch + KDE heatmap from positions JSON
├── data/
│   ├── manifest.json         # Master match registry (committed to repo)
│   ├── match-001/
│   │   ├── stats.json        # Pipeline stats output (committed — small, ~10KB)
│   │   └── positions.json    # Per-player XY positions per frame (committed — ~200KB)
│   └── match-002/
│       ├── stats.json
│       └── positions.json
├── tools/
│   └── export_positions.py   # New pipeline addon: extracts position data for heatmaps
└── (all annotated MP4s live in GitHub Releases, NOT in the repo tree)
```

### Structure Rationale

- **`data/` in repo:** Stats JSON and position JSON are small (10-200KB each). Safe to commit. No external hosting needed.
- **Videos in Releases:** Annotated MP4 files are likely 50-500MB each. GitHub Pages repo limit is 1GB total; Git hard limit is 100MB per file. GitHub Releases accepts files up to 2GB per asset and serves them via CDN with direct-link URLs. This is the correct home for video assets.
- **`manifest.json`:** Single source of truth. Adding a new match means one JSON entry. The browser reads this at page load — no build step required.
- **No build toolchain:** GitHub Pages serves static files directly. Vanilla HTML + JS avoids npm, bundlers, and CI complexity — appropriate for a 1-2 week deadline.

## Architectural Patterns

### Pattern 1: Manifest-Driven Gallery

**What:** A single `manifest.json` lists all matches. The index page fetches this file and renders match cards dynamically. Each match entry contains title, thumbnail URL, video URL (pointing to Releases), stats URL, and heatmap data URL.

**When to use:** Whenever you have N items of the same schema. Adding a new match = adding one JSON object. No HTML edits required.

**Trade-offs:** Requires JavaScript enabled (fine for a coached demo). No SSG overhead. Can become unwieldy past ~50 matches, but for 2-3 matches this is perfect.

**Example:**
```json
{
  "matches": [
    {
      "id": "ncstate-001",
      "title": "NC State vs UNC — Oct 12 2025",
      "thumbnail": "data/match-001/thumbnail.jpg",
      "video_url": "https://github.com/USER/REPO/releases/download/v1.0/ncstate-001-annotated.mp4",
      "stats_url": "data/match-001/stats.json",
      "positions_url": "data/match-001/positions.json",
      "date": "2025-10-12"
    }
  ]
}
```

### Pattern 2: GitHub Releases as Video CDN

**What:** Upload annotated MP4 files as release assets. Reference the direct download URL in `manifest.json`. Embed via HTML5 `<video>` tag with `controls`.

**When to use:** Any video >25MB that must be hosted on GitHub infrastructure (free, no third-party dependency).

**Trade-offs:** URLs are permanent once published. Re-uploading requires a new release or replacing the asset and updating the URL. GitHub Releases serves with reasonable CDN (not Cloudflare-grade, but acceptable for a coach demo). Files up to 2GB per asset. Total release storage has a soft limit of 10GB per repo.

**Example:**
```html
<video
  src="https://github.com/USER/REPO/releases/download/v1.0/match.mp4"
  controls
  style="width: 100%; max-width: 960px;"
  preload="metadata">
</video>
```

### Pattern 3: D3-Soccer Heatmap from Position JSON

**What:** The Python pipeline exports per-player XY positions (in pitch-meter coordinates, already computed by `view_transformer`) into a `positions.json` file. The browser reads this file and renders a kernel density heatmap using `d3.contourDensity()` on a `d3.pitch()` SVG background from the d3-soccer library.

**When to use:** When real-world coordinates are available from the perspective transform — which they are, since `view_transformer.py` already outputs pitch-meter positions.

**Trade-offs:** Requires extracting the position data as a separate pipeline output (one new Python file, ~50 lines). D3-soccer pitch defaults to 105x68m, matching standard pitch dimensions. KDE smoothing makes sparse match data look professional. Canvas or SVG both work; SVG is easier to style.

**Example data format:**
```json
{
  "team_1": {
    "player_3": [[52.1, 34.2], [51.9, 33.8], ...],
    "player_7": [[22.4, 18.1], [23.0, 17.9], ...]
  },
  "team_2": {
    "player_12": [[88.3, 45.1], ...]
  }
}
```

## Data Flow

### Pipeline to Browser

```
Python Pipeline (local)
    ↓ main.py runs
annotated.avi (output_videos/)
stats.json (output_videos/)
    ↓ export_positions.py (new tool)
positions.json (data/match-NNN/)
    ↓ ffmpeg converts AVI → MP4
annotated.mp4
    ↓
Two upload paths:
  [A] stats.json + positions.json → commit to repo → GitHub Pages serves from /data/
  [B] annotated.mp4 → upload as GitHub Release asset → permanent CDN URL
    ↓ manifest.json updated with URLs
Browser loads index.html
    ↓ fetch('manifest.json')
Match gallery renders
    ↓ user clicks match
match.html?id=ncstate-001
    ↓ fetch stats_url → render possession/speed/distance
    ↓ fetch positions_url → render D3 heatmap
    ↓ video src= GitHub Release URL → HTML5 player
```

### State Management

No framework needed. State lives in the URL (`?id=match-001`) and is read on page load.

```
URL param: ?id=match-001
    ↓
match.html reads param
    ↓
fetch manifest.json → find entry by id
    ↓
fetch stats_url, positions_url in parallel
    ↓
render: video player, stats panel, heatmap canvas (tabs or scroll)
```

### Key Data Flows

1. **Match selection:** User clicks card on `index.html` → navigate to `match.html?id=X` — no state management library needed.
2. **Stats rendering:** `match.js` fetches `data/match-001/stats.json` → reads `possession_pct`, `players` array → updates DOM elements directly.
3. **Heatmap rendering:** `heatmap.js` fetches `positions.json` → runs `d3.contourDensity()` → renders contours over `d3.pitch()` SVG — team selector (team 1/2/both) controls which player data is fed to KDE.
4. **Video playback:** `<video>` element with `src` pointing at GitHub Release URL — GitHub serves it; no CORS issues since same origin policy doesn't apply to video elements.

## GitHub Pages Constraints

| Constraint | Limit | Implication |
|------------|-------|-------------|
| Repo size (recommended) | 1 GB | Videos must NOT be in the repo |
| Individual file in git | 100 MB hard limit | AVI outputs commonly exceed this |
| Published site size | 1 GB | Same as repo limit — data JSONs fine |
| Bandwidth (soft) | 100 GB/month | Fine for a coach demo (few users) |
| Git LFS | Not supported on Pages | Cannot use LFS as workaround |
| GitHub Release asset size | 2 GB per file | Video files go here instead |
| Build timeout | 10 minutes | Not relevant for static HTML/JS |

**AVI → MP4 conversion is mandatory.** Browsers do not support AVI natively. The pipeline outputs `.avi` by default. FFmpeg conversion must be added to the pre-upload workflow:
```bash
ffmpeg -i annotated.avi -c:v libx264 -c:a aac -movflags +faststart annotated.mp4
```
The `-movflags +faststart` flag moves the MP4 metadata to the start of the file, enabling streaming without full download.

## Suggested Build Order

Build components in this order to maximize working demos at each step:

1. **Data export tooling first** — Add `export_positions.py` to extract XY positions from the existing pipeline. This unblocks heatmap work and validates that the view transformer output is accessible. No frontend dependency.

2. **Static scaffold + manifest** — Create `index.html`, `match.html`, `manifest.json`, and `assets/` structure. Add one match entry pointing to placeholder data. Verify GitHub Pages deployment works before adding video or heatmap complexity.

3. **Video pipeline** — Convert AVI output to MP4, upload to GitHub Releases, update manifest with real URL, verify `<video>` element plays in browser. This is the highest-risk step (file size, format) so validate early.

4. **Stats panel** — Fetch `stats.json` and render possession %, top speeds, total distances. Vanilla JS + DOM manipulation. No external library needed.

5. **Match gallery** — Render match cards on `index.html` from `manifest.json`. Navigation to `match.html?id=X`.

6. **Heatmap** — Add D3 + d3-soccer, load `positions.json`, render KDE heatmap. Tabs or toggle between team 1 / team 2 / combined.

7. **Polish** — Thumbnails, responsive layout, loading states, error handling for missing data.

## Anti-Patterns

### Anti-Pattern 1: Committing Video Files to the Repo

**What people do:** Run `git add output_videos/annotated.avi` and commit.
**Why it's wrong:** AVI files commonly exceed GitHub's 100MB hard limit and will fail to push. Even smaller files bloat the repo permanently (git history preserves all versions). The 1GB repo limit is hit quickly with 2-3 match clips.
**Do this instead:** Upload via GitHub Releases UI. Reference the release asset URL in `manifest.json`. Keep only small data files (JSON) in the repo.

### Anti-Pattern 2: Hardcoding Match Data in HTML

**What people do:** Write match stats directly into `index.html` or `match.html` as inline HTML.
**Why it's wrong:** Adding a new match requires editing HTML. For 2-3 matches at launch this is tolerable, but the demo pitch will likely prompt "can you add our other games?" and it becomes maintenance debt.
**Do this instead:** All match data lives in `manifest.json` and per-match JSON files. HTML is a template; JavaScript populates it at load time.

### Anti-Pattern 3: Using Raw AVI for Browser Playback

**What people do:** Upload the `.avi` pipeline output directly and reference it in `<video>`.
**Why it's wrong:** AVI is not supported by any major browser's native HTML5 video element. The video simply will not play.
**Do this instead:** FFmpeg conversion to H.264 MP4 with faststart flag is mandatory before any browser embedding.

### Anti-Pattern 4: Fetching Large Position Arrays on Every Page Load

**What people do:** Include all 90 minutes of per-frame XY positions (potentially millions of data points) in `positions.json`.
**Why it's wrong:** A 90-minute match at 25fps = 135,000 frames. Two teams of 11 players = 2,970,000 coordinate pairs. At 12 bytes each this is ~35MB per match. Slow to load, slow to render KDE.
**Do this instead:** Downsample positions to 1Hz (one sample per second). 90 minutes × 11 players × 2 teams = 118,800 coordinate pairs. Roughly 1.4MB — fast to fetch and sufficient for heatmap density.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GitHub Releases | Direct URL in `<video src="">` | Free, permanent, no CORS issues for video elements |
| GitHub Pages | Static file hosting from repo root or `/docs` | No server-side code; pure HTML/CSS/JS |
| d3-soccer (npm/CDN) | Load from jsDelivr CDN or bundle locally | No npm build pipeline required when loaded from CDN |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Python pipeline → browser | File system: JSON files committed to repo | One-way; pipeline writes, browser reads |
| Python pipeline → video CDN | Manual upload workflow | Annotated MP4 → GitHub Release asset |
| `manifest.json` → index page | `fetch('manifest.json')` at page load | Single source of truth for all match metadata |
| `manifest.json` → match page | URL param `?id=X`, then fetch manifest to resolve URLs | Decouples page logic from hardcoded paths |
| stats.json → stats panel | `fetch(match.stats_url)` | Schema must stay stable across pipeline versions |
| positions.json → heatmap | `fetch(match.positions_url)` | New file type; requires new pipeline export step |

## Sources

- GitHub Pages official size limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits (HIGH confidence)
- GitHub large files official docs: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github (HIGH confidence)
- GitHub Releases video embedding pattern: https://www.cazzulino.com/github-pages-embed-video.html (MEDIUM confidence — community blog, consistent with official GitHub behavior)
- d3-soccer library (pitch + heatmap): https://github.com/probberechts/d3-soccer (HIGH confidence — official repo)
- D3 contourDensity for KDE: https://d3js.org/d3-contour/density (HIGH confidence — official D3 docs)
- FFmpeg AVI→MP4 with faststart: https://jshakespeare.com/encoding-browser-friendly-video-files-with-ffmpeg/ (MEDIUM confidence)
- GitHub community discussion on large MP4 on Pages: https://github.com/orgs/community/discussions/22302 (MEDIUM confidence — community discussion confirming Releases workaround)

---
*Architecture research for: Korner Flags static demo site (GitHub Pages)*
*Researched: 2026-03-16*
