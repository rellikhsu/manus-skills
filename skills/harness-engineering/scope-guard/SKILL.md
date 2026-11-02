---
name: scope-guard
description: Use before fixing a bug or failing test, when a fix spreads into tests, helpers or other modules, or when a scope-guard hook fires. Keeps the agent on task.
---

# Scope Guard

Source: OpenAI's [harness-engineering article](https://openai.com/index/harness-engineering/): when the agent fails, the fix is almost never "try harder"; ask "what capability is missing".

## 1. Write the contract

Before the first edit, write `.scope/contract.md` and add `.scope/` to `.git/info/exclude`:

```
Goal:      the behavior of A that must change, one line
Target:    tests that must go from fail to pass
Guard:     tests that must keep passing
Baseline:  tests already failing before you start (not yours)
Write:     src/a/* tests/test_a.py
Read-only: tests/helpers/* tests/conftest.py ci/*
Log:       docs/exec-plans/tech-debt-tracker.md
Base:      <output of git rev-parse HEAD>
Done:      Target passes; Guard gains no failure; the diff stays inside Write
```

The hooks read `Goal`, `Write`, `Read-only`, `Log` and `Base` (globs are relative to the project root; `*` also matches `/`). Use the user's acceptance criteria when they gave any. Once written, the contract is read-only: to widen scope, stop and ask the user.

## 2. Baseline first

Run Target and Guard before changing anything; record what already fails. If regressions outnumber fixes, diagnose before adding changes.

## 3. Depth ladder

- L0, A itself: `Write`.
- L1, A's direct tests: edit only when the contract says the behavior is meant to change; otherwise they are Guard.
- L2, test helpers, fixtures, mocks, conftest: `Read-only`. They check the work. A failure here is not A's problem: record it.
- L3 and below, helper tests, test infrastructure, CI: out of scope. Record it in `Log` and return to A.

Put exploratory files outside the deliverable, in a scratch path. Paths outside the project root are never blocked.

## 4. When a hook fires

- **Write blocked:** do not route around the block with Bash.
- **Same error twice:** do not retry harder. Ask what capability is missing (a tool, a doc, a check, a permission) and add it, or record the problem and return to the goal.

## 5. Finish

The diff stays inside `Write` and `Log`; no Guard or `Read-only` file changed; no new failure against Baseline; Target passes. Then delete `.scope/`.

## Hooks

- PreToolUse on `Edit|Write|MultiEdit|NotebookEdit`: blocks writes outside `Write`/`Log`, to `Read-only`, or to the contract.
- PostToolUseFailure: on the 2nd, 4th, 8th... identical failure in a session, injects the reminder above; without a contract it asks for one.
- Stop: blocks once when `git diff <Base>` plus untracked files leave `Write`/`Log`.

Bash writes do not fire the PreToolUse file matcher; the Stop check catches them. In Codex, plugin hooks run only after the user trusts them in `/hooks`, and Codex has no PostToolUseFailure event.
