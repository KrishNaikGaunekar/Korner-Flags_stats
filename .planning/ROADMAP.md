# Roadmap: Korner Flags

## Overview

Starting from a working CLI pipeline, this roadmap delivers a polished static demo site on GitHub Pages showing pre-processed NC State D1 soccer clips with annotated video, possession stats, speed/distance tables, and team heatmaps. The build order is risk-first: fix two confirmed pipeline bugs before touching the front end, validate YOLO detection on NC State footage before committing to full processing, then layer the site from scaffold to data to visualizations to polish.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Pipeline Fixes and Validation** - Fix two confirmed bugs and validate YOLO detection on NC State footage before any demo footage is processed (completed 2026-03-17)
- [x] **Phase 2: Data Export and Video Processing** - Generate all data artifacts (MP4, stats JSON, positions JSON, heatmap PNGs, manifest) needed by the site (completed 2026-03-17)
- [x] **Phase 3: Site Scaffold and Video Playback** - Deploy GitHub Pages site with Astro and get annotated video playing from GitHub Releases (completed 2026-03-19)
- [x] **Phase 4: Stats Visualizations** - Add possession and speed/distance panels to each clip page (completed 2026-03-19)
- [x] **Phase 5: Heatmap Visualizations** - Embed per-team heatmap PNGs and optionally add browser-side interactive heatmap (completed 2026-03-20)
- [ ] **Phase 6: Polish and Demo Readiness** - NC State content, plain-language labels, "How It Works" explainer, cross-browser QA

## Phase Details

### Phase 1: Pipeline Fixes and Validation
**Goal**: The pipeline produces correct speed, distance, and camera-correction stats on NC State footage, and YOLO detection quality is confirmed sufficient before any full-clip processing begins
**Depends on**: Nothing (first phase)
**Requirements**: PIPE-01, PIPE-02, PIPE-03, PIPE-04
**Success Criteria** (what must be TRUE):
  1. Running the pipeline on a clip with camera pan produces speed/distance values that incorporate camera movement corrections (view_transformer reads `position_adjusted`)
  2. Feature point refresh in the camera movement estimator works without AttributeError and tracking does not degrade on long clips
  3. Pipeline output is an H.264 MP4 file with `-movflags +faststart` that plays in Chrome, Firefox, and Safari without transcoding
  4. Running the pipeline on a 60-second NC State test clip shows at least 80% of visible players tracked with persistent IDs across frames
**Plans:** 3/3 plans complete

Plans:
- [x] 01-01-PLAN.md — Fix view transformer position key, camera movement estimator typo + mask, delete misspelled init files (PIPE-01, PIPE-02)
- [x] 01-02-PLAN.md — Rewrite save_video to H.264 MP4 via ffmpeg, update main.py defaults and stats path (PIPE-03)
- [x] 01-03-PLAN.md — Run pipeline on soccer clip and user validates detection quality (PIPE-04)

### Phase 2: Data Export and Video Processing
**Goal**: All data artifacts for 2-3 NC State clips exist in stable, committed form — annotated MP4s on GitHub Releases, stats JSON and positions JSON in the repo, team heatmap PNGs generated, and manifest.json populated with real URLs
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, HOST-01, HOST-02
**Success Criteria** (what must be TRUE):
  1. Running the pipeline on a full NC State clip produces a `positions.json` with per-player (x,y) coordinates downsampled to 1 Hz
  2. mplsoccer generates a heatmap PNG for each team from positions.json that is visually legible on a pitch background
  3. The stats JSON for each clip includes possession % per team, per-player max/avg speed (km/h), per-player total distance (m), and team assignment
  4. Annotated MP4 files are uploaded to GitHub Releases and accessible via stable CDN URLs (not Git LFS, not committed to repo tree)
  5. `manifest.json` committed to the repo lists each processed clip with its video URL, stats URL, heatmap URLs, and match metadata
**Plans:** 4/4 plans complete

Plans:
- [ ] 02-01-PLAN.md — Add positions.json export and restructure stats JSON to per-player format (DATA-01, DATA-03)
- [ ] 02-02-PLAN.md — Create generate_heatmaps.py for team heatmap PNG generation via mplsoccer (DATA-02)
- [ ] 02-03-PLAN.md — Create upload_release.py and data/manifest.json for GitHub Releases hosting (HOST-01, HOST-02, DATA-04)
- [ ] 02-04-PLAN.md — End-to-end integration verification and visual checkpoint (all requirements)

### Phase 3: Site Scaffold and Video Playback
**Goal**: A live GitHub Pages URL exists where a visitor can browse processed NC State clips and watch the annotated video with Plyr
**Depends on**: Phase 2
**Requirements**: SITE-01, SITE-02, SITE-03
**Success Criteria** (what must be TRUE):
  1. Visiting the project URL shows an index page with a gallery of 2-3 NC State match cards (names, thumbnails or placeholders, links)
  2. Clicking a match card navigates to a match detail page where the annotated MP4 plays in a Plyr video player loaded from the GitHub Releases CDN URL
  3. GitHub Actions automatically rebuilds and deploys the site on every push to main without manual steps
**Plans:** 3/3 plans complete

Plans:
- [ ] 03-01-PLAN.md — Scaffold Astro project, migrate data files, extract thumbnails, create GitHub Actions workflow (SITE-01)
- [ ] 03-02-PLAN.md — Build index gallery, clip detail pages, and Plyr video player components (SITE-02, SITE-03)
- [ ] 03-03-PLAN.md — Enable GitHub Pages, deploy, and verify live site end-to-end (SITE-01, SITE-02, SITE-03)

### Phase 4: Stats Visualizations
**Goal**: Each clip page displays possession percentage and per-player speed and distance data in a format a D1 coach recognizes and trusts
**Depends on**: Phase 3
**Requirements**: SITE-04, SITE-06, SITE-07, SITE-08
**Success Criteria** (what must be TRUE):
  1. Each clip page shows a possession % display (visual chart, not just a number) with per-team breakdown, including an accuracy disclaimer (e.g. "AI-estimated +/-5%")
  2. Each clip page shows a per-player table with speed (max and avg in km/h) and distance (m) using plain coaching language labels (not variable names or technical jargon)
  3. Pass counts, shots, shots on target, and assists appear on the page labeled as "Coming Soon" feature previews without displaying fabricated numbers
**Plans:** 2/2 plans complete

Plans:
- [ ] 04-01-PLAN.md — Create PossessionBar, PlayerStatsTable, and ComingSoonCards Astro components (SITE-04, SITE-06, SITE-07, SITE-08)
- [ ] 04-02-PLAN.md — Wire stats components into clip detail page with build-time data + visual verification (SITE-04, SITE-06, SITE-07, SITE-08)

### Phase 5: Heatmap Visualizations
**Goal**: Each clip page shows team heatmaps that make it immediately obvious where each team spent their time on the pitch
**Depends on**: Phase 4
**Requirements**: SITE-05
**Success Criteria** (what must be TRUE):
  1. Each clip page shows at least two heatmap images (one per team) rendered on a pitch background, generated from positions.json by mplsoccer
  2. The heatmaps are visually distinguishable by team color and labeled clearly enough that a coach can identify which team is which without reading a legend twice
**Plans:** 1/1 plans complete

Plans:
- [ ] 05-01-PLAN.md — Replace heatmaps placeholder with two-column PNG layout in clip detail page (SITE-05)

### Phase 6: Polish and Demo Readiness
**Goal**: The site looks and reads like a credible coaching tool — correct NC State content loaded, plain English throughout, "How It Works" explainer present, and no broken layouts or playback failures across modern browsers
**Depends on**: Phase 5
**Requirements**: CONT-01, CONT-02
**Success Criteria** (what must be TRUE):
  1. At least 2 NC State D1 soccer clips are processed and browsable on the live site (not placeholder content)
  2. A "How It Works" section on the site explains the AI pipeline in plain language that a coaching staff member with no ML background can follow
  3. No stat labels, chart axis titles, or UI strings contain variable names, technical jargon, or code identifiers visible to the end user
  4. The annotated video player loads and plays correctly in Chrome, Firefox, and Safari on desktop without buffering errors or missing controls
**Plans:** 1 plan

Plans:
- [ ] 06-01-PLAN.md — Add second clip to manifest, page intro, and How It Works section (CONT-01, CONT-02)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pipeline Fixes and Validation | 3/3 | Complete   | 2026-03-17 |
| 2. Data Export and Video Processing | 4/4 | Complete   | 2026-03-17 |
| 3. Site Scaffold and Video Playback | 3/3 | Complete   | 2026-03-19 |
| 4. Stats Visualizations | 2/2 | Complete   | 2026-03-19 |
| 5. Heatmap Visualizations | 1/1 | Complete   | 2026-03-20 |
| 6. Polish and Demo Readiness | 0/1 | Not started | - |
