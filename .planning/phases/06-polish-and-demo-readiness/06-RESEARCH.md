# Phase 6: Polish and Demo Readiness — Research

**Researched:** 2026-03-20
**Domain:** Static site content polish — Astro index page, manifest.json, CSS layout
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- "How It Works" lives on the index page, below the clip gallery — no separate page, no extra navigation
- 3-4 plain-English steps with emoji icons — e.g. 🎬 Upload → 🤖 AI Analysis → 📊 Stats
- Zero ML jargon — written for a coaching staff member with no technical background
- Pure static HTML — no client-side JS, consistent with the no-JS pattern from prior phases
- Second clip entry duplicates clip 1's assets (same video URL, same stats/heatmap/thumbnail files) but with a different title: "NC State Match Clip 2"
- `clip_id` must be unique for the second entry
- Add a short one-liner header to the index page above the clip gallery
- Wording example: "Korner Flags — AI-powered match analysis for soccer coaches."
- Clip cards use the `title` field from manifest as-is — no new data fields needed
- Duration, match date, opponent are NOT added

### Claude's Discretion
- Exact emoji choices for the How It Works steps
- Precise wording of each step in the explainer
- CSS layout for the How It Works section (consistent with existing Apple-esque card/section style)
- Whether the one-liner header is an `<h1>` subtitle, `<p>` lead-in, or a hero subtitle element

### Deferred Ideas (OUT OF SCOPE)
- NC State branding (colors, logo) — keep neutral Apple-esque aesthetic for demo
- Custom domain — deferred per Phase 3 decision
- Replacing placeholder second clip with real NC State footage — manual step before actual demo
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CONT-01 | Minimum 2 NC State D1 soccer clips processed and available on the site | manifest.json second entry pattern documented; ClipCard + getStaticPaths confirmed to auto-scale |
| CONT-02 | "How It Works" section explaining the AI pipeline in plain language for coaching audience | Section insertion point identified; CSS pattern documented; jargon audit complete |
</phase_requirements>

---

## Summary

Phase 6 is purely a content and layout phase — no new pipeline code, no new data formats, no new Astro features. All three deliverables (second clip, one-liner header, How It Works section) are additive changes to two files: `site/public/data/manifest.json` and `site/src/pages/index.astro`.

The index page is currently 33 lines and has zero introductory copy above the gallery — it goes straight from the BaseLayout's site-header into a `<section class="gallery">`. The one-liner header and How It Works section both insert below the BaseLayout header slot and above or after the gallery respectively, with no layout restructuring required.

The second clip entry in manifest.json is a drop-in: the `getStaticPaths()` call in `[slug].astro` maps every entry to a route automatically, so a new entry with a unique `clip_id` generates a fully functional clip detail page with no code changes. The only structural constraint is that `clip_id` must be unique (it becomes the URL slug), and all referenced asset filenames must exist in `site/public/data/`.

Jargon audit result: no user-visible technical strings were found in the rendered UI. All column headers in PlayerStatsTable use plain language ("Player", "Top Speed", "Avg Speed", "Distance"). The variable names `max_speed_kmh`, `avg_speed_kmh`, `distance_m`, `team_1_percent` are internal JS only and never rendered as text.

**Primary recommendation:** Two focused tasks — (1) add second manifest entry + one-liner header to index.astro, (2) add How It Works section to index.astro using the card pattern from `.stats-section`/`.heatmaps-section`.

---

## Standard Stack

No new libraries. This phase uses only what is already installed.

### Core (already in place)
| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| Astro | existing (site/) | Static site generation | No new config needed |
| Plyr | existing (site/) | Video player | No changes needed |
| Inter (Google Fonts) | existing | Typography | Already loaded in BaseLayout |

### Installation
None required.

---

## Architecture Patterns

### Current index.astro Structure (annotated)

```
site/src/pages/index.astro (33 lines)
│
├── Frontmatter: imports BaseLayout, ClipCard, manifestData
│
└── <BaseLayout title="Match Analysis">
    └── <section class="gallery">           ← only content currently
        ├── <h2 class="gallery-heading">Match Clips</h2>
        └── <div class="gallery-grid">      ← auto-fill grid, minmax(320px, 1fr)
            └── {clips.map(clip => <ClipCard />)}
```

**Insertion points for Phase 6:**
- One-liner header: a new `<p>` or `<h2>` element inserted BEFORE `<section class="gallery">`, inside `<BaseLayout>`
- How It Works section: a new `<section class="how-it-works">` inserted AFTER `<section class="gallery">`, inside `<BaseLayout>`

### Pattern 1: Section Card (established in [slug].astro)

Every content section on the site uses this CSS block verbatim. The How It Works section MUST use it.

```css
/* Source: site/src/pages/clips/[slug].astro — .stats-section and .heatmaps-section */
margin-top: 2.5rem;
padding: 2rem;
background: #ffffff;
border-radius: 12px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
```

Section heading inside the card:
```css
/* h3 pattern used in both stats-section and heatmaps-section */
font-size: 1.15rem;
font-weight: 600;
margin-bottom: 1rem;   /* or 0.25rem if subtitle follows */
color: #1d1d1f;        /* inherited from body, but explicit in cards */
```

Subtitle / supporting text:
```css
/* .heatmaps-subtitle pattern */
font-size: 0.95rem;
color: #6e6e73;
margin-bottom: 1.25rem;
```

### Pattern 2: Infographic Row (How It Works steps)

The CONTEXT.md specifies an "infographic row" of steps with icon + title + description. The recommended layout is a flex/grid row of step cards, matching the `auto-fill` gallery grid style. Each step card should be self-contained — icon on top, bold step title, one-sentence plain-English description.

Reference grid pattern from ComingSoonCards:
```css
/* Source: site/src/components/ComingSoonCards.astro */
display: grid;
grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
gap: 16px;
```

For How It Works, slightly wider cards are appropriate (minmax ~200px) since each step has a sentence of description.

### Pattern 3: Manifest Second Entry (CONT-01)

```json
// Source: site/public/data/manifest.json — existing entry as reference
{
  "clip_id": "08fd33_4_clip2",         // MUST be unique — becomes URL slug /clips/08fd33_4_clip2/
  "title": "NC State Match Clip 2",    // shown on ClipCard
  "duration_seconds": 30.0,            // ClipCard renders as "0:30"
  "video_url": "https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4",
  "thumbnail_url": "/data/08fd33_4_thumbnail.jpg",
  "stats_url": "/data/08fd33_4_annotated_stats.json",
  "heatmap_team1_url": "/data/08fd33_4_heatmap_team1.png",
  "heatmap_team2_url": "/data/08fd33_4_heatmap_team2.png",
  "positions_url": "/data/08fd33_4_positions.json"
}
```

All asset filenames point to existing files already in `site/public/data/` — no new files needed.

### Pattern 4: One-Liner Header on Index Page

BaseLayout already renders a global site header with `<h1>Korner Flags</h1>` and `<p>AI-Powered Soccer Video Analysis</p>`. The one-liner header for index.astro is a page-level element, not a duplicate of the global header. It should be a brief contextual intro paragraph styled as a lead-in, using the secondary text color:

```css
/* Recommended — consistent with .heatmaps-subtitle pattern */
font-size: 1rem;
color: #6e6e73;
margin-bottom: 2rem;
```

As a `<p class="page-intro">` element rather than a heading — the global `<h1>` already sets the page identity. A `<p>` tag avoids creating a heading hierarchy conflict.

### Anti-Patterns to Avoid

- **Nested headings out of order:** BaseLayout renders `<h1>` globally. Index page uses `<h2>` for "Match Clips". How It Works should use `<h2>` (same level as gallery heading), not `<h3>`.
- **Adding `clip_id` values that match the slug pattern but reference missing assets:** Astro build will succeed but the detail page will have broken images. All asset paths in the second entry must point to files that already exist in `site/public/data/`.
- **Using `<h1>` for the one-liner header:** The global BaseLayout `<h1>` already claims that heading level. Adding a second `<h1>` on the index page breaks accessibility and heading semantics.
- **Using client-side JS in How It Works:** All prior phases use pure static HTML for content sections on the index page. No `client:*` directives, no `<script>` tags.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Second clip page routing | New route file or redirect logic | Just add a second entry to manifest.json — `getStaticPaths()` handles route generation automatically |
| How It Works layout | Custom JS carousel or accordion | Plain CSS grid/flex, static HTML |
| Emoji rendering consistency | Custom SVG icons for steps | Standard Unicode emoji — same cross-platform rendering as existing ComingSoonCards approach (note: ComingSoonCards uses SVG padlock specifically because emoji rendering is inconsistent for that icon; for step emojis like 🎬📊 the CONTEXT.md explicitly calls for emoji) |

---

## Common Pitfalls

### Pitfall 1: clip_id Collision
**What goes wrong:** If the second manifest entry uses the same `clip_id` as clip 1 (`08fd33_4`), `getStaticPaths()` generates duplicate routes and Astro build either errors or silently overwrites.
**Why it happens:** manifest.json has no uniqueness enforcement.
**How to avoid:** Use a distinct `clip_id` value. Suggested: `08fd33_4_clip2` (ties back to original footage, clearly a duplicate placeholder).
**Warning signs:** Astro build log showing "duplicate params" or only one clip page generated.

### Pitfall 2: Stats JSON Import Path Mismatch
**What goes wrong:** `[slug].astro` imports stats JSON using the pattern `` `../../../public/data/${clip.clip_id}_annotated_stats.json` ``. If the second entry's `clip_id` doesn't match the filename of an existing stats JSON, the build fails with a module not found error.
**Why it happens:** Vite's dynamic import resolves the template literal at build time and expects the file to exist.
**How to avoid:** The second entry's `clip_id` must satisfy: `public/data/${clip_id}_annotated_stats.json` exists. Since clip 2 reuses clip 1's assets, `clip_id` should be chosen so this file exists — or the stats_url in manifest should point to the existing file and the `clip_id` chosen accordingly. Simplest solution: use `clip_id: "08fd33_4_clip2"` and create a symlink or copy of the stats file as `08fd33_4_clip2_annotated_stats.json`, OR restructure to use a different clip_id that exactly matches an existing stats filename. The safest approach: choose `clip_id` to match an existing `_annotated_stats.json` filename (i.e., reuse `08fd33_4` exactly is not possible due to route collision, so copy/rename the stats JSON).
**Warning signs:** `Error: Failed to resolve import` during `npm run build` in the site/ directory.

### Pitfall 3: BASE_URL in Index Page Styles
**What goes wrong:** New styles scoped in index.astro that reference public assets (images, etc.) need to use the `${base}` stripping pattern. This is not an issue for the How It Works section (no asset references needed — emoji only) but would matter if thumbnails were added inline.
**Why it happens:** Astro's `BASE_URL` is `/Korner-Flags_stats` and public assets must have the base prepended.
**How to avoid:** The How It Works section uses emoji, not image assets — this pitfall does not apply.

### Pitfall 4: Heading Hierarchy in How It Works
**What goes wrong:** Using `<h1>` or skipping heading levels in the How It Works section creates accessibility violations and confuses screen readers.
**How to avoid:** Section heading = `<h2>` (same as `.gallery-heading`). Step titles within the section = `<h3>` if needed, or `<strong>/<p>` if steps are brief enough.

### Pitfall 5: Speed Values Without Disclaimer
**What goes wrong:** The stats show unrealistically high speed values (e.g., 268 km/h max — flagged in STATE.md Phase 1 notes). The second clip page will display the same data. This is a known limitation documented in STATE.md.
**How to avoid:** The existing `PlayerStatsTable` already renders a disclaimer: "AI-estimated from video — values are approximate". No new disclaimer needed. However, the planner should verify this disclaimer is visible when reviewing the second clip page.

---

## Code Examples

### Second manifest.json Entry
```json
// Source: analysis of site/public/data/manifest.json + site/src/pages/clips/[slug].astro build pattern
{
  "clips": [
    {
      "clip_id": "08fd33_4",
      "title": "NC State Match Clip 1",
      "duration_seconds": 30.0,
      "video_url": "https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4",
      "thumbnail_url": "/data/08fd33_4_thumbnail.jpg",
      "stats_url": "/data/08fd33_4_annotated_stats.json",
      "heatmap_team1_url": "/data/08fd33_4_heatmap_team1.png",
      "heatmap_team2_url": "/data/08fd33_4_heatmap_team2.png",
      "positions_url": "/data/08fd33_4_positions.json"
    },
    {
      "clip_id": "08fd33_4_clip2",
      "title": "NC State Match Clip 2",
      "duration_seconds": 30.0,
      "video_url": "https://github.com/KrishNaikGaunekar/Korner-Flags_stats/releases/download/clip-08fd33_4/08fd33_4_annotated.mp4",
      "thumbnail_url": "/data/08fd33_4_thumbnail.jpg",
      "stats_url": "/data/08fd33_4_annotated_stats.json",
      "heatmap_team1_url": "/data/08fd33_4_heatmap_team1.png",
      "heatmap_team2_url": "/data/08fd33_4_heatmap_team2.png",
      "positions_url": "/data/08fd33_4_positions.json"
    }
  ]
}
```

Note on stats import: `[slug].astro` builds the import path as `${clip_id}_annotated_stats.json`. Since `clip_id` is `08fd33_4_clip2`, the build will look for `public/data/08fd33_4_clip2_annotated_stats.json`. This file does not yet exist — the plan MUST include creating it (a copy of the existing stats file) before or alongside the manifest update.

### Index Page After Phase 6 (structural sketch)
```astro
<!-- site/src/pages/index.astro — annotated target state -->
<BaseLayout title="Match Analysis">

  <!-- NEW: one-liner page intro -->
  <p class="page-intro">Korner Flags — AI-powered match analysis for soccer coaches.</p>

  <!-- EXISTING: clip gallery (unchanged) -->
  <section class="gallery">
    <h2 class="gallery-heading">Match Clips</h2>
    <div class="gallery-grid">
      {manifestData.clips.map((clip) => <ClipCard clip={clip} />)}
    </div>
  </section>

  <!-- NEW: How It Works section -->
  <section class="how-it-works">
    <h2>How It Works</h2>
    <p class="hiw-subtitle">From raw match footage to actionable coaching insights in minutes.</p>
    <div class="hiw-steps">
      <!-- 4 step cards: Record, Analyze, Review, Coach -->
    </div>
  </section>

</BaseLayout>
```

### How It Works Step Card Structure
```html
<!-- Each step — pure static HTML, no JS -->
<div class="hiw-step">
  <span class="hiw-icon" aria-hidden="true">🎬</span>
  <h3 class="hiw-step-title">Record</h3>
  <p class="hiw-step-desc">Film any match with a standard camera.</p>
</div>
```

### CSS for How It Works Section
```css
/* Follows the .stats-section / .heatmaps-section card pattern exactly */
.how-it-works {
  margin-top: 2.5rem;
  padding: 2rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.how-it-works h2 {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #1d1d1f;
}

.hiw-subtitle {
  font-size: 0.95rem;
  color: #6e6e73;
  margin-bottom: 1.5rem;
}

.hiw-steps {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.25rem;
}

.hiw-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.5rem 1rem;
  background: #f5f5f7;
  border-radius: 12px;
}

.hiw-icon {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  line-height: 1;
}

.hiw-step-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 0.4rem;
}

.hiw-step-desc {
  font-size: 0.85rem;
  color: #6e6e73;
  line-height: 1.4;
}

/* Page intro — above gallery */
.page-intro {
  font-size: 1rem;
  color: #6e6e73;
  margin-bottom: 2rem;
}
```

---

## Jargon Audit (CONT-02 prerequisite)

A full scan of all `.astro` files in `site/src/` confirms:

**No user-visible jargon found.** All variable names (`max_speed_kmh`, `avg_speed_kmh`, `distance_m`, `team_1_percent`, `team_2_percent`, `clip_id`, `positions_url`) appear only in JS/frontmatter, never in rendered HTML text.

**Rendered UI strings that are coach-facing:**
- Column headers: "Player", "Top Speed", "Avg Speed", "Distance" — plain language, compliant with SITE-07
- Possession bar labels: "Team 1", "Team 2" — acceptable for placeholder
- Heatmap subtitle: "Where each team spent most of their time on the pitch" — plain language
- Disclaimer: "AI-estimated from video — values are approximate" — plain language
- Coming Soon cards: "Pass Counts", "Shots", "Shots on Target", "Assists" — plain language
- BaseLayout global header: "AI-Powered Soccer Video Analysis" — plain language

**Conclusion:** CONT-02's jargon requirement is already satisfied for existing content. The new "How It Works" section must maintain the same standard (no mention of YOLO, ByteTrack, KMeans, optical flow, etc.).

---

## Cross-Browser Video Playback Assessment

**Plyr setup (site/src/components/VideoPlayer.astro):**
- Uses `import Plyr from 'plyr'` — bundled by Astro/Vite, not a CDN import
- Video source: `<source src={src} type="video/mp4" />`
- H.264 MP4 with `-movflags +faststart` — confirmed in Phase 1 decisions

**Cross-browser analysis (HIGH confidence — based on established web standards):**
- Chrome/Edge: Full support for H.264 MP4 + Plyr. No known issues.
- Firefox: Supports H.264 MP4 (via system/bundled decoder on all platforms). No issues expected.
- Safari: H.264 is natively supported and preferred. The `-movflags +faststart` flag ensures Safari can start playback without downloading the full file — this is the critical flag for Safari's progressive download behavior. Already implemented in Phase 1.
- Mobile Safari: `playsinline` attribute is already present on the `<video>` element, which prevents full-screen forced playback on iOS. Already implemented.

**GitHub Releases CDN URLs:** These are standard HTTPS URLs served from `objects.githubusercontent.com`. They support `Range` requests (required for video scrubbing). No CORS issues for same-origin page loads from GitHub Pages.

**No cross-browser action items needed for Phase 6.** The video stack is already correctly configured.

---

## State of the Art

| Old Approach | Current Approach | Notes |
|--------------|------------------|-------|
| Hardcoded clip list in page template | Manifest-driven `getStaticPaths()` | Already in place — adding clip 2 is a one-line manifest edit (plus stats file copy) |
| Separate explanation page | Inline How It Works section | Decision locked in CONTEXT.md |

---

## Open Questions

1. **Stats file copy for clip 2**
   - What we know: `[slug].astro` derives the stats import path from `clip_id` directly. The second entry uses `clip_id: "08fd33_4_clip2"`, so it expects `08fd33_4_clip2_annotated_stats.json`.
   - What's unclear: Should the plan create this file as a file copy (cp command), or should the `clip_id` be chosen differently to avoid needing a new file?
   - Recommendation: The plan should include a task to copy `08fd33_4_annotated_stats.json` to `08fd33_4_clip2_annotated_stats.json` in `site/public/data/`. This is a ~2KB JSON file and a simple copy. Alternatively the planner could choose `clip_id: "08fd33_4"` and route deduplication strategy — but route collision is the bigger problem. File copy is simplest.

2. **Index page `<title>` tag**
   - What we know: BaseLayout renders `<title>{title} | Korner Flags</title>`. Index.astro passes `title="Match Analysis"`.
   - What's unclear: Should the title be updated to something more descriptive for demo (e.g. "NC State Clips") given the coaching audience?
   - Recommendation: This is discretion territory — low-risk change, low-impact. Planner can include or skip.

---

## Validation Architecture

`nyquist_validation` is `true` in `.planning/config.json`.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Astro build (static site generation) |
| Config file | `site/astro.config.mjs` |
| Quick run command | `cd site && npm run build` |
| Full suite command | `cd site && npm run build && npm run preview` |

No unit test framework (Jest/Vitest) is present or needed — this phase is purely HTML/CSS/JSON edits. The Astro build is the definitive test: if it completes without errors and produces the expected static files, correctness is confirmed.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CONT-01 | Two clip cards appear on index page; two clip detail pages generated at `/clips/08fd33_4/` and `/clips/08fd33_4_clip2/` | Build smoke test | `cd site && npm run build && ls site/dist/clips/` | ❌ Wave 0 (no test file — verified by build output) |
| CONT-02 | How It Works section present in `dist/index.html` with at least one step | Build smoke test | `cd site && npm run build && grep -i "how it works" site/dist/index.html` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd site && npm run build` — confirms no build breakage
- **Per wave merge:** `cd site && npm run build` + manual visual review of built `dist/index.html`
- **Phase gate:** Build green + visual review before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] No automated test files needed — Astro build output is the test artifact
- [ ] Ensure `site/public/data/08fd33_4_clip2_annotated_stats.json` exists before running build (required by `[slug].astro` dynamic import)

---

## Sources

### Primary (HIGH confidence)
- Direct file reads: `site/src/pages/index.astro`, `site/src/pages/clips/[slug].astro`, `site/public/data/manifest.json`, all components in `site/src/components/`, `site/src/layouts/BaseLayout.astro`
- `site/astro.config.mjs` — confirmed BASE_URL and trailingSlash settings
- `site/public/data/08fd33_4_annotated_stats.json` — confirmed stats schema and build-time import path pattern
- `.planning/STATE.md` — confirmed Phase 1 H.264 + faststart + playsinline decisions
- `.planning/phases/06-polish-and-demo-readiness/06-CONTEXT.md` — locked decisions

### Secondary (MEDIUM confidence)
- H.264 cross-browser support: established web standard, no verification gap
- GitHub Releases CDN Range request support: well-documented behavior of `objects.githubusercontent.com`

### Tertiary (LOW confidence)
- None — all claims in this research are verifiable from the local codebase directly

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all existing tools already installed
- Architecture: HIGH — insertion points read directly from source files
- Jargon audit: HIGH — exhaustive grep of all .astro files in site/src/
- Manifest pattern: HIGH — read directly from manifest.json and [slug].astro
- Cross-browser video: HIGH — based on established H.264/MP4 standards + Phase 1 decisions already in codebase
- Pitfalls: HIGH — stats import path pitfall derived from reading [slug].astro build pattern directly

**Research date:** 2026-03-20
**Valid until:** Stable — these are static file patterns; no external dependency changes expected
