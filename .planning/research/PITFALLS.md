# Pitfalls Research

**Domain:** Soccer video analysis demo site — GitHub Pages static hosting with pre-processed video
**Researched:** 2026-03-16
**Confidence:** HIGH (GitHub Pages limits verified against official docs; codec issues verified against MDN/caniuse; ML pitfalls verified against official Ultralytics/Roboflow docs and peer-reviewed papers; codebase bugs independently confirmed in CONCERNS.md)

---

## Critical Pitfalls

### Pitfall 1: GitHub Pages Serves Git LFS Pointer Files, Not Actual Videos

**What goes wrong:**
A developer commits large video files (>100 MB) using Git LFS, deploys to GitHub Pages, and the site appears to work. But visitors loading the video see either a blank player or a download of a 130-byte text file that reads `version https://git-lfs.github.com/spec/v1`. GitHub Pages does not resolve LFS pointers — it serves the pointer text verbatim.

**Why it happens:**
Git LFS is a common recommendation for large binary files in GitHub repos. Developers assume that because git pull works locally, Pages deployment will too. GitHub Actions deployments only pull LFS files if explicitly instructed with `lfs: true` in the checkout step. The default checkout skips LFS, pushing the pointer file to the published branch.

**How to avoid:**
Do not use Git LFS for video files that will be served by GitHub Pages. Either:
- Keep annotated output videos under 100 MB each (compress to H.264 MP4 before committing)
- Host videos on an external service (YouTube unlisted, Cloudflare R2, or AWS S3 public bucket) and reference them by URL in the site
- If using GitHub Actions to deploy, add `with: lfs: true` to the `actions/checkout` step AND confirm the deployed branch contains real binaries, not pointers

**Warning signs:**
- `git lfs ls-files` shows tracked video files
- `git lfs status` shows files as "pushed" but video players on the deployed site show blank or stall immediately
- Downloading the video from the deployed URL produces a file under 200 bytes

**Phase to address:** Video hosting / site scaffolding phase (before any content is committed)

---

### Pitfall 2: AVI Output Cannot Play in Any Browser

**What goes wrong:**
The pipeline outputs `_annotated.avi` by default (confirmed: `main.py` lines 45 and 164). AVI with XVID/MJPEG codec — the default OpenCV VideoWriter codec — is not supported by any major browser's `<video>` element. The video player renders, the file loads, playback never starts. On Chrome and Firefox the spinner appears briefly then stops. No error is shown to the user.

**Why it happens:**
OpenCV's default codec on Windows is XVID wrapped in AVI. XVID is an MPEG-4 Part 2 codec, distinct from H.264 (MPEG-4 Part 10/AVC). Browsers support H.264 in MP4 containers universally; they do not support XVID. AVI as a container also lacks the byte-range request support browsers need for seeking in a `<video>` element.

**How to avoid:**
Before uploading processed videos for the demo:
1. Re-encode every AVI output to H.264 MP4: `ffmpeg -i annotated.avi -c:v libx264 -crf 23 -preset fast -movflags +faststart output.mp4`
2. The `+faststart` flag moves the MP4 moov atom to the front of the file, enabling playback before full download
3. Alternatively modify the pipeline's VideoWriter to output MP4 directly using the `mp4v` fourcc, though this still requires `+faststart` post-processing for web use

**Warning signs:**
- Processed video files have `.avi` extension
- Video plays in VLC locally but not in the browser
- Chrome DevTools Network tab shows the video request completing (200) but the player shows nothing

**Phase to address:** Video processing / pre-processing pipeline phase

---

### Pitfall 3: Repository Size Exceeds GitHub Pages 1 GB Limit Before Demo Day

**What goes wrong:**
Three NC State clips at 1080p, 90 seconds each, annotated at ~8 Mbps H.264, is approximately 270 MB of video. Add heatmap images, stats JSON, the JavaScript bundle, and the original (unannotated) clips if stored, and the repository crosses 1 GB. GitHub Pages has a documented 1 GB published site limit. Exceeding it means Pages may refuse to build or serve the site. Because the limit is "soft," the failure mode is unpredictable — sometimes silent, sometimes causing build timeouts.

**Why it happens:**
Developers scope video size by what "looks reasonable" for 2–3 clips without calculating cumulative repository size including all assets. Git history compounds the problem: a replaced video file remains in history, doubling effective storage.

**How to avoid:**
- Target 30–60 seconds per clip at 720p for demo purposes — coaches care about seeing the annotations, not full-match footage
- Calculate total repo size before committing: `du -sh .git` after staging
- Keep the demo site in a separate repository from the analysis codebase to isolate size budgets
- Use `git gc --aggressive` after removing large files from history with `git filter-repo`
- If clips must be longer, host video files externally (YouTube unlisted or Cloudflare R2) — embed via `<video src="https://...">` rather than committing binaries

**Warning signs:**
- `du -sh .` in the repo exceeds 800 MB
- `git push` times out or returns a "large file" warning
- GitHub Pages build action shows "repository too large" in logs

**Phase to address:** Site scaffolding / asset strategy phase (decision must be made before any video is committed)

---

### Pitfall 4: Speed and Distance Numbers Are Wrong Due to Known Pipeline Bugs

**What goes wrong:**
The speed/distance stats displayed in the demo are calculated incorrectly for any video with camera movement. The `ViewTransformer` reads `position` instead of `position_adjusted` (confirmed: CONCERNS.md, `view_transformer.py` line 54). Camera pan corrections computed by optical flow are silently discarded. The displayed km/h and metres values will be higher than actual for any clip where the camera pans to follow play — which is every broadcast clip.

A second compounding bug: `old_feature` (singular) is assigned instead of `old_features` (plural) in the camera movement loop (CONCERNS.md line 65), meaning feature point refresh never actually takes effect and camera movement estimation itself drifts for any clip longer than a few seconds.

Pitching inaccurate numbers to D1 coaching staff who know what player speeds look like destroys credibility instantly.

**Why it happens:**
The bugs exist in the current codebase and have no workaround. They are silent — no error, no warning, just wrong output numbers.

**How to avoid:**
Fix both bugs before processing any demo footage:
1. In `view_transformer.py` line 54: change `position` to `position_adjusted`
2. In `camera_movement_estimator.py` line 65: change `old_feature` to `old_features`

After fixing, validate speed output on a clip with known camera pan: a player standing still should read 0 km/h regardless of camera movement.

If the perspective transform estimated vertices are also approximate (they are — CONCERNS.md notes they are proportional estimates, not calibrated keypoints), add a visible disclaimer: "Speed/distance estimates are approximate; calibrated field registration planned for v2."

**Warning signs:**
- Displayed player speeds consistently exceed 35 km/h (D1 soccer top speed is ~32 km/h)
- Players standing still show non-zero speed values while camera pans
- Speed values jump discontinuously between frames during camera movement

**Phase to address:** Bug fixes / pipeline validation phase — must be completed before processing demo footage

---

### Pitfall 5: Team Color Assignment Fails on NC State Footage

**What goes wrong:**
`assign_teams` trains KMeans on players visible only in frame 0 of the video (confirmed: `main.py` line 107, CONCERNS.md). If the NC State clip opens on a close-up, a scoreboard shot, a partial view, or a frame where fewer than 4 players are visible, KMeans trains on insufficient samples and produces a garbage color model for the entire clip. All subsequent frames will have players randomly or incorrectly assigned to teams.

Additional failure mode: NC State's red-and-white jersey against a common opponent may have low color separation depending on the opposing team's colors. KMeans with k=2 will always produce two clusters even when color separation is poor, silently giving wrong assignments with no confidence signal.

**Why it happens:**
The single-frame training approach is a design shortcut. It works when the opening frame happens to show both teams in a full field view. This is not guaranteed for broadcast or sideline footage, which frequently opens with a close-up or replay.

**How to avoid:**
- Manually inspect each demo clip and identify a frame index with clear visibility of both teams in full-pitch view
- Modify `main.py` to accept a `--team-frame` argument, or manually seek to a good frame before team assignment
- After processing, visually audit the first 30 seconds of annotated output to confirm team color ellipses are correct before including the clip in the demo
- If a clip shows jersey color ambiguity, choose a different clip or note the limitation explicitly

**Warning signs:**
- Annotated output shows players on the same team with different colored ellipses
- Team 1 and Team 2 possession totals sum to less than 80% of frames (referees and misclassified players absorb possession)
- The opening seconds of the clip show fewer than 8 players

**Phase to address:** Demo footage selection and validation phase

---

### Pitfall 6: YOLO Model Does Not Generalize to NC State Camera Angles

**What goes wrong:**
The model (`models/best.pt`) was trained on specific broadcast footage. NC State sideline/press-box footage from a different camera height, distance, or angle may produce significantly degraded detection: missed players, false positives on referees or spectators, and ball detection failures. Domain shift from training distribution to NC State footage is the single largest unknown in the project.

Specific failure modes: players detected as referees (wrong class → excluded from possession), ball not detected in 40%+ of frames (possession stat unusable), multiple detections per player at high camera distances (tracking ID thrash).

**Why it happens:**
Object detection models are sensitive to camera viewpoint, resolution, and background. A model trained on Premier League broadcast cameras (high, behind goal) may fail on a press-box angle or a wide-angle sideline camera — the scale, pose, and background of players are different distributions.

**How to avoid:**
- Test the model on a 60-second clip of NC State footage before committing to the full pipeline
- Evaluate detection metrics visually: are all visible players detected? Is the ball detected consistently?
- If detection quality is poor, fine-tune the model on a small sample of NC State frames (10–50 labeled frames via Roboflow can significantly improve generalization)
- Lower the confidence threshold (`--confidence 0.10` or `0.12`) if players are being missed; raise it if false positives dominate
- Select demo clips from the camera angle/distance closest to the training distribution

**Warning signs:**
- Fewer than 16 player bounding boxes in frames where 20+ players are visible
- Ball detection is absent for more than 5 consecutive seconds
- Referee bounding boxes vastly outnumber player bounding boxes

**Phase to address:** Model validation phase — must be tested before processing full clips

---

### Pitfall 7: Demo Credibility Destroyed by Showing Technical Metrics to Coaches

**What goes wrong:**
The demo leads with computer vision metrics (mAP, IoU, frame detection rate, confidence scores) or raw JSON stats. Coaches disengage immediately. They do not know what mAP means and do not care. The opportunity to show tactical value is lost within 60 seconds.

**Why it happens:**
Developers build what they can measure and present what they built. The pipeline produces tracking IDs, confidence scores, and detection counts — so those get shown. Coaches evaluate tools by one question: "Does this help me see something about my team I couldn't see before?"

**How to avoid:**
- Lead with the annotated video — show movement, not metrics
- Frame possession % as "your team had the ball 58% of the time in the first half" not "possession tracking accuracy is 94%"
- Frame speed as "your #9 covered 11.2 km — comparable to professional standards" not "speed estimation uses perspective transform"
- Do not show confidence thresholds, bounding box counts, or processing time on the demo
- Provide a one-sentence explanation for every statistic: "Possession % = frames where our team's nearest player was within 2 metres of the ball"

**Warning signs:**
- The demo landing page has a "How It Works" section before the video
- Stats are labeled with variable names from the JSON output (`player_id`, `frame_count`, `kmh`)
- The demo requires scrolling past technical explanation before seeing the video

**Phase to address:** Site UX / content design phase

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Commit videos directly to repo | No external hosting setup | Repo bloats; LFS trap; 1 GB limit hit during demo | Only if total video < 50 MB and no future clips planned |
| Use AVI output directly without re-encoding | Skip ffmpeg step | Videos don't play in browsers | Never for web demo |
| Show raw JSON stats in UI | No formatting work | Coaches see variable names; demo fails | Never for coaching audience |
| Skip bug fixes and add disclaimer | Faster to ship | Inaccurate speed/distance; credibility loss with D1 staff | Never — fix the bugs |
| Use first-frame-only team assignment without validation | Simpler pipeline | Wrong team colors silently in output | Only if clip is manually validated to have good frame 0 |
| Single video format (no WebM fallback) | Less encoding work | Playback failure on older or non-standard browsers | Acceptable if targeting Chrome/Safari/Firefox modern versions with H.264 MP4 |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub Pages deployment | Committing LFS-tracked videos; pointer files served instead of video | Commit real binaries under 100 MB; use external hosting for larger files |
| `<video>` element with AVI | Embedding AVI path directly in HTML | Re-encode to H.264 MP4 with `+faststart`; use `.mp4` extension |
| OpenCV VideoWriter → web | Using default `XVID` fourcc | Use `mp4v` or post-process with ffmpeg to H.264 |
| GitHub Actions Pages deploy | Default `actions/checkout` skips LFS | Add `lfs: true` to checkout step if LFS is used anywhere |
| Perspective transform calibration | Using estimated vertices for reported stats | Label output as "approximate" or calibrate from known field markings |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Entire video loaded into RAM before processing | Processing hangs or crashes silently on clips > 5 minutes | Use `--max-frames` argument; process 30–90 second clips only for demo | ~5 min at 1080p 25fps on 16 GB RAM |
| KMeans fit called twice per player per frame | Processing takes 2× longer than expected during team assignment | Fix the redundant `.fit()` call in `team_assigner.py` (CONCERNS.md) | Visible on clips with > 100 frames |
| Unpinned `supervision` dependency | Works locally, breaks on clean install | Pin `supervision>=0.18.0,<0.25.0` in requirements.txt | Next time someone installs on a fresh machine |
| AVI with XVID on GitHub Pages | Video silently fails to play | Re-encode all output to H.264 MP4 before committing | Every browser, every visitor |

---

## "Looks Done But Isn't" Checklist

- [ ] **Video playback:** Open each embedded video in Chrome, Firefox, and Safari — not just locally in VLC. Autoplay-muted and manual play both tested.
- [ ] **Team colors:** Watch first 30 seconds of each annotated clip — confirm NC State players consistently show one color ellipse, opponents another. Not a 50/50 split across both teams.
- [ ] **Speed values:** Spot-check: a player who appears stationary on screen should show 0–2 km/h. Any value above 35 km/h indicates the camera movement bug is still present.
- [ ] **Possession %:** Should sum to approximately 100% across the two teams plus a small referee fraction. If either team shows > 80%, team assignment likely failed.
- [ ] **Video file sizes:** Run `du -sh .git` after staging video files. Total must stay under 800 MB.
- [ ] **LFS check:** `git lfs ls-files` should return empty. No video files tracked in LFS.
- [ ] **Mobile viewport:** Load site on a phone. Video player must be viewable without horizontal scrolling.
- [ ] **Stats labels:** Every stat shown to a coach has a plain-English label and a one-sentence explanation — no variable names, no jargon.
- [ ] **External video URL check:** If videos are hosted externally, load the site from a different machine/network and confirm videos load (not just from dev machine where cache may mask failures).

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| LFS pointer files served by Pages | MEDIUM | `git lfs untrack "*.mp4"`, re-commit binaries normally, force-push or rewrite history with `git filter-repo` |
| AVI files committed and not playing | LOW | Re-encode with ffmpeg locally, replace files with `git rm` + commit new `.mp4` versions |
| Repo over 1 GB | HIGH | Move videos to external hosting; remove from git history with `git filter-repo --path videos/ --invert-paths` |
| Wrong team colors in output | LOW | Re-process clip with `--team-frame N` pointing to a better frame; re-annotate |
| YOLO fails on NC State footage | MEDIUM | Fine-tune on 20–50 manually labeled NC State frames via Roboflow; takes 1–2 days |
| Inaccurate speed stats in demo | LOW (if bugs fixed) | Apply two-line code fix (CONCERNS.md); re-process clips; takes < 1 hour |
| Demo failed in coaching meeting | HIGH | Rebuild focus on visual output only, defer stats; schedule follow-up demo |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| LFS pointer files | Asset strategy / site scaffolding | `git lfs ls-files` returns empty before first push |
| AVI browser incompatibility | Video processing pre-pass | All `.mp4` files play in Chrome DevTools Network with 206 responses |
| Repository size limit | Asset strategy / site scaffolding | `du -sh .git` under 800 MB before adding any video |
| Wrong speed/distance (pipeline bugs) | Bug fix phase before demo processing | Stationary player test shows < 2 km/h during camera pan |
| Team color assignment failure | Demo footage validation | Visual audit of annotated output confirms consistent team colors |
| YOLO domain shift on NC State footage | Model validation before full processing | 60-second test clip shows > 80% player detection rate |
| Technical metrics shown to coaches | UX / content design phase | Demo walkthrough with non-technical person — can they explain each stat without asking? |

---

## Sources

- [GitHub Pages Limits — Official Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) — HIGH confidence
- [Git LFS does not work with GitHub Pages (official community thread)](https://github.com/orgs/community/discussions/50337) — HIGH confidence
- [GitHub git-lfs issue #3498: git-lfs doesn't work with Github Pages](https://github.com/git-lfs/git-lfs/issues/3498) — HIGH confidence
- [MDN Web Docs: Web video codec guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/Video_codecs) — HIGH confidence
- [Can I Use: MPEG-4/H.264](https://caniuse.com/mpeg4) — HIGH confidence
- [YOLO-Based Object Detection and Player Tracking for Football — Zenodo](https://zenodo.org/records/16929566) — MEDIUM confidence
- [Domain Generalization in Autonomous Driving: Evaluating YOLO variants — arXiv](https://arxiv.org/html/2412.12349v1) — MEDIUM confidence
- [Deep learning detection of players and heatmap generation — Emerald Applied Computing](https://emerald.com/insight/content/doi/10.1108/aci-07-2024-0257/full/html) — MEDIUM confidence
- [Camera Calibration in Sports with Keypoints — Roboflow Blog](https://blog.roboflow.com/camera-calibration-sports-computer-vision/) — MEDIUM confidence
- [Codebase-specific bugs — C:/Korner flag/.planning/codebase/CONCERNS.md](C:/Korner flag/.planning/codebase/CONCERNS.md) — HIGH confidence (first-party audit)

---

*Pitfalls research for: soccer video analysis — GitHub Pages demo site*
*Researched: 2026-03-16*
