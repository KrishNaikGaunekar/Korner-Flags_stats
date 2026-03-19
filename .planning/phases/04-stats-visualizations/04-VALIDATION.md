---
phase: 4
slug: stats-visualizations
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — static Astro site; build success is primary automated check |
| **Config file** | none — no test runner configured |
| **Quick run command** | `cd site && npm run build` |
| **Full suite command** | `cd site && npm run build && npm run preview` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd site && npm run build`
- **After every plan wave:** Run `cd site && npm run build` — grep built HTML for required strings
- **Before `/gsd:verify-work`:** Build clean + visual review of deployed page at realistic viewport
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | SITE-04 | smoke | `cd site && npm run build` — dist HTML contains "Top Speed" | ❌ Wave 0 | ⬜ pending |
| 4-01-02 | 01 | 1 | SITE-06 | smoke | `cd site && npm run build` — dist HTML contains "AI-estimated ±5%" | ❌ Wave 0 | ⬜ pending |
| 4-01-03 | 01 | 1 | SITE-07 | smoke | `cd site && npm run build` — dist HTML contains "Avg Speed", "Distance" | ❌ Wave 0 | ⬜ pending |
| 4-01-04 | 01 | 1 | SITE-08 | smoke | `cd site && npm run build` — dist HTML contains "Coming Soon" | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- No automated test framework exists — build success is the only automated check
- Manual visual review required after deploy to verify layout at realistic viewport

*Existing Astro build infrastructure covers all phase requirements (build errors catch template mistakes).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Possession bar visually resembles broadcast TV split-bar | SITE-04 | CSS layout — cannot be grepped | Load clip page, verify horizontal split bar shows two colored segments with % labels |
| Player table split by team is readable and correctly sorted | SITE-04, SITE-07 | Visual layout | Load clip page, verify Team 1 / Team 2 sections each show player rows sorted by ID ascending |
| Coming Soon cards visually greyed with lock icon | SITE-08 | Visual styling | Load clip page, verify 4 muted cards below player table show lock icon and "Coming Soon" label |
| Zero-stat players filtered from table | SITE-04 | Data quality | Verify no player rows show 0 km/h and 0 m for all columns |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
