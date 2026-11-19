---
name: "harness-engineering:self-harness"
description: Use when an agent is explicitly authorized to improve its own harness from repeated, verifier-grounded execution failures while the model and evaluation controls can remain fixed.
---

# Self-Harness

Change only declared harness surfaces, through controlled experiments you can undo.

Sources: [AHE v4 §3.1–3.3](https://arxiv.org/html/2604.25850v4#S3) gives editable components, layered evidence, and a check of each edit's prediction; [Self-Harness v3 §3](https://arxiv.org/html/2606.09498v3#S3) gives failure clustering, diverse minimal edits, and a two-split rule that accepts only edits with no regression.

**Local changes (neither paper has these steps):**
- Acceptance: AHE keeps or reverts each edit by its next-round verdict. Here the two-split gate decides; verdicts are for diagnosis only.
- Content-hashed discovery, a regression run on combined edits, an untouched final set, and human governance.

## Discover

Rebuild a capability manifest from the real environment. AHE's seven component types: system prompt, tool description, tool implementation, middleware, skill, sub-agent configuration, long-term memory. Per surface, record canonical source, content hash, availability probe, and whether it is observed or explicitly editable.

When a source hash or runtime binding changes, invalidate derived index entries.

## Freeze

Snapshot the parent and pre-campaign baseline. Freeze model, inference settings, evaluator, verifier, task splits, trial counts, budgets, timeouts, sandbox setup, and non-editable runtime settings. Use a fresh sandbox per trial. A declared editable runtime policy may change. If a control drifts, start a new lineage; do not compare it with earlier rounds.

Before starting, split three sets: held-in evidence, the hidden held-out promotion gate, and the untouched final set (local). The proposer must not be able to read hidden task inputs, traces, or task-level outcomes; the gate returns only accept or reject. Fix in advance the repeat protocol for noisy trials and the final acceptance criteria.

## Evolve

1. Run repeated baselines; keep raw traces. Arrange held-in evidence in layers: overview → per-task reports → raw traces. Use summaries first; raw traces only to fill gaps. Give each failure a signature (terminal verifier cause, causal status of behavior, abstract mechanism). Cluster deterministically by exact signature match, and order clusters by support and actionability. Partial-pass tasks are the most useful: compare passing and failing rollouts of the same task. Target only clusters that have evidence and that an editable surface can fix. Exclude anecdotes, infrastructure errors, unstable outcomes, task-specific shortcuts, and model capability limits. Do not drop failed trials from the fixed scoring protocol.
2. The proposer is the same fixed model under the current harness. Give it the editable surfaces, failure patterns, passing behaviors to keep, and summaries of earlier edits. Generate clearly different, minimal edits; each targets one mechanism through the narrowest authorized surface. Before evaluation, record evidence, root cause, target component and why, target held-in cases or behaviors, predicted fixes, and regressions at risk.
3. Evaluate each candidate on its own against its parent, on the held-in and hidden gate sets, with the fixed trial protocol. Reject a candidate that changes no editable surface or fails before producing a valid result. Use total pass counts across repeats: require `delta_held_in >= 0`, `delta_hidden >= 0`, and at least one delta `> 0`. Reject any decrease on either split; repeated trials do not justify tolerating it as noise.
4. Compare each edit's predictions with the observed held-in deltas per task. Record predicted vs. observed fixes and regressions and a verdict per edit, and feed this into the next round. An unexpected gain can qualify, but it does not prove the predicted mechanism was fixed. If a failure class persists for 2+ rounds after fixes at one component level, target a different level next (AHE prompt advice). Reverting an accepted edit is a candidate too and must pass the gate.
5. Combine only qualified, compatible edits. Rerun the full regression suite and the two-split gate against the parent. Roll back failed edits or combinations. Keep successful checkpoints, update the parent, and repeat with new runs on the same fixed held-in split while the stop conditions allow.

When the campaign ends, freeze its best qualifying harness. Compare it and the pre-campaign baseline once on the untouched final set using the fixed protocol. Validation covers only this model/task set. Promote only if total final passes do not decrease and predeclared task criteria pass. Otherwise keep the previously validated harness. Never tune or reselect using the used final set; further experiments need a new untouched final set.

## Record and Stop

Make each logical edit one commit. Version the manifests, diffs, results, per-edit prediction verdicts, accepted and rejected edits, parentage, and restore points. Separate experimental checkpoints from final-validated versions. Store hidden and final-set evidence with the gate, not in files the proposer can read.

Without an objective verifier and a hidden gate set, do not promote. Stop when you run out of evidence, budget, fresh capability data, fixed controls, or authority.

Changes to measurement, permissions, security, deployment, spending, destructive actions, or self-approval need independent human governance. Never auto-promote them.

## Anti-patterns

- Presenting the local changes as requirements of either paper.
