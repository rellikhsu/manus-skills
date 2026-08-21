---
name: etf-overlap
description: "Compare ETF holdings and exposures to understand overlap, redundancy, and diversification."
metadata:
  perplexity:
    display_name: "ETF overlap"
---
# ETF overlap

Build an ETF overlap report for two to five ETF tickers. Treat the first two tickers as the primary comparison and any additional comma-separated tickers as optional multi-ETF context.

## Workflow UI and behavior
- Workflow panel title: Compare ETFs.
- Primary action button label: Compare ETFs.
- Acknowledge the input tickers and analysis plan in concise user-facing updates. State that you will treat the provided tickers as ETF inputs, pull the latest holdings available, and calculate count-based and weight-based overlap.
- State that you are checking the finance connector schema or finance holdings endpoint rather than assuming endpoint shape.
- After fetching holdings, state whether the returned data is full constituent-level holdings or top holdings only.
- If holdings data lacks sector labels, expense ratios, AUM, explicit holdings dates, or other metadata, state that quantitative overlap will remain security-level and unsupported sector/style interpretation will be qualitative.
- State that you are generating overlap math with provenance and will use those numbers directly in the final report.
- Do not over-narrate internal mechanics. Progress updates should build confidence that current holdings data is being used and overlap is computed directly.

## Input handling and validation
- Accept letters, numbers, periods, and hyphens in tickers. Trim whitespace and convert to uppercase for display and tool calls.
- First ETF ticker and Second ETF ticker are required.
- Parse Additional ETF tickers as a comma-separated list.
- Deduplicate tickers across required and additional inputs while preserving first-seen order. Mention duplicates only if removal affects the requested comparison.
- Require at least two unique tickers and no more than five unique tickers. If more than five are provided, ask the user to narrow the set.
- Resolve tickers before fetching holdings. If a ticker resolves to a non-ETF or cannot be resolved, stop and ask the user to correct the ticker.
- If lookup returns multiple plausible instruments, select the US-listed ETF only when unambiguous. Otherwise ask the user to disambiguate.
- If holdings are unavailable for a ticker, clearly say which ETF failed and why, then continue only if at least two valid ETFs have usable holdings; otherwise stop.

## Data-source routing
- Use Perplexity's built-in finance connector whenever available.
- If needed, list and describe finance tools before use. Prefer finance_tickers_lookup and finance_etf_holdings.
- Resolve every input ticker with finance_tickers_lookup using the user-provided ticker strings as queries.
- Preserve resolved ETF display names for the metadata table and holdings call.
- Fetch holdings with finance_etf_holdings using ticker_symbols, ticker_names when available, and a human-readable query such as: Compare ETF holdings overlap for VOO and QQQ.
- Optional fallback order if supported by the runtime: built-in finance connector first; Morningstar only if built-in holdings are unavailable and Morningstar fund IDs can be resolved; approved current fund sponsor CSV/XLS holdings files only when a structured web-fetch path exists.
- Do not scrape brittle pages if a structured connector is available.
- If no reliable holdings source is available, ask the user to try a more common US-listed ETF or provide a holdings file.

## Data freshness and fields
- Use the latest holdings returned by the source.
- If holdings as-of date is present in metadata or file columns, display it in the metadata table.
- If no as-of date is present, display: Not reported in returned holdings file.
- Do not infer or invent as-of dates from current date, call time, or sponsor schedules.
- Required minimum fields per ETF are ETF ticker, holding name, holding symbol or equivalent security identifier, and holding weight or percent of fund.
- Ingest optional fields when available: shares, market value, CUSIP, ISIN, FIGI, sector, industry, asset class, country, currency, holding type, and as-of date.
- Missing sector/industry: do not fabricate sector-level overlap; keep sector/style discussion qualitative and based on recognizable holdings and fund construction.
- Missing fund expense ratio or AUM: do not include those metadata columns unless returned reliably.
- Missing weight: if market value exists, compute weight as holding market value divided by total listed market value and disclose reconstruction.
- Missing ticker symbols: prefer stable security ID such as CUSIP/ISIN; if unavailable use normalized holding name and disclose lower confidence.
- Multiple share classes are distinct holdings by default unless the source provides a common issuer identifier and the user asks for issuer-level overlap.

## Holdings normalization
- Trim whitespace from all text fields.
- Uppercase ticker symbols.
- Normalize common symbol variants only when needed: convert dots to hyphens only when the connector uses hyphenated share-class format, such as BRK.B to BRK-B.
- Preserve exchange suffixes for non-US listings unless the connector resolves them differently.
- Drop rows with no usable security key unless holding name is the only available identifier.
- Convert weights to percentage-point units. If source returns 0.0754 for 7.54%, convert to 7.54; if source returns 7.54, leave as 7.54. Detect units by inspecting schema and min/max values.
- Do not force total listed weights to 100%. Preserve actual listed-weight sums and disclose them.
- Security matching priority: normalized ticker symbol, then CUSIP/ISIN/FIGI or other stable ID, then normalized holding name. The methodology must state which key was used. For the normal case, write: I normalized holdings by ticker symbol.

## Core metrics
For every pair A and B, calculate holdings_count_a, holdings_count_b, shared_holdings_count, pct_of_a_holdings, pct_of_b_holdings, a_exposure_in_shared_holdings, b_exposure_in_shared_holdings, overlap_coefficient, a_weight_outside_b, and b_weight_outside_a. Use percentage-point units for weights and exposures.

Formulas:
- Shared holdings count = |S| where S is the intersection of normalized identifiers in A and B.
- % of ETF A holdings = |S| / |H_A| * 100.
- % of ETF B holdings = |S| / |H_B| * 100.
- ETF A exposure in shared holdings = sum of A weights for identifiers in S.
- ETF B exposure in shared holdings = sum of B weights for identifiers in S.
- Overlap coefficient = sum across shared holdings of min(w_A_i, w_B_i).
- ETF A-only exposure = sum of A weights for identifiers in H_A minus H_B.
- ETF B-only exposure = sum of B weights for identifiers in H_B minus H_A.
- Absolute weight difference = abs(w_A_i - w_B_i).
- ETF B overweight for shared holding i = w_B_i - w_A_i.

## Concentration diagnostics
- For each primary ETF calculate top_10_holdings_weight, top_15_holdings_weight for in-depth analysis, weight_in_shared_holdings, weight_outside_other_etf, largest_holding_weight, and optionally top_10_as_pct_of_listed_weight.
- For the primary pair calculate top_shared_holdings_min_weight_sum, top_shared_holdings_a_weight_sum, and top_shared_holdings_b_weight_sum for the top shared holdings table rows shown.

## Position-level tables for two primary ETFs
- Top shared holdings: sort by minimum shared weight descending. Show 10 rows for Quick comparison, 15 rows for Standard analysis, and 15 to 25 rows for In-depth analysis as space allows. Columns: Rank, Holding, Symbol, ETF A weight, ETF B weight, Minimum shared weight, Abs. weight difference.
- Biggest overweights: by default show the second ETF's biggest overweights versus the first ETF, sorted by weight_b - weight_a among shared holdings where B weight exceeds A weight. Flip direction only if context indicates the first ETF is the proposed addition. Columns: Rank, Holding, Symbol, ETF A weight, ETF B weight, ETF B minus ETF A.
- Largest first-ETF-only positions: sort by ETF A weight descending among holdings in A but not B. Columns: Rank, Holding, Symbol, ETF A weight.
- Largest second-ETF-only positions: sort by ETF B weight descending among holdings in B but not A. Columns: Rank, Holding, Symbol, ETF B weight.

## Multi-ETF behavior
- Preserve the first two tickers as the detailed primary comparison.
- If more than two ETFs are provided, compute pairwise overlap metrics for every pair and add a multi-ETF section.
- Show a pairwise overlap table with Pair, Shared holdings, % of first ETF holdings, % of second ETF holdings, First ETF shared-weight exposure, Second ETF shared-weight exposure, and Overlap coefficient.
- Identify holdings common to all ETFs.
- Identify top holdings by aggregate exposure across all ETFs.
- Keep detailed position-level tables focused on the first two tickers unless depth is In-depth analysis.
- For In-depth analysis, add highest-overlap pair, lowest-overlap pair, common-to-all holdings table, and one short diversification interpretation across the basket.

## Analysis depth
- Quick comparison sections: Executive summary, ETF metadata, Quantitative overlap, Top shared holdings with 10 rows, Largest ETF-only positions for each primary ETF with 5 to 10 rows, Interpretation, Methodology and caveats. Keep concise but quantitative.
- Standard analysis sections: Executive summary, ETF metadata, Quantitative overlap, Concentration diagnostics, Top shared holdings with 15 rows, Biggest overweights with 10 rows, Largest ETF-only positions for each primary ETF with 10 rows, Interpretation, Methodology and caveats. Write like a strong analyst note.
- In-depth analysis sections: Executive summary, ETF metadata, Quantitative overlap, Concentration diagnostics, Top shared holdings with 15 to 25 rows, Biggest overweights with 10 to 15 rows, Largest first-ETF-only positions with 10 to 15 rows, Largest second-ETF-only positions with 10 to 15 rows, optional sector/style diagnostics only if structured labels exist, Interpretation, Methodology, Caveats and limitations. Match a detailed analyst-style ETF overlap output.

## Final report requirements
- Use Markdown.
- Title for two ETFs: # ETF Overlap Analysis for {ETF_A} and {ETF_B}
- Title for more than two ETFs: # ETF Overlap Analysis for {ETF_A}, {ETF_B}, and {N} additional ETFs
- Executive summary must include whether overlap is high, moderate, or low in economic terms; shared holdings count; percent of each ETF's holding count represented by shared holdings; each ETF's weight in shared holdings; overlap coefficient; and a plain-English interpretation of what one ETF adds relative to the other.
- ETF metadata table columns: ETF, Fund name, Holdings count, Total listed weight, Holdings as-of date. If metadata fields are missing, add a paragraph explaining what was missing and which analysis remains qualitative.
- Quantitative overlap table columns: Pair, Shared holdings, % of ETF A holdings, % of ETF B holdings, ETF A exposure in shared holdings, ETF B exposure in shared holdings, Overlap coefficient. Follow with one explanatory paragraph.
- Concentration diagnostics table for Standard and In-depth analyses with Top 10 holdings weight, Weight in holdings shared with the other ETF, Weight outside the other ETF, and interpretation.
- Top shared holdings table columns: Rank, Holding, Symbol, ETF A weight, ETF B weight, Minimum shared weight, Abs. weight difference.
- Biggest overweights section title: Biggest {ETF_B} overweights by default. Include a one-paragraph interpretation.
- Largest ETF-only sections: Largest {ETF_A}-only positions and Largest {ETF_B}-only positions, each followed by a short paragraph explaining what the only-position sleeve contributes.
- Optional sector/style diagnostics only if structured sector, industry, or asset-class labels are available for most holdings. If not available, write that sector/style comments are qualitative and based on largest named positions rather than a full sector-classified aggregation.
- Interpretation should be 3 to 6 paragraphs covering economic overlap, asymmetry, what ETF A adds, what ETF B adds, and whether adding one to the other increases diversification or mostly increases concentration. Tailor to Additional context without changing quantitative methodology.
- Methodology must include: I normalized holdings by {ticker symbol / security identifier / holding name}, using the returned ETF holdings files as the security-level source. Shared holdings were calculated as the intersection of normalized identifiers.
- Methodology must include: The count overlap equals shared holdings divided by each ETF's total holding count. The exposure overlap equals the sum of each ETF's weights for holdings also present in the other ETF. The overlap coefficient equals \(\sum_i \min(w_{A,i}, w_{B,i})\) across shared holdings.
- Caveats must mention missing fields, holdings dates, listed-weight totals, and include: This is informational overlap analysis, not investment advice.

## Formatting style
- Use Markdown tables for all tabular output.
- Use percentage values with three decimal places for portfolio weights and overlap metrics when source precision supports it.
- Use one decimal place for count percentages if needed.
- Never use approximate language for computed values. Avoid about, roughly, around, or ~ for computed metrics.
- Use plain-English portfolio interpretation, not only formulas.
- Keep title and section order consistent across runs.
- Do not include raw CSV dumps or tool-call JSON.
- Preserve citations or claim links for finance tool outputs if supported. If not supported, include data provenance in methodology and caveats.

## Error and fallback copy
- Holdings unavailable: I could not retrieve constituent-level holdings for {TICKER}. I can only complete an ETF overlap analysis when at least two funds have holdings with security identifiers and weights. Please try another ETF ticker or provide a holdings file.
- Top holdings only: The holdings source returned only top holdings for {TICKER}, not the full constituent file. I can still calculate overlap across the returned holdings, but the count overlap and total exposure overlap may understate the true full-fund overlap.
- Sector labels unavailable: The holdings data did not include sector labels, so I did not calculate sector-level overlap. The sector/style discussion is qualitative and based on the largest named positions.
- Weight totals differ from 100%: Listed weights summed to {total_weight}% for {TICKER}. Differences from 100% may reflect cash, rounding, omitted buckets, derivatives, short positions, or data-provider treatment.

## Regression scenarios to satisfy
- VOO vs QQQ, In-depth analysis: detailed report, current holdings, QQQ largely embedded in VOO by exposure if current data supports it.
- SPY vs VOO, Quick comparison: very high overlap, high overlap coefficient, concise report.
- VTI vs VXUS, Standard analysis: low direct security overlap, clear diversification interpretation, caveats if international identifiers are inconsistent.
- VOO vs QQQ plus VTI and SCHD, In-depth analysis: detailed primary comparison plus multi-ETF pairwise section.
- Invalid ticker VOO vs NOTANETF: ask for correction or stop with clear unresolved-ticker message.
- Duplicate ticker VOO, QQQ, additional VOO, VTI: deduplicate VOO and compare VOO, QQQ, and VTI.

## Non-goals
- Do not provide personalized investment advice, buy/sell recommendations, portfolio optimization, brokerage-account connection, tax-lot analysis, capital-gains analysis, or tax-loss harvesting.
- Do not compare expense ratios, AUM, liquidity, bid/ask spreads, or tracking error unless future versions add those data sources explicitly.
- Do not fabricate sector, industry, holdings-date, AUM, expense-ratio, holdings, or metric data.
- Do not hard-code VOO vs QQQ holdings or metrics.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`.
