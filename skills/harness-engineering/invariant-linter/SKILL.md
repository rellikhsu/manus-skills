---
name: invariant-linter
description: Promote prose rules in CLAUDE.md/AGENTS.md into mechanically enforced lints, structural tests, or CI checks. Use when the user says "turn this rule into a lint", "enforce this convention mechanically", "stop agents from violating this pattern", "convert a CLAUDE.md rule into a CI check", "add an architecture/dependency-direction test", "why do agents keep ignoring this rule", or when reviewing instruction files that contain objectively checkable rules (naming conventions, forbidden APIs, layering rules, file size limits, boundary validation, structured logging).
metadata:
  short-description: "Turn objectively checkable prose rules into mechanical lints, structural tests, or CI checks."
---

# Invariant Linter

Convert checkable instruction-file rules into executable feedback, and write the
error message so it teaches the fix inline. A failing check only guards paths
where it runs; it does not itself remove permissions or prevent bypass.

Guiding principle: **enforce boundaries centrally, allow autonomy locally.** Enforce
*that* data is validated at the boundary; do not dictate *which* library does it.

## Step 1 — Collect candidate rules

Read, in this order:

1. `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `CONTRIBUTING.md`, `docs/` conventions,
   nested per-directory `CLAUDE.md` files.
2. If git is available, mine for rules that are *repeatedly violated in practice*:
   - `git log --oneline -300 --grep='fix\|revert\|lint\|convention' -i`
   - `git log -200 --format='%s%n%b' | grep -i 'as discussed\|please use\|should not'`
   - Files with high churn from repeated fix-ups — those are enforcement gaps.
3. Note the stack (package.json / pyproject.toml / go.mod) and existing tooling
   (ESLint, Biome, ruff, mypy, pre-commit, CI workflows). The mechanism must fit
   what already exists.

## Step 2 — Triage: invariant vs. preference

Classify every candidate. Only promote invariants.

**Invariant — mechanically enforce** (violation causes real breakage or erosion):
- Dependency direction / layering (`Types → Config → Repo → Service → Runtime → UI`)
- Data validation at trust boundaries (HTTP, queue, env, file, third-party responses)
- Structured logging only; no bare `console.log` / `print` in production paths
- Security patterns: no secrets in source, no raw SQL interpolation, authz through
  one interface
- Escape hatches: no `any`, no `@ts-ignore`, no `eval`, no `# type: ignore`
- Shared-utility preference over hand-rolled helpers (invariants stay centralized)
- Hard limits: file size, function count per file, public export surface

**Preference — leave to agent discretion** (do NOT lint):
- Which validation library (Zod vs. valibot vs. dataclasses)
- Naming beyond an enforced schema/type suffix convention
- Formatting a formatter already handles
- Function ordering, comment style, test structure
- Anything where two reasonable choices are both fine

If you cannot state a failure that a violation causes, it is a preference. Drop it.

## Step 3 — Choose the minimal viable mechanism

Pick the cheapest thing that actually fails a build. In ascending order of cost:

| Situation | Mechanism |
|---|---|
| No tooling at all | `scripts/check-invariants.sh` (grep/ripgrep) wired into a pre-commit hook + one CI step |
| ESLint/Biome present | `no-restricted-imports`, `no-restricted-syntax`, `no-restricted-globals` first; a custom rule only if selectors cannot express it |
| Python | ruff `flake8-tidy-imports` banned-api / custom `ast`-walking test under `tests/test_architecture.py` |
| Layering rules | Structural test that parses imports and asserts the allowed edge set |
| Type-level rules | Existing tsconfig strictness / mypy settings; account for migration cost and allowed exceptions |

Rules:
- Prefer configuring an existing linter over writing a new one.
- Never introduce a new framework when a 20-line script suffices.
- Every check must run in CI *and* be runnable locally with one documented command.
- Prove the supported boundary with an allowed fixture that passes and a violating
  fixture that fails; run the normal project checks too. Document what the check
  cannot detect. Syntax matching is not proof of all runtime validation.
- A required CI gate only blocks integration if the agent cannot alter or bypass
  that gate. Route authority or permission gaps to `governance-baseline` instead
  of claiming a local check is a security boundary.
- Provide an explicit, greppable escape hatch so legitimate exceptions are visible
  rather than silently disabling the rule. Use the mechanism's own native one where it
  exists — ESLint `// eslint-disable-next-line <rule> -- <reason>`, ruff `# noqa: <code>`
  — and a custom marker (`// invariant-ok: <reason>`) only for grep/AST checks you wrote
  yourself. A custom marker in an ESLint message is a lie: ESLint will not honor it.

## Step 4 — Write the error message as remediation

This is the highest-leverage part. The agent that trips the check should be able to
fix it from the message alone, with no doc lookup.

Every message must contain: **what broke → why it matters → the concrete fix → the
escape hatch.**

Bad:

```
error: invalid import (layer-check)
```

Good:

```
[layering] src/ui/CartView.tsx imports src/repo/orderRepo.ts

  Allowed edges: Types -> Config -> Repo -> Service -> Runtime -> UI.
  UI may not reach into Repo directly; it skips the Service layer where
  authorization and cache invalidation live.

  Fix: add or reuse a function in src/service/orderService.ts that wraps the
  repo call, then import that from the UI.
      - import { getOrder } from '@/repo/orderRepo'
      + import { getOrder } from '@/service/orderService'

  Intentional exception? Add `// invariant-ok: <reason>` above the import and
  note it in docs/architecture.md.
```

## Step 5 — Concrete conversions

### Example A — "Always validate external data at the boundary"

Prose in CLAUDE.md: *"Don't probe request data YOLO-style; validate at the boundary."*

ESLint (`eslint.config.js`), library-agnostic — bans the unsafe access, not the tool:

```js
{
  files: ['src/api/**/*.ts'],
  rules: {
    'no-restricted-syntax': [
      'error',
      {
        // Flags `req.body` etc. everywhere EXCEPT as the direct operand of a
        // parse/safeParse/validate call, which is the validation itself.
        selector:
          "MemberExpression[computed=false][object.name='req'][property.name=/^(body|query|params)$/]" +
          ":not(CallExpression[callee.property.name=/^(parse|safeParse|validate)$/] > MemberExpression)",
        message: [
          '[boundary-validation] Raw access to req.body/query/params.',
          '',
          'Unvalidated request data reaches the service layer and fails deep in the',
          'stack with an unactionable error. Parse the shape here instead.',
          '',
          'Fix: define a schema next to the handler and parse once at the top:',
          '  const CreateOrderInput = z.object({ sku: z.string(), qty: z.number().int().positive() });',
          '  const input = CreateOrderInput.parse(req.body);',
          '',
          'Any parser is fine (zod, valibot, hand-written type guard) as long as the',
          'handler body only sees a typed value.',
          '',
          'Intentional exception? // eslint-disable-next-line no-restricted-syntax -- <reason>',
        ].join('\n'),
      },
    ],
  },
}
```

Then delete the prose rule from CLAUDE.md and replace with one line:
`Boundary validation is enforced by the boundary-validation lint; see its error message.`

### Example B — "Use structured logging" (Python, no linter infra)

`tests/test_invariants.py` — a structural test, zero new tooling:

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

### Example C — "Don't hand-roll helpers that already exist in our utils package"

`scripts/check-invariants.sh` — minimal viable, for repos with no linter:

```bash
#!/usr/bin/env bash
set -euo pipefail
fail=0

command -v rg >/dev/null || { echo "check-invariants: ripgrep (rg) is required"; exit 2; }

# Hand-rolled date formatting instead of @acme/utils formatDate.
# --glob excludes FILES; the per-line escape hatch must be filtered with grep -v.
hits=$(rg -n --glob '!packages/utils/**' \
      'toISOString\(\)\.split|new Intl\.DateTimeFormat' src packages \
      | grep -v 'invariant-ok' || true)

if [ -n "$hits" ]; then
  cat <<EOF
[shared-utils] Hand-rolled date formatting:
$hits

Local date helpers drift: timezone and locale handling then differ per call site.
Fix: import { formatDate } from '@acme/utils/date' and delete the local helper.
If @acme/utils lacks the variant you need, ADD it there rather than inlining here.
Escape hatch: append  // invariant-ok: <reason>  to the line.
EOF
  fail=1
fi

exit $fail
```

Wire it up: add to `.pre-commit-config.yaml` (or `.husky/pre-commit`) and as a CI step.

## Step 6 — Trim the prose

For every rule now enforced mechanically:

1. Delete the paragraph from `CLAUDE.md` / `AGENTS.md`.
2. Optionally leave a single pointer line naming the check and how to run it
   (`npm run lint:invariants`), never a restatement of the rule itself.
3. Keep prose only for rules that remain judgment calls.

A rule that lives in both places is worse than one: agents burn context re-reading
what CI already guarantees, and the two copies drift.

## Step 7 — Report

Deliver a table, then the diffs:

| Prose rule | Verdict | Mechanism | CLAUDE.md action |
|---|---|---|---|
| Validate at boundary | invariant | ESLint `no-restricted-syntax` | remove, link to lint |
| Prefer named exports | preference | none | keep as prose (or drop) |

Then: the actual config/test/script files, the exact command to run them locally, the
CI wiring, and the proposed CLAUDE.md deletion diff. Run the new checks against the
existing codebase before proposing them — report the current violation count and, if
it is large, recommend a baseline/allowlist file so the check can land at zero and
ratchet down, rather than being disabled on day one.

## Anti-patterns

- Promoting a rule to a lint because it's easy to check, not because it's an invariant.
  If Step 2 can't name the concrete breakage, it's a preference — linting it anyway turns
  the checker into a style cop and erodes trust in the real invariants.
- Shipping an error message that only says something failed. Step 4 is the highest-leverage
  step; `error: invalid import` sends the agent back to prose it can't find, defeating the
  reason to convert the rule to a check in the first place.
- Adding a rule with no escape hatch, or an escape hatch the tool doesn't recognize. No
  documented exception path means the first legitimate exception gets the whole rule
  disabled; a custom `// invariant-ok:` marker inside an ESLint message is a lie — ESLint
  will not honor it, only a grep/AST check you wrote yourself can.
- Hand-writing an AST walker when the existing linter already has the primitive. Reach for
  ESLint's `no-restricted-imports`/`no-restricted-syntax` or ruff's banned-api first; a new
  framework is only justified when selectors genuinely cannot express the rule.
- Wiring a new check straight into CI against an unbaselined codebase. Landing hot on day
  one either blocks every unrelated PR with pre-existing violations or gets `--no-verify`d
  and disabled within a week — report the violation count and offer a baseline/allowlist so
  it lands at zero and ratchets down.
- Leaving the prose rule in CLAUDE.md after the check ships. A rule enforced in two places
  drifts: the check evolves with the code, the prose doesn't, and agents end up trusting
  the stale copy.
