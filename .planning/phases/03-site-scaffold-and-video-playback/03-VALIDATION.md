---
phase: 3
slug: site-scaffold-and-video-playback
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None detected — phase introduces new `site/` directory; no test framework exists yet |
| **Config file** | Wave 0 creates `site/` — no test config present |
| **Quick run command** | `cd site && npm run build` |
| **Full suite command** | `cd site && npm run build && npm run preview` (manual visual check) |
| **Estimated runtime** | ~30 seconds (Astro build) |

---

## Sampling Rate

- **After every task commit:** Run `cd site && npm run build` — zero errors is the gate
- **After every plan wave:** Full build + manual visual check via `npm run preview`
- **Before `/gsd:verify-work`:** `curl -I https://krishnaikgaunekar.github.io/Korner-Flags_stats/` must return HTTP 200
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 0 | SITE-01 | build smoke | `cd site && npm run build` | ❌ Wave 0 | ⬜ pending |
| 3-01-02 | 01 | 0 | SITE-02 | build smoke | `cd site && npm run build && test -f site/dist/index.html` | ❌ Wave 0 | ⬜ pending |
| 3-02-01 | 02 | 1 | SITE-02 | build smoke | `cd site && npm run build && grep -l 'clip-card' site/dist/index.html` | ❌ Wave 0 | ⬜ pending |
| 3-02-02 | 02 | 1 | SITE-03 | build smoke | `cd site && npm run build && grep -r 'plyr' site/dist/clips/` | ❌ Wave 0 | ⬜ pending |
| 3-03-01 | 03 | 2 | SITE-01 | smoke | `curl -I https://krishnaikgaunekar.github.io/Korner-Flags_stats/` | ❌ Wave 0 (post-deploy) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `site/` directory — does not exist yet; must be created with `npm create astro@latest`
- [ ] `site/package.json` — created during Astro scaffold (with `astro` and `plyr` dependencies)
- [ ] `site/astro.config.mjs` — created during scaffold, configured with `base: '/Korner-Flags_stats'` + `site: 'https://krishnaikgaunekar.github.io'`
- [ ] `site/public/data/` — must be created; data files copied from `output_videos/`
- [ ] `.github/workflows/deploy.yml` — does not exist; must be authored in Phase 3

*All items are new infrastructure — no existing test infrastructure to extend.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Index page shows clip card gallery visually | SITE-02 | Build smoke only confirms HTML exists, not visual rendering | Run `npm run preview`, visit localhost, confirm cards render with thumbnail, title, duration, and CTA |
| Plyr player loads and video plays from CDN URL | SITE-03 | Requires browser + network + real CDN URL | Open clip detail page in browser, confirm Plyr controls appear, press Play, confirm video loads from GitHub Releases URL |
| GitHub Actions deploy succeeds end-to-end | SITE-01 | Requires GitHub Pages environment | Push to main, check Actions tab for green checkmark, visit `krishnaikgaunekar.github.io/Korner-Flags_stats/` |
| Asset URLs resolve correctly after deploy | SITE-01/02 | Dev works without base prefix; prod 404s if prefix missing | After deploy, check thumbnails and navigation links in browser DevTools network tab |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
