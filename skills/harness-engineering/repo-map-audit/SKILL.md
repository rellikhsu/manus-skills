---
name: repo-map-audit
description: Split a bloated CLAUDE.md/AGENTS.md into a ~100-line map, a docs/ knowledge base, and ARCHITECTURE.md. Use when agent instructions are too long, stale, or ignored, or to structure repo docs.
metadata:
  short-description: "Split bloated agent instructions into a small repository map and a structured docs knowledge base."
---

# repo-map-audit

Turn an "encyclopedia" instruction file into a **map**.

Principle (from OpenAI's writing on harness engineering): the root instruction file is the **table of contents**
(~100 lines), and `docs/` is the **system of record**.

Never delete content without user approval. Move content, and leave a pointer
where each section used to be. Proposed deletions (Step 2) wait for approval.

## Step 1 — Locate and measure

Find the root instruction file(s). Check in this order:
`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/copilot-instructions.md`,
`CONVENTIONS.md`. Also search for nested `**/CLAUDE.md` / `**/AGENTS.md`.

Measure and report this table:

| Metric | How |
|---|---|
| Total lines / words | `wc -lw <file>` |
| Last modified | `git log -1 --format=%ai -- <file>` |
| Code churn since | `git log --oneline --since=<that date> -- . ':!*.md' \| wc -l` |

## Step 2 — Diagnose the problems

Read the whole file. Put **every** section into exactly one bucket and tag its
problems. Report each finding with line ranges, evidence, and a proposed
destination.

< 100 lines: stop if healthy, unless a 10k–200k-line open-source repo lacks `ARCHITECTURE.md` (matklad: propose one).

Flag these symptoms:

1. **Stale rot.** Rules that mention files, dirs, scripts, commands, services,
   or deps that no longer exist. Check with tools: extract every token that
   looks like a path or command and test it (`test -e`, grep in `package.json` /
   `Makefile` / `pyproject.toml` / lockfiles).
2. **Mixed concerns.** One file mixes architecture, code style, build/test
   commands, business/product context, security rules, past one-off notes, and
   plans in progress.
3. **Historical one-offs.** "In March we migrated X, so don't do Y" is a
   changelog note posing as a standing rule. It belongs in a decision log.
4. **Buried critical rules.** A truly important constraint ("never run
   migrations against prod") on line 190 is effectively invisible. Promote
   these into the trimmed map.

## Step 3 — Propose the target structure

Do not create empty
files for concerns the project does not have. Start from this menu and remove what does not apply:

```
CLAUDE.md              # ~100 lines: the map. Loaded every session.
ARCHITECTURE.md        # top-level map (OpenAI)
docs/
  design-docs/
    index.md           # index of design docs, with verification status
    core-beliefs.md    # agent-first operating principles
  exec-plans/
    active/            # in-flight work, one file per effort
    completed/         # archive; where finished plans go
    tech-debt-tracker.md
  product-specs/
    index.md
  references/          # vendored external docs, *-llms.txt files
  generated/           # db-schema.md, api surface, CLI help
  quality-score.md     # per-area / per-layer grades, tracked over time
```

Common project-specific additions: `docs/deployment.md`,
`docs/security.md`, `docs/decisions/NNNN-*.md` (ADRs).

Rules for the structure:
- `ARCHITECTURE.md` follows [matklad](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html):
  short; "only specify things that are unlikely to frequently change. Don't try
  to keep it synchronized with code. Instead, revisit it a couple of times a year."
  - First a bird's eye overview of the problem, then a codemap of coarse modules
    and how they relate. It answers "where's the thing that does X?" and "what does
    the thing that I am looking at do?"
  - Name key files, modules, and types for symbol search; do not link them.
    Convert links after the verbatim move, not during it.
  - Point out invariants (including absent dependencies) and layer/system boundaries; [rust-analyzer](https://github.com/rust-lang/rust-analyzer/blob/d7c99931d05e3723d878bea5dc26766791fa4e69/docs/dev/architecture.md) marks "Architecture Invariant" and "API Boundaries".
  - Cover relevant cross-cutting concerns: rust-analyzer lists code generation, cancellation, testing, error handling, and observability.
  - Check claims against the code. During a verbatim move, list missing or
    uncertain content separately; do not invent it. Per matklad, module details
    go in inline docs (better) or separate docs (here: `docs/`).
- A script writes `docs/generated/`; never edit it by hand. State this at the
  top of each generated file.

Show a mapping table before writing anything:

| Current lines | Section | Verdict | Destination |
|---|---|---|---|
| 12–58 | Architecture overview | move | `ARCHITECTURE.md` |
| 59–96 | Python style | delete (linter covers) | `ruff.toml` (already) |
| 97–140 | Deploy runbook | move | `docs/deployment.md` |
| 141–152 | "Never touch prod DB" | promote | `CLAUDE.md` (map body) |

Then **stop and get explicit approval.** Show the full proposed trimmed
instruction file (it is short) so the user reacts to the real file, not a plan.

## Step 4 — Execute the split

1. Check that the working tree is clean (`git status --porcelain`); if not, ask
   before continuing. Do the whole split in one commit.
2. Create each `docs/` file by **moving text verbatim**. Do not rewrite,
   summarize, or "improve" text during the move; a move that also edits cannot
   be reviewed. Add only a one-line H1 and a one-sentence purpose line.
3. Rewrite the entry file into the map shape below.
4. Fix inbound links: grep the repo for references to the old headings/anchors
   (`grep -rn "CLAUDE.md#" .`) and point them to the new place.
5. Verify: every link in the new entry file resolves; the entry file fits the
   agreed project budget; no
   content was lost (`git show --stat`, and compare the old word count with the
   sum of the new files).

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
- <If it's not load-bearing, it goes in docs/.>

## Conventions
Style is enforced by `ruff` + `prettier` — read the configs, not prose.
Deeper conventions → `docs/design-docs/index.md`.
```

Rules for the map (`ARCHITECTURE.md` names files instead of linking them):
- Every pointer is a real relative path that resolves.
- Say *when* to read something, not only that it exists ("before adding an
  endpoint, read X").
- Target ~100 lines; the example check defaults to 120 through `MAX_LINES`.
  If the project's map still works well at another size, agree on that budget
  and record it in the real check configuration. Size is a signal, not proof of
  quality; do not split a healthy map just to meet this example's default.

## Step 5 — Propose lightweight freshness checks

Do not skip this. Offer it; do not install it unless
asked, and never add a heavy CI system (local policy; OpenAI uses CI).

Write `scripts/check-docs.sh` (adapt it to the repo's language and tools):

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

# 2. Check relative `](path)`.
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
done < <(git ls-files 'docs/*.md' "$ENTRY" ARCHITECTURE.md)

exit $fail
```

Tell the user:
- Hook it into whatever already exists: a `make check` target, a `pre-commit`
  hook, or one CI step. If none exists, leave it as a script the user runs by
  hand.
- Optional: a `docs/generated/` check that fails if the generator output
  differs from the committed file.

## Anti-patterns

- Replacing one giant file with a giant `docs/index.md`.
