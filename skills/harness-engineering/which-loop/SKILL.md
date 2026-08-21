---
name: which-loop
description: Use when composing a non-trivial task harness, especially when several available skills match or the user asks how installed skills fit the workflow.
---

# Which Loop

Compose a task-specific harness from the current runtime catalog. Never assume a plugin, skill, or cached index exists.

1. Discover host-visible skills available this session. Inspect current name, description, exposed source/path, and boundaries. Read full instructions only for candidates. If freshness is unknown, say so and discard prior routing.
2. Map capabilities:
   - Observe — repository context and runtime signals
   - Plan — decisions and durable state
   - Execute — implementation or task procedure
   - Verify — tests, review, debugging, evaluation
   - Govern — permissions, approvals, audit
   - Evolve — maintenance, retuning, harness improvement
3. Select the smallest compatible composition. Skills may fill multiple phases; phases may need none. Chain only when one output fits the next input.
4. Return `phase → skill → reason`. For gaps, use the host's native workflow or report a capability gap. Never invent or require a skill merely to fill the map.

Harness-engineering defines ground-layer constraints; other available skills are adapters, not dependencies. Recompose whenever the runtime catalog or source identity changes.
