---
name: "harness-engineering:execution-plan"
description: Create and maintain durable, repo-checked-in execution plan files for non-trivial multi-step work. Use before starting a multi-step implementation, when the user says "write an exec plan" / "make a plan file" / "track this across sessions", when work will span context resets, sessions, or hand-offs to another agent, or when resuming work that already has a plan file under docs/exec-plans/. Also use to log decisions mid-task, mark a plan complete, or record follow-up tech debt.
description-short: Create and maintain durable, repo-checked-in execution plan files for multi-step work. Use before multi-step work, to track it across sessions, or resuming a plan under docs/exec-plans/.
---

# Execution Plan

A plan that lives only in the conversation does not exist. Context gets reset, compacted, or handed to a different agent — and everything not in a file is gone. Durable plan files are what make a clean context reset safe mid-task.

**Write the plan for a stranger**: a different agent, cold, with no history, must be able to open the file and continue. Never write "as discussed", "the approach we agreed on", or "the file I edited earlier".

## Step 1: Decide plan weight

**Ephemeral plan (no file)** — just use normal in-session planning / TodoWrite:
- Single-session, roughly under ~10 steps, one clear area of code
- Nothing to decide — the approach is obvious
- Fully described by the diff it produces

**Durable plan file** — create it if **any** of these hold:
- Work will span multiple sessions, or is likely to hit a context reset/compaction
- Another agent or subagent will pick it up, or work runs in parallel branches
- Non-obvious design decisions exist, where "what were we trying to do and why" would be unclear a week later
- Migrations, refactors touching many files, or anything with staged rollout
- The user asked for a plan file

If borderline, ask the user once. Do not create plan files for trivial work — clutter costs future agents attention.

## Step 2: Locate the plan directory

1. Check for an existing convention: `docs/exec-plans/`, `docs/plans/`, `plans/`, `.plans/`, or paths named in `CLAUDE.md` / `AGENTS.md`. **Follow whatever already exists.**
2. Otherwise default to:
   ```
   docs/exec-plans/active/<slug>.md
   docs/exec-plans/completed/<slug>.md
   docs/exec-plans/tech-debt-tracker.md
   ```
3. Slug: short kebab-case, e.g. `postgres-connection-pooling`. Optionally prefix a date if the repo does.
4. Plans are repo-local and committed. Never put them in `/tmp` or a scratchpad.

## Step 3: Write the plan file

Use this skeleton. Keep every section; write "none known" rather than deleting one.

```markdown
# <Title>

**Status:** active
**Owner:** <user / agent>
**Started:** <YYYY-MM-DD — use the date if your context/tools supply one; otherwise ask the user. Never invent one; write `unknown` if unavailable.>

## Goal

What problem this solves and *why it matters*. State the current broken/limited
behavior and the desired end state. 3-8 sentences. Include enough background
that a reader with no prior context understands the motivation.

## Scope

**In scope:** …
**Out of scope (explicitly):** … — prevents a resuming agent from over-building.

## Acceptance criteria

Concrete, checkable. Each must be verifiable by running something or reading
a specific file. No "works well" / "is clean".

- [ ] `pytest tests/test_pool.py` passes with pool size configurable via env
- [ ] p99 latency under 200ms on the load script in `scripts/load.py`
- [ ] No direct `psycopg2.connect` calls remain outside `db/pool.py`

## Key context / entry points

Files, commands, and external facts a cold reader needs.

- `src/db/pool.py` — new pooling layer
- Run tests: `make test-db`
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
changed — the diff already shows what changed.

### M1 — pool module landed
- Chose `psycopg_pool` over hand-rolled queue: already a transitive dep, handles
  reconnect. Rejected SQLAlchemy pooling — would pull in the whole ORM.
- Tried a module-level global pool first; failed under pytest-xdist because
  workers forked after init. Now created lazily per process.
- Next: M2, start with `api/handlers/read.py` (lowest risk).
```

## Step 4: Keep it alive while working

The plan is a living document, not a one-time write.

- Append a log entry at each meaningful checkpoint: a design decision, an approach change, a blocker, a milestone done. Do **not** log every file edit.
- Tick milestone and acceptance checkboxes as they truly pass — verify before ticking.
- When reality diverges from the plan, update Scope/Milestones **and** log why.
- Before any context reset, compaction, or hand-off: flush current state to the log first. Treat "I'm about to lose context" as a mandatory write point.
- When resuming: read the plan file *first*, before touching code, and trust it over your own memory.

**Timestamps:** never invent a date or time. Label entries by milestone or ordinal (`M2`, `Session 3`) — those are always safe. A real date is fine when it comes from a real source: the user, your environment/system context, or a command like `date`. Do not write clock times at all.

## Step 5: Complete and close out

When all acceptance criteria pass:

1. Set `**Status:** completed` and add a final log entry with the outcome and anything a future reader should know.
2. Move it into the `completed/` sibling of wherever the plan actually lives (create the directory if needed):
   `mkdir -p <plans-dir>/completed && git mv <plans-dir>/active/<slug>.md <plans-dir>/completed/<slug>.md`
   If the file was never committed, `git mv` fails — use plain `mv`, then `git add`. Keep it, don't delete. Completed plans are the searchable record of why the code looks the way it does.
3. Move any unfinished follow-ups into `docs/exec-plans/tech-debt-tracker.md` rather than dropping them:

```markdown
## Connection pool: workers still use per-task connections
**Source:** exec-plans/completed/postgres-connection-pooling.md (M3 deferred)
**Impact:** ~40 idle connections at peak; risks hitting the staging cap of 100.
**Fix sketch:** reuse `db.pool.get_pool()` in `workers/base.py` teardown.
**Priority:** medium
```

4. Commit the move with the work, so plan state and code state never drift.

## Worked example

> User: "Our API keeps hitting Postgres connection limits, can you fix it?"

1. **Weight:** touches request path + workers, has a real design choice, staged rollout → durable plan.
2. No `docs/plans/` exists → create `docs/exec-plans/active/postgres-connection-pooling.md` using the skeleton above, ask the user for today's date.
3. Implement M1; append the decision log entry shown above (why `psycopg_pool`, why lazy init).
4. M3 blocked on the open worker question → log the blocker, move M3 to the tech-debt tracker, ship M1/M2/M4.
5. Flip status to completed, `git mv` to `completed/`, commit plan + code together.

## Anti-patterns

- Plan file written once and never updated — worse than none, it lies.
- Log entries that restate the diff ("edited pool.py") instead of the reasoning.
- Rewriting history in the log to look tidy; it is append-only.
- Vague acceptance criteria that nobody can check.
- Keeping the plan in chat "because it's faster" — that is exactly the failure mode this prevents.
