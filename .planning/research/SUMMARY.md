# Project Research Summary

**Project:** Korner Flags — Soccer Video Analysis Demo Site
**Domain:** Static sports video analysis demo site (GitHub Pages) with Python heatmap pipeline extension
**Researched:** 2026-03-16
**Confidence:** HIGH

## Executive Summary

Korner Flags is a coaching pitch tool, not a product launch — the goal is to make 2-3 pre-processed NC State clips look credible and polished for D1 coaching staff who already use Hudl and Wyscout daily. The recommended approach is a static site on GitHub Pages (Astro 5.x + Tailwind + Plyr + Chart.js), with annotated MP4 videos hosted on GitHub Releases (bypassing the 100 MB per-file hard limit) and JSON data files committed directly to the repo. A companion Python heatmap export script using mplsoccer generates per-team pitch heatmap PNGs from the existing perspective-transformed position data. The entire stack is deployable in 1-2 weeks with no backend infrastructure.

The single most important technical risk is that the existing codebase has two confirmed bugs — `position` vs `position_adjusted` in the view transformer and `old_feature` vs `old_features` in the camera movement estimator — that silently produce incorrect speed and distance values on any footage with camera pan. These bugs must be fixed before processing any demo footage or the stats shown to D1 coaches will be wrong in an obvious, credibility-destroying way. A second structural risk is YOLO model domain shift: the model was trained on specific broadcast footage and may perform poorly on NC State camera angles; this must be validated on a 60-second test clip before committing to full processing.

The recommended build order prioritizes risk reduction: fix known pipeline bugs first, validate YOLO detection on NC State footage second, then build the static site scaffold and video pipeline, and layer in data visualizations last. This order ensures that at every step there is a working, demonstrable artifact, and that the two highest-risk unknowns (data quality and detection quality) are resolved before front-end effort is committed.

---

## Key Findings

### Recommended Stack

The demo site requires no backend and no JavaScript framework. Astro 5.x generates a zero-JS static site with Tailwind for styling, deployed automatically to GitHub Pages via the official `withastro/action@v3` GitHub Action. Video playback uses Plyr 3.8.4 (7 kB gzipped) against MP4 files hosted as GitHub Release assets. Chart.js 4.5.1 via CDN handles possession and speed/distance charts. Alpine.js 3.14.x covers any lightweight interactivity (tab switching, clip selection) without adding React or Vue.

For the Python pipeline extension, mplsoccer 1.6.1 generates pitch heatmap PNGs from perspective-transformed XY positions. It requires Python >=3.10 and matplotlib >=3.6.0 (already a transitive dependency). Git LFS is explicitly unsupported on GitHub Pages — video files must never be committed to the repo tree.

**Core technologies:**
- Astro 5.x: static site generator — zero-JS default, official GitHub Pages action, templating scales to 2-3 match pages cleanly
- Plyr 3.8.4: video player — 7 kB gzipped, accessible, plays H.264 MP4 directly
- Chart.js 4.5.1: stats charts — framework-agnostic, sufficient for possession/speed/distance visualizations
- Tailwind CSS 3.x: styling — utility-first, integrates into Astro with zero config
- Alpine.js 3.14.x: UI interactivity — lightweight reactive state without React overhead
- GitHub Releases: video hosting — 2 GB per asset, permanent CDN URLs, no egress fees
- mplsoccer 1.6.1: heatmap generation — purpose-built pitch rendering, `bin_statistic` + `heatmap` in two lines
- Cloudflare R2: video hosting alternative — zero egress fees, 10 GB free tier (preferred if demo polish matters more than zero-config setup)

### Expected Features

Research confirmed that D1 coaching staff use Hudl and Wyscout daily and will compare this demo against those tools. The pitch differentiator is that the pipeline requires only a video file — no GPS hardware, no manual tagging, no expensive subscriptions — and this must be stated explicitly on the demo site.

**Must have (table stakes):**
- Annotated video player (H.264 MP4) — the core artifact; AVI-to-MP4 conversion is a hard blocker
- Multi-clip gallery with 2-3 NC State clips — single clip reads as a one-trick demo reel
- Possession % display (visual, not just a number) — the first stat coaches ask for
- Per-player speed and distance table — physical load metrics are expected by every D1 program
- Static per-team heatmap PNG — coaches recognize this format instantly; most visually impressive output
- Match metadata (teams, date, context) — anchors the demo in NC State reality
- "How It Works" section (4-step visual, after the video) — builds credibility for the pitch

**Should have (competitive):**
- Possession timeline (segmented bar over time) — upgrades possession % to show ebb and flow
- Per-player individual heatmaps — useful if coaches ask "where was player 7?"
- Speed timeline chart — shows athletic intensity over match (verify per-frame data export first)

**Defer (v2+):**
- Video upload and cloud processing — requires GPU backend, auth, storage infrastructure
- Pass network visualization — blocked on pass detection which is not in the pipeline
- Interactive heatmaps — worth building once a backend exists
- Player comparison view — scouting feature, relevant post-validation
- Coach accounts and saved sessions — requires auth backend; eliminates GitHub Pages entirely

### Architecture Approach

The architecture separates offline processing (Python pipeline on local machine) from the static demo site (GitHub Pages). JSON data files (stats.json ~10 KB, positions.json ~200 KB after 1 Hz downsampling) commit to the repo. Annotated MP4 files upload as GitHub Release assets and are referenced by URL in a `manifest.json` registry. The browser reads `manifest.json` at page load, renders a match gallery, and on match selection fetches stats/position JSON and sets the video `src` to the Release URL. No build step, no backend, no framework — vanilla HTML + JS is appropriate for this scope and deadline.

**Major components:**
1. Python CLI pipeline (existing) — YOLO detection, ByteTrack, annotation, stats JSON output
2. `export_positions.py` (new, ~50 lines) — extracts per-player XY positions from view transformer output into `positions.json` at 1 Hz
3. FFmpeg AVI-to-MP4 conversion step — mandatory pre-upload; must include `-movflags +faststart`
4. `manifest.json` — master registry of all matches; single source of truth for video URLs, stats URLs, position URLs
5. `index.html` + gallery JS — match browser rendered from `manifest.json`
6. `match.html` + player/stats/heatmap JS — single-match view with Plyr video player, Chart.js stats, D3 heatmap on pitch SVG
7. GitHub Actions workflow — automatic build and deploy via `withastro/action@v3`

### Critical Pitfalls

1. **Git LFS pointer files served by GitHub Pages** — GitHub Pages cannot resolve LFS pointers; visitors see a 130-byte text file instead of a video. Never use Git LFS for video files. Host all videos as GitHub Release assets or on Cloudflare R2.

2. **AVI output does not play in any browser** — The pipeline outputs `.avi` with XVID codec by default. No major browser supports XVID in a `<video>` element. Re-encode every clip with `ffmpeg -i annotated.avi -c:v libx264 -crf 23 -preset fast -movflags +faststart output.mp4` before upload. This step is mandatory; no workaround exists.

3. **Two confirmed pipeline bugs produce wrong speed/distance stats** — `view_transformer.py` line 54 reads `position` instead of `position_adjusted` (discarding camera pan corrections), and `camera_movement_estimator.py` line 65 assigns `old_feature` instead of `old_features` (breaking feature point refresh). Both bugs are silent — no error, just wrong numbers. Showing inflated speed stats to D1 coaching staff who know what 32 km/h looks like destroys credibility instantly. Fix both before processing any demo footage.

4. **Team color assignment fails when frame 0 lacks both teams** — KMeans trains on only the first frame. If the clip opens with a close-up, scoreboard, or partial view, color assignment is garbage for the entire clip and silently wrong. Visually audit the first 30 seconds of every annotated output clip before including it in the demo.

5. **YOLO domain shift on NC State camera angles** — The model was trained on specific broadcast footage; sideline or press-box angles at NC State may produce significantly degraded detection. Test on a 60-second clip before committing to full processing. If detection rate is poor, fine-tune on 20-50 labeled NC State frames via Roboflow.

---

## Implications for Roadmap

Based on combined research, the project has a clear dependency chain: fix known bugs → validate detection quality → build site scaffold and video pipeline → add data visualizations → polish and UX. This order ensures every phase has a shippable artifact and that expensive front-end work is not committed before the pipeline output quality is confirmed.

### Phase 1: Pipeline Bug Fixes and Validation

**Rationale:** Two confirmed bugs produce wrong speed/distance stats, and YOLO domain shift is an unknown that could invalidate the entire demo. Both must be resolved before any other work, because everything downstream depends on correct pipeline output. The bugs take under an hour to fix; the detection validation takes a day at most. This is the cheapest risk reduction available.

**Delivers:** Correct pipeline output on NC State footage; confidence that the demo stats are defensible to D1 coaching staff

**Addresses:** Speed/distance accuracy, team color assignment, YOLO generalization

**Avoids:** Pitfalls 4 (wrong speed stats), 5 (team color failure), 6 (YOLO domain shift)

**Research flag:** Standard — the two bug fixes are documented precisely in PITFALLS.md. Detection validation may require one round of Roboflow fine-tuning if YOLO fails; flag for deeper research only if detection quality is poor.

---

### Phase 2: Data Export and Video Processing

**Rationale:** The site cannot be built without the data files it displays. AVI-to-MP4 conversion and position data export are pre-conditions for all front-end work. This phase also forces the asset strategy decision (GitHub Releases vs. Cloudflare R2) before any video is committed.

**Delivers:** MP4 clips ready for browser playback; `stats.json` confirmed stable; `positions.json` generated and downsampled to 1 Hz; video assets uploaded to GitHub Releases; `manifest.json` populated with real URLs

**Uses:** FFmpeg (AVI-to-MP4 with faststart), mplsoccer (heatmap PNG generation), `export_positions.py` (new pipeline script)

**Avoids:** Pitfalls 1 (LFS trap), 2 (AVI incompatibility), 3 (repo size limit)

**Research flag:** Standard — GitHub Releases upload process is well-documented. mplsoccer heatmap generation has official docs with working code examples. The only uncertainty is per-frame speed data format; check whether the current stats JSON includes per-frame speed or only aggregates before committing to a speed timeline chart.

---

### Phase 3: Static Site Scaffold and Video Playback

**Rationale:** Get a deployed, working site with real video playing before adding any data visualization. This validates the GitHub Pages deployment pipeline, confirms Plyr works with Release asset URLs, and produces a demo-ready artifact even if subsequent phases slip.

**Delivers:** Deployed GitHub Pages site; `index.html` match gallery; `match.html` with working Plyr video player; GitHub Actions CI/CD; NC State match metadata displayed

**Uses:** Astro 5.x, Tailwind CSS 3.x, Plyr 3.8.4, `withastro/action@v3`, `manifest.json` pattern

**Implements:** Match index page, match viewer page, manifest-driven gallery pattern

**Avoids:** Pitfall 7 (video shown first, not technical metrics)

**Research flag:** Standard — Astro + GitHub Pages is a well-documented pattern with an official action. No novel integration required.

---

### Phase 4: Stats Visualizations

**Rationale:** With video playing and the site deployed, add the possession and speed/distance panels that contextualise what coaches are watching. These are table stakes for the demo and require the stable `stats.json` schema confirmed in Phase 2.

**Delivers:** Possession % donut/bar chart; team possession display with team colors; per-player speed and distance table; match stats panel displayed beside the video player

**Uses:** Chart.js 4.5.1 (with chartjs-plugin-datalabels 2.2.0 for possession chart), Alpine.js 3.14.x for tab state

**Implements:** `stats.js` module reading `stats.json`, Chart.js chart instances

**Research flag:** Standard — Chart.js possession and stats patterns are well-documented with no novel integration.

---

### Phase 5: Heatmap Visualizations

**Rationale:** The heatmap is the most visually impressive output and the strongest differentiator from Hudl (which requires manual tagging for equivalent output). It requires `positions.json` from Phase 2 and adds D3 rendering on top of the working site from Phase 3.

**Delivers:** Static per-team heatmap PNG (generated by mplsoccer, embedded as `<img>`); interactive browser-side heatmap using D3 + d3-soccer on position JSON; team toggle (team 1 / team 2 / combined)

**Uses:** mplsoccer 1.6.1 + scipy (offline PNG generation); D3.js + d3-soccer (browser-side KDE heatmap from positions.json)

**Implements:** `heatmap.js` module, D3 contourDensity on pitch SVG

**Research flag:** May need deeper research on d3-soccer API and D3 contourDensity integration — these are medium-complexity integrations with less beginner documentation than Chart.js. The mplsoccer offline PNG is standard and well-documented; implement that first as a fallback.

---

### Phase 6: Polish and Demo Readiness

**Rationale:** The demo is a coaching pitch. Credibility comes from how the site feels as much as what it shows. This phase focuses on UX, plain-English stat labels, loading states, cross-browser testing, and the "How It Works" explainer.

**Delivers:** All stats labeled with plain-English descriptions (no variable names); "How It Works" 4-step visual; thumbnails for match gallery cards; basic responsive layout; cross-browser video playback verified (Chrome, Firefox, Safari); "Looks Done But Isn't" checklist completed

**Avoids:** Pitfall 7 (technical metrics shown to coaches); browser compatibility failures

**Research flag:** Standard — UX and content decisions; no technical research needed.

---

### Phase Ordering Rationale

- **Bug fixes before everything:** Two silent bugs produce demonstrably wrong stats. Every hour of front-end work built on wrong output is wasted effort.
- **Data export before site:** The site is a display layer for the pipeline output. Without confirmed stable data files, front-end development is speculative.
- **Video playback before stats:** A working video demo is the minimum viable pitch. Stats and heatmaps amplify it; they are not prerequisites.
- **Stats before heatmaps:** Stats are lower complexity and higher table-stakes priority. Heatmaps are the differentiator but involve more novel integration (D3 + d3-soccer).
- **Polish last:** Polish phases should never block working features. A working-but-rough demo ships; a polished-but-incomplete demo does not.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1 (Detection validation):** If YOLO detection quality on NC State footage is poor, Roboflow fine-tuning workflow needs research — labeling strategy, training configuration, version pinning.
- **Phase 5 (Heatmap):** D3-soccer library API and d3.contourDensity integration with pitch SVG coordinates has less beginner documentation. Allocate time for implementation research or use the mplsoccer static PNG as the primary deliverable with browser-side heatmap as a stretch goal.

Phases with standard patterns (skip research-phase):
- **Phase 2 (Data export):** mplsoccer and FFmpeg both have comprehensive official documentation.
- **Phase 3 (Site scaffold):** Astro + GitHub Pages is the most-documented static site deployment pattern in 2025.
- **Phase 4 (Stats charts):** Chart.js possession and bar chart patterns are fully documented with working examples.
- **Phase 6 (Polish):** UX decisions; no technical unknowns.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core libraries verified via official docs and CDN; GitHub Pages and Releases constraints verified against official GitHub docs |
| Features | MEDIUM-HIGH | Competitor analysis confirmed across Hudl, Wyscout, Metrica Sports; coaching workflow confirmed via NCAA and performance analyst sources; some features (speed timeline) have a data format dependency to verify |
| Architecture | HIGH | GitHub Pages limits verified from official docs; GitHub Releases video embedding pattern verified from multiple community sources; AVI/MP4 codec support verified from MDN/caniuse |
| Pitfalls | HIGH | Pipeline bugs confirmed in first-party CONCERNS.md audit; GitHub LFS limitation confirmed from official GitHub docs and community issues; AVI codec failure confirmed from MDN; YOLO domain shift from peer-reviewed papers |

**Overall confidence:** HIGH

### Gaps to Address

- **Per-frame speed data format:** The current `stats.json` likely contains only aggregate speed stats, not per-frame or per-window data. A speed timeline chart requires per-frame export. Verify the existing JSON schema before committing to this feature; if not present, add a pipeline output tweak in Phase 2.
- **YOLO detection quality on NC State footage:** Unknown until tested. This is the largest single risk. If detection quality is poor (less than 80% of visible players detected), the path is fine-tuning on NC State frames — add 1-2 days if needed.
- **Perspective transform calibration accuracy:** The `view_transformer.py` estimates pitch vertices proportionally rather than from calibrated keypoints. Speed/distance values are approximate. Add a visible disclaimer ("estimates are approximate; calibrated field registration planned for v2") on the demo site to pre-empt coaching staff questions.
- **mplsoccer vs D3 heatmap decision:** Both approaches are researched. The recommendation is to generate static PNGs with mplsoccer (fast, professional quality, zero browser complexity) and add the browser-side D3 heatmap as a stretch goal in Phase 5. If time pressure hits, drop the D3 interactive heatmap and ship only the static PNG.

---

## Sources

### Primary (HIGH confidence)

- GitHub Pages official limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GitHub large files official docs: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Git LFS does not work with GitHub Pages (official community): https://github.com/orgs/community/discussions/50337
- MDN Web Docs — Video codec guide: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Video_codecs
- Can I Use — MPEG-4/H.264: https://caniuse.com/mpeg4
- mplsoccer PyPI (version 1.6.1, Python >=3.10): https://pypi.org/project/mplsoccer/
- mplsoccer heatmap docs: https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_heatmap.html
- Chart.js docs (version 4.5.1): https://www.chartjs.org/docs/latest/api/
- Astro GitHub Pages deployment: https://docs.astro.build/en/guides/deploy/github/
- d3-soccer library: https://github.com/probberechts/d3-soccer
- D3 contourDensity: https://d3js.org/d3-contour/density
- Codebase-specific bugs: C:/Korner flag/.planning/codebase/CONCERNS.md (first-party audit)

### Secondary (MEDIUM confidence)

- Cloudflare R2 zero-egress pricing and video serving: https://community.cloudflare.com/t/can-we-serve-video-with-r2/406275
- GitHub Releases video embedding pattern: https://www.cazzulino.com/github-pages-embed-video.html
- FFmpeg AVI-to-MP4 with faststart: https://jshakespeare.com/encoding-browser-friendly-video-files-with-ffmpeg/
- GitHub community discussion on large MP4 on Pages: https://github.com/orgs/community/discussions/22302
- YOLO-Based Object Detection and Player Tracking — Zenodo: https://zenodo.org/records/16929566
- Camera Calibration in Sports with Keypoints — Roboflow: https://blog.roboflow.com/camera-calibration-sports-computer-vision/
- Deep learning detection of players and heatmap generation — Emerald: https://emerald.com/insight/content/doi/10.1108/aci-07-2024-0257/full/html
- Metrica Sports automatic tracking: https://www.metrica-sports.com/help-center/playbase-fundamentals/automatic-player-tracking
- Heat Maps in Soccer — Soccer Wizdom: https://soccerwizdom.com/2025/03/13/heat-maps-in-soccer-tracking-movement-performance-and-strategy/
- Digital Shift in College Athletics — Emory Wheel: https://www.emorywheel.com/article/2025/12/the-digital-shift-in-college-athletics-how-technology-is-changing-coaching-strategies

---

*Research completed: 2026-03-16*
*Ready for roadmap: yes*
