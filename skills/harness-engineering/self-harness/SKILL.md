---
name: self-harness
description: Use when an agent is explicitly authorized to improve its own harness from repeated, verifier-grounded execution failures while the model and evaluation controls can remain fixed.
---

# Self-Harness

Evolve only declared harness surfaces through controlled, reversible experiments. Invocation grants no new authority.

## Discover

Rebuild a capability manifest from the actual environment: skills, tools, middleware, subagents, memory, hooks, and runtime limits. Record canonical source, content hash, availability probe, dependencies, triggers, boundaries, overlaps, and whether each surface is observed or explicitly editable.

Invalidate derived index entries when a source hash or runtime binding changes. A catalog is not proof of availability. Reuse an existing responsibility before adding another capability.

## Freeze

Snapshot the parent harness. Keep the model, inference settings, evaluator, verifier, task splits, budgets, timeouts, runtime, sandbox, and non-editable surfaces fixed. Control drift starts a new lineage; it cannot support comparison with earlier rounds.

## Evolve

1. Run repeated baselines and retain raw traces. Cluster failures by terminal verifier cause, causal agent behavior, and reusable mechanism. Exclude anecdotes, unstable infrastructure, task-specific shortcuts, and capability limits.
2. Propose materially distinct, minimal edits. Each targets one mechanism through the narrowest authorized surface and records evidence, expected effect, regression risk, and interaction risk.
3. Evaluate each candidate independently on held-in and hidden gate sets, repeating stochastic trials. Qualify it only when at least one set improves and neither regresses beyond predefined noise tolerance.
4. Combine only qualified edits, rerun the full regression suite, then evaluate once on an untouched final set. Roll back every failed edit or combination.

## Record and Stop

Version manifests, diffs, results, accepted and rejected edits, parentage, and restore points. Preserve the best known harness.

Without an objective verifier and hidden gate set, do not promote. Stop when evidence, improvement, budget, fresh capability data, fixed controls, or authority runs out.

Measurement, permission, security, deployment, spending, destructive, and self-approval changes require independent human governance; never auto-promote them.
