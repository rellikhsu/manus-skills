# Dist and collection-entry validation

Run the deterministic conversion checks with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The four tests execute the real transformer and validator in disposable
directories. They characterize existing behavior: child-only name changes,
instruction-body and root preservation, repeated-run idempotence, and rejection
of unprefixed or wrongly namespaced children. The converter implementation is
unchanged by the collection-entry correction.

## 2026-09-06 collection-entry micro-test

Trace reference: Codex task `01a06b99-0b0e-7722-bf58-f30035bbf2b0` on
2026-09-06. The `collaboration.spawn_agent` calls used `agent_type: default`,
`fork_turns: none`, `model: gpt-5.6-sol`, and `reasoning_effort: medium`.
Raw consumer outputs are the final messages for baseline tasks
`/root/bundle_old_1`, `/root/bundle_old_2`, `/root/bundle_old_3`,
`/root/bundle_old_4`, `/root/bundle_old_5`, and control tasks
`/root/bundle_minimal_1`, `/root/bundle_minimal_2`, `/root/bundle_minimal_3`,
`/root/bundle_minimal_4`, `/root/bundle_minimal_5` in that parent task.

The baseline is `e7d27256c8ebe557e0682589537f4ac76ce34459`. Its harness bundle
template and generated root both imposed `Always use which-loop`.

Before editing the template, run five fresh-context samples using
`gpt-5.6-sol`, reasoning effort `medium`. Each sample reads the full collection
root, selects and reads necessary child instructions, then stops before writing
a plan or changing files. Only that collection is available to the probe;
external skills, memory, network, delegation, and implementation are excluded.

The same user task is used for every sample:

> 一個已確認需求與驗收條件的 migration 會跨三個 session，現在沒有可交接的計畫。
> 請準備 repo 內可持續更新的執行計畫，讓下一個 agent 能從 checkpoint 繼續。
> 這次只處理計畫，不改架構或程式。

The output request asks for the actual child-read sequence and a short reason,
and forbids claiming a load that did not happen. The expected specialist is
`execution-plan`; composition is not required for this clear match. A router
detour is measured separately from selecting the wrong specialist.

After the baseline, remove only the unconditional paragraph, preserving the
existing instruction to read the matching child. Repeat five fresh-context
samples with the same prompt, model, effort, and unchanged child instructions.
This deletion-only candidate is also the no-forced-routing control: no new
conditional policy, index, or selection heuristic was introduced.

| Sample | Baseline: reported child sequence | Deletion-only control: reported child sequence |
|---|---|---|
| 1 | `which-loop` → `execution-plan` | `execution-plan` |
| 2 | `which-loop` → `execution-plan` | `execution-plan` |
| 3 | `which-loop` → `execution-plan` | `execution-plan` |
| 4 | `which-loop` → `execution-plan` | `execution-plan` |
| 5 | `which-loop` → `execution-plan` | `execution-plan` |

All ten outputs were read manually. Baseline explanations attributed the first
load to the root's mandatory router instruction; control explanations matched
the durable plan, session hand-off, and checkpoint requirements directly.

Representative baseline response:

> `which-loop`：頂層 `SKILL.md` 強制要求用它判定工作流。
> `execution-plan`：任務明確涉及 migration、跨三個 session、checkpoint 交接與 repo 內持續更新的計畫。

Representative control response:

> `execution-plan/SKILL.md` — 任務明確涉及跨三個 session、migration、checkpoint 交接，以及 repo 內可持續更新的計畫。
> 未載入其他 child skill。

Both variants selected the appropriate specialist in all five samples. The
observed difference is removal of a forced extra routing step, not a repaired
failure to select the specialist. Child-load sequences are model-reported;
this report does not independently establish full retrieval traces or actual
plan execution. Samples ran in Codex, not Manus. They are a narrow wording
probe, not a cross-host qualification, statistical quality estimate, or token
cost benchmark. Manus library import and live selection still require a Manus
check after publication.
