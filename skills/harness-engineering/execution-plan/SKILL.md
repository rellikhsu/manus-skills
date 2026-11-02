---
name: execution-plan
description: Durable, repo-checked-in plan files for multi-step work. Use before a multi-step implementation, for work spanning sessions or hand-offs, or to resume a plan in docs/exec-plans/.
metadata:
  short-description: "Create durable repo-checked-in plans for multi-step work, cross-session tracking, decisions, and follow-up debt."
---

# Execution Plan

**Write the plan for a stranger**: another agent with no history must be able to open the file and continue. Never write "as discussed", "the approach we agreed on", or "the file I edited earlier".

## Step 1: Decide plan weight

**No file** — use normal in-session planning when:
- One session, one clear area of code
- Nothing to decide; the approach is obvious
- The diff fully describes the work

**Durable plan file** — create one if **any** of these is true:
- The work will span several sessions, or will likely hit a context reset or compaction
- Another agent or subagent will continue it, or work runs in parallel branches
- There are non-obvious design decisions, where "what were we trying to do and why" would be unclear a week later
- Migrations, refactors that touch many files, or anything rolled out in stages
- The user asked for a plan file

Do not create plan files for trivial work.

## Step 2: Locate the plan directory

1. Look for an existing convention: `docs/exec-plans/`, `docs/plans/`, `plans/`, `.plans/`, or paths named in `CLAUDE.md` / `AGENTS.md`. **Use whatever already exists.**
2. Otherwise use these defaults:
   ```
   docs/exec-plans/active/<slug>.md
   docs/exec-plans/completed/<slug>.md
   docs/exec-plans/tech-debt-tracker.md
   ```
3. Plans live in the repo and are committed. Never put them in `/tmp` or a scratchpad.

## Step 3: Write the plan file

Use this skeleton.

```markdown
# <Title>

**Status:** active
**Started:** <YYYY-MM-DD — use the date if your context/tools supply one; otherwise ask the user.>

## Goal

What problem this solves and *why it matters*. State the current broken/limited
behavior and the desired end state.

## Scope

**In scope:** …
**Out of scope (explicitly):** …

## Acceptance criteria

Concrete, checkable criteria from the user's goal, verified by a command or a file. No "works well" / "is clean".

- [ ] `pytest tests/test_pool.py` passes with pool size configurable via env
- [ ] No direct `psycopg2.connect` calls remain outside `db/pool.py`

## Key context / entry points

Files, commands, and external facts a cold reader needs.

- Staging DB caps connections at 100

## Risks and open questions

- RISK: connection leaks under retry — mitigation: assert pool count in teardown
- OPEN: do background workers share the pool? — needs decision before Milestone 3

## Milestones

- [ ] M1 — Introduce pool module behind a feature flag
- [ ] M2 — Migrate request path
- [ ] M3 — Migrate background workers
- [ ] M4 — Remove flag and legacy connect path

## Progress & decision log

Append-only. Never rewrite or delete past entries. One entry per meaningful
checkpoint: a decision made, an approach abandoned, a blocker hit, a milestone
finished. Record *what was tried and why the choice was made*, not just what
changed.

### M1 — pool module landed
- Chose `psycopg_pool` over hand-rolled queue: already a transitive dep, handles
  reconnect. Rejected SQLAlchemy pooling — would pull in the whole ORM.
- Next: M2, start with `api/handlers/read.py` (lowest risk).
```

## Step 4: Keep it alive while working

Update the plan as you work.

- Tick milestone and acceptance boxes only after you verify they pass.
- Log departures from the plan; get approval before changing agreed Scope or acceptance criteria.
- Before any context reset, compaction, or hand-off, write the current state to the log first. "I'm about to lose context" always means: write now.
- When resuming, read the plan file *first*, before touching code, and trust it over your own memory.

## Step 5: Complete and close out

When all acceptance criteria pass:

1. Set `**Status:** completed` and add a final log entry with the result and anything a future reader should know.
2. Move the file into the `completed/` directory next to the plan's current directory:
   `mkdir -p <plans-dir>/completed && git mv <plans-dir>/active/<slug>.md <plans-dir>/completed/<slug>.md`
   If untracked, use `mv`, then `git add`. Keep the file; do not delete it.
3. Move unfinished follow-ups into `docs/exec-plans/tech-debt-tracker.md` instead of dropping them:

```markdown
## Connection pool: workers still use per-task connections
**Source:** exec-plans/completed/postgres-connection-pooling.md (M3 deferred)
**Impact:** ~40 idle connections at peak; risks hitting the staging cap of 100.
**Fix sketch:** reuse `db.pool.get_pool()` in `workers/base.py` teardown.
**Priority:** medium
```

4. Commit the move with the work.

## Anti-patterns

- Log entries that repeat the diff ("edited pool.py") instead of the reasoning.
