---
phase: 5
slug: heatmap-visualizations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — build-time validation only |
| **Config file** | `site/package.json` (build script) |
| **Quick run command** | `cd "C:/Korner flag/site" && npm run build` |
| **Full suite command** | `cd "C:/Korner flag/site" && npm run build` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd "C:/Korner flag/site" && npm run build`
- **After every plan wave:** Run `cd "C:/Korner flag/site" && npm run build`
- **Before `/gsd:verify-work`:** Build must succeed + visual confirmation of heatmap display
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | SITE-05 | smoke (build) | `cd "C:/Korner flag/site" && npm run build` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files or framework setup needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Team 1 image renders left, Team 2 right | SITE-05 | Visual layout — not checkable by build | Open clip page in browser, confirm side-by-side layout |
| Team labels are blue (#0071e3) and orange (#e8732a) | SITE-05 | CSS color — not checkable by build | Inspect element or visually confirm colored headings |
| Section collapses to single column at 640px | SITE-05 | Responsive CSS — requires viewport resize | Resize browser to ≤640px, confirm single-column stacking |
| Images do not 404 after deploy | SITE-05 | Deploy-time path resolution | Check GitHub Actions deploy, confirm images load on live site |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
