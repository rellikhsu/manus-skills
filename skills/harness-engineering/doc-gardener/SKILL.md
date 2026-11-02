---
name: doc-gardener
description: Recurring small-batch cleanup of stale docs and drift from house rules. Use when docs feel out of date, code has drifted from conventions, or for a gardening or tech-debt pass.
metadata:
  short-description: "Recurring small-batch cleanup for stale docs, house-rule drift, tech debt, and code-versus-doc checks."
---

# Doc Gardener

Fix a little on every run.

**How to run:** on a schedule when the host has a scheduler.
- Manual runs are fine; if you repeat them, set up a schedule.

Source: [OpenAI's harness-engineering article](https://openai.com/index/harness-engineering/).
Local policy: the caps and grades below, no automerge, and logging deletions. Explicit project/user policy can change them within its existing authority. A gardening run must not give itself more permissions.

## Step 0 — Ensure golden principles exist

Look for `docs/GOLDEN_PRINCIPLES.md` (also accept `GOLDEN_PRINCIPLES.md`,
`.claude/golden-principles.md`, or a "Golden principles" section in `CLAUDE.md`).

If none exists, create `docs/GOLDEN_PRINCIPLES.md` **before scanning**:

1. Read `CLAUDE.md`/`AGENTS.md`, the README, lint/type config, and typical
   source files from the main layers (entrypoints, data access, shared utils, tests).
2. Draft rules that are **opinionated and mechanically checkable**. Each rule must
   name a concrete violation that grep or a structure check can find.
3. Show the draft to the user and get confirmation before committing it. Human taste is
   captured once here; later runs only enforce it.

**Unattended runs must not invent house rules.** If no principles file exists and no
user can confirm (scheduled/cron run), write the draft to
`docs/GOLDEN_PRINCIPLES.draft.md` on a branch, report that it needs sign-off, and **stop**.
Do not scan or fix against unconfirmed rules.

Example (adapt to the real repo; do not copy blindly):

```markdown
# Golden Principles

1. HTTP: all outbound calls go through `src/lib/http.ts`. No bare `fetch`/`axios` elsewhere.
2. No hand-rolled helpers that duplicate `src/lib/utils/` (dates, slugify, deep-clone, retry).

Quality grade: A = 0 violations, B = 1-3, C = 4+. Update `docs/quality-score.md` each run.
```

## Step 1 — Scope the run

- Find what changed since the last run: `git log --since="<last run>" --name-only`,
  or `--since="7 days ago"` if unknown. Record the last-run marker in the tech-debt file.
- Hard cap: **at most ~40 changed files** per run. If more changed, take the most-changed
  ones and list the rest in the tech-debt file for the next run.
- Start with recently changed files and their docs.
- Start from a clean tree on a new branch (`gardening/<date>`). If the working tree is dirty
  or a rebase/merge is in progress, report and exit. Never garden on top of someone's work.

## Step 2 — Scan for stale docs

Check docs **against the code**. Never trust what the doc says about itself.

For each README, `docs/*.md`, `CLAUDE.md`, and doc comment in scope:
- List every concrete claim: file paths, function/class/CLI names, env vars, commands,
  ports, package names, directory trees, architecture statements.
- Check each one: does the path exist (`ls`), does the symbol exist (`grep`/`rg`), does the
  script exist in `package.json`/`Makefile`/`pyproject.toml`, is the env var still read anywhere?
- Flag architecture claims that the code structure contradicts.
- Flag setup steps that mention removed tools or old versions.

## Step 3 — Scan for code drift

For each golden principle, run its check (grep, AST/`ast-grep`, lint rule) on
the scoped files. Also look for:
- hand-rolled helpers that duplicate an existing shared utility,
- unvalidated boundary data / `any` escapes on external input.

## Step 4 — Triage

Classify each finding:

| Class | Criterion | Action |
|---|---|---|
| **Auto-fix** | Mechanical, behavior-preserving, reviewable in <1 min | Fix now |
| **Log** | Needs judgment, touches behavior, spans many files, or ambiguous intent | Append to tech-debt file |
| **Drop** | False positive after verification | |

**Always Log, never auto-fix**:
- deleting code (dead exports, unused flags, "obsolete" docs),
- anything touching auth, crypto, payments, migrations, CI/CD, or infra config,
- generated files, vendored code, or lockfiles,
- rewriting a doc claim you could not verify against code.

## Step 5 — Apply fixes in small, separate batches

- One theme per commit/PR.
- Hard cap: about 5 files / 100 changed lines per commit. A larger fix is a Log item.
- Run the repo's tests/lint/typecheck for any code change. Do not commit a failing tree.
- The commit message names the rule enforced, e.g.
  `chore(gardening): route notifications through src/lib/http (GP-1)`.
- Cap the whole run at **3 commits**. Anything more is Log, not fix.
- Follow the repo's convention on pushing/opening PRs. If unclear, leave commits on a
  branch and report.

Rules for unattended runs (non-negotiable):
- Never commit or push to the default branch (`main`/`master`) or any protected/release branch.
- Never `push --force`, amend/rebase existing commits, `reset --hard`, `checkout --` over
  uncommitted work, or delete branches, tags, or stashes.
- Never merge or automerge your own PRs.
- Never edit secrets, credentials, or dependency versions.
- If tests/lint cannot run (missing deps, no sandbox), commit no code fixes.
  Turn every code finding into Log. Doc-only fixes may still go ahead.

## Step 6 — Log what you did not fix

Append to the tech-debt file (default `docs/exec-plans/tech-debt-tracker.md`):

```markdown
## 2026-08-01 gardening pass
- [ ] `src/billing/invoice.ts` — 3 hand-rolled currency formatters; consolidating changes
      rounding behavior on 2 call sites. Needs product sign-off. (GP-2)
```

Link external issues here.

## Step 7 — Report

Short summary: files scanned, fixes committed (one line each), items logged, grade changes,
and any principle that keeps being violated. A principle that keeps being violated means the
codebase should make the wrong thing hard (lint rule, type, wrapper). Propose that lint rule.

## Anti-patterns

- Inventing golden principles on an unattended run instead of writing
  `docs/GOLDEN_PRINCIPLES.draft.md` and stopping. A scheduled run with no user to
  confirm the rules must never scan or fix against them.
- Auto-fixing a deletion or an auth/crypto/payments/CI/infra change
  because the diff looked small. These are always Log, whatever the size.
- Committing code fixes when tests/lint cannot run, or gardening on a
  dirty tree or during someone's rebase/merge.
