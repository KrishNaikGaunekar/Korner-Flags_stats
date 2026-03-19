# Phase 4: Stats Visualizations - Research

**Researched:** 2026-03-19
**Domain:** Astro static site — HTML/CSS data visualization (no charting library)
**Confidence:** HIGH

## Summary

Phase 4 is a pure front-end rendering problem with no backend changes. All data is already on disk in `site/public/data/` as static JSON. The stats JSON schema is confirmed and fully understood from reading the actual file. The implementation is: import the stats JSON at Astro build time (same proven pattern as the manifest import), compute derived values in the component's frontmatter, and render possession bar + player table + coming-soon cards using Astro templating and scoped CSS.

No charting library is required. The possession display is a single horizontal bar split into two colored segments — achievable with two inline-width `<div>` elements inside a flex container. The player table is a standard HTML `<table>` with two separate sections (Team 1, Team 2), sorted by player ID ascending. Coming Soon cards are muted `<div>` elements with a lock symbol and label, placed below the table.

The primary risk is data quality: the stats JSON contains many ghost entries (player IDs with `distance_m: 0.0`, `max_speed_kmh: 0.0`, `avg_speed_kmh: 0.0`) and unrealistically high speed values (up to 268 km/h). These are known pipeline limitations. The display must handle zero-value rows gracefully — the planner should include a filter or visual treatment for them.

**Primary recommendation:** Import each clip's stats JSON directly at build time using `import()` with the same relative-path-into-public pattern already proven by the manifest import; render all visuals with Astro + scoped CSS only.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Possession display**
- Horizontal split bar chart: one bar split Team 1 | Team 2 with % labels on each side
- Broadcast TV-style — instantly readable at a glance
- Teams labeled by color only: Team 1 = blue, Team 2 = orange (no team name lookup needed)
- Accuracy disclaimer appears as a small grey caption below the bar: "AI-estimated ±5%"

**Player table design**
- Split into two sections: Team 1 and Team 2 (tabs or visually separated sections)
- ~21 players per team — coaches naturally review by team
- Column labels (plain coaching language):
  - `Player` (= player ID number)
  - `Top Speed` (= `max_speed_kmh`)
  - `Avg Speed` (= `avg_speed_kmh`)
  - `Distance` (= `distance_m`)
- Default sort: by Player ID ascending — stable, no implied ranking
- Speed values shown in km/h, distance in meters

**Speed/distance disclaimers**
- Small grey caption below the player table (same treatment as possession disclaimer)
- Exact wording: "AI-estimated from video — values are approximate"

**Coming Soon previews**
- Greyed-out stat cards with a lock icon and "Coming Soon" label
- Stats previewed: Pass Counts, Shots, Shots on Target, Assists
- Placed below the player table, within the same Match Statistics section
- No fabricated numbers — cards are purely teaser UI

### Claude's Discretion
- Whether the Team 1 / Team 2 split is tabs (client-side toggle) or two visually separated stacked sections (no JS required)
- Exact color values for the possession bar (blue/orange within the Apple-esque palette)
- Horizontal bar implementation: pure CSS or a lightweight SVG — no charting library required given the simplicity
- Lock icon choice and exact card muted style (opacity, color)
- Specific spacing, typography, shadow values — within the established Apple-esque minimal aesthetic

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SITE-04 | Each clip page shows stats panel: possession % (per team), per-player speed and distance | Stats JSON schema confirmed; build-time import pattern proven by manifest |
| SITE-06 | Possession % displayed with accuracy disclaimer (e.g. "AI-estimated ±5%") | CSS caption pattern identified; wording locked in CONTEXT.md |
| SITE-07 | Stats labeled in plain coaching language (not technical jargon) | Column label mapping documented in Standard Stack section |
| SITE-08 | Pass counts, shots, shots on target, assists shown as "Coming Soon" feature previews | Card pattern researched; lock icon via HTML entity or Unicode confirmed |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Astro | ^6.0.5 (installed) | Component rendering, build-time data, scoped CSS | Already in project; static generation with no client-side fetch |
| Vite JSON plugin | built into Astro | Import `.json` files as ES modules at build time | Zero-config, proven by existing manifest import |

### No Additional Libraries Needed
The possession bar, player table, and coming-soon cards require zero npm additions. Pure HTML + CSS covers every element.

**Installation:** No new packages required.

---

## Architecture Patterns

### Recommended Project Structure

```
site/src/
├── pages/clips/[slug].astro      — Replace .stats-placeholder section here
├── components/
│   ├── PossessionBar.astro       — New: possession split bar + disclaimer
│   ├── PlayerStatsTable.astro    — New: Team 1 + Team 2 tables + disclaimer
│   ├── ComingSoonCards.astro     — New: 4 locked teaser cards
│   ├── VideoPlayer.astro         — Existing (unchanged)
│   └── ClipCard.astro            — Existing (unchanged)
└── layouts/BaseLayout.astro      — Existing (unchanged)
```

### Pattern 1: Build-Time Stats JSON Import

**What:** Each clip page imports its own stats JSON as a static ES module at Astro build-time. No `fetch()`, no client-side JavaScript.

**When to use:** Any time a clip-specific JSON file needs to be read in `[slug].astro`.

**How it works:** The `clip.stats_url` in the manifest is `/data/08fd33_4_annotated_stats.json`. The corresponding importable path from `[slug].astro` is `'../../../public/data/08fd33_4_annotated_stats.json'`. At build time, Astro/Vite resolves this and tree-shakes it into the static HTML.

**Example:**
```astro
---
// In [slug].astro frontmatter — build-time only
import manifestData from '../../../public/data/manifest.json';

// Dynamic import keyed by clip_id at build time:
// clip.stats_url = "/data/08fd33_4_annotated_stats.json"
// Strip leading slash and map to import path:
const statsPath = clip.stats_url.replace(/^\//, '');
// Vite supports dynamic import with string template at build time:
const statsModule = await import(`../../../public/${statsPath}`);
const stats = statsModule.default;
---
```

**Important:** Astro's Vite build supports `import()` with template literals in the frontmatter because all paths are statically analyzable at build time (the manifest is known). This pattern works for a small fixed set of files.

**Alternative (simpler, zero risk):** Import each stats JSON at the top of `[slug].astro` using the same relative import syntax as the manifest, conditioned on `clip.clip_id`. Since only one clip exists right now, a direct import also works:

```astro
---
import statsData from '../../../public/data/08fd33_4_annotated_stats.json';
// Then select based on clip.clip_id
---
```

When multiple clips exist, prefer a map object keyed by `clip_id`.

### Pattern 2: Possession Bar (Pure CSS)

**What:** Two `<div>` children inside a flex row. Width set inline via `style` attribute using the percentage values from the stats JSON.

**Example:**
```astro
---
const t1 = stats.possession.team_1_percent;  // e.g. 37.9
const t2 = stats.possession.team_2_percent;  // e.g. 62.1
---
<div class="possession-bar">
  <div class="segment team1" style={`width: ${t1}%`}>
    <span class="label">{t1}%</span>
  </div>
  <div class="segment team2" style={`width: ${t2}%`}>
    <span class="label">{t2}%</span>
  </div>
</div>
<p class="disclaimer">AI-estimated ±5%</p>
```

```css
.possession-bar {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
}
.segment.team1 { background: #0066cc; }  /* Apple blue — already in palette */
.segment.team2 { background: #e67e22; }  /* Orange — within Apple-esque palette */
.label {
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0 0.75rem;
  line-height: 40px;
}
```

### Pattern 3: Player Table — Two Stacked Sections (Recommended over tabs)

**What:** Two `<table>` elements (or one table with a visual divider), one per team. No client-side JavaScript. Coaches scan by team naturally; tabs would require a JS toggle and add complexity for no gain given the static context.

**Data transformation needed in frontmatter:**
```astro
---
// Partition and sort players by team, ascending by player ID
const allPlayers = Object.entries(stats.players)
  .map(([id, data]) => ({ id: Number(id), ...data }))
  .sort((a, b) => a.id - b.id);

const team1 = allPlayers.filter(p => p.team === 1);
const team2 = allPlayers.filter(p => p.team === 2);
---
```

**Column labels mapping (SITE-07):**
| JSON key | Display label |
|----------|---------------|
| player ID | Player |
| `max_speed_kmh` | Top Speed |
| `avg_speed_kmh` | Avg Speed |
| `distance_m` | Distance |

Units: speed in `km/h`, distance in `m`.

### Pattern 4: Coming Soon Cards

**What:** Four `<div>` cards in a CSS grid, each muted (opacity ~0.5, grey background), showing a lock character and "Coming Soon" label. No numbers displayed.

**Lock icon:** Unicode `🔒` is the simplest. If emojis are unwanted per project style, use CSS `::before` with content `"🔒"` or a simple padlock SVG inline. Given the Apple-esque minimal aesthetic, a monochrome SVG padlock or the text label "Coming Soon" in a badge is cleaner.

**Example:**
```astro
{['Pass Counts', 'Shots', 'Shots on Target', 'Assists'].map(name => (
  <div class="coming-soon-card">
    <span class="lock-icon" aria-hidden="true">&#128274;</span>
    <p class="stat-name">{name}</p>
    <p class="soon-label">Coming Soon</p>
  </div>
))}
```

### Anti-Patterns to Avoid

- **Charting library (Chart.js, Recharts, D3):** No charting library is needed or wanted. A CSS flexbox bar is sufficient and avoids bundle size, hydration, and client-JS dependency.
- **Client-side `fetch()` for stats JSON:** All data is static; use build-time import. Fetch adds latency and fails if the file path changes.
- **Displaying all 40+ player rows without filtering:** The stats JSON has ~40 player entries including ghost entries (all zeros, very short tracking duration). Showing all rows produces a confusing table. Recommended: filter to players with `distance_m > 0` or `max_speed_kmh > 0`, or at minimum visually distinguish zero-stat rows.
- **Tabs for Team 1 / Team 2 split:** Introduces client-side JS for no meaningful gain. Two stacked sections with clear headings read fine for ~21 players per team.
- **Fabricating numbers in Coming Soon cards:** Never show placeholder values like "24 passes". Cards must show only the stat name and "Coming Soon" label.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Possession percentage bar | Custom SVG charting logic | Two CSS `div` segments in a flex row | Two lines of CSS, no dependencies |
| Build-time JSON reading | `fs.readFileSync` in SSR | Vite JSON import (`import statsData from '...'`) | Vite handles this natively in Astro frontmatter |
| Lock icon | Custom SVG icon library | Unicode `&#128274;` or inline SVG `<path>` | Zero deps; HTML entity is always available |

**Key insight:** Every visualization in this phase is representable with basic HTML + CSS. Any library addition is pure overhead.

---

## Common Pitfalls

### Pitfall 1: Ghost Player Rows (Zero-Stat Entries)
**What goes wrong:** The stats JSON contains ~15 player entries with `distance_m: 0.0`, `max_speed_kmh: 0.0`, `avg_speed_kmh: 0.0`. These are players ByteTrack detected for only 1-2 frames. Displaying them makes the table look broken and erodes coach trust.
**Why it happens:** ByteTrack assigns IDs to brief detections; the stats exporter includes all tracked IDs.
**How to avoid:** Filter in frontmatter: `allPlayers.filter(p => p.distance_m > 0 || p.max_speed_kmh > 0)`. Alternatively, filter to `distance_m >= 1.0` to exclude trivial detections.
**Warning signs:** Table has rows showing "0 km/h / 0 km/h / 0 m" — these confuse coaches.

### Pitfall 2: Unrealistically High Speed Values
**What goes wrong:** Known pipeline limitation — max speed values reach 268 km/h (confirmed in STATE.md). The disclaimer "AI-estimated from video — values are approximate" is required (SITE-06, SITE-07) and must appear on the page.
**Why it happens:** Perspective transform uses estimated pitch vertices, not calibrated keypoints — speed/distance values are approximate by design.
**How to avoid:** The disclaimer already covers this. Do NOT clamp or hide values — that changes the data. Display them with the required disclaimer.

### Pitfall 3: Dynamic Import Path Resolution in Astro
**What goes wrong:** If `import()` uses a fully dynamic expression like `` import(`/public/${variable}`) ``, Vite cannot statically analyze the import graph and may fail or silently return undefined.
**Why it happens:** Vite requires at least a partial literal in template literals for static analysis (e.g., the directory prefix must be a literal string).
**How to avoid:** Use `` import(`../../../public/data/${clip.clip_id}_annotated_stats.json`) `` — the directory prefix is a literal, only the filename varies. Vite handles this as a glob-like import. Alternatively, use a static import map object keyed by clip_id (zero ambiguity for the current single-clip case).

### Pitfall 4: BASE_URL and Public Asset Path Confusion
**What goes wrong:** The site has `base: '/Korner-Flags_stats'` in `astro.config.mjs`. `import.meta.env.BASE_URL` must be prepended to paths used in `href`/`src` attributes, but NOT to Vite `import()` paths (which are resolved at build time relative to the source file).
**Why it happens:** Conflating the runtime URL base with the build-time module resolution path.
**How to avoid:** Import JSON files with relative paths from the source file (`../../../public/data/...`). Only use `BASE_URL` for HTML attribute values.

### Pitfall 5: Player ID Sorting (String vs Number)
**What goes wrong:** `Object.keys(stats.players)` returns string keys. Sorting strings gives `["1", "10", "103", "11", "12", ...]` instead of numeric order.
**Why it happens:** JSON object keys are always strings; default sort is lexicographic.
**How to avoid:** Always `Number(id)` when building the players array before sorting: `.sort((a, b) => a.id - b.id)`.

---

## Code Examples

### Complete Build-Time Stats Load Pattern
```astro
---
// [slug].astro frontmatter (runs at build time only)
import manifestData from '../../../public/data/manifest.json';

export function getStaticPaths() {
  return manifestData.clips.map((clip) => ({
    params: { slug: clip.clip_id },
    props: { clip },
  }));
}

const { clip } = Astro.props;

// Import stats JSON at build time — clip_id is known statically per page
// Vite resolves this because the directory prefix is a literal string
const statsModule = await import(`../../../public/data/${clip.clip_id}_annotated_stats.json`);
const stats = statsModule.default;

// Partition and sort players
const allPlayers = Object.entries(stats.players)
  .map(([id, data]) => ({ id: Number(id), ...data }))
  .filter(p => p.distance_m > 0 || p.max_speed_kmh > 0)  // exclude ghost entries
  .sort((a, b) => a.id - b.id);

const team1Players = allPlayers.filter(p => p.team === 1);
const team2Players = allPlayers.filter(p => p.team === 2);

const t1Pct = stats.possession.team_1_percent;
const t2Pct = stats.possession.team_2_percent;
---
```

### Possession Bar HTML Structure
```astro
<div class="possession-section">
  <h4>Possession</h4>
  <div class="possession-bar-wrap">
    <span class="poss-label team1-label">Team 1 · {t1Pct}%</span>
    <div class="possession-bar">
      <div class="seg seg-team1" style={`width:${t1Pct}%`}></div>
      <div class="seg seg-team2" style={`width:${t2Pct}%`}></div>
    </div>
    <span class="poss-label team2-label">Team 2 · {t2Pct}%</span>
  </div>
  <p class="disclaimer">AI-estimated ±5%</p>
</div>
```

### Player Table Row Template
```astro
{team1Players.map(p => (
  <tr>
    <td>{p.id}</td>
    <td>{p.max_speed_kmh.toFixed(1)} km/h</td>
    <td>{p.avg_speed_kmh.toFixed(1)} km/h</td>
    <td>{p.distance_m.toFixed(1)} m</td>
  </tr>
))}
```

### Coming Soon Card
```astro
<div class="coming-soon-grid">
  {['Pass Counts', 'Shots', 'Shots on Target', 'Assists'].map(name => (
    <div class="cs-card">
      <div class="cs-lock" aria-hidden="true">&#128274;</div>
      <p class="cs-name">{name}</p>
      <span class="cs-badge">Coming Soon</span>
    </div>
  ))}
</div>
```

---

## Data Schema (Confirmed from Actual File)

The stats JSON at `site/public/data/08fd33_4_annotated_stats.json` has this structure:

```json
{
  "video": {
    "fps": 25.0,
    "resolution": "1920x1080",
    "total_frames": 750,
    "duration_seconds": 30.0
  },
  "possession": {
    "team_1_percent": 37.9,
    "team_2_percent": 62.1
  },
  "players": {
    "1": { "team": 1, "distance_m": 74.2, "max_speed_kmh": 63.3, "avg_speed_kmh": 8.9 },
    "...": "..."
  }
}
```

**Key observations from actual data:**
- `possession.team_1_percent` + `possession.team_2_percent` = 100.0 (confirmed)
- `players` is keyed by string player ID (string-keyed object, not array)
- `team` field is integer 1 or 2
- ~40 total entries; ~15 are ghost entries (all zeros)
- Speed values range from 0 to 268.2 km/h — unrealistic values are a known limitation
- The `clip_id` in `manifest.json` is `"08fd33_4"` and the stats file is named `08fd33_4_annotated_stats.json` — the import path suffix is `_annotated_stats.json`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Client-side `fetch()` for stats | Build-time Vite JSON import | Astro 2+ | Zero latency, works offline, no hydration needed |
| Charting libraries for simple bars | CSS flexbox width trick | Always available | No bundle cost, no flash of unstyled content |
| JS-driven table sorting | Static sort in frontmatter | Astro static gen | No client JS required |

---

## Open Questions

1. **Dynamic import path pattern with multiple clips**
   - What we know: Vite handles `` import(`../../../public/data/${id}_annotated_stats.json`) `` when the directory prefix is a literal.
   - What's unclear: Whether Astro 6 throws a build warning for dynamic imports with template literals in frontmatter.
   - Recommendation: Test with the existing single clip first. If Vite complains, fall back to a static import map object: `const statsMap = { '08fd33_4': import_08fd33_4 }`.

2. **Ghost player row treatment**
   - What we know: ~15 players have all-zero stats. Filtering by `distance_m > 0` removes them.
   - What's unclear: Whether the coach would want to see zero-distance players (they appeared briefly in frame) or not.
   - Recommendation: Filter them out for clarity. The disclaimer covers data accuracy already.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected — this is a static Astro site |
| Config file | None — no test runner configured |
| Quick run command | `cd site && npm run build` (build success = primary validation) |
| Full suite command | `cd site && npm run build && npm run preview` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SITE-04 | Stats panel renders possession + player table | smoke | `cd site && npm run build` — HTML output contains "Top Speed" | ❌ Wave 0 |
| SITE-06 | Disclaimer text appears on page | smoke | `cd site && npm run build` — HTML contains "AI-estimated ±5%" | ❌ Wave 0 |
| SITE-07 | Plain language column headers present | smoke | `cd site && npm run build` — HTML contains "Top Speed", "Avg Speed", "Distance" | ❌ Wave 0 |
| SITE-08 | Coming Soon cards present, no fabricated numbers | smoke | `cd site && npm run build` — HTML contains "Coming Soon" | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd site && npm run build` — verify build succeeds, no Vite errors
- **Per wave merge:** `cd site && npm run build` — grep built HTML for required strings
- **Phase gate:** Build clean + visual review of the deployed page before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] No automated test framework exists — build success is the only automated check
- [ ] Manual visual review required after deploy to verify layout at realistic viewport

*(No test framework infrastructure needed — Astro build errors catch template mistakes; visual review catches layout issues.)*

---

## Sources

### Primary (HIGH confidence)
- Actual file read: `site/public/data/08fd33_4_annotated_stats.json` — schema confirmed directly
- Actual file read: `site/src/pages/clips/[slug].astro` — existing build-time import pattern confirmed
- Actual file read: `site/public/data/manifest.json` — clip_id and stats_url naming confirmed
- Actual file read: `site/src/layouts/BaseLayout.astro` — palette values confirmed (#1d1d1f, #6e6e73, #0066cc)
- Actual file read: `.planning/phases/04-stats-visualizations/04-CONTEXT.md` — locked decisions source

### Secondary (MEDIUM confidence)
- Vite documentation pattern: dynamic imports with partial literal prefix are statically analyzable — verified by Vite's glob import documentation behavior (consistent across Vite 4/5/6)
- Astro 6 JSON import: same behavior as manifest import already working in the project

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; existing Astro + Vite confirmed working
- Architecture: HIGH — data schema read directly from actual file; import pattern proven by existing code
- Pitfalls: HIGH — ghost entries and speed values observed directly in the data file; build-time import caveat based on Vite documented behavior
- Data schema: HIGH — read directly from the canonical file referenced in CONTEXT.md

**Research date:** 2026-03-19
**Valid until:** 2026-06-01 (stable domain — CSS + Astro static gen patterns are not fast-moving)
