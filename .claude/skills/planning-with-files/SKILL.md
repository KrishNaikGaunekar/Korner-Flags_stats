# Planning With Files — Persistent Markdown Planning Skill

## Purpose
Use this skill when starting any non-trivial task. Write a plan to a markdown file first, get alignment, then execute. This prevents wasted work and keeps implementation traceable.

## When to Use
- Multi-file changes (3+ files)
- Architectural decisions or refactors
- New features with unclear scope
- Debugging complex pipeline issues

## Workflow

### Step 1 — Draft the plan file
Create `PLAN.md` (or a task-specific file like `PLAN-speed-fix.md`) at repo root:

```markdown
# Plan: <task title>

## Goal
One sentence: what done looks like.

## Approach
- Step 1: ...
- Step 2: ...
- Step 3: ...

## Files to Change
| File | What changes |
|------|-------------|
| foo.py | Add X |

## Risks / Open Questions
- ...

## Out of Scope
- ...
```

### Step 2 — Confirm with user before coding
Show the plan, ask: "Does this match what you want? Any changes before I start?"

### Step 3 — Execute, updating plan as you go
Check off steps as you complete them. Add a `## Status` section.

### Step 4 — Clean up
Delete or archive the plan file once the work is committed.

## Rules
- Never start implementing without a plan for multi-step tasks
- Plans live in the repo, not just in chat (so they survive context resets)
- Keep plans short — bullet points, not prose
- One plan file per initiative (don't mix unrelated tasks)
