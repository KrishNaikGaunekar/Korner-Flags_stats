# Phase 3: Site Scaffold and Video Playback — Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Build and deploy an Astro static site to GitHub Pages with a manifest-driven clip gallery (index) and per-clip detail pages with a Plyr video player. GitHub Actions auto-deploys on every push to `main`. No stats panels, no heatmaps — those are Phase 4 and 5. No NC State branding — that's Phase 6.

</domain>

<decisions>
## Implementation Decisions

### Visual design
- Apple-esque sleek aesthetic: light background, clean sans-serif typography, generous whitespace, subtle card shadows
- Neutral color palette — no NC State red/white in Phase 3 (added in Phase 6 polish)
- **Index page:** clean grid of match cards — thumbnail + clip title + duration + "View Analysis →" CTA button
- **Clip detail page:** full-width Plyr player at top, content sections (stats, heatmaps) below as empty placeholders for Phase 4/5
- No extra decorative elements — coaching staff need to find the clip and click, not read marketing copy

### Thumbnails
- Extract one frame per annotated MP4 at the 5-second mark using ffmpeg
- ffmpeg command: `ffmpeg -ss 5 -i <video.mp4> -frames:v 1 <stem>_thumbnail.jpg`
- Thumbnails committed to `public/data/` alongside stats JSON and heatmap PNGs
- `thumbnail_url` field added to each clip entry in `manifest.json`

### Data file hosting strategy
- Stats JSON, heatmap PNGs, thumbnails, and manifest.json: **committed to repo** in `public/data/` — GitHub Pages serves them as static assets
- Astro reads `manifest.json` at **build time** (static site generation) — generates one HTML page per clip, no client-side data fetching, no JS required for data loading
- Adding a new clip = run pipeline → commit artifacts + updated manifest → `git push` → GitHub Actions auto-rebuilds

### manifest.json URL updates
- Current relative URLs (`output_videos/...`) must be updated to absolute or root-relative paths that resolve correctly from GitHub Pages
- Stats, heatmap, thumbnail, and positions URLs should use root-relative paths: `/data/<filename>` (served from `public/data/` in Astro)
- Video URLs remain absolute GitHub Releases CDN URLs (unchanged)

### Astro project structure
- Astro site lives in `site/` subfolder of the repo root (keeps Python pipeline and frontend cleanly separated)
- `site/public/data/` — static data files (manifest.json, stats JSONs, heatmap PNGs, thumbnails, positions JSONs)
- `site/src/pages/index.astro` — gallery index
- `site/src/pages/clips/[slug].astro` — dynamic per-clip detail pages (slug = `clip_id` from manifest)
- `site/src/components/` — shared layout components

### GitHub Actions deployment
- Official GitHub Pages approach: `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`
- No third-party actions (no `peaceiris/actions-gh-pages`)
- Trigger: every push to `main`
- Workflow builds from `site/` subdirectory (`cd site && npm run build`)
- Pages source: GitHub Actions (not a `gh-pages` branch)
- Deploy URL: `krishnaikgaunekar.github.io/Korner-Flags_stats` (custom domain deferred — will be added later when co-founder's refereeing integration is ready for launch)

### GitHub Pages setup
- Pages not yet enabled on the repo — Phase 3 plan must include enabling GitHub Pages via repo Settings → Pages → Source: GitHub Actions
- Astro `base` config must be set to `/Korner-Flags_stats` to handle the subpath correctly

### Claude's Discretion
- Exact Astro npm packages and versions
- Plyr integration method (npm package inside Astro or CDN script tag)
- CSS styling details (font choices, spacing values, shadow values) within the Apple-esque minimal aesthetic
- Astro layout component structure
- GitHub Actions workflow YAML specifics (Node version, cache strategy)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST use the `github-actions-deploy` skill before planning or implementing deployment.**

### Requirements
- `.planning/REQUIREMENTS.md` §Demo Site — SITE-01, SITE-02, SITE-03 definitions and acceptance criteria

### Data files
- `data/manifest.json` — current schema (1 clip, relative URLs that need updating to `/data/` paths)
- `output_videos/` — stats JSONs, heatmap PNGs, positions JSONs to be moved/copied to `site/public/data/`

### Prior context
- Phase 2 CONTEXT.md — manifest.json schema decisions (clip_id, video_url, stats_url, heatmap_team1_url, heatmap_team2_url, positions_url, duration_seconds, title)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `data/manifest.json` — single source of truth for clip metadata; Astro reads this at build time
- Annotated MP4s are already on GitHub Releases with stable CDN URLs
- Stats JSONs and heatmap PNGs are in `output_videos/` — need to be copied to `site/public/data/`

### Integration Points
- `manifest.json` `clip_id` field → Astro dynamic route slug (e.g. `clip_id: "08fd33_4"` → `/clips/08fd33_4`)
- `manifest.json` `video_url` → Plyr `src` attribute (absolute CDN URL, no change needed)
- `manifest.json` `thumbnail_url` → match card `<img>` src and Plyr poster attribute
- Phase 4 will add stats panels below the Plyr player — clip detail page layout must leave space for this

</code_context>

<deferred>
## Deferred Ideas

- Custom domain setup — deferred until co-founder's refereeing integration is ready for launch
- NC State branding (colors, logo) — Phase 6
- Stats and heatmap panels on clip pages — Phase 4 and Phase 5
- `base` path removal if custom domain is added later (removes the subpath issue)

</deferred>

<project_notes>
## Project Notes

- Co-founder is building a refereeing analysis feature in a separate workstream; the two will be integrated before the custom domain launch
- Demo target: coaching staff via email link from a mutual contact — site needs to impress at first glance, professional and credible
- Speed disclaimer (known 268 km/h issue from estimated pitch vertices) is Phase 6 work — not in Phase 3 scope

</project_notes>

---

*Phase: 03-site-scaffold-and-video-playback*
*Context gathered: 2026-03-17*
