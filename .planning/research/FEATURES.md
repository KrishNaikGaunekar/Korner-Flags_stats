# Feature Research

**Domain:** Soccer/sports video analysis demo site (static, coaching pitch)
**Researched:** 2026-03-16
**Confidence:** MEDIUM-HIGH (competitor analysis via WebSearch verified across multiple sources; coaching workflow confirmed via NCAA/Frontiers research; UI patterns confirmed from Metrica Sports, Hudl, Wyscout, Spiideo)

---

## Context

This is a **static demo site on GitHub Pages** targeting NC State D1 soccer coaching staff. It is a pitch tool, not a product — the goal is to make 2-3 pre-processed NC State clips look polished, credible, and show what the AI pipeline can do. The audience (D1 coaching staff) already uses Hudl and Wyscout daily. They have seen video analysis tools. They will compare this to those tools, even subconsciously.

The features below are scoped to what a static site can realistically deliver (no backend, no upload flow) in 1-2 weeks.

---

## Feature Landscape

### Table Stakes (Coaches Expect These — Missing = Not Taken Seriously)

Features D1 coaches see in every professional tool they use. Missing these signals "this is a rough prototype."

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Annotated video playback | Every tool from Hudl to Wyscout shows the processed video with overlays — it IS the product | LOW | HTML5 `<video>` + pre-rendered AVI/MP4 from existing pipeline; must convert AVI to MP4 for browser support |
| Possession % display | The single most-cited team stat in coaching circles; coaches lead with "who controlled the ball?" | LOW | Already in stats JSON from pipeline; render as a visual bar or donut chart alongside video |
| Player speed / distance stats | Physical load metrics are table stakes in college athletics; every GPS tracker shows these | LOW | Already in stats JSON; display as per-player table or bar chart |
| Team color differentiation in video | Coaches need to instantly tell which team is which in the overlay — unlabeled colored blobs are useless | LOW | Pipeline already assigns team colors via KMeans; verify colors are visually distinct in output |
| Multi-clip gallery / clip browser | If there's only one video with no navigation, the demo feels like a one-trick demo reel, not a platform | LOW | Static HTML grid of 2-3 clip cards with thumbnail + title; click to view clip + stats |
| Match metadata display | Duration, date, teams involved, clip context — without this coaches can't orient what they're watching | LOW | Static text alongside each clip; NC State vs opponent, date, match context |
| Pitch minimap or tactical view | Coaches expect a bird's-eye pitch view to accompany the video — it's how analysts present to teams | MEDIUM | Can be a static heatmap image generated from position data; does not need to be interactive |
| Clear stats-to-video correlation | Stats must be visually connected to the clip — not a separate tab coaches have to find | LOW | Layout decision: stats panel beside or below the video player, not on a separate page |

### Differentiators (Competitive Advantage / Wow Factor for This Demo)

Features that go beyond what coaches get from Hudl (which doesn't do automatic AI detection from raw video) and show what the AI pipeline uniquely provides.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Per-player heatmap (position density) | Coaches immediately ask "where was player X operating?" — a heatmap is the standard answer and it's visual-first | MEDIUM | Generate as static image from `position_transformed` data in tracks JSON using matplotlib + pitch overlay; render once, embed as `<img>` |
| Automated player ID and tracking callout | Hudl requires manual tagging; showing that IDs were assigned automatically from video alone is the core differentiator — highlight this explicitly in the UI | LOW | Copy/explainer text in the UI; show tracked IDs in the video overlay as proof |
| AI pipeline transparency section | Coaches and admins asking "how does this work?" will trust it more if the pipeline is explained plainly — builds credibility for the pitch | LOW | Simple "How It Works" section: detect → track → cluster → analyze; diagram or step list |
| Speed timeline per player | Not just a single speed number — showing how speed changed across the match demonstrates depth of analysis that GPS vendors charge thousands for | MEDIUM | Line chart of speed-over-frame for a selected player; requires per-frame speed data from JSON which pipeline already produces |
| Team possession timeline (not just %) | A bar-over-time showing which team had possession by frame segment is more compelling than a single % number | MEDIUM | Bin `team_ball_control` array into 30-second windows; render as horizontal segmented bar; data already in JSON |

### Anti-Features (Deliberately NOT Building for v1)

Features that seem reasonable but will blow the 1-2 week deadline, add fragility, or distract from the core pitch.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Live video upload + cloud processing | "Can I upload my own video?" is the first question coaches ask | Requires GPU backend, auth, storage, latency management — minimum 4-6 additional weeks of infrastructure | Pre-process NC State clips locally; frame the demo as "here's what the system produced" with a clear roadmap slide for Phase 2 |
| Interactive heatmap (click to filter by player/time) | Would be impressive | Requires D3.js or similar, JSON data ingestion on the client, significant JS complexity — easily 3-5 extra days | Static heatmap images per player, pre-generated; can cover the same insight without the complexity |
| Pass network visualization | Passes + connections graph is a well-known soccer analytics visual | Pass/event detection is not yet implemented in the pipeline (listed as gap in PROJECT.md) — building this requires new ML work | Defer; list as "coming next" in demo |
| Player comparison side-by-side | Useful for scouts, but not the immediate need for a coaching pitch | Requires multi-player selection UI, layout work, more complex stats panel — scope creep | Single-player speed/distance table covers the need for the demo |
| Full-match scrubbing with live stat updates | Stats update as you scrub through video | Requires video-time-synced JSON parsing in JS, non-trivial synchronization logic | Pre-render the annotated video with overlays baked in (pipeline already does this) |
| Account / login / saved sessions | "So coaches can save their notes" | Eliminates GitHub Pages as hosting option entirely; requires backend | Out of scope; Phase 2 web app |
| Mobile-responsive heavy optimization | Coaches might view on tablet | Demo is a laptop pitch — over-investing in responsive layout delays the core content work | Basic responsive layout only; not the focus |

---

## Feature Dependencies

```
[Multi-clip gallery]
    └──requires──> [Per-clip annotated video (MP4)]
                       └──requires──> [AVI-to-MP4 conversion of pipeline output]

[Stats panel (possession %, speed, distance)]
    └──requires──> [Stats JSON from pipeline]
                       └──already exists in pipeline output

[Per-player heatmap (static image)]
    └──requires──> [position_transformed data in tracks JSON]
    └──requires──> [Heatmap generation script (new Python script)]
                       └──requires──> [matplotlib + mplsoccer or pitch outline drawing]

[Possession timeline visualization]
    └──requires──> [team_ball_control array in stats JSON]
                       └──already exists in pipeline output

[Speed timeline chart]
    └──requires──> [Per-frame speed data in stats JSON]
                       └──NOTE: current stats JSON aggregates speed; per-frame export may need pipeline tweak]

[AI pipeline transparency section]
    └──independent (static content only)

[Match metadata display]
    └──independent (static content, manually authored per clip)
```

### Dependency Notes

- **AVI-to-MP4 conversion is a hard blocker:** Browsers do not reliably play AVI files. Every video feature depends on having MP4 output. This needs to be solved before any video UI work begins. FFmpeg conversion is trivial but must be explicit in the build process.
- **Stats JSON → visualization:** All chart features depend on the stats JSON schema being stable. The pipeline already produces this; confirm the schema before building frontend parsers.
- **Heatmap generation requires new code:** `position_transformed` data exists in the tracks dict but is not currently exported to JSON in a per-frame positional format. The pipeline generates a stats JSON with aggregates; heatmap generation requires either extending the JSON export or a separate post-processing script that reads the stub/pkl data.
- **Per-frame speed data:** The current stats JSON likely contains final aggregate speed stats. A speed timeline chart requires per-frame or per-window data. This may require a pipeline output format change — verify before committing to this feature.
- **Pass network is a hard dependency skip:** Cannot build pass visualization without pass detection, which is not in the pipeline. Do not attempt to fake it.

---

## MVP Definition

### Launch With (v1 — the coaching demo)

Minimum set that makes the demo credible and impactful for an NC State coaching staff pitch.

- [ ] **Annotated video player (MP4)** — the core artifact; everything else is context around it. Must have correct team color overlays, player ellipses, ball triangle visible.
- [ ] **Multi-clip gallery** — at least 2-3 NC State clips with thumbnails; coaches need to see the system works on multiple clips, not just one cherry-picked example
- [ ] **Possession % + team bar** — visual, not just a number; side-by-side team colors with percentages
- [ ] **Per-player speed and distance table** — sortable or at minimum ranked; shows physical output per player
- [ ] **Static per-team heatmap** — one heatmap per team per clip; the most visually impressive output; coaches recognize this format instantly
- [ ] **Match metadata** — teams, date, clip context; anchors the demo in reality (NC State branding helps)
- [ ] **"How It Works" section** — one-paragraph or 4-step visual explaining AI detection; builds trust for the pitch

### Add After Validation (v1.x)

Add these if demo lands well and there's time before the follow-up meeting.

- [ ] **Possession timeline (segmented bar)** — upgrades the possession % to show ebb and flow; moderate effort, high visual impact once data format is confirmed
- [ ] **Per-player individual heatmaps** — drill-down from team heatmap; useful if coaches ask "can I see where player 7 was?"
- [ ] **Speed timeline chart** — shows athletic intensity over match; needs per-frame data export verification first

### Future Consideration (v2+)

Defer until Phase 2 web app is being built.

- [ ] **Video upload + cloud processing** — requires GPU backend infrastructure
- [ ] **Pass and event detection** — requires new ML pipeline work
- [ ] **Interactive heatmaps** — worth building once backend exists
- [ ] **Player comparison view** — scouting-oriented feature; relevant once platform is validated
- [ ] **Coach accounts and saved sessions** — requires auth backend

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Annotated video player (MP4) | HIGH | LOW | P1 |
| AVI-to-MP4 conversion | HIGH | LOW | P1 (blocker) |
| Multi-clip gallery | HIGH | LOW | P1 |
| Possession % display | HIGH | LOW | P1 |
| Player speed/distance table | HIGH | LOW | P1 |
| Team heatmap (static image) | HIGH | MEDIUM | P1 |
| Match metadata | MEDIUM | LOW | P1 |
| "How It Works" section | MEDIUM | LOW | P1 |
| Possession timeline bar | HIGH | MEDIUM | P2 |
| Per-player heatmaps | MEDIUM | MEDIUM | P2 |
| Speed timeline chart | MEDIUM | MEDIUM | P2 (verify data format first) |
| Pass network | HIGH | HIGH | P3 (blocked on pipeline) |
| Interactive heatmap | MEDIUM | HIGH | P3 |
| Upload flow | HIGH | HIGH | P3 (Phase 2) |

---

## Competitor Feature Analysis

| Feature | Hudl (standard D1 use) | Metrica Sports / Wyscout | Our Approach |
|---------|------------------------|--------------------------|--------------|
| Video playback with overlays | Manual tagging required; user draws annotations | Automated tracking overlays, AI-assisted | Pre-rendered annotated video baked in — simpler UX than either competitor |
| Heatmaps | Available but requires tagging workflow | Automated from tracking data | Generated from AI pipeline position data; same quality, zero coach effort |
| Possession % | Manual event-based calculation | Automated from tracking | Automated via nearest-player + 15-frame smoothing; no manual input |
| Speed/distance | Requires GPS vests/hardware ($$$) | Available in premium tiers | Derived purely from video via perspective transform — no hardware needed; this is the pitch |
| Clip library | Full Hudl library with tagging | Match database, complex UI | 2-3 focused NC State clips; simplicity is an asset for a demo pitch |
| Upload own video | Yes (core product) | Yes | Phase 2 roadmap item; demo is pre-processed |

**Key competitive angle:** The pipeline requires only a video file — no GPS hardware, no manual tagging, no complex software installation. For college programs with limited budgets and analyst staff, this is a meaningful differentiator. The demo site should make this explicit.

---

## Sources

- [Metrica Sports — Automatic Player Tracking](https://www.metrica-sports.com/help-center/playbase-fundamentals/automatic-player-tracking)
- [Metrica Sports — Video Analysis Overview](https://www.socceredu.com/en-US/blog/metrica-sports)
- [Hudl Wyscout — Data Analytics Software](https://www.hudl.com/products/wyscout)
- [Spiideo Perform](https://www.spiideo.com/spiideo-perform/)
- [Heat Maps in Soccer — Soccer Wizdom](https://soccerwizdom.com/2025/03/13/heat-maps-in-soccer-tracking-movement-performance-and-strategy/)
- [Action Heatmaps in Football Video Analysis — Zone14 AI](https://zone14.ai/en/blog/heatmaps-data-visualisation-football-video-analysis/)
- [Football Player Performance: Using Heatmaps and Stats — Sofascore](https://www.sofascore.com/news/football-player-performance-how-to-use-heatmaps-stats-and-attribute-overviews-to-measure-contribution/)
- [A Day in the Life of a Performance Analyst — American Soccer Analysis](https://www.americansocceranalysis.com/home/2020/3/18/a-day-in-the-life-of-a-performance-analyst)
- [Digital Shift in College Athletics — Emory Wheel](https://www.emorywheel.com/article/2025/12/the-digital-shift-in-college-athletics-how-technology-is-changing-coaching-strategies)
- [NCAA Experimental Video Review Rule — NCAA.org](https://www.ncaa.org/news/2025/4/17/media-center-experimental-video-review-challenges-approved-in-mens-and-womens-soccer.aspx)
- [Top 10 Features Every Sports Analytics App Must Have in 2026](https://developersappindia.com/blog/top-10-features-every-sports-analytics-app-must-have-in-2026)
- [KINEXON Sports — Benefits and Features of Sports Analysis Software](https://kinexon-sports.com/blog/benefits-and-features-of-sports-analysis-software-for-coaches/)
- [Sports Data UX Design — SGX Studio](https://sgx.studio/sports-data-ux-design-making-complex-stats-digestible/)

---

*Feature research for: Soccer video analysis demo site (static, GitHub Pages, coaching pitch)*
*Researched: 2026-03-16*
