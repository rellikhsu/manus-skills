---
name: "harness-engineering:observability-bridge"
description: Let the agent query logs, UI, metrics, or a running app itself instead of asking a human. Use when debugging goes in circles, the agent asks you to check or paste output, or logs are noise.
metadata:
  short-description: "Make human-only logs, metrics, browser state, or runtime signals directly queryable by the agent."
---

# Observability Bridge

## Step 1 — Audit the feedback surface

Inspect the project and fill in this table.

| Surface | Question | Human-only / Agent-queryable |
|---|---|---|
| Logs | Structured (JSON, key=value) or free-text `print`/`console.log`? Can the agent get the logs of one specific run without a paste? |  |
| App runtime | Can the agent start the app itself (one command, no manual setup, no port clash with the human's instance) and send requests to it? |  |
| UI | Is a browser automation MCP connected (Chrome, Playwright, or the host equivalent)? Can the agent take screenshots, click, read the DOM, and read console + network? |  |
| Metrics/traces | Can anything be queried locally, or only a hosted dashboard behind a human login? |  |

Checks to run:
- `rg --stats 'console\.log|print\('` (number of ad-hoc prints) versus whether a logger exists.
- Look for `dev`/`start` scripts, `docker-compose.yml`, `Procfile`, `.env.example`. Is startup one command, or a ritual only some people know?
- List the MCP/browser tools available.
- Check whether logs go to a file/stdout the agent can `grep`, or only to a terminal the human sees.

## Step 2 — Name the one gap with the biggest payoff

Rank gaps by how often each one now forces a round-trip to a human.

Match the fix to the project's size (local rule).

- Small script / CLI → structured JSON lines to stdout + a `jq` one-liner.
- Web app with no browser tooling connected → connect the existing browser MCP.
- App the agent cannot start → make it start on its own (configurable port, seeded DB, one command), ideally one instance per git worktree (OpenAI).
- Service with real traffic and latency SLOs → only then, local Loki/Prometheus/traces.

## Step 3 — Propose in terms of questions the agent can now answer

Sell the questions that become answerable.
Write each proposal like this:

> **Gap:** verifying the login flow requires you to open the browser and describe what you see.
> **Bridge:** wire the connected Chrome MCP into the debug loop (no new deps).
> **Then tractable:** "confirm the login flow throws no console error and lands on /dashboard" — answered by the agent, with a screenshot and the console dump as evidence.

Present the smallest bridge that works. Get approval before you build it.

## Step 4 — Build the bridge, then prove it works

Build only what was approved. Then, in the same session, run the new capability
once and show the output.

Finish by writing down the new capability where the agent will see it next time.
Add a short line to `CLAUDE.md` (e.g. "logs: JSON lines to `./run.log`, filter with
`jq 'select(.level==\"error\")'`"; "app boots with `PORT=3100 npm run dev`;
drive it with the Chrome MCP").

## Anti-patterns

- Asking the human to check the browser when a browser MCP is already connected.
