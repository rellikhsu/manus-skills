---
name: repo-map-audit
description: Audit a bloated CLAUDE.md / AGENTS.md / .cursorrules and split it into a small table-of-contents entry point plus a structured docs/ knowledge base. Use when the user says the instruction file is too long or bloated, asks to audit / review / clean up / trim / reorganize CLAUDE.md or AGENTS.md, wants to split agent docs into a docs/ directory, complains that agent instructions are stale or ignored, asks how to structure repo docs for agents or set up progressive disclosure, or when you notice the root instruction file exceeds ~150 lines while working on something else.
metadata:
  short-description: "Split bloated agent instructions into a small repository map and a structured docs knowledge base."
---

# repo-map-audit

Turn an "encyclopedia" instruction file into a **map**.

Principle (as argued in OpenAI's writing on harness engineering): context is
scarce. A giant instruction file crowds out the task, the code, and the docs. When
everything is important, nothing is. Monolithic manuals rot and cannot be
checked mechanically. So the root instruction file is the **table of contents**
(~100 lines), and `docs/` is the **system of record**. Agents start small and
are taught where to look next: progressive disclosure.

Never delete content during this skill. Content is moved, and every moved
section leaves a pointer behind.

## Step 1 — Locate and measure

Find the root instruction file(s). Check, in order:
`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/copilot-instructions.md`,
`CONVENTIONS.md`. Also glob for nested `**/CLAUDE.md` / `**/AGENTS.md` —
nested files are usually fine and should be left alone unless also bloated.

Measure and report a table:

| Metric | How |
|---|---|
| Total lines / words | `wc -lw <file>` |
| Section count | count of `^#{1,3} ` headings |
| Lines per section | note any section > 40 lines |
| Last modified | `git log -1 --format=%ai -- <file>` |
| Code churn since | `git log --oneline --since=<that date> -- . ':!*.md' \| wc -l` |
| Contributors | `git log --format=%an -- <file> \| sort -u \| wc -l` |

The churn number is the rot signal: hundreds of code commits since the last
instruction-file edit means the guidance is describing a repo that no longer
exists.

If git is unavailable, skip those rows — do not guess.

## Step 2 — Diagnose the failure modes

Read the whole file. Classify **every** section into exactly one bucket and
tag the problems you find. Report findings with line ranges, evidence, and a
proposed destination — no vague "this could be better".

Size thresholds (rules of thumb, not laws):
- < 100 lines: healthy. Say so and stop unless other symptoms are present.
- 100–150: watch.
- 150–250: suspect — audit properly.
- \> 250: almost certainly an encyclopedia.

Symptoms to flag explicitly:

1. **Generic boilerplate.** Rules that would be true in any repo ("write
   clean code", "add tests", "use meaningful variable names", generic language
   idioms the model already knows). These are pure context tax → **delete**
   (proposed, with user approval), not migrate.
2. **Stale rot.** Rules referencing files, dirs, scripts, commands, services,
   or deps that no longer exist. Verify mechanically: extract every path-like
   and command-like token and test it (`test -e`, grep in `package.json` /
   `Makefile` / `pyproject.toml` / lockfiles). Report each dead reference with
   the exact line.
3. **Mixed concerns.** One file jamming together architecture, code style,
   build/test commands, business/product context, security rules, historical
   one-offs, and in-progress plans. Each of those is a different audience and
   a different update cadence — that mixture is the reason it rots.
4. **Historical one-offs.** "In March we migrated X, so don't do Y" — a
   changelog note masquerading as a standing rule. Belongs in a decision log.
5. **Duplication.** Content already in `README.md`, a linter config, a
   `Makefile`, or CI. Prefer the executable source of truth and point at it.
6. **Unverifiable / soft rules.** "Be careful with the auth module." Either
   make it specific and actionable, or drop it.
7. **Buried critical rules.** A genuinely load-bearing constraint ("never run
   migrations against prod") on line 190 is effectively invisible. These get
   promoted into the trimmed map.

## Step 3 — Propose the target structure

Design the layout from what **this** repo actually has. Do not scaffold empty
files for concerns the project does not have — an empty doc is worse than no
doc. Start from this menu and cut it down:

```
CLAUDE.md              # ~100 lines: the map. Loaded every session.
ARCHITECTURE.md        # system shape, boundaries, data flow (root: high traffic)
docs/
  design-docs/
    index.md           # index of design docs, one line + validation status each
    core-beliefs.md    # agent-first operating principles (e.g. prefer deps the agent can reason about in-repo)
  exec-plans/
    active/            # in-flight work, one file per effort
    completed/         # archive; where finished plans go to stop rotting
    tech-debt-tracker.md
  product-specs/
    index.md
  references/          # vendored external docs, *-llms.txt files
  generated/           # machine-generated; db-schema.md, api surface, CLI help
  quality-score.md     # per-area / per-layer grades, tracked over time
```

Common project-specific additions: `docs/testing.md`, `docs/deployment.md`,
`docs/security.md`, `docs/frontend.md`, `docs/data-model.md`,
`docs/decisions/NNNN-*.md` (ADRs), `docs/glossary.md`.

Rules for the structure:
- `docs/generated/` is written by a script and never hand-edited. Say so at
  the top of each generated file.
- `docs/exec-plans/active/` is the only place with expected high churn; moving
  finished plans to `completed/` is what keeps the rest stable.
- Every directory containing more than ~3 docs gets an `index.md`.

Present as a mapping table before writing anything:

| Current lines | Section | Verdict | Destination |
|---|---|---|---|
| 12–58 | Architecture overview | move | `ARCHITECTURE.md` |
| 59–96 | Python style | delete (linter covers) | `ruff.toml` (already) |
| 97–140 | Deploy runbook | move | `docs/deployment.md` |
| 141–152 | "Never touch prod DB" | promote | `CLAUDE.md` (map body) |

Then **stop and get explicit approval.** Show the proposed trimmed
instruction file in full — it is short — so the user can react to the real
artifact, not a plan.

## Step 4 — Execute the split

Only after approval.

1. Confirm a clean working tree (`git status --porcelain`); if dirty, ask
   before proceeding. Do the whole split in one commit so it is trivially
   revertible.
2. Create each `docs/` file by **moving text verbatim**. Do not rewrite,
   summarize, or "improve" prose during the move — a move that also edits is
   unreviewable. Add only a one-line H1 and a one-sentence purpose header.
3. Rewrite the entry file to the map shape below.
4. Fix inbound links: grep the repo for references to the old headings/anchors
   (`grep -rn "CLAUDE.md#" .`) and repoint them.
5. Verify: every link in the new entry file resolves; total entry-file length
   is at or under 120 lines (target ~100); no content vanished
   (`git show --stat`, and diff word counts old vs. sum of new).

### Target shape of the trimmed entry file

```markdown
# CLAUDE.md

<one paragraph: what this repo is, in two sentences>

## Start here
- Architecture and boundaries → `ARCHITECTURE.md`
- Why we build it this way → `docs/design-docs/core-beliefs.md`
- What's in flight right now → `docs/exec-plans/active/`
- DB schema (generated, do not edit) → `docs/generated/db-schema.md`

## Commands
| Task | Command |
|---|---|
| install | `make bootstrap` |
| test | `make test` (single: `pytest -k <name>`) |
| lint | `make lint` |

## Non-negotiables
- Never run migrations against prod; use `make migrate-staging`.
- All new endpoints require an auth decorator; see `docs/security.md`.
- <5 max. If it's not load-bearing, it goes in docs/.>

## Conventions
Style is enforced by `ruff` + `prettier` — read the configs, not prose.
Deeper conventions → `docs/design-docs/index.md`.
```

Constraints on the map:
- Every pointer is a real relative path that resolves.
- Say *when* to read something, not just that it exists ("before adding an
  endpoint, read X") — that is what makes disclosure progressive.
- No rule the tooling already enforces.
- Target ~100 lines, hard cap 120 (the number `check-docs.sh` enforces). If it
  won't fit, something in it belongs in `docs/`.

## Step 5 — Propose lightweight freshness checks

Do not skip this — unchecked docs rot back into an encyclopedia. Keep it
small: one script, optionally one CI step. Offer it; do not install it
unasked, and never add a heavyweight CI system.

Write `scripts/check-docs.sh` (adapt to the repo's language/tooling):

```bash
#!/usr/bin/env bash
# Lightweight knowledge-base check. Exit non-zero on failure.
set -uo pipefail
fail=0
# Entry file: whichever of these the repo actually uses.
ENTRY=${ENTRY:-CLAUDE.md}
[ -e "$ENTRY" ] || ENTRY=AGENTS.md
STALE_DAYS=${STALE_DAYS:-180}
MAX_LINES=${MAX_LINES:-120}

# 1. Entry file stays a map, not an encyclopedia.
if [ ! -e "$ENTRY" ]; then
  echo "FAIL: no entry instruction file found (CLAUDE.md / AGENTS.md)"
  fail=1
else
  lines=$(wc -l < "$ENTRY")
  if [ "$lines" -gt "$MAX_LINES" ]; then
    echo "FAIL: $ENTRY is $lines lines (limit $MAX_LINES) — move detail into docs/"
    fail=1
  fi
fi

# 2. Every relative markdown link resolves.
# Note: no pipeline around the inner loop, so `fail` is set in this shell.
while IFS= read -r f; do
  while read -r link; do
    case "$link" in http*|mailto:*|"") continue;; esac
    target="$(dirname "$f")/$link"
    [ -e "$target" ] || { echo "FAIL: $f -> missing $link"; fail=1; }
  done < <(grep -oE '\]\(([^)#]+)' "$f" | cut -c3-)
done < <(git ls-files '*.md')

# 3. Freshness: docs untouched while their subject code moved.
now=$(date +%s)
churn=$(git log --oneline --since="$STALE_DAYS days ago" -- . ':!*.md' | wc -l)
while IFS= read -r f; do
  last=$(git log -1 --format=%ct -- "$f")
  [ -n "$last" ] || continue
  age=$(( (now - last) / 86400 ))
  [ "$age" -gt "$STALE_DAYS" ] || continue
  [ "$churn" -gt 0 ] && echo "WARN: $f unchanged ${age}d while code moved ($churn commits)"
done < <(git ls-files 'docs/*.md' "$ENTRY")

exit $fail
```

Notes to convey to the user:
- Link resolution and the size cap are **errors**; staleness is a **warning**
  (it needs human judgement — some docs are correctly stable).
- Wire it in via whatever already exists: a `make check` target, a
  `pre-commit` hook, or one CI step. If none exists, leave it as a script the
  user can run manually rather than introducing CI.
- Tune `STALE_DAYS`; 180 is a starting point.
- Optional extra: a `docs/generated/` regeneration check that fails if the
  generator output differs from the committed file.

## Worked example

**Before** — `CLAUDE.md`, 412 lines, last edited 8 months ago, 340 code
commits since. Sections: project intro (6), architecture (74), Python style
(61), React style (48), test commands (9), deploy runbook (52), "Q2 billing
migration notes" (39), API endpoint catalog (94), misc gotchas (29).

**Audit output:** Python/React style sections duplicate `ruff.toml` and
`.eslintrc` → delete, point at configs. The endpoint catalog references 7
routes deleted in the v3 refactor → regenerate instead of maintaining.
Billing-migration notes are historical → decision log. Buried on line 388:
"staging shares the prod Redis" — critical, invisible.

**After:**
```
CLAUDE.md                        94 lines  (map + commands + 4 non-negotiables)
ARCHITECTURE.md                  74
docs/deployment.md               52
docs/decisions/0001-billing-migration.md  39
docs/generated/api-endpoints.md  auto-generated from the router
docs/gotchas.md                  22  (7 stale items dropped)
scripts/check-docs.sh            offered, user wired into `make check`
```
Per-session context cost: ~412 lines → ~94, with the rest reachable in one
read when relevant.

## Anti-patterns

- Rewriting prose while moving it — do the move first, edit later.
- Creating the full directory tree from Step 3 in a 3-file project.
- Splitting a 90-line file that is working fine. Report "healthy" and stop.
- Replacing one giant file with a giant `docs/index.md`.
- A map full of pointers to empty stubs.
- Doing the split without approval.
