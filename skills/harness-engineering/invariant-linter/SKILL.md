---
name: "harness-engineering:invariant-linter"
description: Turn checkable rules in CLAUDE.md/AGENTS.md into lints, structural tests, or CI checks whose errors explain the fix. Use when agents keep breaking a rule or a convention needs enforcing.
metadata:
  short-description: "Turn objectively checkable prose rules into mechanical lints, structural tests, or CI checks."
---

# Invariant Linter

Turn checkable rules from instruction files into checks, and make each error
message explain the fix.

Guiding principle: **enforce boundaries centrally, allow autonomy locally.**

## Step 1 — Collect candidate rules

Read in this order:

1. Root/nested `CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, `.cursorrules`, `CONTRIBUTING.md`, and `docs/` conventions.
2. If git is available, look for rules that people *break again and again*.
3. Note the stack and the existing tools
   (ESLint, Biome, ruff, mypy, pre-commit, CI workflows).

## Step 2 — Sort: invariant or preference

Classify every candidate. Only turn invariants into checks.

**Invariant — enforce with a check** (breaking it causes real damage or slow decay):
- Domain layering (OpenAI's example: `Types → Config → Repo → Service → Runtime → UI`)
- Cross-cutting concerns (auth, connectors, telemetry, feature flags) enter only
  through one explicit interface — OpenAI's "Providers"
- Data validation at trust boundaries (HTTP, queue, env, file, third-party responses)
- Structured logging only; no bare `console.log` / `print` in production paths
- Security patterns: no secrets in source
- Use shared utilities, not hand-written helpers
- Hard limits: file size

**Preference — let the agent decide** (do NOT lint):
- Which validation library (Zod vs. valibot vs. dataclasses)
- Naming, beyond an enforced schema/type convention
- Formatting that a formatter already handles
- Function order, comment style
- Anything where two reasonable choices are both fine

If you cannot name the failure a violation causes, it is a preference. Drop it.

## Step 3 — Choose the smallest check that works

Pick the cheapest thing that actually fails a build.

| Situation | Mechanism |
|---|---|
| No tooling at all | `scripts/check-invariants.sh` (grep/ripgrep) run from a pre-commit hook + one CI step |
| ESLint present | `no-restricted-imports`, `no-restricted-syntax`, `no-restricted-globals` first; a custom rule only if selectors cannot express it |
| Python | ruff `flake8-tidy-imports` banned-api / custom `ast`-walking test under `tests/test_architecture.py` |
| Layering rules | Structural test that parses imports and checks them against the allowed edges |
| Type-level rules | Existing tsconfig strictness / mypy settings; consider migration cost and allowed exceptions |

Rules:
- Prefer configuring an existing linter over writing a new one.
- Every check must run in CI *and* run locally with one documented command.
- Prove the boundary with an allowed fixture that passes and a violating fixture
  that fails. Run the normal project checks too. Matching syntax does not prove that all runtime validation happens.
- A required CI gate blocks integration only if the agent cannot change or bypass
  it. Send authority or permission gaps to `governance-baseline`. Do not claim a
  local check is a security boundary.

## Step 4 — Write the error message as the fix

The agent that fails the check should be able to fix it
from the message alone, without reading docs.

Every message must contain: **what broke → why it matters → the concrete fix.**

```
[layering] src/ui/CartView.tsx imports src/repo/orderRepo.ts

  Allowed edges: Types -> Config -> Repo -> Service -> Runtime -> UI.
  UI may not reach into Repo directly; it skips the Service layer where
  authorization and cache invalidation live.

  Fix: add or reuse a function in src/service/orderService.ts that wraps the
  repo call, then import that from the UI.
      - import { getOrder } from '@/repo/orderRepo'
      + import { getOrder } from '@/service/orderService'
```

## Step 5 — Concrete conversions

### Example A — "Always validate external data at the boundary"

One option is to put request decoding in `src/api/boundary/`. Handlers call
those adapters and use the validated values they return. Adapt the path and
request name to the project.

Add this entry to the project's existing ESLint flat config:

```js
{
  files: ['src/api/**/*.ts'],
  ignores: ['src/api/boundary/**'],
  rules: {
    'no-restricted-syntax': [
      'error',
      {
        selector:
          "MemberExpression[object.name='req'][computed=false][property.name=/^(body|query|params)$/], " +
          "MemberExpression[object.name='req'][computed=true][property.value=/^(body|query|params)$/]",
        message: [
          '[boundary-validation] Direct raw request access outside the boundary adapter.',
          'Keep decoding in src/api/boundary/ so handlers consume validated values.',
          'Fix: call an adapter such as readCreateOrder(req), validate inside it,',
          'and return the checked value. Any validator library or custom guard can be used there.',
        ].join('\n'),
      },
    ],
  },
}
```

The adapter must
really validate, reject bad input, and return a checked value; test that at
runtime.

**Scope:** the rule does not track aliases, destructuring, or dynamic keys.

Verify: raw
handler reads fail; adapter calls pass. Keep these
fixtures in the target project's tests.

### Example B — "Use structured logging" (Python, no linter infra)

`tests/test_invariants.py` — a structural test with no new tools:

```python
import ast, pathlib

SRC = pathlib.Path(__file__).parent.parent / "src"
EXEMPT = {"cli/entrypoint.py"}  # paths relative to SRC, posix-style

def _print_calls(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
            yield node.lineno

def test_no_bare_print_in_src():
    hits = [
        f"{p}:{ln}" for p in sorted(SRC.rglob("*.py"))
        if p.relative_to(SRC).as_posix() not in EXEMPT
        for ln in _print_calls(p)
    ]
    assert not hits, (
        "[structured-logging] bare print() found:\n  "
        + "\n  ".join(hits)
        + "\n\nprint() output is unstructured, so it is invisible to log search and"
        "\nalerting in production."
        "\n\nFix: use the shared logger with key/value context:"
        "\n  from app.logging import get_logger"
        "\n  log = get_logger(__name__)"
        "\n  log.info('order_created', order_id=order.id, sku=sku)"
        "\n\nUser-facing CLI output is exempt: add the file to EXEMPT in this test."
    )
```

## Step 6 — Report

Give a table, then the diffs:

| Prose rule | Verdict | Mechanism |
|---|---|---|
| Validate at boundary | invariant | ESLint `no-restricted-syntax` |
| Prefer named exports | preference | none |

Then give: the config/test/script files, the exact local command, the CI wiring. Run the new checks on the existing
codebase first and report the current violation count. If it is large, recommend a
baseline/allowlist file so the check starts at zero and the count only goes down,
instead of being disabled on day one.

## Anti-patterns

- Making a rule a lint because it is easy to check, not because it is an invariant.
