---
name: harness-retune
description: Re-evaluate an agent harness after a model upgrade — inventory the scaffolding (sprint/phase decomposition, evaluator passes, contract negotiation, planner stages, forced context resets), empirically test which pieces the current model no longer needs, and identify newly-possible harness patterns. Use when the user says they are on a new model version and asks whether the scaffolding is still needed, "do we still need this sprint structure", "simplify the agent harness", "our workflow feels over-engineered for this model", "re-evaluate our multi-agent workflow after a model upgrade", or when planning a periodic harness audit.
metadata:
  short-description: "Re-evaluate harness scaffolding after a model upgrade and test what can be removed or newly attempted."
---

# Harness Retune

Every piece of scaffolding in a harness is a **hypothesis about a specific model limitation**. When the model changes, the hypothesis must be re-tested — not assumed to still hold. This skill runs that re-test.

Guiding principle: *find the simplest solution, only adding complexity when needed.* Remove one component at a time and measure the impact.

Retuning goes **both directions**: some scaffolding becomes removable, and some newly ambitious harness patterns become viable. Do not treat this as a cleanup-only exercise.

## Step 1 — Inventory the scaffolding

Read the workflow definition: skill/subagent files, orchestration code, prompt templates, CI glue, exec-plan docs, CLAUDE.md rules. Build a table with one row per **structural step that exists to compensate for a model limitation**, not per feature. Typical candidates:

- Sprint / phase decomposition (work chopped into small chunks)
- A separate evaluator or QA pass (per-sprint, per-file, or end-of-run)
- Contract / interface negotiation steps before implementation
- A dedicated planner stage separate from execution
- Forced context resets, compaction points, or handoff summaries
- Retry / self-check loops, output schema re-validation
- Fan-out to subagents purely to conserve context
- Human-approval gates that exist only for model reliability, not policy

For each row record:

| Element | Failure it prevents | Model/date it was added for | Evidence it was ever needed | Cost per run (tokens/latency/complexity) |

Concretely, to fill this in: `git log --diff-filter=A` / `git log -p` on the harness files to find when each step appeared and what the commit message or PR said; grep the workflow for words like "because", "otherwise", "drifts", "to avoid", "safeguard"; and check any prior retune record (Step 4). Order the rows by cost — the most expensive scaffolding is where ablation pays off first.

**If the "why" is not recorded anywhere, that is a finding in itself.** Undocumented scaffolding is unmaintainable scaffolding — you cannot test a hypothesis nobody wrote down. Flag it, and reconstruct the most likely intent from git history/PR discussion before proceeding. Never delete an element just because its rationale is missing; missing rationale means *test it*, not *drop it*.

## Step 2 — Controlled comparison, one element at a time

For each candidate, run an **ablation**: the same task, on the current model, with that single element removed, against the baseline harness with it in place. Change one thing per trial.

Do it properly:

1. Pick 2–3 representative tasks, including the hardest one the harness is expected to survive.
2. Fix everything else: same prompt, same repo state, same tools, same model.
3. **Before running anything, write down a one-line falsifiable prediction**: what you expect the ablated variant to do relative to baseline, and why ("removing per-sprint QA: no quality delta on tasks under ~8 files, drifts on the largest one — the model's coherent runtime should cover the smaller tasks but not the biggest"). This is what turns the ablation into a test of a stated belief instead of a fishing expedition, and it is what Step 3 scores against, not just the raw numbers. Skipping this and judging post-hoc is how "the model seems better now" sneaks back in as a conclusion.
4. Run baseline and ablated variants. More than one run each where output is stochastic and budget allows.
5. Score against criteria decided **before** running — e.g. tests passing, requirements met, architectural coherence at the end of the run, drift/regression in later stages, hallucinated APIs, human-fix minutes. Also record cost and wall-clock. Then compare the outcome against the prediction from step 3: did it hold, or was the hypothesis wrong? A wrong prediction that still gets called a win is a sign the criteria in step 5 were chosen after the fact — redo the call honestly.

If running both is genuinely infeasible, degrade honestly to reasoned analysis and **label it as such**: state the original failure mode, state what the current model is documented to do (coherent runtime, context window, self-critique quality, instruction adherence), and judge whether the failure mode still plausibly applies. Mark the recommendation as unverified and lower-confidence. Never present reasoning as if it were a measurement.

Elements can interact: two pieces may each be individually removable but fail when removed together (e.g. sprint decomposition and the per-sprint evaluator both guard the same drift). After the single-element passes, run one combined ablation for any set you intend to remove together, and validate additions the same way — a newly-possible pattern is a hypothesis too, so A/B it against the current harness rather than adopting it on optimism.

Watch for failure modes that only appear late: coherence loss and self-evaluation bias usually surface at the *end* of a long run, so a short smoke test is not evidence.

## Step 3 — Decide, conservatively for removal

- **Remove** only where the ablation shows no meaningful quality loss and a real cost/complexity saving — and score the outcome against the Step 2 prediction. A removal the data supports but you didn't predict is still a removal; record the miss explicitly rather than quietly dropping it, because a wrong prediction means the mental model of this harness was stale even though the verdict landed right. "The model seems better now" is not a result.
- **Downgrade instead of delete** when the element helps sometimes: make it optional, conditional on task size, or move it from per-sprint to once at the end.
- **Keep** where the failure reappears — and update the rationale note with the fresh evidence and date, so the next retune starts informed.
- **Add** where the current model's new capabilities unlock something. Longer coherent runtime → attempt larger units of work, or a whole build in one pass. Better self-critique → a lighter self-review may replace a separate evaluator agent. Bigger/cheaper context → drop compaction, or fan in more source material. Improved tool use → collapse an orchestration layer.

The interesting space of harness combinations does not shrink as models improve — it *moves*. Spend part of every retune asking "what is newly tractable?", not only "what can be deleted?".

## Step 4 — Record before/after

Write a short record (pairs naturally with the `execution-plan` skill; keep it under `docs/exec-plans/` or alongside the harness definition):

```markdown
# Harness retune — <workflow> — <date>
Model: <previous> → <current>

| Element | Predicted (pre-ablation) | Verdict | Evidence | Prediction held? | Cost delta |
|---|---|---|---|---|---|
| Per-sprint evaluator | No quality delta if downgraded; risk on the largest task only | Downgraded to single end-of-run pass | 3/3 tasks equal quality; 1 late-stage nit caught by final pass | Yes | -38% tokens |
| Sprint decomposition | Would drift on tasks >8 files | Kept, now optional >8 files | Ablation drifted on the largest task | Yes | — |
| Planner stage | Expected to still add value on ambiguous specs | Removed | No quality delta on any task | No — over-predicted its value | -1 model call |

New patterns tried: <...>
Open questions for next retune: <...>
```

The "prediction held?" column is the point, not decoration: a retune record full of confirmed predictions means the mental model of the harness is accurate. A record with several "No"s means the assumptions about this model are stale even where the verdict landed right — flag that explicitly, because the next retune should not trust the reasoning that got lucky.

This record is the baseline for the next retune. Without it, every upgrade restarts from zero.

## Step 5 — Make it a cadence, not a one-off

Say this explicitly to the user: **revisit the harness every time a notable new model ships.** Scaffolding accretes silently and never removes itself. Recommend a standing trigger — a checklist item on model-upgrade, a scheduled review, or a note in the workflow's README pointing at the last retune record.

## Worked example (generic pattern)

A full-stack build harness on the previous model needed: (a) work split into small sprints to stay coherent, and (b) a QA/evaluator pass after *every* sprint, because the model drifted from the spec over long runs and could not reliably critique its own output.

On the new model, retune:

1. **Inventory** — both elements traced to the same documented failure: coherence loss past ~40 minutes of autonomous work.
2. **Predict** — before running anything: "per-sprint QA is redundant with a single end-of-run pass on tasks the model can now sustain coherently; sprint decomposition still matters above ~8 files because that's a scope problem, not a coherence problem."
3. **Ablate** — run the same three builds four ways: baseline; no per-sprint QA (single QA at the end); no sprint decomposition (one continuous run); neither.
4. **Result** — the new model ran 2+ hours coherently. Single end-of-run QA matched per-sprint QA on all three builds at ~40% lower cost. Removing sprint decomposition matched on two builds but drifted on the largest.
5. **Decide** — both predictions held. Evaluator downgraded to one end-of-run pass; sprint structure made *optional*, applied only above a size threshold. Newly possible: because the model sustains long coherent runs, try a more ambitious single-pass build with a richer up-front spec — an addition, not a simplification.
6. **Record** the table above with the predictions and their outcomes, and re-test at the next model release.

The lesson to generalize: the evaluator is not a fixed yes/no decision. Scaffolding is worth its cost only when the task exceeds what the current model can reliably do on its own — and that boundary moves with every release.

## Anti-patterns

- Ablating on a single easy task and declaring the scaffolding removable across the whole harness — Step 2 requires 2–3 tasks including the hardest one because coherence and drift failures surface only under load.
- Running the ablation first and deciding what it means afterward — skipping the pre-run falsifiable prediction is exactly how "the model seems better now" passes for a result.
- Quietly dropping a removal the data supports because the prediction was wrong, or writing the prediction up after the fact so it reads as foresight — a miss gets recorded honestly, not hidden or backfilled.
- Deleting scaffolding just because its original rationale isn't documented — Step 1 is explicit that missing rationale means test it, not drop it.
- Auditing only for what to remove and skipping the "what's newly possible" half of Step 3, or shipping a newly-possible pattern on optimism instead of A/B testing it like any other ablation.
- Treating a short smoke test as evidence a coherence- or drift-guarding element is safe to cut — those failure modes surface late in a long run, so only a full-length trial counts.
- Running the retune once and never recording it, or recording it but leaving no trigger for the next model upgrade — Step 5 exists because scaffolding accretes silently between releases.
