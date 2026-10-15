---
name: mattpocock-skills
description: Matt Pocock's complete engineering and agentic productivity workflow suite. Includes Socratic grilling, spec-driven development (to-spec, to-tickets, implement-spec), deep module codebase design, high-seam TDD, systematic bug diagnosis, code review, PR generation, retrospectives, triage, interactive wizards, and writing engines. Use when planning features, stress-testing designs, breaking specs into dependency-graphed tickets, executing outside-in TDD, restructuring software architecture, or authoring agentic skills.
---

# Matt Pocock Skills: Engineering & Agentic Workflow Suite

A cohesive engineering and productivity operating system for human-agent collaboration, created by Matt Pocock and remixed for Manus and modern autonomous coding agents.

This master skill acts as the **central router and orchestration map** for the 38 bundled workflows. When executing any workflow, follow the principles here and load the matching child `SKILL.md` via Progressive Disclosure.

---

## Core Engineering Philosophy

1. **Deep Modules**: High leverage at small interfaces. Maximize the behavior a caller or test can exercise per unit of interface complexity. Hide deep implementation behind clean seams.
2. **Outside-In TDD with High Seams**: Prefer few, high seams over many brittle mocks. Test behavior at the highest stable boundary.
3. **Spec-Driven Tracer Bullets**: Settle decisions and dependencies before touching code. Synthesize specs without redundant interrogation; break specs into dependency-graphed tickets.
4. **Socratic Grilling**: Map architectural decisions as a branching design tree. Resolve the settled "frontier" in structured rounds before coding.
5. **Progressive Disclosure**: Keep context lean. Only load the specific child workflow required for the active phase.
6. **Environment Retrospectives**: After a build, harden the agent's environment (linters, pre-commit hooks, steering files, test seams) rather than just fixing individual code lines.

---

## The Feature Delivery Lifecycle

The primary spine for taking an idea from raw concept to verified production pull request:

```
┌────────────────────────────────────────────────────────┐
│ 1. Align & Interrogate (grill-with-docs / grilling)    │
│    Explore design tree; document ADR & Glossary        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Synthesize Spec (to-spec)                           │
│    Produce self-contained spec without redundant Q&A  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Deconstruct Work (to-tickets)                       │
│    Generate tracer-bullet tickets with blocking edges  │
└──────────────────────────┬─────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
   [Large / Parallelizable]      [Focused / Single Seam]
┌───────────────────────────┐ ┌───────────────────────────┐
│ 4a. Orchestrate Subagents │ │ 4b. Direct Implementation │
│     (implement-spec)      │ │     (implement + tdd)     │
│     Fan out across graph  │ │     Outside-in red-green  │
└───────────┬───────────────┘ └───────────┬───────────────┘
            └──────────────┬──────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 5. Review & Ship (code-review + pr)                    │
│    Two-axis review (Standards + Spec) & visual PR body │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 6. Environment Retro (retro)                           │
│    Turn human corrections into automated agent checks  │
└────────────────────────────────────────────────────────┘
```

---

## Quick Decision Matrix & On-Ramps

| Task / User Trigger | Recommended Workflow | Child Path |
| :--- | :--- | :--- |
| **Stress-test an idea, decision, or feature** | `grilling` / `grill-with-docs` | `grilling/SKILL.md` |
| **Turn conversation / concept into formal spec** | `to-spec` | `to-spec/SKILL.md` |
| **Break spec/plan into dependency tickets** | `to-tickets` | `to-tickets/SKILL.md` |
| **Execute full ticket graph in parallel** | `implement-spec` | `implement-spec/SKILL.md` |
| **Implement single ticket or feature test-first** | `implement` + `tdd` | `tdd/SKILL.md` |
| **Diagnose hard, flaky, or elusive bugs** | `diagnosing-bugs` | `diagnosing-bugs/SKILL.md` |
| **Review branch/PR on Spec and Standards** | `code-review` | `code-review/SKILL.md` |
| **Compose high-signal Pull Request description** | `pr` | `pr/SKILL.md` |
| **Post-build retro to improve agent environment**| `retro` | `retro/SKILL.md` |
| **Triage incoming raw bugs or requests** | `triage` | `triage/SKILL.md` |
| **Explore throwaway UI or logic prototype** | `prototype` | `prototype/SKILL.md` |
| **Investigate technical docs / primary sources** | `research` | `research/SKILL.md` |
| **Map huge multi-session epic with decisions** | `wayfinder` | `wayfinder/SKILL.md` |
| **Guide human through manual dashboard/keys task**| `wizard` | `wizard/SKILL.md` |
| **Audit codebase architecture & find seams** | `improve-codebase-architecture` | `improve-codebase-architecture/SKILL.md` |
| **Deep module vocabulary & architectural patterns**| `codebase-design` | `codebase-design/SKILL.md` |
| **Domain ubiquitous language & ADR management** | `domain-modeling` | `domain-modeling/SKILL.md` |
| **Enforce TypeScript architectural boundaries** | `setup-ts-deep-modules` | `setup-ts-deep-modules/SKILL.md` |
| **Pre-commit hooks (Husky, lint-staged, tests)** | `setup-pre-commit` | `setup-pre-commit/SKILL.md` |
| **Block dangerous destructive Git commands** | `git-guardrails-claude-code` | `git-guardrails-claude-code/SKILL.md` |
| **Writing: Explore (mine fragments)** | `writing-fragments` | `writing-fragments/SKILL.md` |
| **Writing: Shape (paragraph structure)** | `writing-shape` | `writing-shape/SKILL.md` |
| **Writing: Exploit (beats & cognitive journey)** | `writing-beats` | `writing-beats/SKILL.md` |
| **Authoring skills or agent prompt guidelines** | `writing-for-agents` | `writing-for-agents/SKILL.md` |
| **Interactive tutoring & skill curriculum** | `teach` | `teach/SKILL.md` |

---

## Context Hygiene & Phase Boundaries

Follow these rules (distilled from `ask-matt/PHASE-BOUNDARIES.md`):

1. **Keep Phases 1–3 in One Window**: Keep Grilling, Spec Synthesis, and Ticket Decomposition in one unbroken context window whenever possible so the reasoning remains verbatim.
2. **Continue**: If current context is relevant and within the smart zone (~150k tokens), continue in the same session.
3. **Compact**: If context is growing large before implementation, compact with an explicit steering instruction pointing to the target ticket.
4. **Subagent Delegation**: Delegate self-contained, parallelizable execution (such as `implement-spec` or background `research`) to subagents.
5. **Handoff**: Use `handoff` only when transferring work to a different harness, different repo, or human colleague.

---

## Complete Catalog of Bundled Workflows

Every workflow retains its exact upstream identifier and lives in `/home/ubuntu/skills/mattpocock-skills/<workflow>/SKILL.md`:

### 1. Interrogation & Socratic Alignment
- **`grilling`** (`grilling/SKILL.md`): Stress-test thinking one round at a time via a frontier-based decision tree.
- **`grill-me`** (`grill-me/SKILL.md`): Direct entry point to `grilling`.
- **`grill-with-docs`** (`grill-with-docs/SKILL.md`): Grilling coupled with live ADR and Glossary creation.
- **`loop-me`** (`loop-me/SKILL.md`): Grilling tailored specifically for designing workflows within the workspace.
- **`wait-what`** (`wait-what/SKILL.md`): Stop and re-pitch an idea when the previous message failed to land.
- **`to-questionnaire`** (`to-questionnaire/SKILL.md`): Transform open decisions into an async questionnaire for external collaborators.

### 2. Architecture, Modeling & Seams
- **`codebase-design`** (`codebase-design/SKILL.md`): Core vocabulary for deep modules (Interface, Implementation, Seam, Depth, Leverage, Locality). Includes `DEEPENING.md` and `DESIGN-IT-TWICE.md`.
- **`domain-modeling`** (`domain-modeling/SKILL.md`): Domain ubiquitous language; formats for `GLOSSARY-FORMAT.md` and `ADR-FORMAT.md`.
- **`improve-codebase-architecture`** (`improve-codebase-architecture/SKILL.md`): Automated codebase scan identifying deepening opportunities; produces an interactive visual report (`HTML-REPORT.md`).
- **`prototype`** (`prototype/SKILL.md`): Build throwaway prototypes to sanity-check logic (`LOGIC.md`) or UI (`UI.md`) before implementation.
- **`setup-ts-deep-modules`** (`setup-ts-deep-modules/SKILL.md`): Enforce deep module boundaries in TypeScript repos using `dependency-cruiser.config.cjs`.

### 3. Specification & Deconstruction Pipeline
- **`to-spec`** (`to-spec/SKILL.md`): Synthesize context into a clean, test-seam-aware specification without repetitive interrogation.
- **`to-tickets`** (`to-tickets/SKILL.md`): Decompose specs into tracer-bullet tickets with explicit blocking edges.
- **`wayfinder`** (`wayfinder/SKILL.md`): Long-horizon planning for complex epics spanning multiple sessions via an issue-tracker decision map.
- **`triage`** (`triage/SKILL.md`): State machine for triage roles, categorizing raw bugs, verifying reports, and authoring agent-ready briefs (`AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`).

### 4. Implementation & Quality Engineering
- **`implement`** (`implement/SKILL.md`): Direct implementation of a spec or ticket within the current context.
- **`implement-spec`** (`implement-spec/SKILL.md`): Orchestrate parallel subagents across the dependency graph on an integration branch.
- **`tdd`** (`tdd/SKILL.md`): Test-Driven Development with high seams. Includes `mocking.md` and `tests.md`.
- **`diagnosing-bugs`** (`diagnosing-bugs/SKILL.md`): Systematic hypothesis-driven debugging loop. Includes human-in-the-loop harness `scripts/hitl-loop.template.sh`.
- **`code-review`** (`code-review/SKILL.md`): Dual-axis code review evaluating diffs against both Project Standards and Feature Spec.
- **`pr`** (`pr/SKILL.md`): High-signal pull request generation (smallest visual proof, before/after evidence, door-type evaluation). Includes `CREDITS.md`.
- **`retro`** (`retro/SKILL.md`): Retrospective on coding sessions focused on hardening the agent environment and automated checks.
- **`migrate-to-shoehorn`** (`migrate-to-shoehorn/SKILL.md`): Refactor TypeScript tests from unsafe `as` type assertions to `@total-typescript/shoehorn`.

### 5. Agent Tooling, Safety & Governance
- **`ask-matt`** (`ask-matt/SKILL.md`): Master navigational assistant and context hygiene guide. Includes `PHASE-BOUNDARIES.md`.
- **`chief-of-staff`** (`chief-of-staff/SKILL.md`): Executive agent assistant for prioritization and task routing.
- **`handoff`** (`handoff/SKILL.md`): Generic context compaction for inter-agent or inter-session handoffs.
- **`claude-handoff`** (`claude-handoff/SKILL.md`): Claude Code specialized handoff format.
- **`git-guardrails-claude-code`** (`git-guardrails-claude-code/SKILL.md`): Protective hooks blocking destructive git operations (`scripts/block-dangerous-git.sh`).
- **`setup-pre-commit`** (`setup-pre-commit/SKILL.md`): Automated setup for Husky, lint-staged, Prettier, TypeScript checks, and test suites.
- **`setup-matt-pocock-skills`** (`setup-matt-pocock-skills/SKILL.md`): Bootstrap repo issue trackers (GitHub, GitLab, Local), triage labels, and domain doc layout.
- **`wizard`** (`wizard/SKILL.md`): Generator for interactive bash wizards walking humans through manual-only tasks (`template.sh`).

### 6. Writing, Research & Education
- **`writing-fragments`** (`writing-fragments/SKILL.md`): Explore phase: mine raw ideas and fragments without early structuring.
- **`writing-shape`** (`writing-shape/SKILL.md`): Exploit phase: organize material into narrative paragraphs.
- **`writing-beats`** (`writing-beats/SKILL.md`): Sequence beats into a cognitive journey, grounding each concept before leaning on it.
- **`writing-for-agents`** (`writing-for-agents/SKILL.md`): Rules and patterns for authoring agent-facing documents. Includes `SKILL-MECHANICS.md`.
- **`research`** (`research/SKILL.md`): Investigate questions against authoritative primary sources and save findings to repository markdown.
- **`teach`** (`teach/SKILL.md`): Interactive Socratic teaching environment. Includes `GLOSSARY-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`, `MISSION-FORMAT.md`, and `RESOURCES-FORMAT.md`.
- **`scaffold-exercises`** (`scaffold-exercises/SKILL.md`): Scaffold course and workshop exercise directories with solutions and explainers.
