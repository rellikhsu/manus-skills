---
name: generator-evaluator
description: "Run a generator/evaluator harness loop for subjective-quality work where there is no binary pass/fail test. Use for UI/UX redesigns, \"make this look good\", visual design review, frontend polish passes, product-feel critique, or any multi-sprint build where \"is this actually done and correct?\" needs independent judgment. Builds an explicit scoring rubric first, then iterates with a separate evaluator agent so the model never grades its own work. Triggers on: subjective quality task, design review loop, does this look good, UX pass, redesign, avoid self-grading bias, iterate until it's good, rubric-scored iteration, contract negotiation before a sprint."
metadata:
  short-description: "Run an independent generator/evaluator rubric loop for subjective-quality work without a binary test."
---

# Generator / Evaluator Harness

Two failure modes make naive single-agent execution unreliable on subjective work:

- **Context anxiety** — a long-running agent winds work down prematurely as it nears its perceived context limit. Fix with context *reset*, not compression: a fresh context plus the evaluator's written feedback beats a summarized history that drags stale framing forward.
- **Self-evaluation bias** — a model grading its own output is systematically optimistic, worst on subjective dimensions (design quality, UX, "does this feel right"). Fix by making the evaluator a **separate agent invocation with its own context**, prompted to critique.

Everything below follows from those two.

---

## Step 0 — Decide if you need this at all

Start with the simplest harness that could work. Do **not** default to the heavy version.

| Situation | Harness |
|---|---|
| Objectively checkable (tests pass, types compile, output matches spec, script runs) | **No generator/evaluator loop.** Do the authorized work and run the objective check; tests and tools still form part of the harness. |
| Single subjective artifact (one page, one component, one doc) | Rubric + generator + independent evaluator, 5–10 rounds |
| Large multi-step build (full app, several features) | Add sprint structure + **contract negotiation** (Step 5), 10–15 rounds |

If the user asked for the loop but the task is objectively checkable, tell them plainly: "This has a real pass/fail check (`npm test`); a rubric loop would add cost without adding signal." Then just do the work.

---

## Step 1 — Write the rubric before running anything

Turn "is this good?" into 3–5 named, weighted criteria. A criterion is well-written when two independent evaluators would score it within ~1 point of each other.

Rules:

- **Name each dimension** and define it by observable properties, not by adjective.
- **Weight them** — sum to 100.
- **Set a hard floor per dimension**, not just an average. Falling below any single floor fails the round. An average lets one strong dimension mask a broken one.
- **Avoid vague superlatives.** The exact wording steers what the generator converges on. "Museum-quality" pushed real runs toward homogenous minimalism; "award-winning", "world-class", "beautiful" do the same. Write what you want to *see*, not how impressed you want to be.
- **Name the anti-patterns explicitly.** Generic purple gradients, centered hero + three feature cards, default shadcn-with-no-changes, emoji-as-icons, Inter-everywhere — if you don't name the slop, you get the slop.
- Show the rubric to the user and get a nod before spending iterations on it.

### Rubric template

```markdown
## Rubric: <artifact>
Scale 1–10 per dimension. Pass = weighted total >= 8.0 AND every dimension >= its floor.

1. Design Quality — weight 30, floor 7
   Color, typography, and layout cohere into one deliberate visual language.
   Type scale is intentional; spacing follows a consistent unit; the palette
   has a clear role assignment (surface / content / accent / state).

2. Originality — weight 25, floor 6
   Evidence of specific decisions rather than template defaults. Explicitly
   penalize: purple/blue gradient hero, unmodified component-library defaults,
   stock centered-hero + 3-card grid, emoji standing in for icons.

3. Craft — weight 25, floor 7
   Typographic hierarchy readable at a glance; optical alignment; consistent
   corner radii and border treatment; text contrast >= 4.5:1; no layout shift,
   overflow, or clipped text at 375px / 768px / 1440px.

4. Function — weight 20, floor 8
   Every stated task is completable by clicking through the real UI. Empty,
   loading, and error states exist. No dead controls, no console errors.
```

For full-stack sprint work, swap in: Product Depth / Functionality / Visual Design / Code Quality, same floor mechanic.

---

## Step 2 — Spawn the generator

Use the host's subagent API to launch a **fresh generator context** with: the task, the **full rubric text**, and (from round 2 on) the evaluator's written feedback verbatim. In Codex, use its multi-agent execution to spawn an independent subagent; in another host, use that host's equivalent fresh-context subagent call.

You are the orchestrator. Do **not** write the artifact yourself in this context — if you generate it here, you have no clean context left to evaluate from.

- Give it the rubric up front — it should build *toward* the criteria, not be surprised by them.
- Ask it to end its run with a short "what I changed and where" note, plus how to run/see the result (URL, command). The evaluator needs this.
- Do **not** ask the generator to score itself. A self-score anchors the evaluator if it leaks into the next context.
- **Never reuse the generator's context across rounds.** New round = new subagent, seeded with the original task + rubric + latest feedback. This is the context-anxiety fix.

---

## Step 3 — Spawn an independent evaluator

A **separate subagent invocation** — a second, brand-new context, never a continuation of the generator. Concretely:

- Start a new subagent. **Do not** send follow-up instructions to the generator, and do not ask it to "now switch hats and critique". Both keep the generator's context and reproduce exactly the self-evaluation bias this skill exists to remove.
- Do not evaluate in *your own* orchestrator context either — you saw the generator's plan and report, so you are contaminated too. Your job is to pass the rubric and artifact pointer in, and read the scores out.
- The evaluator prompt contains only: the rubric verbatim, the original user requirements, how to reach the artifact (path / URL / command), and the required output format. It must not contain the generator's reasoning, rationale, self-assessment, or "what I changed" narrative beyond the bare pointer to where the artifact is.

For UI targets, the evaluator must *drive the real thing*:

1. Check for a connected browser MCP or browser tool (Playwright, Chrome, or the host's equivalent) using the host's normal tool-discovery mechanism. If none exists, tell the user the loop will be substantially weaker and ask whether to proceed on screenshots only.
2. Start/serve the app, navigate to it, and **actually interact** — click every primary control, submit forms with valid *and* invalid input, navigate between views, resize to 375 / 768 / 1440, read the console.
3. Judging code, a static screenshot, or a description of the UI does not count. Broken interaction flows are invisible in a screenshot.

Evaluator output format — enforce this:

```markdown
### Scores
| Dimension | Score | Floor | Pass |
|---|---|---|---|
| Design Quality | 6 | 7 | NO |
...
Weighted total: 7.1 / 10 — FAIL (Design Quality below floor)

### Blocking issues (must fix)
1. <file:line or screen+element> — what's wrong — what "fixed" looks like
2. ...

### Non-blocking improvements
...

### What is working — do not regress
...
```

A bare number is a useless round. Every deduction must name a location and a concrete target state. Also require the "do not regress" list — without it, round N+1 breaks what round N fixed.

---

## Step 4 — Iterate, and watch for plateau

Default cap: **5–15 rounds** (5 for one component, 10–15 for a full build). Let the user override.

Each round: fresh generator (task + rubric + feedback) → fresh evaluator → record the score line in a running log.

Stop early when:

- Pass condition met (total ≥ target **and** every floor cleared), or
- **Plateau**: weighted total moves < 0.3 across two consecutive rounds, or the same blocking issue survives two rounds. Stop and report — don't burn the remaining budget. A plateau usually means a bad rubric criterion, a missing capability (evaluator can't actually reach the feature), or a genuine design tradeoff needing a human call. Say which you think it is.
- Score *regresses* two rounds running — revert to the best-scoring revision and report.

Report to the user: score trajectory per round, what finally passed or blocked, and the diff of what changed.

---

## Step 5 — Contract negotiation (large builds only)

For multi-sprint work, most waste comes from building the wrong thing well. Before **any** code for a sprint:

1. **Generator proposes a contract**: what it will deliver this sprint, the visible behavior when done, and *how the evaluator will verify each item* (exact click path, exact expected state).
2. **Evaluator reviews the contract itself** — is the scope right, is the verification method actually able to detect failure, is anything untestable-as-written or missing?
3. Iterate on the contract (usually 1–2 exchanges). Only then implement.
4. Evaluate against the agreed contract plus the standing rubric.

Cheap to fix a contract; expensive to fix a sprint.

Optionally add a **Planner** ahead of all this: expand a one-line prompt into a spec and sprint breakdown, so each sprint is a bounded contract.

---

## Worked example — redesigned settings page

**0. Warranted?** Yes — "make the settings page not feel like a form dump" has no test.

**1. Rubric.** The four dimensions above, with Function's task list pinned to this page: change theme, update email with validation, toggle notifications, delete account behind a confirm.

**2. Round 1 generator.** Subagent gets the rubric + `src/pages/Settings.tsx`. Rebuilds with grouped sections, a real type scale, sticky save bar. Reports: "run `npm run dev`, open /settings".

**3. Round 1 evaluator.** Separate subagent, browser MCP. Clicks through:
- Design Quality **6** (floor 7) — section headers and field labels are the same size/weight; no hierarchy between group and field.
- Originality **7** — good, sections aren't the default card grid.
- Craft **5** (floor 7) — helper text `#9CA3AF` on white = 2.8:1; save bar overlaps the last field at 375px.
- Function **6** (floor 8) — invalid email shows no error, submits anyway; delete-account confirm has no cancel.
- Total 6.0 — **FAIL**, three floors missed. Do not regress: the sticky save bar and the grouping.

**4. Round 2.** *Fresh* generator context: original task + rubric + that feedback verbatim. Fixes hierarchy, contrast, mobile padding, email validation, cancel button. → 8.4, all floors cleared. **Pass in 2 rounds.** Report trajectory 6.0 → 8.4 and the diff.

---

## Anti-patterns

- Evaluating in the generator's own context — including sending follow-up instructions to the generator to "now review your work", or an orchestrator that generated the artifact then grades it. That is self-review; it defeats the entire skill. The evaluator is always a fresh subagent invocation.
- Summarizing a long generator history into the next round instead of resetting. Carry the *feedback*, not the transcript.
- Score-only feedback with no locations or target states.
- Rubrics of vague superlatives — they converge every run onto the same look.
- Averaging without floors, so one broken dimension hides.
- Running the full 15 rounds on a task that had a real test all along.
