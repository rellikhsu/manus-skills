---
name: harness-retune
description: Re-test agent scaffolding after a model upgrade, one piece at a time, and try what is newly possible. Use when a new model ships or a workflow feels over-engineered.
metadata:
  short-description: "Re-evaluate harness scaffolding after a model upgrade and test what can be removed or newly attempted."
---

# Harness Retune

Each piece of harness scaffolding is a **hypothesis about a specific model limitation**. When the model changes, re-test the hypothesis; do not assume it still holds.

Guiding principle: *find the simplest solution, only adding complexity when needed.*

Sources: Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), “Iterating on the harness” and “Removing the sprint construct”; the prediction/verification record adapts [AHE v4 §3.3](https://arxiv.org/html/2604.25850v4#S3.SS3).

**Local defaults:** the task count, cadence, and record format below are local choices. Fit them to the actual model upgrade and evaluation budget.

## Step 1 — Inventory the scaffolding

Read workflows (skills, subagents, orchestration, prompts, CI, plans, rules). Record step budgets and per-task timeouts for the old model/reasoning tier. Tabulate one row per **structural step compensating for model limits**, not per feature. Candidates:

- Sprint / phase decomposition
- A separate evaluator or QA pass
- Contract / interface negotiation before implementation
- A planner stage separate from execution
- Forced context resets, compaction points, or handoff summaries
- Retry / self-check loops, output schema re-validation
- Fan-out to subagents only to save context
- Human-approval gates that exist only for model reliability, not policy

For each row record:

| Element | Failure it prevents | Model/date it was added for | Evidence it was ever needed | Cost per run (tokens/latency/complexity) |

If the reason is not recorded anywhere, rebuild the most likely intent from git history or PR discussion before you continue. Never delete an element only because its reason is missing; a missing reason means *test it*, not *drop it*.

## Step 2 — Controlled comparison, one element at a time

For each candidate, run an **ablation**: the same task, on the current model, with that one element removed, compared with the baseline harness that keeps it.

Steps:

1. Pick 2–3 representative tasks, including the hardest one the harness must handle.
2. Keep everything else fixed: same prompt, repo state, tools, and model.
3. **Before running anything, write down a falsifiable prediction**: which tasks should improve and which may regress, what the ablated variant will do compared with baseline, and why ("removing per-sprint QA: no quality delta on tasks under ~8 files, drifts on the largest one — the model's coherent runtime should cover the smaller tasks but not the biggest").
4. Run the baseline and ablated variants. Run each more than once when output is random and budget allows.
5. Score against criteria chosen **before** running, e.g. tests passing, requirements met, architectural coherence at the end of the run, drift or regression in later stages, hallucinated APIs, minutes of human fixing. Also record cost and wall-clock time. Then compare the result with the prediction from step 3: did it hold, or was the hypothesis wrong?

If running both is truly not possible, fall back to reasoned analysis and **label it as such**: state the original failure mode, state what the current model is documented to do (coherent runtime, context window, self-critique quality, instruction following), and judge whether the failure mode still plausibly applies. Mark the recommendation as unverified and lower confidence.

Elements can interact: two pieces may each be removable alone but fail when removed together. After the single-element runs, run one combined ablation for any set you plan to remove together. Test additions the same way: a newly possible pattern is also a hypothesis, so A/B test it against the current harness instead of adopting it on hope.

## Step 3 — Decide, conservatively for removal

- **Remove** only where the ablation shows no meaningful quality loss and a real saving in cost or complexity, and score the result against the Step 2 prediction. The ablation decides.
- **Downgrade instead of delete** when the element helps only sometimes: make it optional, make it depend on task size, or move it from every sprint to once at the end.
- **Keep** where the failure comes back, and update the reason note with the new evidence and date.
- **Add** where the current model's new abilities unlock something. Longer coherent runtime → try larger units of work, or a whole build in one pass.

The set of useful harness designs does not shrink as models improve; it *moves*. In every retune, also ask "what is newly possible?", not only "what can be deleted?".

## Step 4 — Record before/after

Write a short record (keep it under `docs/exec-plans/` or next to the harness definition):

```markdown
# Harness retune — <workflow> — <date>
Model: <previous> → <current>

| Element | Predicted (pre-ablation) | At-risk tasks | Verdict | Evidence | Prediction held? | Cost delta |
|---|---|---|---|---|---|---|

New patterns tried: <...>
Open questions for next retune: <...>
```

The "prediction held?" column: judge hit rates over several retunes, not from a few misses.

This record is the baseline for the next retune.

## Step 5 — Make it a cadence, not a one-off

Tell the user directly: **revisit the harness every time a notable new model ships.** Recommend a standing trigger: a checklist item for model upgrades, a scheduled review, or a note in the workflow's README that links to the last retune record.

## Anti-patterns

- Treating a short smoke test as evidence that an element guarding against coherence loss or drift is safe to cut. Those failures appear late in a long run, so only a full-length trial counts.
