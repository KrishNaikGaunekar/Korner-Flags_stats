# Stack Research

**Domain:** Static soccer analysis demo site + Python heatmap pipeline extension
**Researched:** 2026-03-16
**Confidence:** MEDIUM-HIGH (web stack HIGH, Python heatmap additions HIGH, video hosting MEDIUM due to GitHub Pages constraints)

---

## Context

The existing pipeline (Python, YOLO11, ByteTrack, OpenCV, supervision) is complete and out of scope for this milestone. This research covers two new concerns:

1. **Demo site stack** — static GitHub Pages site displaying pre-processed annotated videos and stats
2. **Python heatmap additions** — extending the existing pipeline to generate heatmap images alongside the current output

---

## Recommended Stack

### Demo Site: Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Astro | 5.x (latest) | Static site generator / build tool | Ships zero JS by default; Markdown + HTML pages work natively; official GitHub Actions deployment support; content-focused sites are its primary use case; faster build than Jekyll |
| Plyr | 3.8.4 | HTML5 video player | ~7 kB gzipped, no dependencies, keyboard/screen-reader accessible, customizable CSS, plays standard MP4/WebM directly; last published 2 months ago (active) |
| Chart.js | 4.5.1 | Stats visualization (possession %, speed, distance bar/donut charts) | Framework-agnostic CDN usage; minimal setup; works with vanilla JS; 6 chart types cover all demo stats needs; the standard choice for "ship something fast" dashboards |
| Tailwind CSS | 3.x | Styling | Utility-first; works as PostCSS in Astro with zero config; produces minimal CSS in production builds; avoids custom CSS sprawl on a 1-2 week timeline |

### Demo Site: Video Hosting

| Approach | Cost | Recommendation |
|----------|------|----------------|
| Cloudflare R2 + public bucket | Free tier: 10 GB storage, 0 egress fees | **PRIMARY RECOMMENDATION** — upload MP4s to R2 public bucket, reference URLs in site JSON config; zero bandwidth cost; video files never enter the Git repo |
| YouTube unlisted embeds | Free | **FALLBACK** — If R2 setup is too slow for demo deadline; iframe embeds work directly in GitHub Pages; loses branded player control but is zero friction |
| Git LFS | NOT SUPPORTED | Git LFS cannot be used with GitHub Pages — files are served as pointer text, not the binary. Do not attempt. |

**Decision rationale:** GitHub enforces a 100 MB per-file hard limit and Git LFS is explicitly unsupported on GitHub Pages. Annotated soccer match clips will easily exceed 100 MB. Cloudflare R2 has no egress fees (unlike S3 or GCS), a 10 GB free tier, and public bucket URLs are simple `<video src="...">` drops. Setup takes under 30 minutes with the Cloudflare dashboard.

### Demo Site: Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Chart.js chartjs-plugin-datalabels | 2.2.0 | Show numeric values directly on charts | Use on possession donut chart for clean % labels without hover |
| Alpine.js | 3.14.x | Lightweight JS interactivity (tab switching, clip selection) | Use if you need any reactive UI state without React/Vue overhead; ~15 kB; compatible with Astro's islands architecture |
| canvas-confetti | — | One-time polish effect | Skip unless demo mood calls for it |

### Heatmap Generation: Python Additions

| Library | Version | Purpose | Why Recommended |
|---------|---------|---------|-----------------|
| mplsoccer | 1.6.1 | Soccer pitch drawing + heatmap rendering on correctly proportioned pitch | Purpose-built for this exact use case; `Pitch.heatmap()` method takes x/y bins directly; produces publication-quality pitch images; released November 2025 |
| matplotlib | >=3.6.0 (already transitive) | Render and save heatmap PNG | mplsoccer renders to matplotlib figures; `fig.savefig("heatmap.png", dpi=150, bbox_inches="tight")` writes the output |
| scipy | >=1.9.0 | `gaussian_kde` / `ndimage.gaussian_filter` for density smoothing | Smooths sparse player position data into a continuous density field before binning; prevents patchy heatmaps from limited clips |
| numpy | >=1.24.0 (already in stack) | Position array accumulation across frames | Already a dependency; no new install needed |

**Why mplsoccer over raw matplotlib:** mplsoccer draws a correctly-proportioned soccer pitch (with penalty area, center circle, goal boxes) at the right aspect ratio, supports multiple pitch standard coordinate systems (StatsBomb, Opta, custom), and its `bin_statistic` + `heatmap` methods handle the binning pipeline in two lines. Rolling your own pitch geometry with matplotlib patches takes ~150 lines and still looks worse.

**Why NOT the Ultralytics built-in heatmap:** The Ultralytics Heatmap solution (`from ultralytics.solutions import Heatmap`) renders heatmap overlays on the raw video frame, not on a pitch diagram. This is useful for motion visualization but does not produce a clean, shareable pitch heatmap PNG suitable for a demo site panel. Use mplsoccer for the shareable static image and Ultralytics' solution only if you want heatmap video output.

---

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Astro CLI (`npm create astro@latest`) | Scaffold and local dev server | `npx astro dev` watches changes with HMR; `npx astro build` emits to `dist/` |
| GitHub Actions (`withastro/action@v3`) | CI/CD to GitHub Pages | Official Astro action handles Node setup, build, and Pages deployment in one workflow file; no manual setup |
| Wrangler CLI (Cloudflare) | Upload MP4s to R2 | `wrangler r2 object put bucket/clip.mp4 --file=clip.mp4`; one-time upload per processed video |
| Python `venv` | Isolate heatmap dependencies | mplsoccer pulls in seaborn + matplotlib; use existing venv or create new one to avoid conflicts |

---

## Installation

### Demo Site

```bash
# Scaffold Astro project
npm create astro@latest korner-flags-site
cd korner-flags-site

# Add Tailwind integration
npx astro add tailwind

# Chart.js via CDN in Astro component — no npm install needed for static use
# <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>

# Plyr via CDN
# <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/plyr@3.8.4/dist/plyr.css">
# <script src="https://cdn.jsdelivr.net/npm/plyr@3.8.4/dist/plyr.min.js"></script>
```

### Python Heatmap Pipeline Extension

```bash
# In existing Python environment
pip install mplsoccer>=1.6.1 scipy>=1.9.0

# matplotlib is already pulled in by mplsoccer but verify:
pip install matplotlib>=3.6.0
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Astro | Plain HTML/CSS/JS (no build tool) | If the site is truly 1-2 static pages with no templating needs; but Astro's templating pays off immediately when adding 2-3 match clips with shared layout |
| Astro | Next.js / SvelteKit | If Phase 2 backend is starting immediately; premature for a static demo milestone with 1-2 week deadline |
| Astro | Jekyll | Only if the team already knows Jekyll; Astro builds faster, has better DX, and official GitHub Pages action is as simple |
| Plyr | Vidstack | Vidstack is the newer option and technically the successor Plyr is merging toward; but Vidstack 1.x CDN story is less mature and its docs are more complex for simple MP4 playback use case |
| Plyr | Video.js | Video.js is ~500 kB uncompressed; overkill for a demo with pre-processed MP4 files; no HLS/DASH needed |
| Chart.js | D3.js | D3 only if you need bespoke custom visuals (e.g., animated player movement traces); possession % and speed bars do not need D3's power |
| Chart.js | ECharts | ECharts is excellent but heavier (~700 kB min); Chart.js is sufficient and lighter for this scope |
| Cloudflare R2 | Amazon S3 | S3 has egress fees; R2 has $0 egress; for a demo with no budget there is no reason to choose S3 |
| Cloudflare R2 | YouTube unlisted | YouTube is zero setup fallback but loses player UI control and branding; R2 is preferred if demo polish matters |
| mplsoccer | seaborn kdeplot on blank axes | Seaborn KDE on blank axes requires manually painting pitch markings; mplsoccer does this correctly in one line and the output looks professional |
| mplsoccer | Ultralytics built-in Heatmap | Ultralytics renders onto raw video frames — wrong output type for a static site panel image |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Git LFS for video files | GitHub Pages explicitly does NOT serve LFS files — the file pointer text is served instead of the binary; video will not play | Cloudflare R2 public bucket or YouTube unlisted embed |
| React / Vue for the demo site | Adds build complexity and JS bundle weight for what is essentially a read-only display page; counter to 1-2 week deadline constraint | Astro (zero-JS default) + Alpine.js for minimal interactivity |
| Video.js | ~500 kB uncompressed; designed for HLS/DASH adaptive streaming, not simple MP4 playback; overkill | Plyr (7 kB gzipped) |
| Jekyll | Slower builds, Ruby dependency, worse DX than Astro; the only reason to use Jekyll in 2025 is legacy familiarity | Astro with official GitHub Pages action |
| Storing processed videos in Git without LFS | Files >50 MB trigger Git warnings; >100 MB are hard-blocked by GitHub push; videos will not land in the repo | Upload to Cloudflare R2, store only the URL in a JSON config file |
| OpenCV `cv2.applyColorMap` for the shareable pitch heatmap | Produces a heatmap on the raw video frame aspect ratio, not a pitch diagram; output is video-overlay style, not a clean PNG for a stats panel | mplsoccer `Pitch.heatmap()` |
| Recharts | React-only; adds a React dependency to the static site for no reason | Chart.js (framework-agnostic) |

---

## Stack Patterns by Variant

**If demo deadline is <1 week (emergency mode):**
- Skip Astro; use a single `index.html` with Plyr, Chart.js, and YouTube unlisted embeds
- No build step, no CI/CD; just push HTML to `main` and enable Pages from root
- Heatmap: run mplsoccer locally, commit PNG images directly to `assets/`

**If polished demo (full 1-2 weeks available):**
- Astro with Tailwind, Plyr + R2 videos, Chart.js, GitHub Actions deploy
- mplsoccer heatmaps generated locally, PNGs committed to repo as assets (small enough)
- Stats JSON files committed to repo (text files, always small)

**If Phase 2 backend starts immediately after demo:**
- Consider Astro with React islands instead of Alpine.js — easier migration path to Next.js/React later
- Keep video hosting on R2 (R2 will serve Phase 2 backend just as well)

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| mplsoccer 1.6.1 | Python >=3.10 | Requires `KW_ONLY` from `dataclasses`, not available in Python 3.9 |
| mplsoccer 1.6.1 | matplotlib >=3.6.0 | matplotlib is a direct dependency; pulled automatically by pip |
| Chart.js 4.5.1 | chartjs-plugin-datalabels 2.2.0 | Plugin requires Chart.js 4.x; do not use plugin v3.x with Chart.js 4.x |
| Plyr 3.8.4 | Modern browsers (Chrome, Firefox, Safari, Edge) | No IE11 support; fine for a coaching demo targeting modern browsers |
| Astro 5.x | Node.js >=18.17.1 | Astro 5 dropped Node 16; use Node 20 LTS in GitHub Actions |

---

## Sources

- mplsoccer PyPI — version 1.6.1, Python >=3.10 requirement — HIGH confidence: https://pypi.org/project/mplsoccer/
- mplsoccer docs heatmap guide — `bin_statistic` + `heatmap` API — HIGH confidence: https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_heatmap.html
- Plyr jsDelivr — version 3.8.4 confirmed latest — MEDIUM confidence (npmjs.com 403'd, jsDelivr CDN shows 3.8.4 as current): https://cdn.jsdelivr.net/npm/plyr@3.8.3/
- Chart.js docs — version 4.5.1 — HIGH confidence: https://www.chartjs.org/docs/latest/api/
- GitHub Pages LFS limitation — official GitHub docs: Git LFS cannot be used with GitHub Pages — HIGH confidence: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
- GitHub 100 MB file size hard limit — HIGH confidence: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Cloudflare R2 zero-egress pricing and video serving capability — MEDIUM confidence (community posts, official docs not directly fetched): https://community.cloudflare.com/t/can-we-serve-video-with-r2/406275
- Astro GitHub Pages deployment — official Astro docs and official GitHub action — HIGH confidence: https://docs.astro.build/en/guides/deploy/github/
- Ultralytics heatmap guide (shows video-overlay output, not pitch diagram) — HIGH confidence: https://docs.ultralytics.com/guides/heatmaps/
- Vite static deploy docs (relevant to Astro build) — HIGH confidence: https://vite.dev/guide/static-deploy

---

*Stack research for: Korner Flags demo site + heatmap pipeline extension*
*Researched: 2026-03-16*
