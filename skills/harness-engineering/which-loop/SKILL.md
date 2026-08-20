---
name: "harness-engineering:which-loop"
description: "Router for picking the right review, planning, or debugging loop when several installed skills could apply. Use when about to review code, start a plan, debug something, or design a module and more than one skill fits — or when the user asks which skill to use, what the difference is between two loops (requesting-code-review vs code-review, tdd vs test-driven-development, execution-plan vs subagent-driven-development), or when to run a review at all. Also use before starting any non-trivial coding task to pick the loop up front rather than improvising."
description-short: Router for picking the right review, planning, or debugging loop when several installed skills could apply. Use before reviewing code, starting a plan, or debugging when more than one skill fits.
---

# Which Loop

Three families of skills are installed and they operate at **different altitudes**.
They are not competitors — picking wrongly means either skipping a check that
mattered or running a heavyweight loop where a light one would do.

```
GROUND LAYER — the environment itself, not any one task
  harness-engineering: repo-map-audit · invariant-linter · governance-baseline
                       observability-bridge · doc-gardener · harness-retune
                       self-harness

TASK LAYER — one unit of work
  INNER  (per task)      superpowers:requesting-code-review
  OUTER  (per branch)    mattpocock-skills:code-review
  SUBJECTIVE (no spec)   harness-engineering:generator-evaluator
```

The ground layer is what makes the task layer work well. A tight debugging loop
is far easier to build in a repo that already ran `observability-bridge`.

When a task fails, the fix is rarely "try harder". Ask what capability is
missing, then make it legible and enforceable:

| Missing | Skill |
|---|---|
| The agent can't see it | `observability-bridge` |
| Nothing stops it | `governance-baseline` |
| The rule is prose, not enforced | `invariant-linter` |
| The entry doc is a manual, not a map | `repo-map-audit` |
| Context won't survive the session | `execution-plan` |
| Docs and code have drifted | `doc-gardener` |
| The same failure keeps repeating | `self-harness` |

Run `governance-baseline` before handing an agent broader autonomy (auto-merge,
unattended scheduled runs, production access) — not after an incident makes the
gap obvious.

`harness-retune` and `self-harness` both edit the harness, keyed to different
triggers: harness-retune re-tests existing scaffolding on a model upgrade (cadence:
months, evidence: an inventory of what's already there). self-harness runs a mining →
proposal → gate → merge loop keyed to this round's actual execution-record evidence,
gated by whatever tier the project supports. Different questions, different cadence —
not alternatives.

---

## Picking a review loop

| Situation | Use | Why this one |
|---|---|---|
| Finished one task in a larger plan, outside an SDD run | `superpowers:requesting-code-review` | Light, fast, one subagent, Critical/Important/Minor. Keeps problems from compounding across tasks. |
| Branch is ready to merge | `mattpocock-skills:code-review` | Two parallel axes — Standards (repo conventions + Fowler smell baseline) and Spec (does it match the issue/PRD). Answers "did we build the right thing", which the inner loop does not. |
| Work has no spec to compare against (design, UX, copy, product feel) | `harness-engineering:generator-evaluator` | Both loops above assume a spec or documented standard exists. Subjective work needs an explicit rubric plus an **independent** evaluator agent, or the model grades itself and inflates. |

Run both the inner and outer loops on a real branch — they catch different
classes of problem. The inner loop passing does not make the outer one redundant.

Loop until convergence, not one pass: address the feedback, re-run the review,
repeat until a round raises nothing new — this is the source article's own loop,
where Codex reviews its change, then other agents review, until every agent
reviewer is satisfied. Same blocking item twice → stop, get a human.

**This is a gate, not a suggestion.** If the unit of work ends in a commit, the
outer loop (`mattpocock-skills:code-review`) must actually run before that
commit — "the inner loop passed" is not sufficient on its own, and whether the
outer loop runs is not a judgment call left to the agent doing the work. State
this explicitly when routing a task that will end in a commit; do not let the
calling agent infer it from "branch is ready to merge" being a separate row.

No conflict with the source article: its "minimal blocking merge gates — fixes are
cheap, waiting is expensive" is scoped to CI and flaky tests, not to review.

**SDD exception:** `superpowers:subagent-driven-development` already owns its
inner loop: every task gets a task-scoped Spec + Quality review, and the branch
gets a broad final `requesting-code-review`. Do not recursively add another
`requesting-code-review` after each SDD task. After SDD completes, run the
`mattpocock-skills:code-review` outer loop before merge.

---

## Picking a planning / execution loop

| Situation | Use |
|---|---|
| Executing a written plan, tasks mostly independent, staying in this session | `superpowers:subagent-driven-development` |
| Executing a plan in a separate session with human checkpoints | `superpowers:executing-plans` |
| Need a durable record of goal / acceptance criteria / decisions that survives sessions | `harness-engineering:execution-plan` |
| Requirements still fuzzy — nothing written down yet | `superpowers:brainstorming` first |

**The one real overlap.** `subagent-driven-development` keeps a ledger at
`.superpowers/sdd/<plan>/progress.md` and deletes only that plan's git-ignored
scratch directory when the plan completes — **not** the repository or Git
worktree. It is execution-time scratch, not an archive. `execution-plan` writes
to `docs/exec-plans/` and is meant to be read months later. They are sequential,
not alternatives: when an SDD run finishes and its scratch directory is about to
be deleted, move the durable outcome and key decisions into an `execution-plan`
completed file first. Do not run both on the same task concurrently.

---

## Picking a debugging loop

`mattpocock-skills:diagnosing-bugs` and `superpowers:systematic-debugging` solve
the same problem with different emphasis, and either is fine:

- **`diagnosing-bugs`** — organised around building one tight, red-capable
  feedback loop first; strongest when the bug is hard to reproduce or is a
  performance regression.
- **`systematic-debugging`** — organised around root-cause phases with an
  explicit "3 failed fixes means question the architecture" circuit breaker.

Either way: if the agent is guessing because it cannot observe the system, stop
and run `harness-engineering:observability-bridge` first. Debugging without a
queryable signal is the failure both skills exist to prevent.

---

## Picking a design skill

| Situation | Use |
|---|---|
| Designing a module interface, deciding where a seam goes | `mattpocock-skills:codebase-design` |
| Pinning down domain vocabulary, recording an ADR | `mattpocock-skills:domain-modeling` |
| A layering/dependency rule was just agreed and must not silently rot | `harness-engineering:invariant-linter` |

These chain: `codebase-design` decides what the layering is,
`invariant-linter` turns that decision into a mechanical check so a later agent
cannot quietly violate it.

---

## Genuinely redundant pairs

Pick one and stay consistent; running both is waste:

- `mattpocock-skills:tdd` vs `superpowers:test-driven-development` — same
  discipline, different voice. `superpowers` is stricter and more explicit about
  rationalizations; `mattpocock` is shorter and focuses on seams and test quality.

---

## When to use none of them

Trivial mechanical edits, one-line config changes, and conversational questions
do not need a loop. Naming a skill does not make small work safer — it just
makes it slower.
