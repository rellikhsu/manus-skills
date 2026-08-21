# Deep-Mode Enrichment Catalog

Loaded only when deep mode is triggered. Fast mode does not need this file.

## Core principle

The production screener stops at the SQL table. Deep mode adds cited depth for the top survivors. The cost killer in v1 was calling these tools **per-ticker, sequentially**. Every tool below accepts `ticker_symbols` as an **array**, so you batch the whole survivor list into ONE call per tool, and issue the (few) calls you need **in parallel** in a single turn.

## Enrichment tool table

| Want | Tool | Batched input |
|------|------|---------------|
| Live price, market cap, P/E, dividend yield, volume, 52-wk range | `finance_quotes` | `ticker_symbols[]` + `fields[]` (request only needed fields) |
| Standardized financials — revenue, margins, debt, FCF (TTM/annual/quarter) | `finance_company_financials` | `ticker_symbols[]` + `period` + `income_statement_metrics[]` / `balance_sheet_metrics[]` / `cash_flow_metrics[]` + `as_of_*` + `limit` |
| Pre-computed ratios — ROE, ROIC, D/E, margins, EV/EBITDA, P/E, yields | `finance_company_ratios` | `ticker_symbols[]` + `ratio_ids[]` (pass only the ratios you need) |
| Forward estimates — EPS / revenue / EBITDA | `finance_estimates` | `ticker_symbols[]` + `period_type` |
| Price targets, consensus, upgrades/downgrades | `finance_analyst_research` | `ticker_symbols[]` + `limit` |

Specialty tools — use ONLY when the query explicitly calls for them:

| Want | Tool |
|------|------|
| Earnings beat/miss history | `finance_earnings_history` |
| Segment KPIs / unit economics | `finance_segments` |
| Price history / technicals / momentum | `finance_ohlcv_histories` |
| Insider transactions | `finance_insider_transactions` |
| Institutional holders | `finance_institutional_holders` |
| Politician holders | `finance_politician_ticker_holders` |
| Bull/bear sentiment | `finance_ticker_sentiment` |

## Tool-selection rules (the cap)

Pick only what the query actually needs. Examples:

- "Cheap growth" → `finance_quotes` (price/P/E) + `finance_estimates` (forward P/E). 2 tools.
- "Dividend quality" → `finance_quotes` (yield) + `finance_company_ratios` (payout, D/E). 2 tools.
- "Sector-relative quality" → `finance_company_ratios` (ROIC, margin, EV/EBITDA). 1 tool.
- "Analyst sentiment on the top names" → `finance_analyst_research` + `finance_ticker_sentiment`. 2 tools.

If you reach 4+ tools, stop and reconsider — you are over-enriching.

## Deep-mode workflow

1. Start from the fast-mode results table (the survivors).
2. Take the **top 5** by the screen's sort (max 10).
3. Select 1–3 enrichment tools per the selection rules.
4. Build **one call per tool**, each with the full `ticker_symbols` array of the top 5.
5. Issue **all calls in parallel** in a single assistant turn.
6. Merge results into the table. Pass every numeric value through `cite()` per `default-tools.md`; render as `[value](claim:N)`. SQL-only values stay labeled as screening-db output.
7. Add a ranking explanation (why the top names passed + mixed signals) and refreshed-as-of dates.

## Batching do / don't

- DO: `finance_quotes(ticker_symbols=["AAPL","MSFT","NVDA","META","GOOGL"], fields=["price","pe","dividendYieldTTM","marketCap"])` — one call, five tickers.
- DON'T: loop over tickers calling `finance_quotes` once each — five calls, serial.
- DO: issue `finance_quotes`, `finance_estimates`, and `finance_analyst_research` as three parallel `call_external_tool` calls in one turn.
- DON'T: call them one after another across three turns.

## Fallbacks

- If a batched call fails or times out, retry that single call once; do not fall back to per-ticker looping.
- If a needed metric is null for some tickers, exclude-and-disclose in the output (state which tickers were dropped and why).
