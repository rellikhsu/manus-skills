---
name: "harness-engineering:observability-bridge"
description: Audit what the agent can actually query in this project versus what only a human can see, then build the smallest bridge that closes the gap. Use when debugging is going in circles because the agent is guessing instead of checking, when the agent says "I can't verify this myself" or "can you check the browser / paste the logs", when logs are unstructured print/console.log noise, when a UI change needs visual or console verification, when someone asks to make logs queryable, wire up browser automation through the host's browser MCP for debugging, make the app bootable so the agent can drive it, or expose metrics/traces to the agent.
metadata:
  short-description: "Make human-only logs, metrics, browser state, or runtime signals directly queryable by the agent."
---

# Observability Bridge

An agent's judgment is capped by what it can query, not by how well it reasons.
Anything it cannot access in-context while running effectively does not exist for it.
This skill finds the one blind spot blocking work right now and removes it.

Scope discipline: you are not standing up an observability platform. You are
converting one "a human has to look and describe it" step into one
"the agent checks it itself" step.

## Step 1 — Audit the feedback surface

Inspect the project and fill in this table. Answer from evidence (files, scripts,
configs, MCP tools actually available), not assumption.

| Surface | Question | Human-only / Agent-queryable |
|---|---|---|
| Logs | Structured (JSON, key=value) or free-text `print`/`console.log`? Can the agent get the logs of one specific run without a paste? |  |
| App runtime | Can the agent boot the app itself (one command, no manual setup, no port collision with the human's instance) and hit it? |  |
| UI | Is a browser automation MCP connected (Chrome, Playwright, or the host equivalent)? Can the agent screenshot, click, read the DOM, read console + network? |  |
| Metrics/traces | Anything queryable locally, or only a hosted dashboard behind a human login? |  |
| Tests | Does a failing test print enough to localize the fault, or just `AssertionError: False is not True`? |  |

Concrete checks to run:
- `rg --stats 'console\.log|print\('` (count of ad-hoc prints) versus presence of a logger (`pino`, `winston`, `structlog`, `zap`, `slog`).
- Look for `dev`/`start` scripts, `docker-compose.yml`, `Procfile`, `.env.example` — is booting one command or a tribal ritual?
- List available MCP/browser tools; if Chrome, Playwright, or an equivalent browser tool exists and the project has a UI, that is a free capability that is probably unused.
- Check whether logs go to a file/stdout the agent can `grep`, or only to a TTY the human sees.

## Step 2 — Name the single highest-leverage gap

Rank gaps by: how often does this blind spot currently force a human round-trip?

Match the fix to project scale. Do **not** propose LogQL/PromQL/OTel/ephemeral
per-worktree stacks unless the project already runs at that scale.

- Small script / CLI → structured JSON lines to stdout + a `jq` one-liner.
- Web app, no browser tooling wired → wire the existing browser MCP. Zero infra.
- App the agent can't start → make it independently bootable (configurable port, seeded DB, one command).
- Service with real traffic and latency SLOs → then, and only then, local Loki/Prometheus/traces.

State the gap in one sentence: *"Right now, verifying X requires a human to look at Y."*

## Step 3 — Propose in terms of newly tractable prompts

Never pitch infrastructure. Pitch the questions that become answerable.
Format each proposal as:

> **Gap:** verifying the login flow requires you to open the browser and describe what you see.
> **Bridge:** wire the connected Chrome MCP into the debug loop (no new deps).
> **Then tractable:** "confirm the login flow throws no console error and lands on /dashboard" — answered by the agent, with a screenshot and the console dump as evidence.

> **Gap:** request failures are `console.log("error", err)` scattered across 40 files.
> **Bridge:** one `log()` helper emitting JSON lines to stderr, adopted on the error paths only.
> **Then tractable:** "which endpoint produced 5xx during that run, and with what payload" — `jq 'select(.level=="error")' run.log`.

Present the smallest viable bridge and the effort in minutes. Get approval before implementing.

## Step 4 — Implement the bridge, then prove it

Implement only what was approved. Then, in the same session, actually run the
new capability once and show the output. An unused bridge is not a bridge.

Finish by recording the new capability where the agent will see it next time:
add a short line to `CLAUDE.md` (e.g. "logs: JSON lines to `./run.log`, filter with
`jq 'select(.level==\"error\")'`"; "app boots with `PORT=3100 npm run dev`;
drive it with the Chrome MCP"). If the capability is not documented in-context,
the next session will not know it exists — and the blind spot returns.

## Worked example

**Project:** small Python FastAPI service. Debugging an intermittent 500 has taken
three rounds of "can you paste the traceback?"

**Audit:** logging is `print(f"failed for user {uid}: {e}")` in 12 places, output only
to the terminal the human runs. App boots with `uvicorn app:app` but hardcodes port 8000,
which the human's instance already holds. No browser tooling needed (JSON API).

**Highest-leverage gap:** the agent cannot obtain the logs of a run it triggered itself.

**Bridge (about 15 minutes):**
1. Add `structlog` (or stdlib `logging` with a JSON formatter); replace the 12 `print`s with
   `log.error("request_failed", user_id=uid, path=path, exc_info=True)`.
2. Emit JSON lines to `./run.log` in dev.
3. Read the port from `PORT` so the agent can boot on 8100 alongside the human.

**Now tractable, verified live in-session:**
```bash
uvicorn app:app --port 8100 > run.log 2>&1 &
curl -s localhost:8100/checkout -d @fixture.json
jq -c 'select(.level=="error") | {path, user_id, event}' run.log
```
Prompts that now get a real answer: *"reproduce the 500 and tell me which user_id and
path trigger it"*, *"confirm no error-level log appears after the fix"*.

**Recorded in CLAUDE.md:** boot command, log location, the `jq` filter.

## Anti-patterns

- Proposing a full observability stack for a 500-line project.
- Adding instrumentation that nothing in the current task will read.
- Building the bridge and never running it.
- Leaving the new capability undocumented, so the next session goes back to guessing.
- Asking the human to check the browser when a browser MCP is already connected.
