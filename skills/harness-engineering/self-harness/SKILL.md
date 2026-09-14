---
name: self-harness
description: Use when an agent is explicitly authorized to improve its own harness from repeated, verifier-grounded execution failures while the model and evaluation controls can remain fixed.
---

# Self-Harness

Evolve only declared harness surfaces through controlled, reversible experiments. Invocation grants no new authority.

Sources: [AHE v4 §3.1–3.3](https://arxiv.org/html/2604.25850v4#S3) supplies editable components, layered evidence, and per-edit prediction verification; [Self-Harness v3 §3](https://arxiv.org/html/2606.09498v3#S3) supplies failure clustering, diverse minimal edits, and a non-regressive two-split acceptance rule. This skill combines them rather than reproducing either experiment verbatim.

**Local safeguards:** content-hashed capability discovery, combined-edit regression, a third untouched final set, and independent human governance below are additional policies. They are not all required steps in the original papers.

## Discover

Rebuild a capability manifest from the actual environment: skills, tools, middleware, subagents, memory, hooks, and runtime limits. Record canonical source, content hash, availability probe, dependencies, triggers, boundaries, overlaps, and whether each surface is observed or explicitly editable.

Invalidate derived index entries when a source hash or runtime binding changes. A catalog is not proof of availability. Reuse an existing responsibility before adding another capability.

## Freeze

Snapshot the parent harness and pre-campaign baseline. Keep the model, inference settings, evaluator, verifier, task splits, trial counts, budgets, timeouts, sandbox, and non-editable runtime settings fixed. A declared editable runtime policy remains eligible for an experiment. Control drift starts a new lineage; it cannot support comparison with earlier rounds.

Separate held-in evidence, the hidden held-out promotion gate, and the locally required untouched final set before starting. Hidden task inputs, traces, and task-level outcomes stay outside proposer-readable state; the gate returns only its acceptance decision. Fix the stochastic repetition protocol and final acceptance criteria in advance.

## Evolve

1. Run repeated baselines and retain raw traces. Organize held-in evidence as an overview → per-task reports → raw traces. Cluster failures by terminal verifier cause, causal agent behavior, and reusable mechanism. Exclude anecdotes, unstable infrastructure, task-specific shortcuts, and capability limits as edit rationales; do not silently drop failed trials from the fixed scoring protocol.
2. Invoke the same fixed model under the current harness as proposer. Generate materially distinct, minimal edits, each targeting one mechanism through the narrowest authorized surface. Before evaluation, record evidence, target held-in cases/behaviors, predicted fixes, at-risk regressions, and interaction risk.
3. Evaluate each candidate independently against its parent on held-in and hidden gate sets with the fixed trial protocol. Use aggregate pass counts across repeats: require `delta_held_in >= 0`, `delta_hidden >= 0`, and at least one delta `> 0`. Reject a decrease on either split; repeat trials do not authorize a noise-tolerance exception.
4. Compare each edit's predictions with observed held-in task-level deltas. Record predicted vs. observed fixes/regressions and a per-edit verdict, then feed that evidence into the next round. Keep attribution separate from acceptance: an unexpected gain can qualify, but is not proof that the predicted mechanism was fixed. Keep hidden details in the gate's protected record.
5. Combine only qualified, compatible edits and rerun the full regression suite and two-split gate against the parent. Roll back failed edits or combinations. Preserve successful checkpoints, update the parent, and repeat with fresh held-in evidence while the stop conditions permit.

After the entire campaign stops, freeze its best qualifying harness. Evaluate that single selection and the pre-campaign baseline once on the untouched final set using the fixed trial protocol. Require no decrease in aggregate final pass count plus any predeclared task-specific criteria before promotion. A failure retains the previously validated harness; do not tune or select another candidate using the consumed final set. Continued experimentation needs a new untouched final set.

## Record and Stop

Version manifests, diffs, results, per-edit prediction verdicts, accepted and rejected edits, parentage, and restore points. Preserve the best known harness and distinguish experimental checkpoints from final-validated versions. Store hidden/final evidence with the gate, not in proposer-readable artifacts.

Without an objective verifier and hidden gate set, do not promote. Stop when evidence, improvement, budget, fresh capability data, fixed controls, or authority runs out.

Measurement, permission, security, deployment, spending, destructive, and self-approval changes require independent human governance; never auto-promote them.

## Anti-patterns

- Treating aggregate improvement as proof that each edit's predicted repair occurred.
- Accepting a split regression as noise, changing controls mid-comparison, or exposing hidden task evidence to the proposer.
- Reusing the final set to tune candidates, or presenting the local safeguards as requirements of both original papers.
