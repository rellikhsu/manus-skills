# Screener Templates

Ready-made fast and deep screen specs. Adapt thresholds to the user's ask.
Every fast-mode template below is a complete `--spec-json` payload for
`scripts/run_screen.py` — no hand-authored SQL, no preparatory calls.

**Unit-aware values (v3.2):** thresholds below use human-readable unit
strings (`"$2B"`, `"20%"`, `"25x"`) where that's the natural way a user
would state them — pass the user's stated units straight through rather
than pre-converting to raw numbers. Bare JSON numbers still work exactly as
before (backward-compatible canonical units) and are used below only where
a bare number is the more natural/unambiguous form (e.g. `current_ratio`,
`ev_ebitda` multiples without an explicit "x"). See
`references/metric-registry.md` → "Unit-aware value parsing" for the full
rules.

## Fast-mode templates (default — spec → run_screen.py → table)

**Trailing P/E sector screen**

```json
{
  "universe": {"sectors": ["Industrials"]},
  "filters": [{"metric": "pe_trailing", "op": "lt", "value": "11x"}],
  "sort": {"metric": "pe_trailing", "direction": "asc"}
}
```

**Cheap growth** — revenue growth > 20%, positive FCF, P/E < 25, sort by growth desc:

```json
{
  "universe": {"countries": ["US"]},
  "filters": [
    {"metric": "revenue_growth_yoy_ttm", "op": "gt", "value": "20%"},
    {"metric": "positive_fcf", "op": "eq", "value": true},
    {"metric": "pe_trailing", "op": "lt", "value": "25x"}
  ],
  "sort": {"metric": "revenue_growth_yoy_ttm", "direction": "desc"}
}
```

**Dividend quality** — yield > 3%, payout < 75%, positive FCF, D/E < 1, market cap > $5B:

```json
{
  "universe": {"countries": ["US"], "market_cap_min": "$5B"},
  "filters": [
    {"metric": "dividend_yield_ttm", "op": "gt", "value": "3%"},
    {"metric": "payout_ratio_ttm", "op": "lt", "value": "75%"},
    {"metric": "positive_fcf", "op": "eq", "value": true},
    {"metric": "debt_to_equity", "op": "lt", "value": "1x"}
  ],
  "sort": {"metric": "dividend_yield_ttm", "direction": "desc"}
}
```

Note: `dividend_yield_ttm`/`payout_ratio_ttm` are documented approximations
(see `references/metric-registry.md`) — say so in the output.

**Mid-cap discovery** — $2B–$10B market cap, revenue growth > 25%, positive FCF:

```json
{
  "universe": {"countries": ["US"], "market_cap_min": "$2B", "market_cap_max": "$10B"},
  "filters": [
    {"metric": "revenue_growth_yoy_ttm", "op": "gt", "value": "25%"},
    {"metric": "positive_fcf", "op": "eq", "value": true}
  ],
  "sort": {"metric": "revenue_growth_yoy_ttm", "direction": "desc"}
}
```
Label results as unverified starting points for deeper research.

**Sector-relative quality** — within-sector percentile ranking on margin and EV/EBITDA:

```json
{
  "universe": {"sectors": ["Technology"]},
  "filters": [
    {"metric": "net_margin_ttm", "op": "gt", "value": "10%"},
    {"metric": "ev_ebitda", "op": "between", "low": 0, "high": 25}
  ],
  "sort": {"metric": "net_margin_ttm", "direction": "desc"},
  "sector_percentile_rank": true,
  "columns": ["ev_ebitda", "net_margin_ttm"]
}
```

**Watchlist refresh** — re-run a saved filter set against the user's tickers:

```json
{
  "universe": {"tickers": ["AAPL", "MSFT", "NVDA", "META", "GOOGL"]},
  "filters": [],
  "sort": {"metric": "market_cap", "direction": "desc"}
}
```

**High growth without dilution** — growth filter + share-count-change filter:

```json
{
  "universe": {"countries": ["US"]},
  "filters": [
    {"metric": "revenue_growth_yoy_ttm", "op": "gt", "value": "20%"},
    {"metric": "share_count_change_yoy", "op": "lt", "value": "2%"}
  ],
  "sort": {"metric": "revenue_growth_yoy_ttm", "direction": "desc"}
}
```

**India screen** — INR, NSE/BSE, active only, plus metric filters:

```json
{
  "universe": {"currency": "INR", "exchanges": ["NSE", "BSE"]},
  "filters": [{"metric": "pe_trailing", "op": "lt", "value": "20x"}],
  "sort": {"metric": "pe_trailing", "direction": "asc"}
}
```

**Balance-sheet strength screen** — cash-rich, low leverage, healthy current ratio:

```json
{
  "universe": {"market_cap_min": "$1B"},
  "filters": [
    {"metric": "debt_to_equity", "op": "lt", "value": "0.5x"},
    {"metric": "current_ratio", "op": "gt", "value": 2},
    {"metric": "cash", "op": "gt", "value": "$500M"}
  ],
  "sort": {"metric": "current_ratio", "direction": "desc"},
  "columns": ["cash", "total_debt", "debt_to_equity"]
}
```

Invocation for any of the above:

```bash
python3 skills/finance-screener-workflow-fast/scripts/run_screen.py \
  --spec-json '<paste one of the JSON specs above>' \
  --output /home/user/workspace/screen.csv
```

## Deep-mode templates (opt-in — screen + batched parallel enrichment)

Use only when the user asks to enrich or needs forward/consensus data.

- **Cheap growth + forward view** — fast "cheap growth" spec above, then deep
  mode: top 5, `finance_quotes` (price, pe, marketCap) + `finance_estimates`
  (forward EPS/revenue) in parallel. Cite all.
- **Dividend quality deep** — fast "dividend quality" spec above, then deep
  mode: top 5, `finance_quotes` (dividendYieldTTM) + `finance_company_ratios`
  (payout_ratio, debt_to_equity, current_ratio) in parallel — use these to
  replace the fast-mode approximations with tool-sourced values.
- **Event-driven shortlist** — fast screen for the universe, then deep mode
  top 5 with `finance_estimates` + `finance_ticker_sentiment`.
- **Analyst-backed finalists** — fast screen, then deep mode top 5 with
  `finance_analyst_research` (targets, consensus) + `finance_ticker_sentiment`
  in parallel.
- **Income-statement comparison** — given a screened cohort (or user-supplied
  tickers), deep mode: batch all tickers into one
  `finance_company_financials` call (`period=annual`, `limit=3`, income
  metrics) and build a side-by-side dashboard.

## Export

- `run_screen.py` always writes CSV + generated SQL as part of the standard
  fast path.
- **Generated SQL (mandatory, v3.3):** after the one `bash` call, always
  call `share_file` on `generated_sql_path` (from the telemetry JSON) to
  attach the `.sql` file — this makes every screen reproducible. Never
  paste the SQL text inline in the response; the file share is the only
  delivery mechanism.
- **CSV:** call `share_file` on the CSV `--output` path when the user
  requests an export or the full result set is materially larger than the
  displayed table. Unlike the SQL file, CSV sharing stays conditional.
- Create Excel only when explicitly requested; use the spreadsheet workflow
  after the fast screen completes.
