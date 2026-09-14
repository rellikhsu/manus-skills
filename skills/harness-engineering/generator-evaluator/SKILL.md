---
name: generator-evaluator
description: "Run a generator/evaluator harness loop for subjective acceptance criteria that objective checks do not fully cover, including mixed correctness/UX tasks. Use for UI/UX redesigns, \"make this look good\", visual design review, frontend polish passes, product-feel critique, or any multi-sprint build where \"is this actually done and correct?\" needs independent judgment. Builds an explicit scoring rubric first, then iterates with a separate evaluator agent so the model never grades its own work. Triggers on: subjective quality task, design review loop, does this look good, UX pass, redesign, avoid self-grading bias, iterate until it's good, rubric-scored iteration, contract negotiation before a sprint."
metadata:
  short-description: "Run an independent generator/evaluator rubric loop for subjective criteria not fully covered by objective checks, including mixed correctness/UX tasks."
---

# Generator / Evaluator Harness

Two failure modes make naive single-agent execution unreliable on subjective work:

- **Context anxiety** — some models wind work down prematurely as context fills. A reset with a structured handoff can help when compaction does not; whether it is needed depends on the model and task. Measure before imposing it on every round.
- **Self-evaluation bias** — a model grading its own output is systematically optimistic, worst on subjective dimensions (design quality, UX, "does this feel right"). Fix by making the evaluator a **separate agent invocation with its own context**, prompted to critique.

Source: Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), especially “Frontend design”, “The architecture”, and “Running the harness”. That harness removed resets with Opus 4.5 while retaining separate roles and automatic compaction. Role isolation and context lifetime are separate choices.

**Local adaptation:** this skill specializes in subjective acceptance criteria. Rubric weights, floors, round caps, plateau thresholds, and viewport sizes below are adjustable starting points, not universal values from the article.

---

## Step 0 — Decide if you need this at all

Start with the simplest harness that could work. Do **not** default to the heavy version.

| Situation | Harness |
|---|---|
| Trusted objective checks cover every acceptance criterion | Use those checks; a subjective rubric loop adds no uncovered criterion. |
| Mixed task: tests cover correctness, but UX/design still needs judgment | Run objective checks and use the independent evaluator for the remaining subjective criteria. |
| Single subjective artifact (one page, one component, one doc) | Rubric + generator + independent evaluator, 5–10 rounds |
| Large multi-step build (full app, several features) | Add sprint structure + **contract negotiation** (Step 5), 10–15 rounds |

The existence of `npm test` alone does not establish complete coverage. Map checks to the actual acceptance criteria. Skip this subjective loop only when trusted checks cover them all; honor an explicit request for additional independent review.

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

### Calibrate the evaluator

Before relying on scores, trial the evaluator on a few actual samples with known human judgments, including a clear pass and a clear failure. Compare its reasons and scores with those judgments; inspect evaluator logs and adjust its prompt or rubric when it is lenient, inconsistent, or rewards the wrong qualities. Rerun the samples after an adjustment. Keep samples and judgments isolated from generator reasoning.

Record the rubric version and calibration evidence. If human reference judgments are unavailable, label scores uncalibrated and do not report rubric passage as validated alignment with user preferences. A changed rubric starts a new scoring series: re-score the comparison artifacts before using a trajectory or plateau rule.

### Choose each role's context lifetime

Start separate generator and evaluator sessions. Each may retain its own session across rounds with host compaction. Reset a role when observed context anxiety or drift persists, or when a controlled comparison supports resetting. Record the reason; use `harness-retune` after model changes. If the host cannot resume subagents, use fresh calls as a host constraint, not as a source requirement. A generator handoff carries the task, rubric, current artifact/state, open work, and evaluator feedback; an evaluator handoff carries only its evaluation contract, calibration, and prior findings.

## Step 2 — Run the generator

Use the host's subagent API to start the generator with the task and **full rubric text**. From round 2, resume its own session or use the reset policy above, supplying the evaluator's written feedback verbatim and the current artifact/state. In Codex, use its multi-agent execution; in another host, use the equivalent subagent API.

You are the orchestrator. Do **not** write the artifact yourself in this context — if you generate it here, you have no clean context left to evaluate from.

- Give it the rubric up front — it should build *toward* the criteria, not be surprised by them.
- Ask it to end its run with a short "what I changed and where" note, plus how to run/see the result (URL, command). The evaluator needs this.
- Do **not** ask the generator to score itself. A self-score anchors the evaluator if it leaks into the next context.
- Keep the generator in its own role across rounds. Reset only under the chosen context policy, carrying a sufficient handoff rather than assuming feedback alone reconstructs the work.

---

## Step 3 — Spawn an independent evaluator

Start a **separate evaluator session**, never a continuation of the generator. On later rounds, it may resume its own evaluation session under the chosen context policy. Concretely:

- Use the independent evaluator, or replace it if a reset is warranted. **Do not** ask the generator to "now switch hats and critique"; that retains the generator's context and reproduces the self-evaluation bias this skill exists to remove.
- Do not evaluate in *your own* orchestrator context either — you saw the generator's plan and report, so you are contaminated too. Your job is to pass the rubric and artifact pointer in, and read the scores out.
- The evaluator receives only evaluation inputs: the rubric verbatim, human calibration samples/judgments when available, the original user requirements, how to reach the current artifact (path / URL / command), its prior findings, and the required output format. It must not contain the generator's reasoning, rationale, self-assessment, or "what I changed" narrative beyond the bare pointer to where the artifact is.

For UI targets, the evaluator must *drive the real thing*:

1. Check for a connected browser MCP or browser tool (Playwright, Chrome, or the host's equivalent) using the host's normal tool-discovery mechanism. If none exists, tell the user the loop will be substantially weaker and ask whether to proceed on screenshots only.
2. Start/serve the app, navigate to it, and **actually interact** — click every primary control, submit forms with valid *and* invalid input, navigate between views, resize to 375 / 768 / 1440, read the console.
3. Judging code, a static screenshot, or a description of the UI does not count. Broken interaction flows are invisible in a screenshot.

Evaluator output format — enforce this:

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

### What is working — do not regress
...
```

A bare number is a useless round. Every deduction must name a location and a concrete target state. Also require the "do not regress" list — without it, round N+1 breaks what round N fixed.

---

## Step 4 — Iterate, and watch for plateau

Default cap: **5–15 rounds** (5 for one component, 10–15 for a full build). Let the user override.

Each round: generator revision → run required objective checks → independent evaluator checks that same artifact → record check results, scores, rubric version, and context-policy decisions. Resume or reset each role according to Step 1; role isolation remains required in either mode.

Stop early when:

- Pass condition met: all required objective checks pass on the evaluated artifact revision **and** total ≥ target **and** every floor cleared. A failing or unrun required check blocks acceptance regardless of rubric scores; later edits require fresh checks. Or
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

**1. Rubric and calibration.** Pin Function to this page: change theme, update email with validation, toggle notifications, delete account behind a confirm. Trial the rubric on user-rated pass/fail samples; correct evaluator leniency before trusting its scores.

**2. Round 1 generator.** Subagent gets the rubric + `src/pages/Settings.tsx`. Rebuilds with grouped sections, a real type scale, sticky save bar. Reports: "run `npm run dev`, open /settings".

**3. Round 1 evaluator.** Separate subagent, browser MCP. Clicks through:
- Design Quality **6** (floor 7) — section headers and field labels are the same size/weight; no hierarchy between group and field.
- Originality **7** — good, sections aren't the default card grid.
- Craft **5** (floor 7) — helper text `#9CA3AF` on white = 2.8:1; save bar overlaps the last field at 375px.
- Function **6** (floor 8) — invalid email shows no error, submits anyway; delete-account confirm has no cancel.
- Total 6.0 — **FAIL**, three floors missed. Do not regress: the sticky save bar and the grouping.

**4. Round 2.** Resume the generator's own session with that feedback verbatim, or reset with the structured handoff if the chosen policy calls for it. Fixes hierarchy, contrast, mobile padding, email validation, cancel button. → 8.4, all floors cleared. **Pass in 2 rounds.** Report trajectory 6.0 → 8.4 and the diff.

---

## Anti-patterns

- Evaluating in the generator's own context — including sending follow-up instructions to the generator to "now review your work", or an orchestrator that generated the artifact then grades it. That is self-review; it defeats the entire skill. The evaluator always has a separate role and context from the generator; it can retain its own evaluation history.
- Treating resets as mandatory for every model, or continuing a drifting session despite evidence that compaction is insufficient. Keep generator reasoning out of the evaluator in either mode.
- Trusting uncalibrated scores as proof of user preference, or comparing scores across rubric changes without re-scoring the artifacts.
- Score-only feedback with no locations or target states.
- Rubrics of vague superlatives — they converge every run onto the same look.
- Averaging without floors, so one broken dimension hides.
- Running subjective scoring when trusted objective checks already cover every criterion, or skipping UX evaluation merely because some tests exist.
