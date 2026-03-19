# Phase 5: Heatmap Visualizations — Research

**Researched:** 2026-03-19
**Domain:** Astro static site — HTML/CSS display of pre-generated PNG heatmaps
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Layout:** Side-by-side two-column grid — Team 1 left, Team 2 right
- **Responsive breakpoint:** Collapses to single column at 640px (same as existing patterns)
- **Image sizing:** Images fill full column width (`width: 100%`) — no max-width cap
- **Team labeling:** Colored heading above each PNG — "Team 1" in `#0071e3` (blue), "Team 2" in `#e8732a` (orange) — same colors as Phase 4 possession bar
- **Label order:** Header first (above), then PNG below
- **Section heading:** "Team Heatmaps" (matches current placeholder heading)
- **Subtitle:** "Where each team spent most of their time on the pitch" — one line below section heading
- **Card treatment:** Same white card style as stats section — `background: #ffffff`, `border-radius: 12px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`
- **AI disclaimer:** Small grey caption at bottom, exact wording: "AI-estimated from video — values are approximate"
- **No interactive heatmaps** — static PNG display only; interactive heatmaps (HEAT-01, HEAT-02) are v2

### Claude's Discretion

- Exact gap/spacing between the two heatmap columns (within Apple-esque minimal aesthetic)
- Whether to use CSS Grid or Flexbox for the two-column layout
- `alt` text for each heatmap image (accessibility)
- Whether the Astro component is inline in `[slug].astro` or extracted to a `HeatmapSection.astro` component

### Deferred Ideas (OUT OF SCOPE)

- None — discussion stayed within phase scope (interactive heatmaps already deferred to v2 per REQUIREMENTS.md)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SITE-05 | Each clip page shows team heatmaps (static PNG, one per team) from mplsoccer output | Heatmap PNGs already exist in `site/public/data/`. `clip.heatmap_team1_url` and `clip.heatmap_team2_url` already available in `[slug].astro` from manifest. This is pure display work: replace `.heatmaps-placeholder` section with two-column image layout. |
</phase_requirements>

---

## Summary

Phase 5 is a narrow display phase. The hard work is already done: mplsoccer generated the heatmap PNGs in Phase 2, the manifest schema was extended with `heatmap_team1_url` and `heatmap_team2_url` in Phase 2, and those fields are already available in `[slug].astro` via the `clip` prop at build time. Confirmed: `site/public/data/08fd33_4_heatmap_team1.png` and `08fd33_4_heatmap_team2.png` exist on disk.

The entire implementation is replacing the 4-line `.heatmaps-placeholder` section in `[slug].astro` with a two-column image layout. No new data pipeline work, no new manifest fields, no new dependencies, no client-side JavaScript.

The only technical decision left to Claude is CSS Grid vs Flexbox for the two-column layout and whether to extract a `HeatmapSection.astro` component. Both are trivial choices with no wrong answer.

**Primary recommendation:** Replace `.heatmaps-placeholder` inline in `[slug].astro` — no new component needed given the section is one-off and its data is already bound to `clip` props in that file.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Astro | ^6.0.5 (project-installed) | Static site generation | Already in use — all pages are Astro components |
| HTML `<img>` | Native | Render PNG heatmaps | PNGs are static files served from GitHub Pages |
| CSS Grid | Native browser | Two-column responsive layout | No dependencies needed; two-column grid with `@media` breakpoint is one declaration |

### Supporting

No additional libraries needed. All display needs are met by HTML + CSS.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS Grid | Flexbox | Both work for two-column layout. Grid is cleaner for equal-width columns with a single `grid-template-columns: 1fr 1fr` declaration. Flexbox requires `flex: 1` on children and is marginally less readable at-a-glance. |
| Inline in `[slug].astro` | `HeatmapSection.astro` component | Component extraction adds a file and an import for a section that only appears once and whose data (`clip.heatmap_team1_url`, `clip.heatmap_team2_url`) is already in scope in `[slug].astro`. Inline is simpler. |

**Installation:** No new packages needed.

---

## Architecture Patterns

### Recommended Structure

No new files or directories needed. The change is localized to one file:

```
site/src/pages/clips/[slug].astro   — Replace .heatmaps-placeholder section (in-place)
```

### Pattern 1: BASE_URL image path construction

**What:** All public assets served via GitHub Pages require the base path prefix (`/Korner-Flags_stats/`). The `base` constant is already declared at the top of `[slug].astro`.

**When to use:** Every `src` attribute pointing to `site/public/data/` files.

**Established in project (from ClipCard.astro and [slug].astro):**
```astro
const base = import.meta.env.BASE_URL;
// ...
src={`${base}${clip.thumbnail_url.replace(/^\//, '')}`}
```

Apply the same pattern to heatmap URLs:
```astro
src={`${base}${clip.heatmap_team1_url.replace(/^\//, '')}`}
src={`${base}${clip.heatmap_team2_url.replace(/^\//, '')}`}
```

The manifest URLs are prefixed with `/` (e.g. `/data/08fd33_4_heatmap_team1.png`), so the `.replace(/^\//, '')` strips the leading slash before prepending `base`.

### Pattern 2: Two-column grid with 640px collapse

**What:** CSS Grid responsive layout matching the existing 640px breakpoint used elsewhere in the site.

**When to use:** Side-by-side heatmap display.

```css
.heatmaps-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 640px) {
  .heatmaps-grid {
    grid-template-columns: 1fr;
  }
}
```

### Pattern 3: Team-colored heading above image

**What:** Colored `<h4>` above each `<img>`, using exact Phase 4 colors — no legend needed.

```astro
<div class="heatmap-col">
  <h4 class="team-label team1-label">Team 1</h4>
  <img
    src={`${base}${clip.heatmap_team1_url.replace(/^\//, '')}`}
    alt="Team 1 positional heatmap showing areas of pitch coverage"
    class="heatmap-img"
    loading="lazy"
  />
</div>
```

### Pattern 4: Disclaimer text

**What:** Reuse the existing `.disclaimer-text` / `.disclaimer` pattern from Phase 4 and PossessionBar.

**Source:** `PossessionBar.astro` uses `.disclaimer { color: #86868b; font-size: 0.8rem; }` — apply same treatment.

```astro
<p class="disclaimer-text">AI-estimated from video — values are approximate</p>
```

### Pattern 5: Section subtitle

**What:** A secondary paragraph below the `<h3>` heading, styled in grey (`#6e6e73`), consistent with `site-header p` and other secondary text.

```astro
<h3>Team Heatmaps</h3>
<p class="section-subtitle">Where each team spent most of their time on the pitch</p>
```

### Anti-Patterns to Avoid

- **Do NOT use `src={clip.heatmap_team1_url}` directly** — the raw manifest URL starts with `/` which resolves to the domain root, bypassing the `/Korner-Flags_stats/` base path. This causes 404s on GitHub Pages.
- **Do NOT add client-side JavaScript** — images are static PNGs; no hydration or interactivity needed. This page uses zero client-side JS by design.
- **Do NOT import the heatmap PNG as an Astro asset** — the PNGs live in `public/`, not `src/`. They are served as-is and must be referenced by URL, not imported.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Responsive two-column grid | Custom JS-based layout toggling | CSS Grid + `@media` | Native CSS solves this in 4 lines; no JS needed |
| Image path resolution | Custom path-joining utility | `${base}${url.replace(/^\//, '')}` pattern | Already established in ClipCard.astro and [slug].astro — reuse verbatim |

---

## Common Pitfalls

### Pitfall 1: Forgetting BASE_URL prefix on heatmap image src

**What goes wrong:** Images 404 on the deployed GitHub Pages site while working fine in local dev (where `base` is `/`).

**Why it happens:** GitHub Pages serves the site under `/Korner-Flags_stats/` subpath. Raw manifest URLs begin with `/data/...` which resolves to the domain root (`krishnaikgaunekar.github.io/data/...`) instead of `krishnaikgaunekar.github.io/Korner-Flags_stats/data/...`.

**How to avoid:** Apply `${base}${clip.heatmap_team1_url.replace(/^\//, '')}` pattern — identical to how thumbnail images are handled in ClipCard.astro.

**Warning signs:** Images display in `astro dev` but appear broken after `astro build` + `astro preview` or after GitHub Actions deploy.

### Pitfall 2: Using wrong grey for disclaimer text

**What goes wrong:** Disclaimer uses the wrong shade of grey, looking inconsistent with Phase 4 disclaimers.

**Why it happens:** Two grey values exist in the project — `#6e6e73` (secondary body text, e.g. `placeholder-text`) and `#86868b` (disclaimer text in PossessionBar). These are different.

**How to avoid:** Use `#86868b` for the disclaimer (matches PossessionBar's `.disclaimer` style), and `#6e6e73` for the subtitle (matches `.placeholder-text` and site-wide secondary text).

### Pitfall 3: Renaming `.heatmaps-placeholder` class without removing old styles

**What goes wrong:** Old `.heatmaps-placeholder` styles in the `<style>` block continue to apply (or don't apply) causing visual inconsistency.

**Why it happens:** The class is defined in `[slug].astro`'s scoped `<style>` block. If the HTML class name changes but the CSS class name remains (or vice versa), styles silently stop working.

**How to avoid:** When replacing the placeholder section, also remove or rename the `.heatmaps-placeholder`, `.placeholder-text` CSS rules in the same file's `<style>` block. Add new styles for the new class names in the same pass.

---

## Code Examples

Verified patterns from existing project code:

### Complete replacement section structure

```astro
<!-- Replace the existing .heatmaps-placeholder section -->
<section class="heatmaps-section">
  <h3>Team Heatmaps</h3>
  <p class="heatmaps-subtitle">Where each team spent most of their time on the pitch</p>
  <div class="heatmaps-grid">
    <div class="heatmap-col">
      <h4 class="team-label team1-label">Team 1</h4>
      <img
        src={`${base}${clip.heatmap_team1_url.replace(/^\//, '')}`}
        alt="Team 1 positional heatmap — pitch coverage density for this match"
        class="heatmap-img"
        loading="lazy"
      />
    </div>
    <div class="heatmap-col">
      <h4 class="team-label team2-label">Team 2</h4>
      <img
        src={`${base}${clip.heatmap_team2_url.replace(/^\//, '')}`}
        alt="Team 2 positional heatmap — pitch coverage density for this match"
        class="heatmap-img"
        loading="lazy"
      />
    </div>
  </div>
  <p class="disclaimer-text">AI-estimated from video — values are approximate</p>
</section>
```

### CSS for the heatmaps section

```css
/* Add to [slug].astro <style> block — replaces .heatmaps-placeholder rules */
.heatmaps-section {
  margin-top: 2.5rem;
  padding: 2rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.heatmaps-section h3 {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.heatmaps-subtitle {
  font-size: 0.95rem;
  color: #6e6e73;
  margin-bottom: 1.25rem;
}

.heatmaps-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 640px) {
  .heatmaps-grid {
    grid-template-columns: 1fr;
  }
}

.team-label {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.team1-label {
  color: #0071e3;
}

.team2-label {
  color: #e8732a;
}

.heatmap-img {
  width: 100%;
  display: block;
  border-radius: 8px;
}

.disclaimer-text {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #86868b;
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `.heatmaps-placeholder` with "Coming in the next update" text | Two-column static PNG display | Phase 5 | Replaces placeholder with real content — no structural changes to site |

**Nothing is deprecated** — this phase adds to the existing structure without changing any prior component or data contract.

---

## Open Questions

1. **Aspect ratio of the mplsoccer PNG output**
   - What we know: mplsoccer pitch plots typically have a landscape aspect ratio (roughly 3:2 or 4:3 depending on configuration). The existing PNG files are on disk.
   - What's unclear: Exact pixel dimensions of `08fd33_4_heatmap_team1.png` — unknown without inspecting the file.
   - Recommendation: Use `width: 100%` with no fixed height as decided in CONTEXT.md. The browser will scale proportionally. If the images happen to be very tall (portrait), consider adding `aspect-ratio` CSS to constrain the column height — but this is unlikely given mplsoccer's default landscape pitch orientation.

2. **`loading="lazy"` safety on GitHub Pages**
   - What we know: `loading="lazy"` is supported in all modern browsers (Chrome 77+, Firefox 75+, Safari 15.4+). The target audience is D1 coaching staff using modern browsers.
   - What's unclear: Whether the coaching demo context warrants eager loading to ensure images appear immediately on scroll.
   - Recommendation: Use `loading="lazy"` — the heatmaps section is below the fold on the clip detail page. Lazy loading is appropriate.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected in project — no test config files, no test scripts in package.json |
| Config file | None — Wave 0 gap |
| Quick run command | `cd site && npm run build` (build-time check catches Astro template errors) |
| Full suite command | `cd site && npm run build` |

The Astro project has no unit test framework. The project's validation model for this phase is:
1. **Build check:** `npm run build` — catches template syntax errors, missing props, broken imports
2. **Visual inspection:** Open built output in browser, confirm heatmap images load and layout matches spec

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SITE-05 | Heatmap section renders two team PNG images from manifest URLs | smoke (build) | `cd "C:/Korner flag/site" && npm run build` | ✅ (build pipeline) |
| SITE-05 | Team 1 image renders in left column, Team 2 in right column | visual | manual browser inspection | N/A |
| SITE-05 | Team labels are blue (#0071e3) and orange (#e8732a) | visual | manual browser inspection | N/A |
| SITE-05 | Section collapses to single column at 640px | visual | manual browser inspection at narrow viewport | N/A |
| SITE-05 | Images do not 404 on deployed site (BASE_URL correct) | smoke (deploy) | GitHub Actions build + deploy | ✅ (existing workflow) |

### Sampling Rate

- **Per task commit:** `cd "C:/Korner flag/site" && npm run build` (verifies Astro template syntax compiles cleanly)
- **Per wave merge:** `cd "C:/Korner flag/site" && npm run build` (same — only one wave in this phase)
- **Phase gate:** Build succeeds + visual confirmation both heatmaps display before `/gsd:verify-work`

### Wave 0 Gaps

No test framework gaps block this phase. The build command is sufficient to catch template errors. Visual verification is manual-only by nature of static image display.

- [ ] No unit test framework exists in the site — not a blocker for this phase; CSS/image display validation is inherently visual. No automated tests need to be written for SITE-05.

---

## Sources

### Primary (HIGH confidence)

- Project codebase: `site/src/pages/clips/[slug].astro` — confirmed `.heatmaps-placeholder` location, `clip` prop availability, `base` const, existing card styles
- Project codebase: `site/public/data/manifest.json` — confirmed `heatmap_team1_url` and `heatmap_team2_url` fields exist and are populated
- Project codebase: `site/public/data/` directory listing — confirmed `08fd33_4_heatmap_team1.png` and `08fd33_4_heatmap_team2.png` exist on disk
- Project codebase: `site/src/components/ClipCard.astro` — confirmed `${base}${url.replace(/^\//, '')}` path pattern for public assets
- Project codebase: `site/src/components/PossessionBar.astro` — confirmed `#86868b` disclaimer color and `#0071e3`/`#e8732a` team colors
- Project codebase: `site/src/layouts/BaseLayout.astro` — confirmed `#6e6e73` secondary text color, Inter font, global resets
- Project codebase: `site/astro.config.mjs` — confirmed `base: '/Korner-Flags_stats'` requiring path prefix on all public assets
- `05-CONTEXT.md` — all locked decisions confirmed

### Secondary (MEDIUM confidence)

- None needed — all required information is available from the project codebase directly.

### Tertiary (LOW confidence)

- None.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries; everything is native HTML/CSS in an already-working Astro project
- Architecture: HIGH — patterns are directly observed from existing components in the codebase; no inference needed
- Pitfalls: HIGH — BASE_URL pitfall is verified against the existing pattern (ClipCard.astro shows the fix); color values verified from PossessionBar.astro

**Research date:** 2026-03-19
**Valid until:** Stable indefinitely — no fast-moving dependencies; Astro 6 and native CSS are stable
