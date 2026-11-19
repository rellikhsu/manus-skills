---
name: "harness-engineering:generator-evaluator"
description: Separate generator and evaluator agents iterate against a rubric. Use for subjective quality (UI/UX, design, polish) or when deciding if work is really done needs a judge other than its author.
metadata:
  short-description: "Run an independent generator/evaluator rubric loop for subjective criteria not fully covered by objective checks, including mixed correctness/UX tasks."
---

# Generator / Evaluator Harness

Two failure modes make a single agent unreliable:

- **Context anxiety**: some models wrap up work too early as the context fills.
- **Self-evaluation bias**: a model that grades its own output is too optimistic, most of all on subjective qualities. Fix: make the evaluator a **separate agent call with its own context**, told to critique.

Source: Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps).

**Local adaptation:** this skill focuses on subjective acceptance criteria. The rubric weights, floors, round caps, plateau thresholds, and viewport sizes below are starting points you can change, not universal values from the article.

---

## Step 0 — Decide if you need this at all

Start with the simplest harness that could work.

| Situation | Harness |
|---|---|
| Trusted objective checks cover every acceptance criterion | Use those checks. |
| Mixed task: tests cover correctness, but UX/design still needs judgment | Run objective checks and use the independent evaluator for the remaining subjective criteria. |
| Single subjective artifact (one page, one component, one doc) | Rubric + generator + independent evaluator |
| Large multi-step build (full app, several features) | Add sprint structure + **contract negotiation** (Step 5) |

Having `npm test` does not by itself prove full coverage. Map checks to the real acceptance criteria. Honor an explicit request for extra independent review.

---

## Step 1 — Write the rubric before running anything

Turn "is this good?" into 3–5 named, weighted criteria. A criterion is well written when two independent evaluators would score it consistently.

Rules:

- **Name each dimension** and define it by what you can observe, not by adjectives.
- **Weight them**: weights sum to 100.
- **Set a hard floor per dimension**, not just an average. Falling below any one floor fails the round.
- **Avoid vague superlatives.** The exact words steer what the generator produces.
- **Name the anti-patterns explicitly.**
- Show the rubric to the user and get approval before spending rounds on it.

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

For full-stack sprint work, use instead: Product Depth / Functionality / Visual Design / Code Quality.

---

### Calibrate the evaluator

Before trusting scores, test the evaluator on a few real samples with known human judgments. Compare its reasons and scores with those judgments and read its logs. If it is lenient, inconsistent, or rewards the wrong qualities, fix its prompt or rubric and rerun the samples.

Record the rubric version and the calibration evidence. If no human reference judgments exist, label scores uncalibrated and do not claim that passing the rubric means it matches user preferences. A changed rubric starts a new scoring series: re-score the comparison artifacts before applying a plateau rule.

### Choose how long each role's context lives

Start separate generator and evaluator sessions. Each may keep its own session across rounds, with host compaction. Reset a role when context anxiety or drift keeps showing up, or when a controlled comparison favors resetting. Record why. Use `harness-retune` after model changes. A generator handoff carries the task, rubric, current artifact/state, open work, and evaluator feedback.

## Step 2 — Run the generator

Use the host's subagent API to start the generator with the task and the **full rubric text**. From round 2, give it the evaluator's written feedback word for word and the current artifact/state.

You are the orchestrator. Do **not** write the artifact yourself in this context.

- Ask it to end with a short "what I changed and where" note, plus how to run/see the result (URL, command).

---

## Step 3 — Spawn an independent evaluator

Start a **separate evaluator session**, never a continuation of the generator's.

- **Do not** ask the generator to "now switch hats and critique".
- Do not evaluate in *your own* orchestrator context either.
- The evaluator gets evaluation inputs: the rubric word for word, human calibration samples/judgments when available, the original user requirements, how to reach the current artifact (path / URL / command), its prior findings, and the required output format.

For UI targets, the evaluator must *use the real thing*:

1. Check for a connected browser MCP or browser tool (Playwright, Chrome, or the host's equivalent) with the host's normal tool discovery. If there is none, tell the user the loop will be much weaker.
2. Start/serve the app, open it, and **actually interact**: click every main control, submit forms with valid *and* invalid input, move between views, resize to 375 / 768 / 1440, read the console.
3. Reading code, a static screenshot, or a description of the UI does not count.

Evaluator output format (enforce it):

```markdown
### Objective checks
Artifact revision: <revision/hash>
Required checks: <commands and pass/fail evidence, or none required>

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

### What is working
...
```

Every deduction must name a location and what the fixed state looks like.

---

## Step 4 — Iterate, and watch for plateau

Default cap: **5–15 rounds** (5 for one component, 10–15 for a full build).

Each round: generator revises → run required objective checks → independent evaluator checks the same artifact → record check results and scores.

Stop early when:

- The pass condition is met: all required objective checks pass on the evaluated artifact revision **and** total ≥ target **and** every floor is cleared. A failing or unrun required check blocks acceptance, whatever the rubric scores. Any later edit needs fresh checks. Or
- **Plateau**: the weighted total changes by < 0.3 across two rounds in a row, or the same blocking issue survives two rounds. A plateau usually means a bad rubric criterion, a missing capability (the evaluator can't reach the feature), or a real design tradeoff that needs a human decision. Say which you think it is.

Report to the user: score per round, what finally passed or blocked, and the diff of what changed.

---

## Step 5 — Contract negotiation (large builds only)

Before writing **any** code for a sprint:

1. **The generator proposes a contract**: what it will deliver this sprint, the visible behavior when done, and *how the evaluator will verify each item* (exact click path, exact expected state).
2. **The evaluator reviews the contract**: is the scope right, can the verification method actually detect failure, is anything untestable as written or missing?
3. Revise the contract. Only then implement.
4. Evaluate against the agreed contract plus the standing rubric.

Optional: add a **Planner** before all this. It expands a one-line prompt into a spec and sprint breakdown.

---

## Anti-patterns

- Evaluating in the generator's own context.
