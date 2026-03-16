# Korner Flags

## What This Is

AI-powered soccer/football video analysis tool. Takes any uploaded match video, runs YOLO11 detection + ByteTrack tracking, classifies teams by jersey color, calculates possession/speed/distance, and outputs an annotated video with stats overlay. Built to pitch to soccer coaches and demonstrate generalization across different teams, fields, and camera setups.

## Core Value

A coach can drop in any match video and immediately see annotated footage with player tracking, possession %, and speed/distance stats — no setup, no expertise required.

## Requirements

### Validated

- ✓ CLI pipeline processes any soccer video (python main.py --input video.mp4) — existing
- ✓ YOLO11 + ByteTrack detects and tracks players/ball with persistent IDs — existing
- ✓ KMeans jersey color clustering assigns players to teams — existing
- ✓ Possession % calculated with 15-frame smoothing — existing
- ✓ Player speed (km/h) and distance (m) via perspective transform — existing
- ✓ Annotated video output (ellipses, triangles, overlays) — existing
- ✓ Stats JSON output alongside annotated video — existing
- ✓ Camera movement estimation via optical flow — existing

### Active

- [ ] Static demo site on GitHub Pages showing pre-processed NC State D1 clips
- [ ] Annotated video player with stats panel (possession %, speed, distance) per clip
- [ ] Browse multiple pre-analyzed matches
- [ ] Heatmap generation (player position density over match)
- [ ] Pass/event detection flagging
- [ ] Demo-ready with 2-3 NC State D1 soccer clips processed and uploaded

### Out of Scope

- Live video upload + cloud processing — deferred to Phase 2 web app (needs GPU backend, too complex for 1-2 week demo deadline)
- Real-time processing — latency requirements incompatible with current pipeline
- Mobile app — not needed for coach demo
- Multi-match comparison dashboard — future feature after validated

## Context

- **Current state:** Working CLI pipeline. Run `python main.py --input match.mp4` to get annotated video + stats JSON.
- **Demo target:** NC State soccer coaching staff — needs to be polished, browsable at a URL, focused on D1 footage
- **Video footage:** NC State D1 soccer clips still need to be sourced/acquired
- **Domain:** User has a domain name available for deployment
- **Timeline:** 1-2 weeks to demo
- **Known gaps:** Heatmaps and pass/event detection not yet implemented — these are new features needed for demo
- **Codebase state:** See `.planning/codebase/` for full analysis. Main concerns include hardcoded paths in some areas, no test suite, perspective transform uses estimated pitch vertices.
- **PRD:** `docs/Korner-Flags-PRD.docx`

## Constraints

- **Timeline:** 1-2 weeks to working demo — static site first, backend upload later
- **Hosting:** GitHub Pages (static) for demo; FastAPI + Next.js backend planned for Phase 2
- **Tech stack:** Python, ultralytics YOLO11, roboflow supervision, OpenCV, scikit-learn — keep existing stack
- **Video footage:** Must use NC State D1 soccer clips specifically for the coaching demo
- **Processing:** Videos processed locally, results uploaded to repo — no cloud GPU required for Phase 1

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Static site first (GitHub Pages) | 1-2 week deadline makes backend too risky; pre-processing locally is reliable and zero server cost | — Pending |
| YOLO11 + ByteTrack for tracking | Industry-standard combo for sports tracking; already implemented and working | ✓ Good |
| KMeans jersey color for team assignment | No hardcoded player IDs needed; generalizes to any team | ✓ Good |
| FastAPI + Next.js for Phase 2 web app | Standard stack for ML-backed web apps; clean separation of concerns | — Pending |

---
*Last updated: 2026-03-16 after initialization*
