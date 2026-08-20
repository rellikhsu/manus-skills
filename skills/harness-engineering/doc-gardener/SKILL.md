---
name: "harness-engineering:doc-gardener"
description: Recurring small-batch cleanup pass for docs and code drift. Use when docs feel stale or out of date, when the codebase has drifted from its house rules, when asked to run a gardening/cleanup pass, garbage-collect tech debt, check docs against actual code behavior, or set up golden principles for a repo. Intended for recurring host-scheduled runs, and also usable ad hoc when things feel like they've drifted.
description-short: Recurring small-batch cleanup pass for docs and code drift. Use when docs feel stale, the codebase drifted from house rules, or you're asked to garbage-collect tech debt or check docs vs code.
---

# Doc Gardener

Continuous garbage collection for a codebase: stale documentation and drift away
from the repo's own rules. Agents replicate whatever patterns already exist, so
uneven patterns compound. Pay the debt down in small increments, every run.

**Anti-pattern this exists to replace:** saving cleanup for a "big refactor day"
every Friday. That does not scale and produces unreviewable diffs. Every run
should produce a handful of one-minute-reviewable changes, or nothing at all.

**Intended invocation:** scheduled/recurring when the host provides a scheduler.
- Use the host's recurring-task facility, CI cron, or another daily/weekly scheduler.
- ad hoc is fine, but if you find yourself running it ad hoc repeatedly, set up a schedule instead.

## Step 0 — Ensure golden principles exist

Look for `docs/GOLDEN_PRINCIPLES.md` (also accept `GOLDEN_PRINCIPLES.md`,
`.claude/golden-principles.md`, or a "Golden principles" section in `CLAUDE.md`).

If none exists, create `docs/GOLDEN_PRINCIPLES.md` **before scanning**:

1. Read `CLAUDE.md`/`AGENTS.md`, the README, lint/type config, and 5-10 representative
   source files across the main layers (entrypoints, data access, shared utils, tests).
2. Draft 5-12 rules that are **opinionated and mechanically checkable** — each rule must
   name a concrete grep-able or structurally-detectable violation. "Write clean code" is
   not a rule. "Use `src/lib/http.ts`; never call `fetch` directly outside it" is.
3. Show the draft to the user and get confirmation before committing it. Human taste is
   captured once here; every later run just enforces it.

**Unattended runs must not invent house rules.** If no principles file exists and there is no
user available to confirm (scheduled/cron run), write the draft to
`docs/GOLDEN_PRINCIPLES.draft.md` on a branch, report that it needs sign-off, and **stop** —
do not scan or fix against unconfirmed rules.

Example (adapt to the actual repo — do not copy blindly):

```markdown
# Golden Principles

1. HTTP: all outbound calls go through `src/lib/http.ts`. No bare `fetch`/`axios` elsewhere.
2. No hand-rolled helpers that duplicate `src/lib/utils/` (dates, slugify, deep-clone, retry).
3. No untyped data access. DB reads go through the generated client; external JSON is
   parsed with a zod schema at the boundary. No `as any` on network/DB results.
4. Errors: throw `AppError` subclasses; never `throw new Error("string")` in `src/`.
5. Config comes from `src/config.ts` only. No `process.env.*` outside that file.
6. Every exported function in `src/lib/` has a JSDoc line and a unit test.
7. No `console.log` in `src/`; use `logger`.
8. React: server components by default; `"use client"` requires a one-line comment saying why.

Quality grade: A = 0 violations, B = 1-3, C = 4+. Update the grade table each gardening run.
```

## Step 1 — Scope the run

- Determine what changed since the last pass: `git log --since="<last run>" --name-only`,
  or `--since="7 days ago"` if unknown. Record the last-run marker in the tech-debt file.
- Hard scope cap: **at most ~40 changed files** per run. If more changed, take the most-touched
  ones and note the deferred remainder in the tech-debt file for the next run.
- Prioritize recently-touched files and their docs. Never do a whole-repo sweep on a scheduled
  run; a bounded scope is what keeps diffs small and the run cheap.
- Start from a clean tree on a fresh branch (`gardening/<date>`). If the working tree is dirty
  or you are mid-rebase/merge, report and exit — never garden on top of someone's work.

## Step 2 — Scan for doc staleness

Cross-check docs **against the code**, never trust the doc's own claims.

For each README, `docs/*.md`, `CLAUDE.md`, and doc comment in scope:
- Extract every concrete claim: file paths, function/class/CLI names, env vars, commands,
  ports, package names, directory trees, architecture statements.
- Verify each one: does the path exist (`ls`), does the symbol exist (`grep`/`rg`), does the
  script exist in `package.json`/`Makefile`/`pyproject.toml`, is the env var still read anywhere?
- Flag architecture claims contradicted by structure ("all state in Redux" when half the app
  uses Zustand; "service X calls Y directly" when a queue now sits between them).
- Flag setup steps referencing removed tooling or old versions.

## Step 3 — Scan for code drift

For each golden principle, run its concrete detection (grep, AST/`ast-grep`, lint rule) over
the scoped files. Also look for:
- duplicated hand-rolled helpers where a shared utility already exists,
- unvalidated boundary data / `any` escapes on external input,
- style and naming inconsistencies newly introduced relative to neighbors,
- dead code: exports with zero references, feature flags long since fully rolled out.

## Step 4 — Triage

Classify each finding:

| Class | Criterion | Action |
|---|---|---|
| **Auto-fix** | Mechanical, behavior-preserving, reviewable in <1 min, covered by existing tests | Fix now |
| **Log** | Needs judgment, touches behavior, spans many files, or ambiguous intent | Append to tech-debt file |
| **Drop** | False positive after verification | Say nothing |

When in doubt, log rather than fix. Never silently skip a real finding.

**Always Log, never auto-fix**, regardless of how small the diff looks:
- deleting code (dead exports, unused flags, "obsolete" docs) — reachability across DI,
  reflection, and other repos cannot be proven from a grep,
- anything touching auth, crypto, payments, migrations, CI/CD, or infra config,
- generated files, vendored code, or lockfiles,
- changes to files with no test coverage,
- rewriting a doc claim you could not verify against code — record the uncertainty instead.

## Step 5 — Apply fixes in small, separate batches

- One coherent theme per commit/PR. Doc fixes and code drift fixes are **never** the same commit.
- Hard cap: roughly 5 files / 100 changed lines per commit. If a fix exceeds that, it is a Log item.
- Run the repo's tests/lint/typecheck for anything touching code. Do not commit a red tree.
- Commit message states the rule enforced, e.g.
  `chore(gardening): route notifications through src/lib/http (GP-1)`.
- Cap the whole run at **3 commits**. Anything beyond that is Log, not fix.
- Follow the repo's convention for whether to push/open PRs; if unclear, leave commits on a
  branch and report.

Unattended-run rails (non-negotiable):
- Never commit or push to the default branch (`main`/`master`) or any protected/release branch.
- Never `push --force`, amend/rebase existing commits, `reset --hard`, `checkout --` over
  uncommitted work, or delete branches, tags, or stashes.
- Never merge or automerge your own PRs; open them as drafts if the repo uses PRs.
- Never edit CI config, secrets, credentials, or dependency versions.
- If tests/lint cannot be run (missing deps, no sandbox), do not commit code fixes at all —
  downgrade every code finding to Log. Doc-only fixes may still proceed.
- If anything is ambiguous, produce zero commits and a report. A no-op run is a success.

## Step 6 — Log what you did not fix

Maintain `docs/TECH_DEBT.md`. Append (never rewrite history):

```markdown
## 2026-08-01 gardening pass
- [ ] `src/billing/invoice.ts` — 3 hand-rolled currency formatters; consolidating changes
      rounding behavior on 2 call sites. Needs product sign-off. (GP-2)
- [ ] `docs/architecture.md` "single Postgres instance" — read replicas added in #1841;
      rewrite needs someone who knows the failover story. (doc)
- Grades: lib A, api B (2), web C (5, up from 3) — web regressing on GP-3.
```

Reuse an existing tracker (Linear/GitHub issues) instead if the repo clearly uses one.

## Step 7 — Report

Short summary: files scanned, fixes committed (one line each), items logged, grade changes,
and any principle that keeps getting violated — a repeatedly-violated principle means the
codebase should make the wrong thing hard (lint rule, type, wrapper), not that the principle
should be re-enforced by hand forever. Propose that lint rule.

## Worked example

Scope: 14 commits since yesterday, mostly `src/notifications/`.

**Finding 1 (doc, auto-fix).** `docs/setup.md` says: "Run `npm run seed:dev` then set
`NOTIFY_API_KEY`." Verified: `package.json` has no `seed:dev` (renamed to `db:seed` in
`a1b3f0d`), and `rg NOTIFY_API_KEY src/` returns nothing — `src/config.ts` now reads
`NOTIFICATIONS_TOKEN`. Fix: update both, 2 lines.
Commit: `docs(setup): fix renamed seed script and notification env var`.

**Finding 2 (drift, auto-fix).** `src/notifications/send.ts` calls `fetch(url, ...)` directly
with a hand-rolled retry loop — violates GP-1 and GP-2. `src/lib/http.ts` already exports
`post()` with the same retry semantics. Fix: replace with `post()`, delete 18 lines of retry.
Existing tests in `send.test.ts` pass unchanged.
Commit: `chore(gardening): use src/lib/http post() in notifications (GP-1, GP-2)`.

**Finding 3 (log).** `src/notifications/templates.ts` parses provider webhook JSON with
`as any` (GP-3). A zod schema would change behavior for three malformed-payload cases
currently swallowed. Too risky to auto-fix → appended to `docs/TECH_DEBT.md`.

Result: 2 tiny PRs, each reviewable in under a minute, one tracked debt item, `notifications`
grade B → B (unchanged, one open GP-3 violation).

## Anti-patterns

- Inventing golden principles on an unattended run instead of drafting to
  `docs/GOLDEN_PRINCIPLES.draft.md` and stopping — a scheduled run with no user to
  confirm them must never scan or fix against unconfirmed rules.
- Sweeping the whole repo instead of the scoped, changed-since-last-run files —
  the ~40-file cap is what keeps a scheduled pass small; a full sweep produces
  exactly the unreviewable diff this skill exists to avoid.
- Auto-fixing a deletion, an auth/crypto/payments/CI/infra change, or anything with
  no test coverage because the diff looked small — those are always Log, regardless of size.
- Mixing a doc fix and a code-drift fix in one commit, or exceeding the
  5-file/100-line/3-commit caps — anything over cap is a Log item, not a bigger commit.
- Rewriting a doc claim you could not actually verify against the code — that just
  swaps one unverified claim for another; log the uncertainty instead.
- Committing code fixes when tests/lint cannot be run, or gardening on top of a
  dirty tree or someone's mid-rebase/merge state.
