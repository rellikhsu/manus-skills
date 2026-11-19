---
name: "perplexity:key-driver-analysis"
description: "Identify which fundamentals, estimates, peers, macro factors, and guidance changes actually move a stock."
metadata:
  perplexity:
    display_name: "Key driver analysis"
---
# Key driver analysis

# Institutional Stock Key Driver Analysis

Identify what makes a stock go up and down using a rigorous institutional public-equity process. Do not frame the work as any single investor's style, do not use a named-investor label, and do not imply the analysis depends on one person's philosophy. The quality should come from disciplined driver decomposition, evidence weighting, lead/lag testing, guidance and estimate analysis, valuation attribution, and a practical monitoring framework.

The core question is: which variables actually explain, anticipate, or catalyze the stock's movement, and which commonly cited factors do not matter?

## Analytical Standard

Use the best practices common across prominent public-market investors:

1. **Variant perception**: State the consensus narrative and the likely variant view. Identify what the market appears to be pricing in, then test which data would confirm or break that view.
2. **Business model decomposition**: Build a driver tree from revenue units, pricing, mix, take rate, retention, margins, capex, working capital, free cash flow, and segment economics.
3. **Leading indicator discipline**: Separate predictors from coincident variables. The most important output is not the highest same-quarter correlation; it is what tends to lead future stock movement.
4. **Estimate revision focus**: Analyze consensus revenue, EPS, EBITDA, operating income, and free cash flow revisions because estimate direction often drives multiple expansion and contraction.
5. **Guidance-to-actuals tracking**: Treat forward guidance as a catalyst and leading indicator. Compare guidance ranges and midpoint changes to actual results and post-earnings stock moves.
6. **Catalyst mapping**: Identify the events, metrics, and surprises that trigger outsized one-day and one-quarter moves.
7. **Valuation bridge**: Separate fundamental improvement from multiple expansion or compression. Explain whether the stock moved because earnings power changed, the multiple changed, or both.
8. **Peer and macro controls**: Control for market beta, peer group performance, sector rotation, rates sensitivity, dollar/commodity exposure, and other relevant macro proxies.
9. **False-positive rejection**: Explicitly call out variables that look important narratively but show weak, unstable, or non-leading evidence.
10. **Monitorability**: End with a practical signal dashboard: what to track, how often, thresholds that matter, and what would change the thesis.

## Phase 1: Setup and Data Collection

Use finance tools first for market and company data. Always resolve the ticker before data pulls, derive all as-of parameters from the run date, and download all CSV files to a `finance_data/` directory before analysis. When the user selects a non-Perplexity preferred source, use that source when available; otherwise proceed with Perplexity Finance and clearly note the fallback.

Gather the following, constrained to the selected time horizon where possible:

1. **Price data**: Weekly closing prices for the ticker; end-of-quarter close; one-day post-earnings moves; total return if available.
2. **Fundamentals**: Quarterly revenue, gross profit, operating income, EBITDA where available, net income, EPS, gross/operating/net margins, FCF, operating cash flow, capex, working capital, share count, SBC, and other relevant standardized financial metrics, up to 20 quarters where available.
3. **Segments and KPIs**: Quarterly segment revenue, segment operating income, mix, and company-specific operating KPIs such as ARPU, subscribers, MAU/DAU, GMV, take rate, bookings, units, traffic, capacity, utilization, retention, churn, RPO, ARR, NRR, same-store sales, backlog, or other sector-specific metrics.
4. **Peers**: Weekly prices for 4-5 closest peers, using the finance peer tool when available, plus QQQ/SPY and a relevant sector ETF when useful.
5. **Macro proxies**: TLT or 10-year Treasury proxy, Fed Funds Rate where available, dollar index, commodity inputs, oil, semiconductor index, housing starts, PMI, unemployment, or other macro variables relevant to the company.
6. **Earnings history**: EPS and revenue actuals versus consensus estimates, operating income or EBITDA surprises when available, and post-earnings one-day and one-week price moves.
7. **Management guidance**: Pull the last 8-12 earnings call transcripts where available. Extract next-quarter and full-year guidance ranges for revenue, gross margin, operating margin/income, EPS, EBITDA, FCF, capex, and company-specific KPIs. Match guidance to actual results to compute beat/miss and guide-up/guide-down.
8. **Analyst estimates**: Pull consensus estimates for revenue, EPS, EBITDA, operating income, FCF, or sector-specific KPIs. Track estimate revision direction and magnitude over time where available.
9. **Valuation metrics**: Collect P/E, EV/Revenue, EV/EBITDA, P/FCF, free-cash-flow yield, gross-profit multiple, or sector-relevant multiples. Gather enough history to separate earnings growth from multiple change.
10. **Transcript evidence**: Pull management commentary and analyst Q&A from recent calls to identify which debates are currently salient.

Use public web sources only after finance tools are insufficient, and cite public web sources inline when they are used.

## Phase 2: Driver Tree and Hypothesis Formation

Before running statistics, create a qualitative driver tree:

1. Define the business model in one paragraph.
2. List the plausible drivers of stock movement in five groups: fundamentals, segments/KPIs, estimates/guidance, valuation/multiple, and external factors.
3. State the initial hypothesis for the top 3 likely drivers and why each could be leading, coincident, or lagging.
4. Identify likely false positives that investors may talk about but that need evidence.
5. Define the measurement method for each driver, including data frequency, transformation, and expected sign.

Do not let the initial hypothesis determine the conclusion. Use the statistical and event evidence to update it.

## Phase 3: Correlation and Lead/Lag Analysis

Using Python with pandas, scipy.stats, numpy, and statsmodels where available, compute:

### Contemporaneous Correlations

1. Quarterly price changes for the stock using end-of-quarter close.
2. QoQ changes for every fundamental metric, segment metric, macro variable, valuation metric, estimate metric, and peer stock.
3. YoY growth rates for fundamentals and YoY stock returns.
4. Pearson and Spearman correlations with p-values between stock price changes and all variables in the same quarter.
5. Rolling 8-quarter and 12-quarter correlations where sample size allows, to identify whether driver relationships are stable or regime-dependent.

### Leading Indicator Analysis

This is the key output. Do not stop at same-quarter correlations.

1. **1-quarter lead**: Correlate each variable at time T with stock price change at T+1. This answers: if this metric improves this quarter, does the stock tend to go up next quarter?
2. **2-quarter lead**: Correlate each variable at time T with stock price change at T+2 for slower-moving drivers.
3. **Cross-correlation function**: For the top 5 candidate fundamental, segment, guidance, estimate, and macro drivers, compute cross-correlations at lags -4 to +4 quarters. Plot the cross-correlogram to visually identify optimal lead/lag.
4. **Granger causality tests**: For the top 10 candidate variables, run Granger causality with 2-4 lags using `statsmodels.tsa.stattools.grangercausalitytests`. Note sample-size limitations and avoid overclaiming where observations are sparse.
5. **Partial correlations or simple regressions**: Where data permits, test whether a candidate driver remains useful after controlling for QQQ/SPY, peer basket performance, and rates proxy.
6. **Direction consistency**: For each top driver, calculate how often the expected sign holds. A useful driver should not just have a high correlation; it should work in a reasonable percentage of observations.
7. **Outlier sensitivity**: Re-run top-driver correlations excluding the largest one or two stock-return quarters to flag relationships driven by a single event.

### Guidance and Estimate Analysis

1. **Guidance level**: Correlate forward guidance midpoint for revenue, operating income, EBITDA, EPS, or KPI guidance with stock performance through the guided period.
2. **Guidance revision**: Compare this quarter's guidance midpoint versus the prior quarter's midpoint and correlate the change with immediate post-earnings move and next-quarter stock return.
3. **Beat versus guide**: Compare actual results to prior guidance low, midpoint, and high end. Identify whether the stock rewards clearing the high end, merely beating midpoint, or raising future guidance.
4. **Estimate revisions**: Track whether consensus estimates are revised up or down. Correlate revision direction and magnitude with subsequent-quarter stock returns and multiple expansion/compression.
5. **Narrative inflection**: Use transcripts to identify whether guidance changes are driven by demand, pricing, mix, margins, cost cuts, FX, macro, product cycles, or one-time items.

### Earnings Reaction Analysis

1. Correlate EPS, revenue, operating income, EBITDA, FCF, and KPI surprise magnitude with one-day and one-week post-earnings moves.
2. Correlate change in forward guidance with post-earnings moves; emphasize guidance surprise because it often matters more than reported beat/miss.
3. Identify the biggest positive and negative earnings reactions and write a short event read-through for each: what mattered, what did not, and what changed in forward expectations.
4. Distinguish reported-quarter surprise from forward-quarter revision.

### Valuation and Multiple Bridge

1. Decompose stock returns into earnings/FCF/EBITDA growth versus multiple expansion or compression where data permits.
2. Compare the company's multiple change to peer and market multiple changes.
3. Identify whether the key driver is fundamental acceleration, improved quality/durability, estimate revisions, lower discount rate/rates, peer sympathy, or pure multiple rerating.
4. Include a concise bridge explaining how much of the stock move is tied to fundamentals versus valuation.

Rank all drivers by predictive usefulness, not just raw correlation magnitude. Use a scoring framework that considers lead correlation strength, p-value, sample size, sign consistency, outlier sensitivity, economic logic, transcript support, and monitorability.

## Phase 4: Chart Generation

Create 10-12 matplotlib charts with DPI 150, figsize 12x7, and seaborn-v0_8-whitegrid style. Use this chart palette: #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553. Chart titles should state the insight, not just the data, for example `Forward Guidance Revisions Lead Stock Returns` rather than `Guidance vs Price`.

Required charts:

1. Stock price versus the #1 leading fundamental or KPI driver, with the lead visually clear.
2. Stock price versus operating margin, FCF margin, or the most relevant profitability metric.
3. Cross-correlogram for the top 3 leading indicators, with bars showing correlation at each lag.
4. Normalized peer performance comparison, base=100.
5. Stock price versus TLT, rates proxy, commodity proxy, or other relevant macro factor.
6. Post-earnings price moves versus EPS, revenue, operating income, EBITDA, or KPI surprise scatter.
7. Segment revenue/profit breakdown over time.
8. Correlation heatmap with separate panels for contemporaneous versus lag-1 relationships.
9. Management guidance versus actuals bar chart.
10. Forward guidance trajectory versus stock price, with shaded guidance range where available.
11. Guidance surprise or estimate revision magnitude versus next-quarter stock return scatter.
12. Valuation multiple bridge or multiple history versus peers.

Save all charts as PNGs.

## Phase 5: Output Creation

Honor the selected output format. When no selected format is available or the run is ambiguous, default to XLSX because the analysis is data-heavy and should remain auditable.

### Excel Workbook

Build a professional Excel workbook with openpyxl. Derived workbook values should use Excel formulas where practical so they remain auditable. Create these sheets:

1. **Executive Summary**: Key findings in 3-5 bullets; ranked tables for leading indicators, contemporaneous drivers, earnings catalysts, and valuation drivers; thesis verdict; and sheet navigation links.
2. **Driver Scorecard**: All candidate drivers scored by lead correlation, same-quarter correlation, p-value, sign consistency, sample size, outlier sensitivity, economic logic, transcript support, and monitorability.
3. **Leading Indicators**: The most important sheet. Include a table of all variables with lag-1, lag-2, cross-correlation, and Granger causality results. Highlight variables that statistically and economically lead price.
4. **Guidance & Estimates**: Guidance versus actuals, guidance revision history, estimate revision history, beat/miss rates, and charts showing guidance/estimate changes versus stock moves.
5. **Valuation Bridge**: Multiple history, peer multiple comparison, and decomposition of stock returns into fundamentals versus multiple change.
6. **Correlation Matrix**: Full contemporaneous and lagged correlation matrix with conditional formatting and top 5 highlighted in each panel.
7. **Quarterly Data**: Time series of all quarterly data with YoY growth rates and QoQ changes, formatted as an Excel table with data bars.
8. **Price vs Fundamentals**: Embedded charts showing stock versus key fundamental and KPI drivers.
9. **Peers & Macro**: Normalized peer comparison, rate or macro sensitivity charts, and peer correlation table.
10. **Earnings Reactions**: Earnings surprise table with post-earnings moves, scatter charts, and event notes for the largest moves.
11. **Segment Deep Dive**: Full segment data, revenue mix percentage, growth rates, and margin contribution by segment.
12. **Sources & Methodology**: Provider traceability, methodology notes, caveats, sample-size limitations, and data dictionary.

Workbook formatting requirements:

- Calibri font.
- Dark teal #1B474D headers with white text.
- Currency as `$#,##0` with unit-bearing headers such as `Revenue ($M)`.
- Percentages as `0.0%`.
- Blue text for hardcoded inputs.
- Freeze panes on tables.
- Column A width 3 margin on report sheets.
- Source notes on every sheet: `Source: SEC filings and market data via selected provider unless otherwise noted`.

After building the workbook, run the recalculation script: `python skills/office/xlsx/scripts/recalc.py <output_file>`. Fix any formula errors before sharing.

### PDF Report

Create a concise research report with the same conclusion, ranked tables, chart package, methodology, and source notes. Include inline source links for all public web sources and source traceability for provider figures where available.

### PDF Presentation

Create a slide-style PDF with one insight per page. Use the same chart package and conclusion. Each page should have a clear takeaway headline, one chart or table, and a short interpretation.

### Dashboard

Build and deploy a private interactive dashboard with ranked driver tables, chart filters, correlation heatmaps, earnings event cards, guidance/estimate trackers, valuation bridge, and methodology notes.

## Phase 6: Institutional Investor Conclusion

Write a concise conclusion answering: `What makes this stock go up and down?` Structure it as:

1. **Leading indicators**: The 2-3 metrics that best predict future price movement, with lead correlation, sign consistency, and any Granger or cross-correlation support. These are the signals to monitor.
2. **Contemporaneous drivers**: What moves with the stock in real time, such as market beta, peer correlation, rates sensitivity, or sector factor exposure.
3. **Earnings catalysts**: What specifically triggers big post-earnings moves, such as guidance surprise, operating income beat versus high end, KPI surprise, or estimate revisions.
4. **Valuation driver**: Whether multiple expansion/compression, earnings growth, FCF growth, or peer rerating explains the stock's move.
5. **What is priced in**: Summarize the market's likely embedded expectations and what would need to happen for upside or downside.
6. **What does not matter**: Commonly assumed drivers that show weak, unstable, non-leading, or economically implausible evidence.
7. **Monitoring framework**: Specific metrics and thresholds to watch, update cadence, source, and how far in advance each signal tends to matter.
8. **What would change the view**: The 2-3 datapoints that would invalidate or materially alter the conclusion.

Be direct about uncertainty. If sample size is too small, say so. If evidence conflicts, explain the conflict and identify what evidence carries the most weight.

Share the selected output file or deployed dashboard and present the conclusion in the response.

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## Provider Traceability Requirement

When `data_source` is `daloopa`, `factset`, or `morningstar`, or when provider-specific data is used, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:

1. Make raw figures clickable wherever the provider returns a URL, deep link, report link, document reference, filing link, cell-level reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source/source-note cells where feasible, and include a `Sources & Traceability` or `Source Map` sheet with provider, company/security/entity, metric, period, as-of timestamp, provider metric/series/document ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, KPI tile, chart datapoint, tooltip, or detail drawer that displays a raw provider figure must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Daloopa document, filing, and company-series links/references; FactSet entity, metric, document, and any returned URL/deep link; Morningstar security, datapoint, report, and URL references.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity/security identifier, metric or series ID/name, period, as-of timestamp, and document/report identifier where available, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures. Derived calculations should link or reference the source cells/figures used in the calculation.

---

## PDF Formatting and Private Artifact Standards

Apply these standards whenever the requested output includes `pdf`, `pdf_presentation`, or any presentation-style PDF output:

1. Alignment: section titles/headings and section body text must both be left-aligned to the same content edge. Do not center section titles except on a cover/title page. Keep captions, source notes, and exhibit titles aligned to the same left grid as the body.
2. Layout grid: use one consistent margin and content grid across the entire PDF. Each section title, paragraph block, table, and chart should snap to that grid so the document feels intentionally aligned.
3. Table sizing: all primary tables must use the same overall width across the output. In portrait PDFs, primary tables should span the full text/content width. In PDF presentations, primary tables should use the same exhibit width and left edge on each slide. If a table has fewer columns, keep the same total table width and adjust column proportions rather than shrinking the table.
4. Chart sizing: charts must use consistent dimensions across comparable pages/slides. Primary charts should share the same width, height, left edge, and caption/source placement unless a deliberate full-page exhibit is required.
5. Numeric formatting: keep numeric values right-aligned in tables and use consistent units, decimals, currency, percentages, and date formats throughout the PDF.
6. Private internal artifacts: never show internal workspace artifacts from data pulls or intermediate processing in any user-facing output, notes, citations, appendices, dashboards, PDFs, XLSX files, filenames, metadata, tooltips, source maps, methodology sections, or final response text. This includes workspace paths, sandbox paths, temporary filenames, cache files, raw provider/API response files, logs, intermediate CSV/JSON/parquet/XLSX exports, extraction screenshots, notebook/script names, and any `file://`, `/home/user/workspace`, `/tmp`, or sandbox-only references. These artifacts are private implementation details and must be omitted or replaced with user-safe source labels.
7. Allowed references: user-provided filenames may be referenced when useful, and public/source URLs or provider-native traceability links may be cited when available. Do not confuse legitimate source citations with private internal artifacts.
8. Final visual/privacy QA: before delivery, inspect the PDF and any accompanying files for left-aligned titles and body text, consistent table widths, consistent chart dimensions, aligned captions/source notes, no text overflow, no mid-word wrapping, no cramped or misaligned exhibits, and no private internal workspace artifact exposure.

## Excel File Integrity Check

When the requested output includes `xlsx` or an Excel workbook, run an Excel integrity check before sharing the file:
1. Verify the workbook file exists, is accessible, and can be opened successfully by a standard XLSX reader without corruption warnings or repair prompts.
2. Reopen the saved workbook after creation, for example with openpyxl and/or LibreOffice in headless mode, and confirm all expected worksheets are present.
3. If Excel, LibreOffice, openpyxl, or another validation tool reports the workbook is corrupt, unreadable, inaccessible, or requires repair, fix and regenerate the workbook before sharing.
4. Do not call `share_file` or otherwise deliver the XLSX until the workbook is confirmed accessible, openable, and not requiring repair.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `investment-research`, `finance/finance-markets`, `office/xlsx`.
