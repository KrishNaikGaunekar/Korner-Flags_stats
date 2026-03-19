# Requirements: Korner Flags

**Defined:** 2026-03-16
**Core Value:** A coach can drop in any match video and immediately see annotated footage with player tracking, possession %, and speed/distance stats — no setup, no expertise required.

## v1 Requirements

### Pipeline Fixes

- [x] **PIPE-01**: Fix `view_transformer.py` to read `position_adjusted` instead of `position` so camera movement corrections apply to speed/distance calculations
- [x] **PIPE-02**: Fix `old_feature` → `old_features` bug in camera movement estimator so feature refresh actually works
- [x] **PIPE-03**: Pipeline outputs H.264 MP4 with `-movflags +faststart` (browser-compatible) instead of AVI
- [x] **PIPE-04**: YOLO detection validated on at least one NC State D1 soccer clip before full processing

### Data Export

- [x] **DATA-01**: Pipeline exports `positions.json` with per-player (x,y) coordinates downsampled to 1Hz for heatmap generation
- [x] **DATA-02**: Pipeline generates team heatmap PNGs (one per team) using mplsoccer for each processed clip
- [x] **DATA-03**: Stats JSON schema includes possession %, per-player speed (max/avg km/h), per-player total distance (m), and team assignment
- [x] **DATA-04**: `manifest.json` committed to repo listing all processed clips with video URL, stats URL, heatmap URLs, and match metadata

### Video Hosting

- [x] **HOST-01**: Processed MP4 annotated videos uploaded to GitHub Releases (bypasses 100 MB Pages file limit)
- [x] **HOST-02**: Video URLs in manifest.json point to stable GitHub Release CDN URLs

### Demo Site

- [x] **SITE-01**: GitHub Pages site deployed and accessible at project URL
- [x] **SITE-02**: Index page shows gallery of all processed NC State clips (manifest-driven, 2-3 clips)
- [x] **SITE-03**: Each clip page shows annotated video player (Plyr) with H.264 MP4 from GitHub Releases
- [ ] **SITE-04**: Each clip page shows stats panel: possession % (per team), per-player speed and distance
- [ ] **SITE-05**: Each clip page shows team heatmaps (static PNG, one per team) from mplsoccer output
- [ ] **SITE-06**: Possession % displayed with accuracy disclaimer (e.g. "AI-estimated ±5%")
- [ ] **SITE-07**: Stats labeled in plain coaching language (not technical jargon)
- [ ] **SITE-08**: Pass counts, shots, shots on target, assists shown as "Coming Soon" feature previews

### Content

- [ ] **CONT-01**: Minimum 2 NC State D1 soccer clips processed and available on the site
- [ ] **CONT-02**: "How It Works" section explaining the AI pipeline in plain language for coaching audience

## v2 Requirements

### Event Detection

- **EVNT-01**: Per-player pass count detected from video
- **EVNT-02**: Per-player shot count detected from video
- **EVNT-03**: Shots on target detected from video
- **EVNT-04**: Assist attribution (player who last touched before a goal)
- **EVNT-05**: Pass network visualization per team

### Interactive Heatmaps

- **HEAT-01**: Browser-side interactive heatmap with per-player toggle (D3 + d3-soccer)
- **HEAT-02**: Heatmap time-slice filtering (first half / second half / full match)

### Web Upload App

- **UPLOAD-01**: User can upload a soccer video and get it processed
- **UPLOAD-02**: FastAPI backend processes uploaded video with YOLO pipeline
- **UPLOAD-03**: Processed results displayed on a match detail page
- **UPLOAD-04**: Processing status shown while video is being analyzed

### Deployment

- **DEPLOY-01**: Custom domain configured for the web app
- **DEPLOY-02**: Backend deployed on Railway or Render

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time video processing | Requires GPU backend and streaming infrastructure — v2+ |
| Live video upload in demo | Too complex for 1-2 week timeline; static pre-processed demo is sufficient |
| Per-player interactive heatmaps in v1 | D3 implementation adds 2-3 days; static PNG achieves the visual goal for demo |
| Heuristic pass/shot stats in v1 | Inaccurate stats would damage credibility with D1 coaching audience |
| Mobile app | Web-first; not needed for coach demo pitch |
| Multi-match comparison dashboard | Future feature after initial validation |
| Real-time score overlay | Requires manual input or different data source |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 1 | Complete |
| PIPE-02 | Phase 1 | Complete |
| PIPE-03 | Phase 1 | Complete |
| PIPE-04 | Phase 1 | Complete |
| DATA-01 | Phase 2 | Complete |
| DATA-02 | Phase 2 | Complete |
| DATA-03 | Phase 2 | Complete |
| DATA-04 | Phase 2 | Complete |
| HOST-01 | Phase 2 | Complete |
| HOST-02 | Phase 2 | Complete |
| SITE-01 | Phase 3 | Complete |
| SITE-02 | Phase 3 | Complete |
| SITE-03 | Phase 3 | Complete |
| SITE-04 | Phase 4 | Pending |
| SITE-06 | Phase 4 | Pending |
| SITE-07 | Phase 4 | Pending |
| SITE-08 | Phase 4 | Pending |
| SITE-05 | Phase 5 | Pending |
| CONT-01 | Phase 6 | Pending |
| CONT-02 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-16*
*Last updated: 2026-03-16 after roadmap creation*
