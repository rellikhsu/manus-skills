# Metric Registry & Spec Schema Reference

`scripts/run_screen.py` is the only supported fast-mode entry point. It
compiles a **typed JSON screen specification** into deterministic DuckDB SQL
using the metric registry below. Unknown fields, metrics, or operators are
rejected with an explicit error — there is no free-form SQL path.

## Spec schema

```json
{
  "universe": {
    "sectors": ["Industrials"],
    "industries": ["Industrial - Machinery"],
    "countries": ["US"],
    "exchanges": ["NASDAQ", "NYSE", "AMEX"],
    "currency": "USD",
    "tickers": ["AAPL", "MSFT"],
    "market_cap_min": "$2B",
    "market_cap_max": "$10B",
    "active_only": true,
    "exclude_etfs_funds": true,
    "exclude_non_common": true
  },
  "filters": [
    {"metric": "pe_trailing", "op": "lt", "value": "15x"},
    {"metric": "revenue_growth_yoy_ttm", "op": "between", "low": "5%", "high": "100%"},
    {"metric": "positive_fcf", "op": "eq", "value": true}
  ],
  "sort": {"metric": "pe_trailing", "direction": "asc"},
  "limit": 500,
  "display_rows": 25,
  "sector_percentile_rank": false,
  "columns": ["fcf_yield", "debt_to_equity"]
}
```

All fields are optional; defaults: `universe.currency = "USD"`,
`universe.active_only = true`, `universe.exclude_etfs_funds = true`,
`universe.exclude_non_common = true`, `limit = 400`, `display_rows = 25`,
`sector_percentile_rank = false`, `filters = []`, `columns = []`, `sort = null`.

**Validation rules (all enforced, all fail loudly):**
- Any field not in the schema above → rejected (`Unknown field(s) in ...`).
- Any `metric` not in the registry below → rejected.
- Any `op` not in `{lt, lte, gt, gte, eq, between}` → rejected.
- `between` requires both `low` and `high`, `low <= high` (after unit-aware
  normalization — see below); boolean metrics do not support `between`.
- Boolean metrics (`positive_net_income`, `positive_fcf`) only support `op: eq`
  with a boolean `value`.
- `limit` must be an integer in `[1, 1000]`.
- `display_rows` must be an integer in `[0, 25]`.
- `universe.market_cap_min <= universe.market_cap_max` when both given (after
  unit-aware normalization).
- `sort.direction` must be `asc` or `desc`.
- Every numeric-metric `value`/`low`/`high`, and `universe.market_cap_min`/
  `market_cap_max`, is parsed by the **unit-aware value parser** (see the
  dedicated section below) according to the metric's unit family —
  malformed, ambiguous, or wrong-family values are rejected, never guessed.

## Universe filters (fast-mode scope)

| Field | Effect |
|---|---|
| `sectors` / `industries` / `countries` / `exchanges` | `IN (...)` against `company_profiles` |
| `currency` | `company_profiles.currency = ...` (default `USD`) |
| `tickers` | `company_profiles.symbol IN (...)` — use for watchlists/user-supplied lists |
| `market_cap_min` / `market_cap_max` | band on `quotes.market_cap` (DOUBLE) |
| `active_only` | `company_profiles.is_actively_trading = 'true'` (default on) |
| `exclude_etfs_funds` | `is_etf = 'false' AND is_fund = 'false'` (default on) |
| `exclude_non_common` | name/symbol-pattern proxy for warrants, SPAC units, preferred/depositary shares, and rate-bearing notes/bonds (default on) — **there is no dedicated security-type column**, so this is a heuristic, not a guarantee |

## Metric registry (fast-mode scope)

Every metric below maps to one fixed SQL expression. The spec can only pick
metric keys, operators, and numeric thresholds — no raw expression is ever
accepted from the spec.

| Metric key | Definition | Source table(s) |
|---|---|---|
| `price` | Latest quote price | `quotes.price` |
| `market_cap` | Latest market cap (DOUBLE) | `quotes.market_cap` |
| `pe_trailing` | market cap / TTM net income. **Auto-guards `ttm_net_income > 0`** when filtered/sorted, so negative earnings can't trivially satisfy "< N". | `quotes`, `income_statement` |
| `ev_ebitda` | (market cap + latest total_debt − latest cash) / TTM EBITDA. **Auto-guards `ttm_ebitda > 0` AND enterprise value > 0** when filtered/sorted. | `quotes`, `income_statement`, `balance_sheet` |
| `fcf_yield` | TTM free cash flow / market cap. No guard needed (denominator always positive). | `quotes`, `cash_flow` |
| `revenue_growth_yoy_ttm` | (TTM revenue − prior-year TTM revenue) / \|prior-year TTM revenue\|; NULL unless 8 quarters exist. Denominator already `ABS()`-wrapped, so no additional guard needed. | `income_statement` |
| `net_income_growth_yoy_ttm` | Same convention, net income. Denominator already `ABS()`-wrapped. | `income_statement` |
| `gross_margin_ttm` | TTM gross_profit / TTM revenue. **Auto-guards `ttm_revenue > 0`** when filtered/sorted. | `income_statement` |
| `operating_margin_ttm` | TTM operating_income / TTM revenue. **Auto-guards `ttm_revenue > 0`** when filtered/sorted. | `income_statement` |
| `net_margin_ttm` | TTM net_income / TTM revenue. **Auto-guards `ttm_revenue > 0`** when filtered/sorted. | `income_statement` |
| `positive_net_income` (boolean) | TTM net income > 0 | `income_statement` |
| `positive_fcf` (boolean) | TTM free cash flow > 0 | `cash_flow` |
| `debt_to_equity` | latest total_debt / latest total_stockholders_equity. **Auto-guards `total_stockholders_equity > 0`** when filtered/sorted. | `balance_sheet` |
| `current_ratio` | latest total_current_assets / total_current_liabilities. **Auto-guards `total_current_liabilities > 0`** when filtered/sorted. | `balance_sheet` |
| `cash` | latest cash_and_cash_equivalents | `balance_sheet` |
| `total_debt` | latest total_debt | `balance_sheet` |
| `dividend_yield_ttm` | **APPROXIMATION** — TTM common dividends paid (cash-flow outflow, negated) / market cap. No dedicated dividend-yield field exists; this is trailing shareholder-yield-on-cost, not a forward/announced yield. No guard needed (denominator always positive). | `quotes`, `cash_flow` |
| `payout_ratio_ttm` | **APPROXIMATION** — TTM common dividends paid / TTM net income. **Auto-guards `ttm_net_income > 0`** when filtered/sorted. | `income_statement`, `cash_flow` |
| `eps_ttm` | **APPROXIMATION** — TTM net income / latest shares_outstanding (not a sum of reported per-quarter EPS, since `income_statement.eps` is a VARCHAR per-period field, not additive). No guard needed: `shares_outstanding` is always positive when present, and a negative TTM EPS from a genuine net loss is a real value, not a sign-flip artifact. | `quotes`, `income_statement` |
| `share_count_change_yoy` | **APPROXIMATION** — % change in average `weighted_average_shs_out` between current TTM window (quarters ranked 1-4) and prior-year TTM window (5-8); positive = dilution. Denominator already `ABS()`-wrapped. | `income_statement` |

## Unit-aware value parsing (v3.2)

Every metric is tagged with a **unit family** in the registry, and every
numeric-valued spec field (`universe.market_cap_min`/`market_cap_max`, filter
`value`, `between` `low`/`high`) is parsed according to that family. Agents
should pass the user's original units straight into the spec as a string
(see `SKILL.md` → "Pass user-stated units as-is") — the parser normalizes
deterministically and rejects anything it cannot resolve unambiguously.

### Unit families by metric

| Unit family | Metrics | Canonical unit (bare JSON number) |
|---|---|---|
| `currency` | `universe.market_cap_min`/`market_cap_max`, `price`, `market_cap`, `cash`, `total_debt` | dollars |
| `percentage` | `revenue_growth_yoy_ttm`, `net_income_growth_yoy_ttm`, `gross_margin_ttm`, `operating_margin_ttm`, `net_margin_ttm`, `fcf_yield`, `dividend_yield_ttm`, `payout_ratio_ttm`, `share_count_change_yoy` | decimal fraction (`0.10` = 10%) |
| `multiple` | `pe_trailing`, `ev_ebitda`, `debt_to_equity`, `current_ratio` | raw multiple (`30` = 30x) |
| `plain` | `eps_ttm` | raw number, no unit suffixes accepted |
| `boolean` | `positive_net_income`, `positive_fcf` | unchanged — JSON `true`/`false` only, never routed through the unit parser |

### Accepted string forms

- **Currency:** a leading `$` or a 3-letter ISO code (`USD`, `EUR`, `GBP`,
  `JPY`, `CNY`, `INR`, `CAD`, `AUD`, `CHF`, `HKD`) before or after the number;
  thousands commas; an optional scale suffix, case-insensitive:
  `K`=1e3, `M`/`MM`/`MN`=1e6, `B`/`BN`=1e9, `T`/`TN`=1e12. A sign (`+`/`-`)
  may appear before or after the currency symbol. A bare numeric string with
  no suffix (e.g. `"500000000"`) is accepted as dollars — unambiguous, since
  there is only one currency-like canonical unit. Examples: `"$500M"`,
  `"USD 20B"`, `"2.5bn"`, `"1,250,000"`, `"-$5M"`.
- **Percentage:** a trailing `%` (divide by 100) or trailing `bps`/` bps`
  (divide by 10,000), with an optional leading sign. Examples: `"10%"`,
  `"-5.5%"`, `"150 bps"`. **A bare numeric string with no unit (e.g. `"10"`
  or `"0.10"`) is explicitly rejected** — see "Deliberate ambiguity
  rejection" below.
- **Multiple:** an optional trailing `x`/`X`. Examples: `"30x"`, `"1.5x"`. A
  bare numeric string with no suffix (e.g. `"30"`) is accepted — unambiguous
  for this family, since a multiple has no alternate canonical
  interpretation.
- **Plain (`eps_ttm` only):** a bare number or numeric string; any unit
  suffix (`%`, `bps`, `x`, `$`, currency code) is rejected, since `eps_ttm`
  is a per-share dollar figure with no scale ambiguity worth suffixing.

### Bare JSON numbers always keep their existing canonical unit

For **every** unit family, a bare JSON number (`int`/`float`, not a string)
is passed straight through as the pre-v3.2 canonical unit — this is the
backward-compatibility contract and it never changes: `0.10` for a
percentage metric still means 10%, `30` for a multiple metric still means
30x, `500000000` for a currency metric still means $500,000,000. Only
strings go through unit-suffix parsing.

### Deliberate ambiguity rejection (the root-cause fix)

A bare numeric **string** (e.g. `"10"`) supplied to a `percentage`-family
field is rejected outright, even though the equivalent JSON number `10`
would be accepted (as 1000%, per the canonical decimal-fraction rule above).
This is intentional: a human typing `"10"` for a percentage field is far
more likely to mean "10%" than "1000%", but the parser has no reliable way
to distinguish that intent from someone deliberately passing a
decimal-fraction string. Rather than guess and risk silently misinterpreting
the threshold by 100x (exactly the failure mode that prompted this feature:
`>10%` growth was previously misread as `>10`, i.e. `>1000%`), the parser
requires an explicit unit (`"10%"`) or a JSON number (`0.10`) for
percentage-family fields. Currency and multiple families do not have this
restriction, because a bare numeric string is unambiguous for them (there is
only one plausible canonical interpretation).

### Worked examples (agent-facing)

| User intent | Spec fragment | Normalized value |
|---|---|---|
| Market cap $500M–$20B | `"market_cap_min": "$500M", "market_cap_max": "$20B"` | `500000000.0`, `20000000000.0` |
| Revenue growth > 10% | `{"metric": "revenue_growth_yoy_ttm", "op": "gt", "value": "10%"}` | `0.10` |
| P/E < 30x | `{"metric": "pe_trailing", "op": "lt", "value": "30x"}` | `30.0` |
| D/E < 1.5x | `{"metric": "debt_to_equity", "op": "lt", "value": "1.5x"}` | `1.5` |
| FCF yield > 150 bps | `{"metric": "fcf_yield", "op": "gt", "value": "150 bps"}` | `0.015` |

### Rejections (non-exhaustive, all raise `SpecError` with an actionable message)

- Non-finite numbers: `NaN`, `Infinity`, `-Infinity` (any family).
- A boolean (`true`/`false`) supplied to any non-boolean-family field.
- A percentage form (`%`, `bps`) supplied to a `currency` or `multiple` field.
- A currency form (`$`, ISO code, K/M/B/T suffix) supplied to a
  `percentage`, `multiple`, or `plain` field.
- A multiple form (trailing `x`) supplied to a `currency` or `percentage`
  field.
- An unrecognized scale suffix (e.g. `"500Q"`) or unrecognized currency code
  (e.g. `"XYZ 500M"`).
- An empty or whitespace-only string.
- A bare numeric string supplied to a `percentage` field (see "Deliberate
  ambiguity rejection" above).
- Reversed `between` bounds (`low > high`) after normalization — including
  when the reversal is only apparent after unit conversion (e.g. accidentally
  swapping `"$20B"` and `"$500M"` between `low`/`high`).

## Ratio-sanity guards (deterministic, auto-applied)

Certain ratio metrics divide two values that can each independently be
negative in this dataset (restatements, distressed balance sheets, negative
EBITDA, negative enterprise value). A negative numerator divided by a
negative denominator produces a **positive ratio that looks attractive**
(cheap, low-levered, low-payout) while describing a financially distressed
or undefined situation, not a genuine bargain. The compiler automatically
adds a guard clause to the `WHERE` clause whenever the metric is used in a
`filter` or as the `sort.metric` — never when it only appears in `columns`
(display-only). Guards for the same clause are applied at most once even if
shared by multiple active metrics.

| Metric | Guard clause added | Confirmed real-world failure mode without the guard |
|---|---|---|
| `pe_trailing` | `ttm_income.ttm_net_income > 0` | Negative TTM net income makes P/E negative, trivially passing "P/E < N". |
| `ev_ebitda` | `ttm_income.ttm_ebitda > 0` **and** `(qt.market_cap + COALESCE(bs.total_debt,0) - COALESCE(bs.cash_and_cash_equivalents,0)) > 0` | BNC (CEA Industries Inc.) showed `ev_ebitda = -2.79`: positive EBITDA divided by a *negative* enterprise value (large cash balance relative to market cap + debt) — both legs must be positive for the multiple to mean "cheap", so both are guarded. |
| `gross_margin_ttm` / `operating_margin_ttm` / `net_margin_ttm` | `ttm_income.ttm_revenue > 0` | Negative TTM revenue with negative profit produces a spuriously *positive* margin via a double-negative sign flip (confirmed in this dataset up to +993% "net margin" on negative-revenue rows). |
| `debt_to_equity` | `bs.total_stockholders_equity > 0` | AERO (Grupo Aeroméxico) showed `debt_to_equity = -6.36`: positive total_debt divided by *negative* stockholders' equity (accumulated deficit), trivially passing "D/E < N" despite being financially distressed, not conservatively levered. |
| `current_ratio` | `bs.total_current_liabilities > 0` | A reported zero/negative current-liabilities figure is a data-quality artifact, not a real balance-sheet state, and would otherwise produce an undefined or sign-flipped ratio. |
| `payout_ratio_ttm` | `ttm_income.ttm_net_income > 0` | A company paying dividends during a TTM net loss produces a negative payout ratio, trivially passing "payout ratio < N" despite dividends not being earnings-covered at all. |

**No guard is registered (and none is needed) for:** `fcf_yield`,
`dividend_yield_ttm`, and `eps_ttm` (denominator is `market_cap` or
`shares_outstanding`, both always positive when present), and
`revenue_growth_yoy_ttm` / `net_income_growth_yoy_ttm` /
`share_count_change_yoy` (denominator is already wrapped in `ABS()` in the
registry expression, so the sign of the growth rate always reflects the
direction of change, never a spurious flip).

These guards only take effect when the metric is filtered or sorted on —
rows are never silently dropped from `columns`-only display, and the raw
(unguarded) value is always what gets projected if the metric is requested
only as a display column. State this explicitly if a user asks why a
filtered count differs from an unfiltered display count for the same
metric.

## TTM / balance-sheet conventions (exact semantics)

- **TTM window:** `income_statement`/`cash_flow` quarterly rows (`period IN
  ('Q1','Q2','Q3','Q4')`) are ranked per symbol by `date DESC`. Ranks 1–4 = the
  current TTM; ranks 5–8 = the prior-year TTM. YoY metrics require
  `prior_quarter_count = 4`, else NULL — never silently zero-filled.
- **Latest balance-sheet snapshot:** `balance_sheet` rows are ranked per
  symbol by `date DESC`; only `bs_rank = 1` is used (no summing across
  quarters — balance-sheet items are point-in-time, not flow items).
- **No fan-out:** `ttm_income`, `ttm_cf` (`GROUP BY symbol`), and `latest_bs`
  (`bs_rank = 1`) are all guaranteed at most one row per symbol before being
  joined to `company_profiles`/`quotes`, so joins never multiply row counts.
- **VARCHAR casts:** every statement-table numeric column is `TRY_CAST(... AS
  DOUBLE)` inside the CTE before use; `quotes` columns are already typed
  DOUBLE/VARCHAR appropriately at the source and are not re-cast.
- **Zero/NULL denominators:** every division in the registry uses `NULLIF(
  denominator, 0)` (or a `CASE`-guarded window count) so a zero or missing
  denominator produces NULL, not an error or a divide-by-zero row drop.

## Sorting, limits, and ranking

- `sort.metric` may be any registry metric key or a standard bundle column
  (`ticker`, `company`, `industry`, `price`, `market_cap`, `pe_trailing`,
  `pct_change`, `volume`, `revenue_growth_yoy_ttm`, `net_margin_ttm`).
- `direction: "asc"` or `"desc"`; NULLs always sort last regardless of
  direction.
- `limit` caps the raw SQL result (default 400, ≤ 1000); `display_rows` caps
  how many of those rows are rendered as Markdown (default 25, ≤ 25). The
  full result is always written to CSV regardless of `display_rows`.
- `sector_percentile_rank: true` adds `PERCENT_RANK() OVER (PARTITION BY
  cp.sector ORDER BY <metric>)` columns for every metric in `columns` (or the
  sort metric if `columns` is empty), suffixed `_sector_pctile`.

## Output bundle

Every screen always projects, in order: `ticker`, `company`, `industry`,
`price`, `market_cap`, `pe_trailing`, `pct_change`, `volume`,
`revenue_growth_yoy_ttm`, `net_margin_ttm` — then any metrics listed in
`columns` (de-duplicated against the standard bundle) — then any
`_sector_pctile` columns. No `SELECT *`.

## Known parity limitations (state these to the user when relevant)

- **Dividend yield / payout ratio / EPS TTM / share-count change** are
  documented approximations (see table above) because the database has no
  dedicated dividend, EPS-summable, or diluted-share-count-history field.
- **`exclude_non_common`** is a name/symbol heuristic, not a security-type
  flag — it can occasionally under- or over-exclude edge cases (e.g. a
  legitimately named company that happens to match a pattern). Report counts
  before/after if the user needs exactness. In particular, some
  preferred/note instruments in this dataset have their coupon truncated
  from the company name (e.g. `"Prudential Financial, Inc. 5.62"` with no
  `%`/`PFD`/`Notes` suffix surviving) and are **not** caught by this proxy —
  there is no reliable name pattern to distinguish them from a genuine
  common-stock name ending in a number. If exact security-type filtering
  matters, verify top candidates manually or via deep-mode enrichment.
- **No index-membership table** — "S&P 500"/"Nasdaq 100" screens must be
  approximated via `market_cap_min`/`exchanges`/`sectors`, or via deep-mode
  ETF-holdings enrichment (out of fast-mode scope).
- **Forward P/E, analyst targets, consensus, and sentiment** are not in these
  five tables at all — deep mode only (see `references/enrichment-catalog.md`).
