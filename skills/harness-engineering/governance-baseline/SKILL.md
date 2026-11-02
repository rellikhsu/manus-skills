---
name: governance-baseline
description: Audit what an agent can do unchecked (merge, deploy, spend, secrets, destructive commands) and add the smallest guardrail. Use before granting more autonomy or when asked for guardrails.
metadata:
  short-description: "Audit unchecked agent actions and add the smallest permission, audit, or human-approval boundary for the highest risk."
---

# Governance Baseline

An agent's authority is limited by what stops it, not by how well it reasons.
Whatever it can do with no mechanical check or human gate, it eventually will.

Name both the enforcement point and who can change or bypass it. Local hooks,
typechecks, and wrappers only guard the execution path they manage. They are not an
authority boundary while the agent still has unrestricted shell/Git or config access.
An integration gate protects its target only if the agent cannot change or bypass
its policy. A sandbox or independent approval must sit outside the controls the
agent can edit.

## Step 1 — Inventory unchecked authority

Fill in this table from evidence, not assumptions.

| Capability | Can the agent do this today with no mechanical check or human approval? | Blast radius if wrong |
|---|---|---|
| Shell / file writes outside the repo | | |
| Network calls to arbitrary hosts | | |
| Secrets / credentials in scope (env, vault, `.env`) | | |
| Merge / push / deploy | | |
| Destructive commands (`rm -rf`, `DROP TABLE`, force-push, `reset --hard`) | | |
| Spend (API cost, cloud resources, third-party billing) | | |
| Unattended/scheduled runs (cron or host scheduler) with no session cap | | |

Checks to run:
- Read CI/CD config and branch protection. Does anything actually block an
  agent-authored push to `main`, or is it only a convention?
- `grep -rn` for how secrets reach the agent's environment. Are they env vars the
  model can see, or fetched at execution time and never shown in context?
- Check whether the agent's shell/tool access is limited (sandboxed, allow-listed) or
  effectively unrestricted.

## Step 2

Match the response to what the project really exposes.

| Situation | Response |
|---|---|
| Agent can merge or deploy | Gate destructive/irreversible actions specifically; leave everything else alone. |
| Agent's environment can reach secrets/credentials | Vault + placeholder pattern — the agent invokes named actions, never sees raw values. |
| Agent runs unattended (cron or host scheduler) | Session/spend cap plus a structured audit trail — the two questions unattended runs raise are "how far could this go" and "what did it actually do". |

## Step 3 — Propose the smallest mechanism

Stop at the first one that actually closes the gap:

1. **Static permission boundary.** An allow-list of paths/commands/network hosts, or a
   sandbox with limited filesystem/network access. Easy to inspect, but cannot
   express task-specific intent.
2. **Human approval hook.** Name
   the class (destructive commands).
   Gate rarely, and only when stakes are real.
3. **Structured audit trail.** One JSONL line per governed action: which tool, which
   args, which risk class, which result.
4. **Declarative policy file (YAML).** Non-developers
   (security, compliance) can review and diff a YAML file: pipeline mode, allowed/denied tool patterns, a
   token budget, an audit destination.

Present as:

> **Gap:** the agent can force-push and nothing blocks it.
> **Mechanism:** host-side branch protection on `main`, administered separately from the agent's credentials, with no bypass available to that agent.
> **Then true:** the agent cannot force-update that protected ref. Any exception requires independently authorized policy change; a local hook is only additional feedback.

Get approval before implementing. This changes what the agent (and maybe the
human) can do; do not ship it silently.

## Step 4 — Implement, then prove the gate holds

Implement only what was approved. In a safe fixture, show one allowed action and
one denied/escalated action. Also check any other entry point the agent still
has. Report the scope you tested and the bypasses that remain. Do not claim
production protection from a local fixture alone.

Record the verified boundary in the project's existing agent entry point
(`AGENTS.md`, `CLAUDE.md`, or its real equivalent): protected action, enforcing
mechanism, configuration owner, and approved escalation path.

Hand off checkable code and dependency rules to `invariant-linter`.
Keep permission, credential, and approval enforcement in the host's real governance
mechanism.

If tamper resistance is required, store the audit log where the agent cannot change it.

## Anti-patterns

- Treating a log as a gate.
