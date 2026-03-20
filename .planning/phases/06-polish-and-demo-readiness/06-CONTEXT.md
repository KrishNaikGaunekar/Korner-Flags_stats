# Phase 6: Polish and Demo Readiness — Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the site demo-ready for NC State coaching staff: add a second clip so the gallery has 2 entries, add a "How It Works" section on the index page, and add a short one-liner header/intro to the index page. No new pipeline changes. No new stat features. No backend work.

</domain>

<decisions>
## Implementation Decisions

### "How It Works" section
- Lives on the **index page**, below the clip gallery — no separate page, no extra navigation
- **3-4 plain-English steps** with **emoji icons** — e.g. 🎬 Upload → 🤖 AI Analysis → 📊 Stats
- Zero ML jargon — written for a coaching staff member with no technical background
- Pure static HTML — no client-side JS, consistent with the no-JS pattern from prior phases

### Second clip (CONT-01)
- Add a **second entry to manifest.json** that duplicates clip 1's assets (same video URL, same stats/heatmap/thumbnail files) but with a different title: "NC State Match Clip 2"
- This satisfies CONT-01 (≥2 clips browsable on site) and proves the multi-clip gallery layout works
- Placeholder approach: swap in real NC State footage before the actual demo by updating the entry

### Index page polish
- Add a **short one-liner header** to the index page: sets context for a coach opening the link cold
- Wording example: "Korner Flags — AI-powered match analysis for soccer coaches."
- Clip cards use the **`title` field from manifest** as-is — no new data fields needed
- Duration, match date, opponent are NOT added — keeps manifest simple, avoids new data work

### Claude's Discretion
- Exact emoji choices for the How It Works steps
- Precise wording of each step in the explainer
- CSS layout for the How It Works section (consistent with existing Apple-esque card/section style)
- Whether the one-liner header is an `<h1>` subtitle, `<p>` lead-in, or a hero subtitle element

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Site structure
- `site/src/pages/index.astro` — Index page; add one-liner header and How It Works section here
- `site/src/components/ClipCard.astro` — Existing card component; gallery renders one per clip
- `site/public/data/manifest.json` — Single source of truth for clips; add second clip entry here

### Design system
- `.planning/phases/03-site-scaffold-and-video-playback/03-CONTEXT.md` — Apple-esque aesthetic: light bg, clean sans-serif, generous whitespace, subtle card shadows; neutral palette
- `.planning/phases/04-stats-visualizations/04-CONTEXT.md` — Color values (`#1d1d1f` headings, `#6e6e73` secondary text), card pattern (white bg, `border-radius: 12px`, `box-shadow: 0 1px 3px`)

### Requirements
- `.planning/REQUIREMENTS.md` §Content — CONT-01 (≥2 clips), CONT-02 ("How It Works" section)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `site/src/pages/index.astro` — Gallery grid already reads `manifest.json` at build time; adding a second clip entry automatically produces a second card
- `site/src/components/ClipCard.astro` — Renders thumbnail, title, duration, CTA button; no changes needed for the second clip
- Existing `.heatmaps-section` / `.stats-section` card CSS pattern — reuse for How It Works section styling

### Established Patterns
- No client-side JS — all content is static, rendered at Astro build time
- Public assets served from `site/public/data/` as static files
- BASE_URL stripping pattern: `${base}${url.replace(/^\//, '')}` for public asset references

### Integration Points
- `manifest.json` → `getStaticPaths()` in `[slug].astro` — adding a second entry automatically generates a second clip detail page
- `manifest.json` `clip_id` must be unique per entry — second entry needs a distinct `clip_id`

</code_context>

<specifics>
## Specific Ideas

- The "How It Works" steps should feel like an infographic row: icon + step title + one-sentence description per step
- Suggested steps: 🎬 Record → 🤖 Analyze → 📊 Review → ✅ Coach
- The index page one-liner should appear above the clip gallery, not buried after it

</specifics>

<deferred>
## Deferred Ideas

- NC State branding (colors, logo) — user did not select this area; keep neutral Apple-esque aesthetic for demo
- Custom domain — deferred per Phase 3 decision (waiting for co-founder's refereeing integration)
- Replacing placeholder second clip with real NC State footage — manual step before actual demo

</deferred>

---

*Phase: 06-polish-and-demo-readiness*
*Context gathered: 2026-03-20*
