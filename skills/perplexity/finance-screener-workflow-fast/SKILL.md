---
name: "perplexity:finance-screener-workflow-fast"
description: "Fast natural-language public-equity screening that mirrors perplexity.ai/finance/screener. DEFAULT fast mode compiles a typed screen spec into deterministic DuckDB SQL and runs it with exactly one bash call. OPT-IN deep mode batches and parallelizes finance_* enrichment across the top survivors. Use for 'find stocks that…', candidate-list generation, sector/market-cap/valuation/growth/income screens, and watchlist discovery. Not for single-ticker deep dives or personal portfolio holdings."
metadata:
  perplexity:
    display_name: "Finance screener"
---

# Finance Screener Workflow (v3.3.2 — deterministic single-entry fast mode)

A faithful, reproducible mirror of the Perplexity Finance Screener. The real
screener is a natural-language → read-only SQL pipeline against a structured
public-equities database; results return as a table you can sort, export,
and share. This workflow reproduces that, in two modes:

- **Fast mode (default):** parse intent → typed JSON spec → **one bash call**
  to `scripts/run_screen.py` → table. Target < 1 minute. The script itself
  calls `finance_analyst`, downloads data, compiles SQL, and renders output —
  the agent never touches SQL, `describe_external_tools`, or
  `call_external_tool` for supported requests.
- **Deep mode (opt-in):** after the screen, batch + parallel-enrich the top
  survivors via `finance_*` tools. Use only when the user explicitly asks to
  enrich, deep-dive the top names, or needs data the SQL DB lacks (forward
  estimates, analyst targets/consensus, live price refresh, sentiment).

## When to use

- "Find stocks that…" / "screen for…" / "show me companies with…"
- Building candidate lists for deeper research
- Sector, market-cap, valuation, growth, or income screens
- Refreshing a watchlist against a filter set

Do NOT use for: a single named ticker deep-dive (use `finance_*` tools
directly), personal portfolio holdings (use personal-finance tools), or
anything requiring live execution/trading.

## The single supported fast-mode path (mandatory)

For **every** fast-mode request, the entire tool budget is **one bash call**:

```bash
python3 skills/finance-screener-workflow-fast/scripts/run_screen.py \
  --spec-json '{
    "universe": {"sectors": ["Industrials"]},
    "filters": [{"metric": "pe_trailing", "op": "lt", "value": 11}],
    "sort": {"metric": "pe_trailing", "direction": "asc"}
  }' \
  --output /home/user/workspace/screen.csv
```

Run this with `api_credentials=["external-tools"]`. The script:

1. Validates the spec against the metric registry (unknown fields, metrics,
   or operators are rejected with an explicit error — fix and resubmit).
   This is pure CPU and runs first, so an invalid spec exits `2` promptly
   without paying for a DuckDB install.
2. Bootstraps DuckDB **before any network work** — installs it and
   transparently `os.execve` re-executes itself if the sandbox lacks it
   (still one bash call). The ordering is load-bearing: the re-exec restarts
   the process from scratch, so bootstrapping *after* the `finance_analyst`
   call and download (as v3.3 did) discarded and repeated both, doubling the
   two most expensive phases on a cold sandbox.
3. Compiles deterministic DuckDB SQL from the spec (metric registry, no
   agent-authored SQL, no `SELECT *`, no fan-out joins).
4. Calls `finance_analyst` itself via the `external-tool` CLI
   (`source_id=finance`, `tool_name=finance_analyst`,
   `{"query": "..."}`) — the agent does **not** call
   `describe_external_tools`/`call_external_tool` for this.
5. Downloads only the needed parquet tables concurrently. On S3 `HTTP 400
   InvalidToken`, it transparently calls `finance_analyst` one more time and
   retries the download exactly once, inside the same process — no
   agent-visible retry, no second bash call.
6. Saves the CSV and the generated SQL, then prints a machine-readable
   telemetry JSON line, then a Markdown table.

**This direct single-call invocation is mandatory for every request that
fits the spec schema below.** For these requests, the following are
**forbidden**: `describe_external_tools` on `finance_analyst`,
`call_external_tool` on `finance_analyst`, hand-authored SQL, and manual
schema inspection or manual URL/token handling. `scripts/run_screen.py` is
the sole entry point — there is no preset-based or legacy runner. If a
request truly cannot be expressed by the spec schema (see
`references/metric-registry.md`), say so explicitly and fall back to the
documented deep-mode / manual `finance_analyst` path — do not silently
approximate it inside a "supported" call.

### Spec schema (typed JSON — the only input to the script)

```json
{
  "universe": {
    "sectors": [], "industries": [], "countries": [], "exchanges": [],
    "currency": "USD", "tickers": [],
    "market_cap_min": null, "market_cap_max": null,
    "active_only": true, "exclude_etfs_funds": true, "exclude_non_common": true
  },
  "filters": [{"metric": "...", "op": "lt|lte|gt|gte|eq|between", "value": 0, "low": 0, "high": 0}],
  "sort": {"metric": "...", "direction": "asc|desc"},
  "limit": 400,
  "display_rows": 25,
  "sector_percentile_rank": false,
  "columns": []
}
```

Full metric registry, exact TTM/balance-sheet/zero-denominator semantics,
and known approximations: **read `references/metric-registry.md` before
constructing a spec for any metric you haven't used before.**

### Pass user-stated units as-is — never pre-convert them yourself (introduced v3.2, still in effect)

**Do not mentally convert currency scales or percentages before writing the
spec.** `market_cap_min`/`market_cap_max` and every absolute-money, percentage,
and multiple metric now accept the user's original human-readable string
directly — the script parses and normalizes it deterministically, and
rejects anything ambiguous rather than guessing. Hand-converting units
yourself is exactly what caused two prior incidents: `$500M-$20B` was
misconverted to `$500M-$50B`, and `>10%` growth was misread as `>10` (i.e.
`>1000%`, since a bare JSON number `10` for a percentage metric means 1000%
by the canonical decimal-fraction convention below).

**Required behavior — put the user's units straight into the spec string:**

| User said | Put in the spec (do NOT convert) |
|---|---|
| market cap between $500M and $20B | `"market_cap_min": "$500M", "market_cap_max": "$20B"` |
| revenue growth above 10% | `{"metric": "revenue_growth_yoy_ttm", "op": "gt", "value": "10%"}` |
| P/E under 30x | `{"metric": "pe_trailing", "op": "lt", "value": "30x"}` |
| debt-to-equity under 1.5x | `{"metric": "debt_to_equity", "op": "lt", "value": "1.5x"}` |
| FCF yield above 150 bps | `{"metric": "fcf_yield", "op": "gt", "value": "150 bps"}` |

Accepted string forms by field type — see `references/metric-registry.md`
("Unit-aware value parsing") for the full rules and rejection list:

- **Currency** (`market_cap_min`/`market_cap_max`, `price`, `market_cap`,
  `cash`, `total_debt`): `"$500M"`, `"USD 20B"`, `"2.5bn"`, `"1,250,000"`,
  K/M/B/T suffixes (case-insensitive, MM/MN/BN/TN also accepted), or a bare
  JSON number in dollars (unchanged canonical unit).
- **Percentage** (`revenue_growth_yoy_ttm`, `net_income_growth_yoy_ttm`, all
  `*_margin_ttm`, `fcf_yield`, `dividend_yield_ttm`, `payout_ratio_ttm`,
  `share_count_change_yoy`): `"10%"`, `"-5.5%"`, `"150 bps"`, or a bare JSON
  number as a decimal fraction (unchanged canonical unit — `0.10` means
  10%). **A bare numeric *string* (e.g. `"10"`) is rejected** — it is
  ambiguous between 10% and the decimal fraction 1000%; use `"10%"` or the
  JSON number `0.10`.
- **Multiple** (`pe_trailing`, `ev_ebitda`, `debt_to_equity`,
  `current_ratio`): `"30x"`, `"1.5x"`, or a bare number/numeric string
  (unambiguous — unchanged canonical unit).
- **Boolean** (`positive_net_income`, `positive_fcf`): unchanged — JSON
  `true`/`false` only.

Malformed, ambiguous, wrong-unit-for-the-field, non-finite (NaN/Inf), or
unknown-suffix values raise an explicit `SpecError` (exit code `2`) — read
the message and correct the spec string; the script never silently guesses
a unit.

Supported metrics (fast-mode scope): `price`, `market_cap`, `pe_trailing`,
`ev_ebitda`, `fcf_yield`, `revenue_growth_yoy_ttm`,
`net_income_growth_yoy_ttm`, `gross_margin_ttm`, `operating_margin_ttm`,
`net_margin_ttm`, `positive_net_income`, `positive_fcf`, `debt_to_equity`,
`current_ratio`, `cash`, `total_debt`, `dividend_yield_ttm`,
`payout_ratio_ttm`, `eps_ttm`, `share_count_change_yoy`.

**Exit codes:** `0` success. `2` spec validation failed (message printed as
JSON — fix the spec and resubmit; this is not a retry, it's a corrected
input). `1` runtime failure (message printed as JSON — read it before
concluding the runner is broken).

### Ambiguity map (resolve before building the spec)

- "cheap" → `pe_trailing` or `ev_ebitda` below a threshold (state which)
- "quality / profitable" → `positive_net_income` or `positive_fcf` (state which)
- "mid-cap" → `market_cap_min`/`market_cap_max` band — state the band
- "growth" → `revenue_growth_yoy_ttm` or `net_income_growth_yoy_ttm` over what period (this DB only supports TTM YoY, not QoQ/3-yr CAGR — say so if the user wants otherwise)
- "high growth without dilution" → growth filter + `share_count_change_yoy` filter
- "dividend stock" → `dividend_yield_ttm` (state it's an approximation — see registry doc)
- Named sector/ETF/index universe without a direct `company_profiles` match → proxy via a market-cap/sector band and disclose the proxy; there is no index-membership table

### Validate and return the table (mirror the screener)

- Read the telemetry JSON line the script prints: check `total_rows` (0 →
  recheck filters; 1000/`limit` → likely too broad, tighten) and any
  `download_retry_count`/`finance_tool_calls` > expected.
- Timing fields are per-phase: `finance_tool_elapsed_seconds`,
  `download_elapsed_seconds`, `query_elapsed_seconds`, and
  `total_elapsed_seconds` (this process only). `duckdb_ready_seconds` is the
  time spent making DuckDB importable (~0 when already installed).
  `duckdb_bootstrap_reexec: true` means this process is the re-exec'd child
  of a cold bootstrap — the parent's pip-install and startup time happened
  before this process existed and is therefore **not** included in
  `duckdb_ready_seconds` or `total_elapsed_seconds`. Do not present
  `total_elapsed_seconds` as full wall-clock cost when that flag is true.
- Telemetry also includes `normalized_spec` (post unit-parsing, exactly what
  was executed — e.g. the actual `market_cap_min`/`market_cap_max` dollar
  bounds and filter thresholds) and `original_spec` (as supplied). Use
  `normalized_spec` to audit that a `"$500M"`/`"10%"`-style input normalized
  to the value you intended before reporting results — do not just trust
  that the string round-tripped correctly.
- Treat script output as final screening data. Do not rerun merely to
  restyle numbers — format while composing the response.
- Output schema:
  1. **Summary** — restate the query in plain English, universe, filters
     applied, raw (`total_rows`) vs displayed (`displayed_rows`) count, sort.
  2. **Results table** — reproduce the Markdown table the script printed
     (standard bundle + requested columns). Label all values as
     screening-db output; do not fabricate `cite()` markers for SQL-only
     values.
  3. **Ranking note** — one or two lines on why the top names passed the
     filters and any mixed signals (e.g. strong growth offset by weak
     balance sheet).
  4. **Caveats** — data periodicity (latest quarter/TTM vs live quote),
     trailing vs forward, any metric flagged as an approximation in the
     registry doc, missing-data NULLs, index-proxy vs true membership.
  5. **Generated SQL** — read `generated_sql_path` from the telemetry JSON
     and call `share_file` on that path to attach the `.sql` file to your
     response. **Do not paste the SQL text inline into the chat response**
     (no "View Code" block, no fenced SQL dump) — the file share is the
     delivery mechanism. Mention in prose that the generated SQL is
     attached, and (if useful) name the tables it reads from.

**Fast-mode discipline:** do NOT enrich, do NOT add a second formatter or
pandas pass, do NOT re-run the script to reformat — the script already saved
CSV + SQL and rendered Markdown. Sharing the `.sql` file is the one
permitted post-execution step beyond formatting the response — see
"Performance contract" below.

## DEEP MODE (opt-in enrichment)

Trigger deep mode ONLY when the user explicitly asks to: enrich / deep-dive
the top names, pull analyst targets/consensus or forward estimates, refresh
live price or current-period financials, or get sentiment. Otherwise stay in
fast mode.

When triggered, read `references/enrichment-catalog.md` for the full tool
table and the batching/parallel workflow. The non-negotiable rules:

- **Two-stage approximation:** if a requested filter requires non-SQL data
  (forward estimates, analyst targets, sentiment), do NOT pretend you
  screened the whole universe on it. Use the fast-mode script to narrow the
  universe first, then batch-enrich a capped candidate pool, and label the
  result explicitly as a two-stage approximation (unless the user gave you a
  small ticker list to start).
- **Batch the describes too:** call `describe_external_tools` ONCE with the
  full selected tool list, then issue all `call_external_tool` calls in the
  same assistant turn. Never describe tools one-by-one.
- **Batch:** pass the entire survivor list in one `ticker_symbols` array per
  tool. Never loop per-ticker.
- **Parallel:** issue all selected enrichment tools in a single assistant
  turn (parallel `call_external_tool` calls). They are independent.
- **Cap tools:** select only the 1–3 tools the query actually needs.
- **Cap N:** enrich the top 5 by default (max 10).
- **Cite:** every numeric value from a `finance_*` tool must pass through
  `cite()` per `default-tools.md` from `finance/finance-markets`; never
  fabricate claim markers.

Output adds to the fast-mode table: enriched columns (cited), a ranking
explanation, and refreshed-as-of dates.

## Guardrails

- **Data periodicity:** label each metric as TTM, latest-quarter snapshot
  (balance sheet), or live/current quote. Do NOT claim all SQL financials are
  from the last annual filing. For time-sensitive decisions, refresh live
  price via `finance_quotes` and current financials via
  `finance_company_financials` (`as_of`) — deep mode only.
- **Metric definitions:** be explicit about trailing vs forward, TTM vs
  annual. Forward P/E requires `finance_estimates` (deep mode only — not in
  the fast-mode registry).
- **Sector-relative:** use `sector_percentile_rank: true` in the spec rather
  than computing percentiles by hand.
- **Index membership:** no dedicated index-membership table — proxy via
  market-cap/sector bands or ETF-holdings enrichment (deep mode) and say so.
- **Ticker ambiguity:** for user-supplied names (not symbols), resolve via
  `finance_tickers_lookup` (deep mode) before passing `universe.tickers`;
  never assume a symbol.
- **Missing data:** exclude-and-disclose is the default for explicit
  filters; for the **default-display metrics** the script already applies
  the documented NULL semantics (see `references/metric-registry.md`) —
  never re-derive these by hand.
- **Ratio-sanity guards:** when `ev_ebitda`, `debt_to_equity`,
  `current_ratio`, `payout_ratio_ttm`, `pe_trailing`, or any margin metric is
  filtered or sorted on, the script auto-adds a positivity guard on the
  relevant numerator/denominator (see `references/metric-registry.md` for
  the exact clause per metric) so a distressed name with a negative
  denominator (e.g. negative equity, negative enterprise value) can't
  trivially pass a "low/cheap" filter via a double-negative sign flip. This
  is automatic — never add your own denominator filter to work around it.
- **Not investment advice:** state plainly in the output.

## Model & subagent guidance (speed)

- **Primary: `claude_sonnet_5_0`** — fastest available model (★★★★★ speed),
  strong quality (★★★★), cheapest capable option. Best default for parsing
  intent into a spec and orchestrating the single script call.
- **Alt for complex specs: `gpt_5_4`** — best-in-class structured reasoning
  (★★★★★ quality) when a request needs several combined filters and precise
  metric selection; slower (★★★ speed).
- **Avoid for the screen:** `claude_opus_4_8`, `claude_fable_5`, `gpt_5_5`,
  and Deep Research mode — overkill for a filter+table tool.
- **Run inline; do not spawn subagents** for the screen or enrichment.
- **Parallelize via tool calls, not subagents** in deep mode.

## Performance contract

- **Fast mode:** < 1 min. Hard budget: **exactly one** `bash` call to
  `scripts/run_screen.py` with `api_credentials=["external-tools"]`. No
  `describe_external_tools`, no `call_external_tool`, no manual SQL, no
  manual schema inspection, no manual URL handling, no dependency
  installation, no extra formatting pass, no enrichment. The script's
  internal one-time `finance_analyst` retry on `InvalidToken` is not an
  extra agent call and does not count against this budget. After that one
  `bash` call, exactly one `share_file` call on `generated_sql_path` is
  required and permitted — it is a non-compute delivery action (attaching
  the already-saved `.sql` file), not a second execution step, and does not
  count against the one-bash-call budget.
- **Deep mode:** < 1 min via batching + parallelism + caps. Hard budget: 1
  `describe_external_tools` call (all selected tools at once) + max 3
  parallel `call_external_tool` enrichment calls.
- **Stop rule:** if either mode would exceed its budget, or the request
  can't be expressed by the spec schema, pause and ask the user to narrow
  scope or confirm a deep-mode/manual fallback rather than silently
  over-fetching or hand-rolling SQL.
- See `references/templates.md` for ready-made fast and deep screen specs,
  and `references/metric-registry.md` for the full metric/field reference.
