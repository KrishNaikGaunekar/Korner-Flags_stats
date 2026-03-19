# Phase 4: Stats Visualizations — Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace the `stats-placeholder` section on each clip detail page with real possession and per-player speed/distance stats, displayed in a format a D1 coach recognizes and trusts. No heatmaps (Phase 5). No NC State branding (Phase 6). No backend changes — stats are read from existing stats JSON at Astro build time.

</domain>

<decisions>
## Implementation Decisions

### Possession display
- Horizontal split bar chart: one bar split Team 1 | Team 2 with % labels on each side
- Broadcast TV-style — instantly readable at a glance
- Teams labeled by color only: Team 1 = blue, Team 2 = orange (no team name lookup needed)
- Accuracy disclaimer appears as a small grey caption below the bar: "AI-estimated ±5%"

### Player table design
- Split into two sections: **Team 1** and **Team 2** (tabs or visually separated sections)
- ~21 players per team — coaches naturally review by team
- Column labels (plain coaching language):
  - `Player` (player ID number)
  - `Top Speed` (= `max_speed_kmh`)
  - `Avg Speed` (= `avg_speed_kmh`)
  - `Distance` (= `distance_m`)
- Default sort: by Player ID ascending — stable, no implied ranking
- Speed values shown in km/h, distance in meters

### Speed/distance disclaimers
- Small grey caption below the player table (same treatment as possession disclaimer)
- Exact wording: "AI-estimated from video — values are approximate"

### Coming Soon previews
- Greyed-out stat cards with a lock icon and "Coming Soon" label
- Stats previewed: Pass Counts, Shots, Shots on Target, Assists
- Placed **below the player table**, within the same Match Statistics section
- No fabricated numbers — cards are purely teaser UI

### Claude's Discretion
- Whether the Team 1 / Team 2 split is tabs (client-side toggle) or two visually separated stacked sections (no JS required)
- Exact color values for the possession bar (blue/orange within the Apple-esque palette)
- Horizontal bar implementation: pure CSS or a lightweight SVG — no charting library required given the simplicity
- Lock icon choice and exact card muted style (opacity, color)
- Specific spacing, typography, shadow values — within the established Apple-esque minimal aesthetic

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §Demo Site — SITE-04, SITE-06, SITE-07, SITE-08 definitions and acceptance criteria

### Data schema
- `site/public/data/08fd33_4_annotated_stats.json` — Actual stats JSON schema: `possession.team_1_percent`, `possession.team_2_percent`; `players` keyed by player ID with `team`, `distance_m`, `max_speed_kmh`, `avg_speed_kmh`

### Existing site structure
- `site/src/pages/clips/[slug].astro` — Clip detail page; contains `.stats-placeholder` section to be replaced
- `site/src/layouts/BaseLayout.astro` — Base layout and CSS variables to extend
- `.planning/phases/03-site-scaffold-and-video-playback/03-CONTEXT.md` — Visual design decisions (Apple-esque aesthetic, neutral palette, card shadow style)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `site/src/pages/clips/[slug].astro` — The `stats-placeholder` section is the direct insertion point; stats JSON path is already available via `clip.stats_url`
- `site/public/data/manifest.json` — Build-time data; `stats_url` field already present per clip
- Existing `.stats-placeholder` and `.heatmaps-placeholder` card styles (white bg, `border-radius: 12px`, `box-shadow: 0 1px 3px`) — reuse this card pattern for all new sections

### Established Patterns
- Stats JSON is fetched at **build time** via Astro static generation (no client-side JS data fetching)
- Apple-esque palette: `#1d1d1f` headings, `#6e6e73` secondary text, `#0066cc` links, white cards
- All data files served from `site/public/data/` as static assets

### Integration Points
- `clip.stats_url` in `[slug].astro` → fetch stats JSON at build time → render possession bar + player table
- Stats section replaces `.stats-placeholder` directly — no new routes or pages needed
- Phase 5 (heatmaps) inserts into `.heatmaps-placeholder` — Phase 4 must leave that section untouched

</code_context>

<specifics>
## Specific Ideas

- The possession display should feel like broadcast TV soccer stats — clean split bar, not a donut chart
- Team distinction is color-based only (no real team names available in the data)
- Coming Soon cards should visually preview the future stat layout so coaches see the roadmap, not just "feature missing"

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-stats-visualizations*
*Context gathered: 2026-03-19*
