# Phase 3: Site Scaffold and Video Playback — Research

**Researched:** 2026-03-17
**Domain:** Astro static site, Plyr video player, GitHub Pages via Actions, manifest-driven routing
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Astro framework, site lives in `site/` subfolder
- Plyr video player (npm package)
- GitHub Pages with official `actions/configure-pages` + `actions/upload-pages-artifact` + `actions/deploy-pages`
- Deploy on every push to `main`
- Static generation at build time from `manifest.json`
- Data files (stats JSON, heatmap PNGs, thumbnails) in `site/public/data/`
- Astro `base` config = `/Korner-Flags_stats` for subpath handling
- Apple-esque minimal light design
- ffmpeg thumbnail extraction at 5s mark per clip
- GitHub repo: KrishNaikGaunekar/Korner-Flags_stats
- No stats panels, no heatmaps — those are Phase 4 and Phase 5
- No NC State branding — that is Phase 6

### Claude's Discretion
- Exact Astro npm packages and versions
- Plyr integration method (npm package inside Astro or CDN script tag)
- CSS styling details (font choices, spacing values, shadow values) within the Apple-esque minimal aesthetic
- Astro layout component structure
- GitHub Actions workflow YAML specifics (Node version, cache strategy)

### Deferred Ideas (OUT OF SCOPE)
- Custom domain setup
- NC State branding (colors, logo)
- Stats and heatmap panels on clip pages
- `base` path removal if custom domain is added later
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SITE-01 | GitHub Pages site deployed and accessible at project URL | GitHub Actions workflow with `withastro/action@v5` + `actions/deploy-pages@v4`, permissions block, concurrency guard |
| SITE-02 | Index page shows gallery of all processed NC State clips (manifest-driven, 2-3 clips) | `getStaticPaths` reads `manifest.json` at build time; `index.astro` maps clips to card components |
| SITE-03 | Each clip page shows annotated video player (Plyr) with H.264 MP4 from GitHub Releases | Plyr npm package in Astro `<script>` tag importing from npm, `video_url` from manifest as `src`, `thumbnail_url` as `data-poster` |
</phase_requirements>

---

## Summary

Phase 3 builds an Astro 6 static site in `site/`, deployed to GitHub Pages at `krishnaikgaunekar.github.io/Korner-Flags_stats` via GitHub Actions using the official `withastro/action@v5`. The site is fully manifest-driven: `manifest.json` in `site/public/data/` is read at build time by `getStaticPaths` to generate one HTML page per clip. Plyr 3.8.4 is integrated via npm import inside an Astro `<script>` tag (no `is:inline` needed — Astro bundles it). The critical configuration detail throughout is the `base: "/Korner-Flags_stats"` setting: every `src` and `href` pointing to public assets must be prefixed with `import.meta.env.BASE_URL` manually, since Astro does NOT auto-prepend `base` to public folder references.

The deployment workflow uses a two-job pattern: `build` (runs `withastro/action@v5` with `path: ./site`) then `deploy` (runs `actions/deploy-pages@v4`). The permissions block — `pages: write` and `id-token: write` — is required and frequently missing in manual setups. The `concurrency: cancel-in-progress: false` guard prevents race-clobbering concurrent deploys.

**Primary recommendation:** Use `withastro/action@v5` (which handles install + build + upload-pages-artifact automatically) with the `path: ./site` parameter. Manually prefix every public asset reference with `import.meta.env.BASE_URL`. Import Plyr from npm inside a `<script>` tag so Astro bundles it with the rest of the client JS.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| astro | 6.0.5 | Static site framework | Locked decision; file-based routing, zero-JS by default, built-in TypeScript |
| plyr | 3.8.4 | HTML5 video player | Locked decision; clean API, accessible controls, poster support via `data-poster` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @astrojs/check | 0.9.8 | TypeScript diagnostics in Astro | Add to `astro check` in CI for type safety |
| typescript | 5.9.3 | Type checking | Astro strongly recommends; `strict` mode for component props |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `withastro/action@v5` | Manual `npm ci && npm run build` + `actions/upload-pages-artifact` | Manual approach is more steps, same result; the action is the official recommendation and is simpler |
| Plyr npm import | `is:inline` CDN script | CDN introduces external dependency; npm bundling is more reliable for offline/preview builds |
| `astro-plyr` wrapper package | Bare Plyr npm + `<script>` | `astro-plyr` is a community wrapper with 22 commits and unclear maintenance; bare Plyr is 3.8.4 stable |

**Installation (inside `site/`):**
```bash
cd site
npm create astro@latest . -- --template minimal --no-install
npm install plyr
```

**Version verification (confirmed 2026-03-17):**
- `astro`: 6.0.5 (npm view astro version)
- `plyr`: 3.8.4 (npm view plyr version)
- `withastro/action`: v5.2.0 (released 2026-02-11)

---

## Architecture Patterns

### Recommended Project Structure
```
site/
├── astro.config.mjs          # base: "/Korner-Flags_stats", site: "https://krishnaikgaunekar.github.io"
├── package.json
├── tsconfig.json
├── public/
│   └── data/                 # manifest.json, stats JSONs, heatmap PNGs, thumbnails
│       ├── manifest.json
│       ├── 08fd33_4_annotated_stats.json
│       ├── 08fd33_4_heatmap_team1.png
│       ├── 08fd33_4_heatmap_team2.png
│       ├── 08fd33_4_positions.json
│       └── 08fd33_4_thumbnail.jpg
└── src/
    ├── layouts/
    │   └── BaseLayout.astro   # <html>, <head>, global CSS, <slot />
    ├── components/
    │   ├── ClipCard.astro     # thumbnail + title + duration + CTA button
    │   └── VideoPlayer.astro  # <video> markup + <script> Plyr init
    └── pages/
        ├── index.astro        # gallery grid — reads manifest.json, renders ClipCard per clip
        └── clips/
            └── [slug].astro   # per-clip detail — getStaticPaths, Plyr player, placeholder sections
```

### Pattern 1: Astro Config for GitHub Pages Subpath

**What:** `astro.config.mjs` must declare both `site` (full URL) and `base` (subpath) for GitHub Pages to serve assets correctly.

**When to use:** Always — without this, all asset paths resolve against the repo root instead of the Pages subpath.

```javascript
// Source: https://docs.astro.build/en/guides/deploy/github/
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://krishnaikgaunekar.github.io',
  base: '/Korner-Flags_stats',
});
```

### Pattern 2: Manifest-Driven getStaticPaths

**What:** Import `manifest.json` at the top of `[slug].astro`. `getStaticPaths` maps each clip to a URL slug. The full clip object is passed via `props` so the page never needs to fetch data at runtime.

**When to use:** Any page that needs a URL per clip and full clip data.

```astro
---
// Source: https://docs.astro.build/en/reference/routing-reference/#getstaticpaths
import manifestData from '../../public/data/manifest.json';

export function getStaticPaths() {
  return manifestData.clips.map((clip) => ({
    params: { slug: clip.clip_id },
    props: { clip },
  }));
}

const { clip } = Astro.props;
---
<h1>{clip.title}</h1>
```

**Key:** `params` values must be strings (they become URL segments); `props` can be any shape.

### Pattern 3: Public Asset URLs with Base Prefix

**What:** Astro does NOT auto-prepend `base` to `src` or `href` attributes pointing to `public/`. You must manually prefix with `import.meta.env.BASE_URL`.

**When to use:** Every `<img src>`, `<a href>`, or CSS `url()` that points to a file in `public/`.

```astro
---
const base = import.meta.env.BASE_URL;
// base === "/Korner-Flags_stats/" (includes trailing slash per Astro default)
---
<img src={`${base}data/${clip.clip_id}_thumbnail.jpg`} alt={clip.title} />
```

**Alternative (recommended for cleaner code):** Add `<base href={import.meta.env.BASE_URL} />` in `<head>` and use relative paths everywhere:

```astro
<!-- In BaseLayout.astro <head> -->
<base href={import.meta.env.BASE_URL} />

<!-- In components — relative paths resolve correctly -->
<img src={`data/${clip.clip_id}_thumbnail.jpg`} alt={clip.title} />
```

Note: The HTML `<base>` tag approach only works for `href`/`src` attributes, not CSS `background-url`. Pick one approach and be consistent.

### Pattern 4: Plyr Integration in Astro

**What:** Import Plyr from npm inside an Astro `<script>` tag. Astro bundles it automatically. Use `data-poster` (not `poster`) to avoid duplicate video preload downloads.

**When to use:** Any page with an HTML5 video player.

```astro
---
// VideoPlayer.astro — server-side (frontmatter)
const { src, poster, title } = Astro.props;
const base = import.meta.env.BASE_URL;
---

<video
  id="plyr-player"
  playsinline
  controls
  data-poster={poster}
  class="plyr-video"
>
  <source src={src} type="video/mp4" />
</video>

<script>
  // Source: https://github.com/sampotts/plyr#using-npm
  import Plyr from 'plyr';
  import 'plyr/dist/plyr.css';

  const player = new Plyr('#plyr-player', {
    controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'fullscreen'],
  });
</script>
```

**CSS note:** `import 'plyr/dist/plyr.css'` inside an Astro `<script>` tag injects the styles globally. This is the correct location — do not put it in `<style>` (scoped styles do not affect Plyr's shadow DOM-like structure).

### Pattern 5: GitHub Actions Workflow for Astro + Pages

**What:** Two-job workflow. `build` uses `withastro/action@v5` (auto-detects package manager, installs, builds, uploads Pages artifact). `deploy` uses `actions/deploy-pages@v4`. The permissions block is non-negotiable.

**When to use:** Every push to `main` triggers a full rebuild and deploy.

```yaml
# Source: https://github.com/withastro/action + https://docs.astro.build/en/guides/deploy/github/
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'site/**'
      - 'data/**'
      - '.github/workflows/deploy.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install, build, and upload site
        uses: withastro/action@v5
        with:
          path: ./site
          node-version: 22

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Important:** `withastro/action@v5` internally calls `actions/configure-pages` and `actions/upload-pages-artifact` — you do NOT add those steps manually when using the official action.

### Anti-Patterns to Avoid

- **Hardcoding `/Korner-Flags_stats/` in asset paths:** Use `import.meta.env.BASE_URL` — if the base ever changes, you only update `astro.config.mjs`.
- **Using `poster` attribute on `<video>`:** Use `data-poster` instead — `poster` causes the browser to download the image twice (once as poster, once when Plyr replaces the element).
- **Putting `actions/configure-pages` and `actions/upload-pages-artifact` as separate steps when using `withastro/action`:** The action handles these internally; adding them again causes duplication errors.
- **Using `is:inline` for Plyr script:** Opt out of Astro bundling only if the library cannot be bundled. Plyr works fine as an npm import inside a standard `<script>` tag.
- **Placing `upload-pages-artifact` and `deploy-pages` in the same job:** GitHub requires these to be in separate jobs — `upload` in `build`, `deploy` in a dependent `deploy` job.
- **Forgetting `cancel-in-progress: false` in concurrency:** Using `true` will cancel an in-flight deploy when a second push arrives, leaving Pages in an inconsistent state.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Video player controls | Custom `<video>` + JS controls | Plyr 3.8.4 | Keyboard navigation, fullscreen API, mobile inline play, accessibility — weeks of edge cases |
| Subpath asset URL management | Template string helpers | `import.meta.env.BASE_URL` | Already computed by Astro's build pipeline from `base` config |
| Static page generation from JSON | Manual HTML templating | Astro `getStaticPaths` | Type-safe, file-based, auto-handles 404s for unknown slugs |
| CI/CD pipeline for Astro | Custom npm + upload scripts | `withastro/action@v5` | Handles lockfile detection, caching, Pages API, artifact format automatically |
| Thumbnail extraction | Python/Node script | ffmpeg CLI command | One command, no dependencies beyond already-installed ffmpeg |

**Key insight:** Every item in this table has been solved by the standard toolchain. Custom solutions in these areas will be inferior and slower to ship.

---

## Common Pitfalls

### Pitfall 1: Missing permissions block causes 403 on deploy
**What goes wrong:** The `deploy-pages` step fails with a cryptic HTTP 403. The workflow log says "Resource not accessible by integration."
**Why it happens:** The `GITHUB_TOKEN` needs explicit `pages: write` and `id-token: write` permissions. These are not granted by default.
**How to avoid:** Always include the full permissions block at the workflow level (or job level for the deploy job):
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```
**Warning signs:** 403 error in the `deploy-pages` action step output.

### Pitfall 2: Asset URLs resolve correctly in dev but 404 in production
**What goes wrong:** `npm run dev` works fine. After deploying, images and data files return 404.
**Why it happens:** In dev, Astro serves from `/`. On GitHub Pages, the site is at `/Korner-Flags_stats/`. Absolute paths like `/data/manifest.json` resolve to `krishnaikgaunekar.github.io/data/manifest.json` (404) instead of `krishnaikgaunekar.github.io/Korner-Flags_stats/data/manifest.json`.
**How to avoid:** Always use `import.meta.env.BASE_URL` prefix for all `src`/`href` attributes pointing to public assets, or use the HTML `<base>` tag in `<head>` with relative paths.
**Warning signs:** Everything works locally, 404s appear only after deploy.

### Pitfall 3: Jekyll strips Astro's `_astro/` folder
**What goes wrong:** After deploy, the site loads but has no CSS or JS (blank page or unstyled).
**Why it happens:** GitHub Pages runs Jekyll by default, and Jekyll ignores any file or folder starting with `_`. Astro outputs its bundled assets to `dist/_astro/`.
**How to avoid:** `withastro/action@v5` automatically creates `.nojekyll` in the output — this is handled if you use the official action. If manually assembling the deploy, add `touch dist/.nojekyll` before uploading.
**Warning signs:** Site deploys but renders as unstyled HTML with broken scripts.

### Pitfall 4: Plyr CSS not applied — player renders as plain `<video>`
**What goes wrong:** Plyr initializes (JS runs) but the player looks like a native browser video element with no custom styling.
**Why it happens:** Plyr's CSS is not imported, or it is imported in a scoped `<style>` block (which Astro hashes class names for — Plyr's class names don't match).
**How to avoid:** Import `plyr/dist/plyr.css` inside the `<script>` tag (not `<style>`):
```javascript
import 'plyr/dist/plyr.css';
```
This makes the CSS global, which is what Plyr requires.
**Warning signs:** Video player appears unstyled; browser DevTools shows no Plyr CSS rules applied.

### Pitfall 5: GitHub Pages source not set to "GitHub Actions"
**What goes wrong:** The Actions workflow completes successfully, but visiting the URL shows a 404 or the old content.
**Why it happens:** GitHub Pages still has the default source set to "Deploy from a branch" (or no source set). The `deploy-pages` action requires the source to be set to "GitHub Actions" in the repo settings.
**How to avoid:** Before the first deploy, go to repo Settings → Pages → Source → set to "GitHub Actions". This is a one-time manual step.
**Warning signs:** Green checkmark in Actions, but 404 at the Pages URL; no "github-pages" environment visible in repo deployments.

### Pitfall 6: manifest.json URLs still use relative paths from Phase 2
**What goes wrong:** Stats JSON, heatmap PNGs, and thumbnails 404 on the deployed site.
**Why it happens:** `manifest.json` currently contains relative paths like `output_videos/08fd33_4_annotated_stats.json` from Phase 2 schema decisions. These paths must be updated to root-relative paths like `/data/08fd33_4_annotated_stats.json` before the site can use them.
**How to avoid:** Update `manifest.json` as part of Phase 3 data migration: copy all data files to `site/public/data/`, update all URL fields to `/data/<filename>` format, add `thumbnail_url` field.
**Warning signs:** Manifest loads, clip cards render, but detail pages show broken images/missing data.

---

## Code Examples

Verified patterns from official sources:

### astro.config.mjs — GitHub Pages subpath
```javascript
// Source: https://docs.astro.build/en/guides/deploy/github/
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://krishnaikgaunekar.github.io',
  base: '/Korner-Flags_stats',
});
```

### index.astro — Gallery reading manifest at build time
```astro
---
// Source: https://docs.astro.build/en/guides/routing/#dynamic-routes
import manifestData from '../public/data/manifest.json';
import BaseLayout from '../layouts/BaseLayout.astro';
import ClipCard from '../components/ClipCard.astro';
---
<BaseLayout title="Korner Flags — NC State Analysis">
  <div class="gallery-grid">
    {manifestData.clips.map((clip) => (
      <ClipCard clip={clip} />
    ))}
  </div>
</BaseLayout>
```

### clips/[slug].astro — Dynamic route with full clip props
```astro
---
// Source: https://docs.astro.build/en/reference/routing-reference/#getstaticpaths
import manifestData from '../../public/data/manifest.json';
import BaseLayout from '../../layouts/BaseLayout.astro';
import VideoPlayer from '../../components/VideoPlayer.astro';

export function getStaticPaths() {
  return manifestData.clips.map((clip) => ({
    params: { slug: clip.clip_id },
    props: { clip },
  }));
}

const { clip } = Astro.props;
const base = import.meta.env.BASE_URL;
---
<BaseLayout title={clip.title}>
  <VideoPlayer
    src={clip.video_url}
    poster={`${base}data/${clip.clip_id}_thumbnail.jpg`}
    title={clip.title}
  />
  <!-- Phase 4: stats panel placeholder -->
  <!-- Phase 5: heatmap panel placeholder -->
</BaseLayout>
```

### ffmpeg thumbnail extraction
```bash
# Source: https://ffmpeg.org/ (verified with current docs)
# Extracts one frame at 5-second mark; -q:v 2 = high JPEG quality
ffmpeg -ss 5 -i 08fd33_4_annotated.mp4 -frames:v 1 -q:v 2 08fd33_4_thumbnail.jpg
```
Output goes to `site/public/data/` alongside the other data files.

### Updated manifest.json schema (Phase 3 target)
```json
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
    }
  ]
}
```
Note: `video_url` stays as absolute CDN URL. All other URLs switch from `output_videos/...` to `/data/...` root-relative paths (served by Astro from `site/public/data/`).

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `peaceiris/actions-gh-pages` push-to-branch | `withastro/action@v5` + `actions/deploy-pages@v4` | 2022-2023 | Official Pages API, deployment URL in PR, org-policy compliant |
| Astro `Astro.glob()` for reading JSON | Static ESM import at top of component | Astro 5.0 | `Astro.glob()` removed in Astro 6; direct import is simpler |
| Astro legacy content collections | Content Layer API | Astro 5.0 | Not relevant to this project (we read JSON directly, not using content collections) |
| `withastro/action@v3` | `withastro/action@v5` | 2026-02 | v5.2.0 released 2026-02-11; Node 22 default |
| `actions/checkout@v3` | `actions/checkout@v4` | 2023 | Required for Node 20+ environments |

**Deprecated/outdated:**
- `Astro.glob()`: Removed in Astro 6.0. Use direct ESM imports instead.
- `withastro/action@v3`: Uses Node 18 (EOL). Upgrade to v5 for Node 22.
- Plyr 3.7.x CDN URLs in old documentation: Current version is 3.8.4 at `https://cdn.plyr.io/3.8.4/plyr.css`.

---

## Open Questions

1. **Node version for Astro 6 builds**
   - What we know: `withastro/action@v5` defaults to Node 22; Astro 6 dropped Node 18 and 20 support.
   - What's unclear: Whether the GitHub Actions ubuntu-latest runner has Node 22 pre-installed or if the action installs it independently.
   - Recommendation: Explicitly set `node-version: 22` in the `withastro/action` `with:` block to guarantee correct version regardless of runner defaults.

2. **`.nojekyll` with `withastro/action@v5`**
   - What we know: The skill notes that `.nojekyll` is mandatory for `_astro/` folders and that the action handles it automatically.
   - What's unclear: Whether v5 of the action definitely creates `.nojekyll` or if it relies on `actions/configure-pages` doing so.
   - Recommendation: Verify during Wave 0 by inspecting the deployed artifact — if `_astro/` assets 404, add an explicit `.nojekyll` creation step.

3. **`import.meta.env.BASE_URL` trailing slash consistency**
   - What we know: Astro docs state the value is influenced by `trailingSlash` config; default includes a trailing slash, so `BASE_URL = "/Korner-Flags_stats/"`.
   - What's unclear: Whether template literals like `${base}data/file.jpg` produce a double slash if `base` is `/Korner-Flags_stats//`.
   - Recommendation: In `astro.config.mjs`, set `trailingSlash: "always"` explicitly and always write `${base}data/...` (no leading slash on the path segment) to produce clean URLs.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected — this phase introduces a new `site/` directory; no test framework exists yet |
| Config file | Wave 0 creates `site/` — no test config present |
| Quick run command | Manual browser check: `npm run dev` in `site/`, visit localhost |
| Full suite command | Build smoke test: `cd site && npm run build` (zero errors = green) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SITE-01 | GitHub Pages URL responds with HTTP 200 | smoke | `curl -I https://krishnaikgaunekar.github.io/Korner-Flags_stats/` | ❌ Wave 0 (run post-deploy) |
| SITE-02 | Index page renders clip cards from manifest | build smoke | `cd site && npm run build && test -f dist/index.html` | ❌ Wave 0 |
| SITE-03 | Clip detail page includes Plyr `<video>` element with correct src | build smoke | `cd site && npm run build && grep -r 'plyr' dist/clips/` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd site && npm run build` — zero errors is the gate
- **Per wave merge:** Full build + manual visual check in browser via `npm run preview`
- **Phase gate:** `curl` smoke test against live Pages URL before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `site/` directory — does not exist yet; must be created with `npm create astro@latest`
- [ ] `site/package.json` — created during Astro scaffold
- [ ] `site/astro.config.mjs` — created during scaffold, then configured with `base` + `site`
- [ ] `site/public/data/` — must be created; data files copied from `output_videos/`
- [ ] `.github/workflows/deploy.yml` — does not exist; must be authored in Phase 3

---

## Sources

### Primary (HIGH confidence)
- Astro official docs — deploy/github: https://docs.astro.build/en/guides/deploy/github/
- Astro configuration reference: https://docs.astro.build/en/reference/configuration-reference/#base
- Astro routing reference (getStaticPaths): https://docs.astro.build/en/reference/routing-reference/#getstaticpaths
- Astro client-side scripts guide: https://docs.astro.build/en/guides/client-side-scripts/
- `withastro/action` GitHub repo (v5.2.0): https://github.com/withastro/action
- GitHub starter workflows (astro.yml): https://github.com/actions/starter-workflows/blob/main/pages/astro.yml
- Plyr GitHub README: https://github.com/sampotts/plyr#using-npm
- Project skill: `.claude/skills/github-actions-deploy/SKILL.md`

### Secondary (MEDIUM confidence)
- npm registry version check (confirmed 2026-03-17): `astro@6.0.5`, `plyr@3.8.4`
- Astro 6 release notes (breaking changes — `Astro.glob()` removed): https://astro.build/blog/astro-6/
- Astro subpath asset URL community pattern: https://spuxx.dev/blog/2023/astro-assets-base/

### Tertiary (LOW confidence)
- `astro-plyr` community wrapper: https://github.com/Liumingxun/astro-plyr — NOT recommended; low activity, bare Plyr npm import is more reliable

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions confirmed against npm registry 2026-03-17
- Architecture patterns: HIGH — sourced from Astro official docs and `withastro/action` README
- Plyr integration: HIGH — sourced from Plyr official README + Astro client scripts guide
- GitHub Actions workflow: HIGH — sourced from official starter workflow YAML + `withastro/action` docs + project skill
- Pitfalls: HIGH — sourced from official docs and the `github-actions-deploy` skill (project-captured institutional knowledge)
- Subpath base URL handling: MEDIUM — documented behavior but trailing slash edge cases need validation in Wave 0

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (Astro releases frequently; verify `astro` version before starting if >2 weeks elapsed)
