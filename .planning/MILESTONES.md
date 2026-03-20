# Milestones

## v1.0 MVP (Shipped: 2026-03-20)

**Phases completed:** 6 phases, 14 plans
**Timeline:** 2026-03-15 → 2026-03-20 (4 days)
**Git range:** Pipeline fixes → Phase 6 polish
**Files changed:** ~30 files, 4,501 insertions

**Key accomplishments:**

1. Fixed pipeline bugs — view transformer now reads `position_adjusted`, camera movement estimator typo fixed, H.264 MP4 output via ffmpeg with faststart for browser compatibility
2. Built full data export layer — positions.json (1Hz downsampling), team heatmap PNGs via mplsoccer, per-player stats JSON, GitHub Releases upload helper
3. Launched GitHub Pages site with Astro — manifest-driven clip gallery, Plyr video player, GitHub Actions CI/CD
4. Added stats visualizations — possession % bar with AI disclaimer, per-player speed/distance tables in coaching language, coming-soon feature previews
5. Added team heatmap display — two-column PNG layout per clip page, team-colored headings, AI disclaimer
6. Demo-ready polish — 2-clip NC State gallery, coaching-audience intro, 4-step "How It Works" section, zero ML jargon in any user-visible text

**Requirements:** 20/20 v1 requirements shipped (PIPE-01–04, DATA-01–04, HOST-01–02, SITE-01–08, CONT-01–02)

---
