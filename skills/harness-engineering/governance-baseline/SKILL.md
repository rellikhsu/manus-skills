---
name: governance-baseline
description: Audit what an autonomous coding agent can do unchecked in this project — merge, deploy, spend, touch secrets, run destructive commands — then add the smallest permission boundary, audit trail, or human-approval gate that closes the highest-risk gap. Use when an agent is being given broader autonomy (auto-merge, autonomous PR loops, production access, credentials, unattended scheduled runs), when the user asks to "lock down" or "add guardrails" to agent actions, when reviewing what an agent is allowed to do unsupervised, or when an incident review shows an agent took an action nobody explicitly authorized.
metadata:
  short-description: "Audit unchecked agent actions and add the smallest permission, audit, or human-approval boundary for the highest risk."
---

# Governance Baseline

An agent's authority is capped by what stops it, not by how well it reasons. Anything
it can do without a mechanical check or a human gate, it eventually will do — not out
of malice, just because nothing said no. This skill finds the one unchecked capability
with the worst plausible blast radius and closes it.

Scope discipline: you are not building a permission framework, an RBAC system, or a
policy DSL. You are converting one "the agent could do this and nobody would notice
until it mattered" gap into one governed action.

Name both the enforcement point and who can change or bypass it. Local hooks,
typechecks, and wrappers guard their managed execution path; they are not an
authority boundary while the agent retains unrestricted shell/Git or config access.
An integration gate protects its target only when its policy cannot be changed or
bypassed by that agent. A sandbox or independent approval must sit outside the
agent's editable controls. Invoking this skill grants no new authority.

## Step 1 — Inventory unchecked authority

Fill in this table from evidence — actual tool access, actual CI/CD permissions,
actual credentials the agent's environment can reach — not assumption.

| Capability | Can the agent do this today with no mechanical check or human approval? | Blast radius if wrong |
|---|---|---|
| Shell / file writes outside the repo | | |
| Network calls to arbitrary hosts | | |
| Secrets / credentials in scope (env, vault, `.env`) | | |
| Merge / push / deploy | | |
| Destructive commands (`rm -rf`, `DROP TABLE`, force-push, `reset --hard`) | | |
| Spend (API cost, cloud resources, third-party billing) | | |
| Unattended/scheduled runs (cron or host scheduler) with no session cap | | |

Concrete checks to run:
- Read CI/CD config and branch protection — does anything actually block an agent-
  authored push to `main`, or is it convention only?
- `grep -rn` for how secrets reach the agent's environment — injected as env vars the
  model can see, or fetched at execution time and never exposed to context?
- Check whether the agent's shell/tool access is scoped (sandboxed, allow-listed) or
  effectively unrestricted.
- If the agent runs on a schedule (host scheduler or cron agent), check whether it has a
  session/spend cap or can run indefinitely.

## Step 2 — Rank by (likelihood × blast radius), pick ONE

Match the response to what the project actually exposes. Do **not** default to the
heavy version.

| Situation | Response |
|---|---|
| Local dev only, no prod access, no secrets in scope | Likely nothing needed. Say so and stop. |
| Agent can merge or deploy | Gate destructive/irreversible actions specifically; leave everything else alone. |
| Agent's environment can reach secrets/credentials | Vault + placeholder pattern — the agent invokes named actions, never sees raw values. |
| Agent runs unattended (cron or host scheduler) | Session/spend cap plus a structured audit trail — the two questions unattended runs raise are "how far could this go" and "what did it actually do". |
| Numerous, evolving rules that prose can't track | Only then, a declarative policy file (YAML) — see Step 3. |

State the gap in one sentence: *"Right now, nothing stops the agent from doing X."*

## Step 3 — Propose the smallest mechanism

In ascending order of cost — stop at the first one that actually closes the gap:

1. **Static permission boundary.** An allow-list of paths/commands/network hosts, or a
   sandboxed execution environment with restricted filesystem/network access. Easy to
   inspect, cannot express task-specific intent — fine for most projects.
2. **Human-in-the-loop hook on a specific action class.** Not "approve everything" —
   name the class (destructive commands, spend over $X, prod deploy, anything touching
   auth/payments/migrations) and gate only that. Frequent, low-stakes approval prompts
   train reflexive clicking, not scrutiny — a mobile-permissions study found only 17%
   of users even read the prompt and 3% could answer comprehension questions about
   what they'd granted. Gate rarely, on real stakes.
3. **Structured audit trail.** One JSONL line per governed action: what tool, what
   args, what risk class, what result. This is `observability-bridge`'s territory if
   the project doesn't have queryable logs yet — chain to it rather than duplicating.
   A log is not a gate: it tells you what happened, not whether it should have.
4. **Declarative policy file (YAML).** Only once rules are numerous or change often
   enough that prose in `CLAUDE.md` can't stay accurate. Non-developer stakeholders
   (security, compliance) can review and diff a YAML file; they can't safely review
   scattered prose. Keep it small — pipeline mode, allowed/denied tool patterns, a
   token/spend budget, an audit destination. Do not invent a policy DSL from scratch.

Present as:

> **Gap:** the agent can force-push and nothing blocks it.
> **Mechanism:** host-side branch protection on `main`, administered separately from the agent's credentials, with no bypass available to that agent.
> **Then true:** the agent cannot force-update that protected ref. Any exception requires independently authorized policy change; a local hook is only additional feedback.

Get approval before implementing — this changes what the agent (and possibly the
human) can do; do not land it unannounced.

## Step 4 — Implement, then prove the gate holds

Implement only what was approved. In a safe fixture, demonstrate both an allowed
action and a denied/escalated action, and check any alternate entry point the
agent actually retains. Report the tested scope and remaining bypasses; do not
claim a production protection from a local fixture alone.

Record the verified boundary in the project's existing agent entry point
(`AGENTS.md`, `CLAUDE.md`, or its actual equivalent): protected action, enforcing
mechanism, configuration owner, and approved escalation path. An undocumented
gate can look like a bug the next session tries to work around.

Hand off checkable code or dependency rules to `invariant-linter`. Keep permission,
credential, and approval enforcement with the host's actual governance mechanism;
an added lint cannot remove an agent's authority.

## Worked example

**Project:** a repo runs `doc-gardener` on a daily scheduled job with commit access.
No one asked "what's the worst this could do unattended."

**Audit:** the cron agent can commit and open PRs; nothing caps how many commits per
run or blocks it from touching `.github/workflows/`. Doc-gardener's own skill text
already says "never edit CI config" and "cap the whole run at 3 commits" — but that's
prose inside the skill, not an enforced boundary in the repo.

**Highest-leverage gap:** an unattended run with a bug in its own logic could commit
far more than intended before anyone notices, or touch CI config despite the skill
saying not to.

**Smallest proposal depends on actual control:**
1. A local `pre-commit` check and commit-count wrapper can provide early feedback,
   but do not close this authority gap if raw Git/config writes remain available.
2. If the host already supports an independently controlled action gate, validate
   every allowed commit before it happens, deny workflow-file changes, and reject
   the fourth commit before side effects. The agent must not control that gate or
   its counter. If this cannot be enforced, retain human approval for committing.
3. Record one JSONL audit event per attempted governed action. Keep audit storage
   outside agent control if tamper resistance is part of the requirement.

**Verification to perform:** an allowed fixture commit succeeds; a workflow change
and a fourth commit are rejected without creating a commit. Check whether direct
Git/config access still bypasses the mechanism. Record failures as an open gap,
not as a proven boundary.

## Anti-patterns

- Building RBAC, a policy DSL, or a permissions framework for a project with no prod
  access and no secrets in scope.
- Gating everything, so approval prompts become routine and stop getting read.
- A rule that lives only as prose in `CLAUDE.md` with no mechanical backing — that is
  a stated requirement, not a proven boundary. Choose code checks or actual
  permission controls according to what it constrains.
- Calling a local hook or wrapper unbypassable while the agent controls alternate
  commands or the enforcing configuration.
- Treating a log as a gate. Audit trails answer "what happened"; they do not stop
  anything on their own.
- Standing up a full audit platform when one JSONL file and `jq` answers every
  question anyone actually has.
