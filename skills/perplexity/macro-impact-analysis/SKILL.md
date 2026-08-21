---
name: macro-impact-analysis
description: "Analyze how macro and geopolitical forces affect a company through quantified transmission channels, scenarios, historical episodes, and leading indicators."
metadata:
  perplexity:
    display_name: "Macro impact analysis"
---
# Macro Impact Analysis

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `ticker` (Company ticker (or tickers for a portfolio))

OPTIONAL — assume the default (or omit) unless the user specifies:
- `holdings_file` (Holdings file (portfolio mode)) Ask the user to attach the file(s) in chat. No default — omit silently if the user does not provide it.
- `macro_focus` (Macro & geopolitical focus areas) — Leave blank to let the evidence rank all channels; selected areas are always addressed, even if immaterial. Options: `rates` (Rates & central banks); `inflation` (Inflation & input costs); `fx` (FX & the dollar); `commodities` (Commodities & energy); `tariffs_trade` (Tariffs & trade policy); `geopolitics` (Geopolitics, sanctions & conflicts); `elections_policy` (Elections & regulatory regimes); `consumer_cycle` (Consumer & business cycle); `credit` (Credit conditions & spreads). No default — omit silently if the user does not provide it.
- `lookback` (Historical lookback window) Options: `5-years` (5 years); `10-years` (10 years); `15-years` (15 years). Default: `10-years`.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Morningstar, PitchBook) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Macro Impact Analysis

Analyze how macro and geopolitical forces affect a specific company (or portfolio) through quantified transmission channels. This is not a generic macro essay: every macro observation must connect to this company's revenue, costs, margins, cash flow, or valuation through an explicit, evidence-tested channel. Do not frame the work as any single investor's style. The core questions are: which macro and geopolitical forces actually move this company's fundamentals and stock, by how much per unit of macro move, which widely discussed forces do NOT matter for it, and what should the investor monitor?

## Analytical Standard

1. **Channel-first, not theme-first**: Start from the company's actual disclosed exposures, not from the macro headlines of the day. A tariff or rate cycle only matters if a transmission channel exists and is material.
2. **Quantified transmission**: For every channel that survives screening, estimate direction, magnitude per unit macro move, lag, and confidence — with the same lead/lag evidentiary discipline used in institutional key-driver analysis (lagged correlations, sign consistency, outlier sensitivity, sample-size honesty).
3. **Falsifiability and false-positive rejection**: Saying what does NOT matter is half the value. Explicitly reject channels that are narratively popular but show small exposure, weak or unstable historical evidence, or effective hedging.
4. **Realized, not theorized**: Ground forward views in how this company (or close analogs) actually performed through comparable historical macro regimes.
5. **Priced-in discipline**: A macro impact is only investable if it differs from what consensus estimates and the current valuation already embed.
6. **Quote-backed claims**: When management quantifies a macro impact (FX headwind, tariff cost, rate sensitivity), capture the verbatim quote with speaker and quarter.
7. **Exactness**: Show the exact figure, never "~". Every number sourced; market and macro data carries an as-of date. Never fabricate links or data; where data is missing, state the limitation.

## Phase 1: Setup and Data Collection

Use finance tools first for market, company, and macro data. Resolve the ticker(s) before any ticker-dependent pull, derive all as-of parameters from the run date, and save all raw tabular pulls as CSVs to a `finance_data/` working directory before analysis.

### Data sources (one or more, collected at intake)

`data_source` is a set of one or more sources collected at intake: draw on every selected provider rather than routing to a single one. Options: Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc (alt data), and Guidepoint (expert calls); the default selection is Perplexity Finance, FactSet, Daloopa, Carbon Arc, and Guidepoint. Perplexity Finance built-in tools are the always-available baseline.

1. **BYOL availability check**: Premium providers are bring-your-own-license. For each selected provider, verify its connector is connected before planning pulls. If a provider is selected but not connected, proceed without it and add one line to the deliverable's sourcing note naming what it would have added — e.g., “Daloopa was selected but is not connected; connecting it would add as-reported segment and KPI history for estimating realized macro sensitivities.” Never stall or fail the run over an unavailable provider.
2. **Provider of record per domain**: Assign each data domain to the strongest selected-and-connected provider and state the provider under every exhibit: fundamentals, segment, and KPI history — Daloopa > FactSet > Morningstar > built-in; consensus estimates and revisions — FactSet > built-in; macro series — the built-in macro snapshot/history tools are the macro system of record for this skill; high-frequency demand/transaction signals — Carbon Arc; expert qualitative evidence on transmission — Guidepoint; private-company data (rarely load-bearing here) — PitchBook > built-in.
3. **Complementarity and cross-validation**: Providers cover different evidence layers — filings and Daloopa give the disclosed/reported record, Carbon Arc the high-frequency real-time read, Guidepoint the practitioner ground truth. Cross-check every load-bearing figure (stated FX sensitivity, floating-rate debt %, geographic revenue mix, consensus EPS) against a second source when two selected providers cover it; where providers disagree materially, show both values with the basis difference explained — never silently average.
4. **Series integrity**: One time series or table column = one provider basis. Never splice providers mid-series without an explicit footnote at the splice point.

**Portfolio mode**: If multiple tickers or a holdings file are provided, run the exposure mapping (Phase 2) for each material position (positions ≥ 3% of portfolio weight, or the top 10 by weight), aggregate exposures at the portfolio level weighted by position size, and note where positions offset each other (e.g., long an importer and an exporter of the same input). Run the transmission, episode, and scenario phases on the aggregated portfolio channels, with per-holding detail for the largest contributors to each channel.

### Company-side data (per ticker, constrained to the selected lookback window)

1. **Financials**: Quarterly revenue, gross profit, operating income, EBITDA, net income, EPS, margins, FCF, capex, and interest expense/income for the full lookback (up to 40 quarters where available).
2. **Segments and geography**: Segment and geographic revenue, segment profit, and company KPIs via the segments tool (use the segments capability for segment/geographic/KPI data, not the general financials tool). This is the primary source for revenue-by-geography and implied currency mix.
3. **Ratios and valuation**: Valuation multiples, margins, returns, and leverage time series; peer multiples for context.
4. **Estimates**: Consensus forward revenue, EPS, EBITDA, and margins for the next 4-8 quarters and 2-3 fiscal years — this is the baseline scenarios are measured against.
5. **Earnings history**: Actuals vs consensus and post-earnings moves, to identify quarters where macro was the stated driver of a surprise.
6. **Transcripts (prepared remarks AND Q&A)**: The last 8-12 earnings call transcripts. Extract every management quantification of macro impact — FX headwinds/tailwinds in points of growth, tariff costs in dollars or margin bps, commodity/freight cost inflation, rate-driven demand commentary, hedging program updates — as verbatim quotes with speaker and quarter. Then, for each candidate macro factor, build a factor-by-quarter language track across the trailing ~8 quarters: how management characterizes the sensitivity, whether the characterization has shifted, and what analysts pushed on in Q&A. This is the “stated sensitivity” record; Phase 3 tests what management SAYS the sensitivity is against what the reported numbers show.
7. **Filings (primary source for exposure structure)**: From the latest 10-K/20-F (and 10-Qs where updated), pull: Item 7A quantitative and qualitative disclosures about market risk (companies often state their own FX/rate/commodity sensitivity — e.g., "a 10% strengthening of the dollar would reduce revenue by $X"); the debt footnote (fixed vs floating mix, maturity schedule, upcoming refinancing wall, weighted average rate); the derivatives/hedging footnote (instruments, notional amounts, hedge horizon, designated vs economic hedges); geographic revenue and long-lived asset tables; customer financing or captive finance disclosures; supplier concentration, manufacturing footprint, and country-of-origin/import-content commentary; government/regulatory dependence (subsidies, price regulation, licenses). Also review the 10-Qs across the trailing ~8 quarters and recent 8-Ks for updated hedging notionals, debt issuance or refinancing, and new tariff/sanctions/risk-factor language — exposure structure changes faster than the annual filing cadence. Pull earnings press releases and earnings presentations as well: quantified FX, commodity, and tariff bridges often appear only in the presentation deck, not the transcript.
8. **Prices**: Weekly adjusted prices for the ticker, 4-5 peers (via the peer tool), SPY/QQQ, and a relevant sector ETF over the lookback.

### Macro-side data

Use the macro snapshot tool for current readings and the macro history tool (approximately 15,000 series across 196 countries) for time series over the lookback. Pull only series with a plausible channel to the company — typically 10-20 series drawn from:

- **Rates**: Policy rates, 2y/10y sovereign yields, and yield-curve slope for the company's key markets.
- **FX**: The dollar index and specific currency pairs matching the company's revenue and cost geographies.
- **Commodities**: Oil, natural gas, and the specific metals, ag, or energy inputs named in the company's cost disclosures.
- **Inflation**: CPI and PPI headline plus the specific components matching the company's input basket and pricing (e.g., PPI industrial chemicals, CPI new vehicles).
- **Demand and activity**: Manufacturing/services PMIs for relevant countries, retail sales, industrial production, consumer confidence, housing starts/permits where relevant.
- **Labor**: Unemployment, wage growth where labor cost or consumer income matters.
- **Credit**: High-yield and investment-grade spreads where financing conditions matter for the company or its customers.

### Provider-specific evidence (when selected and connected)

- **Daloopa**: Pull as-reported segment-level and KPI history at maximum granularity for the full lookback. This is the preferred input for Phase 3: realized sensitivities estimated on segment/KPI series (a specific geography's revenue against its currency pair, a commodity-linked segment's margin against the input price) are sharper than consolidated regressions. Preserve Daloopa document/series references for traceability.
- **Carbon Arc**: Pull high-frequency demand/transaction signals for the company and its industry — the earliest read on whether a macro channel is actually biting in the current quarter (e.g., is rate pressure visible in transaction volumes yet?). Reconcile the latest signals against the most recent reported KPIs and consensus for the in-progress quarter, and carry the result into Phase 5 (what's priced in) and Phase 6 (monitoring).
- **Guidepoint**: Search recent expert interviews on the company AND its peers, suppliers, and customers for real-world transmission evidence: is pricing pass-through actually sticking, are order patterns and backlogs shifting with rates/FX/tariffs, is hiring slowing? Include reverse references — experts interviewed about other companies who mention the target. Attribute each insight by expert role and interview date, and use it to corroborate or challenge the statistical betas in Phase 3.

### Geopolitical and policy news

Analyze macro and geopolitical news broadly over the trailing 12-18 months as it bears on this company: elections and policy platforms in the company's major markets, tariff and trade-policy actions, sanctions and export controls, active conflicts affecting supply routes or demand, regulatory regime changes, and subsidy programs. Prefer primary sources — official government and central-bank releases, trade-authority announcements, and the company's own disclosures — over commentary; cite all public web sources inline. Use public web sources only where finance tools are insufficient.

## Phase 2: Exposure Mapping and Channel Ranking

Map the company's actual macro exposures from disclosures, then rank them. Assess each of these six exposure families:

1. **Revenue geography and currency**: Revenue by region and inferred billing currency vs the company's reporting currency; translation vs transaction exposure; local pricing power to offset FX.
2. **Input-cost structure**: Decompose COGS and opex into commodity, energy, freight, purchased-component, and labor intensity using filings and transcript evidence; note pass-through mechanisms (surcharges, contract escalators, pricing lag).
3. **Rate sensitivity**: Balance-sheet side (floating vs fixed debt %, refinancing wall, cash yields, pension) and demand side (customer financing/captive finance, financed purchases, project IRR sensitivity, housing-linked demand).
4. **Demand cyclicality**: Consumer vs enterprise vs government mix; discretionary vs non-discretionary; short-cycle vs long-cycle/backlog-buffered; operating leverage into a downturn.
5. **Trade, tariffs, and supply chain**: Manufacturing footprint by country, import content, exposure to existing or proposed tariff lists and export controls, sanctions exposure, single-country supplier concentration.
6. **Policy, regulation, and geopolitics**: Election outcomes, subsidies and industrial policy, price regulation, tax regimes, conflict exposure to assets, routes, or demand.

For each exposure family, record both the **stated** exposure (Item 7A sensitivities, hedging footnotes, transcript commentary) and the **realized** exposure implied by the reported history (segment, KPI, and margin behavior against the relevant macro series). A material divergence between the two — management downplaying a sensitivity the numbers show, or overstating one the numbers do not — is itself a finding to carry into Phase 3.

Score each candidate channel on: (a) exposure size — the % of revenue, COGS, EBIT, or debt actually touched; (b) plausible macro move size over 12-24 months; (c) historical evidence strength (Phase 3 pre-screen); (d) hedging or structural offset; (e) whether the market is already focused on it. Rank and select the **3-6 channels that matter**. For everything else, write an explicit **"What does NOT matter"** table stating each rejected channel, why it is rejected (small exposure, effective hedge, natural offset, no historical relationship), and the evidence. If the user specified macro focus areas, always address them — but if the evidence says a requested area is immaterial for this company, say so directly rather than manufacturing significance.

## Phase 3: Transmission Quantification (per surviving channel)

For each of the 3-6 material channels, quantify the transmission using Python (pandas, scipy.stats, numpy, statsmodels where available):

1. **Historical beta with lag testing**: Correlate quarterly (or annual where reporting frequency requires) changes in the relevant company variable — revenue growth, gross margin, EBIT margin, segment KPI, EPS — against changes in the macro series at lag 0, and at leads of 1-4 quarters (macro at T vs company variable at T+1…T+4). Report Pearson and Spearman with p-values, the best-fit lag, and a cross-correlation profile from -4 to +4 quarters for the top channels. Where sample size permits (generally 20+ observations), run simple regressions controlling for overall demand (e.g., market or peer-basket growth) and note Granger-style causality evidence; where it does not, say so plainly and do not overclaim. Where segment-level or KPI history is available (Daloopa preferred, built-in segments tool otherwise), estimate betas at the segment/KPI level — a region's revenue against its currency pair, a commodity-linked segment's margin against the input price — and aggregate to the company level; segment-level fits are typically cleaner and more attributable than consolidated regressions.
2. **Sign consistency and outlier sensitivity**: Report how often the expected sign holds, and re-run excluding the 1-2 most extreme quarters to flag relationships driven by a single event (e.g., 2020).
3. **Magnitude per unit macro move**: Express the beta in investor-usable units — e.g., "each 10% trade-weighted dollar appreciation has historically corresponded to a 2.3pp revenue-growth headwind and 40bp of gross-margin pressure at a 1-2 quarter lag." Reconcile the statistical estimate against (a) the company's own Item 7A stated sensitivity and (b) management's quantified guidance commentary; where they disagree, explain which carries more weight and why. Also score management's track record as a base rate: across the trailing ~8 quarters, how often did guided macro impacts (FX points of growth, tariff dollars, commodity margin bps) match the subsequently realized figure within a stated tolerance? Weight the stated sensitivity in your net estimate according to that hit rate.
4. **Hedging attenuation**: From the hedging footnote and transcript commentary, state notional coverage as a % of exposure, hedge horizon, and instrument type. Be explicit about what hedges do: cash-flow hedges typically delay rather than eliminate FX and commodity impact (state the effective delay in quarters), fixed-rate debt mutes rate exposure until the maturity wall, and translation exposure is usually unhedged. Restate the net-of-hedge beta and the horizon over which protection rolls off.
5. **Confidence rating**: Assign each channel High/Medium/Low confidence based on sample size, stability across rolling windows, statistical strength, disclosure corroboration, economic logic, and — where Guidepoint evidence exists — whether practitioners corroborate the transmission in practice. Present all channels in a single transmission scorecard table.

## Phase 4: Historical Episode Analysis

Test the channels against realized history — how the company actually performed, not how theory says it should have. Select 3-5 macro regimes from the lookback window relevant to the surviving channels (choose from episodes such as the 2013 taper tantrum, the 2014-16 dollar surge and commodity collapse, the 2018-19 US-China tariff escalation, the 2020 pandemic shock, the 2021-23 inflation and rate-hiking cycle, the 2022 sanctions and energy shock, or region-specific analogs). For each episode document:

1. The macro move: exact magnitude and duration of the relevant series' move.
2. Realized company impact: revenue growth, margin, and EPS deltas vs the pre-episode trend; stock performance absolute and vs peers and the market; estimate revisions through the episode.
3. Management response: pricing actions, hedging changes, supply-chain or footprint shifts, guidance behavior — with transcript quotes.
4. Recovery profile: quarters to margin and estimate recovery.

If the company's listed history is too short to cover an episode (recent IPO, post-spin), use 1-2 close operating analogs, name them, justify the analogy, and state its limits. Conclude the phase with what the episodes confirm or contradict about the Phase 3 betas.

## Phase 5: Forward Scenarios and What's Priced In

Construct 2-4 internally coherent macro scenarios over the next 12-24 months. One must be a base case anchored to current consensus macro expectations and market-implied paths; the alternates should be the coherent regimes most relevant to the surviving channels (e.g., soft landing with dollar weakness; reflation with commodity spike; hard landing with credit stress; tariff/geopolitical escalation). For each scenario:

1. Specify exact macro variable paths for every channel input (policy rate, FX level, commodity price, PMI level, tariff rate) — coherent across variables, not independent shocks.
2. Apply the Phase 3 net-of-hedge betas per channel to estimate revenue, margin, EPS, and FCF impact vs consensus — include the cash-flow channels (working-capital swings from input-cost moves, interest expense on floating and soon-to-refinance debt, capex deferral) — showing per-channel contributions and the aggregate as a bridge. State lag timing (which quarters absorb the impact). Present all scenarios in one consolidated quantified scenario table — macro shock → channel → estimated EPS/FCF impact — with every assumption stated in the table itself, not buried in text.
3. Estimate the valuation impact: the earnings effect plus a disciplined multiple effect where rates or risk appetite are part of the scenario (justify any multiple change against the company's own multiple-vs-rates history from Phase 3, not an assumed rule of thumb).
4. Assign a rough probability with rationale.

Then assess **what the market currently prices**: compare scenario EPS paths against consensus estimates; the current multiple against its own history and peers; market-implied macro paths (futures-implied policy rates, forward FX, commodity curves where available) against each scenario's assumptions; and recent sell-side and positioning commentary. Where Carbon Arc is connected, weigh its latest high-frequency demand signals against consensus for the in-progress quarter — an early divergence is the most direct evidence that a scenario is under- or over-priced. Identify the asymmetry: which scenario is under-priced, and what the risk/reward skew looks like. In portfolio mode, present scenario impacts at the portfolio level with the top single-name contributors and any internal offsets.

## Phase 6: Leading Indicators to Monitor

For each surviving channel, define 1-3 leading indicators with, for each: the exact series or release name and source; the current reading with as-of date (from the macro snapshot tool or primary release); the threshold or rate-of-change that would signal the channel activating; the historical lead time to company impact (from Phase 3 lag testing); and the update cadence. Distinguish leading indicators from coincident ones — the monitor should be built on series that move before the company's results do. Include event-based triggers for geopolitical channels (election dates, tariff review deadlines, sanctions decisions) with their scheduled dates. Where Carbon Arc is connected, include its high-frequency demand signal for the top demand-linked channel alongside the official series — it typically leads reported results by the most.

## Phase 7: Charts

Create 8-10 matplotlib charts with DPI 150, figsize 12x7, seaborn-v0_8-whitegrid style. Palette: #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553. Chart titles state the insight, not just the data (e.g., "Dollar Strength Hits Revenue With a Two-Quarter Lag", not "USD vs Revenue"). Required set (adapt to channels):

1. Exposure map: revenue by geography/currency and cost-structure decomposition (stacked bars).
2. Channel ranking: materiality scores with kept vs rejected channels distinguished.
3. One overlay chart per top channel (up to 3): company variable vs macro series with the lag visually clear.
4. Cross-correlogram for the top 3 channels.
5. Historical episode exhibit: indexed stock and fundamentals vs peers through the most relevant episode, with the episode window shaded.
6. Scenario bridge: per-channel EPS impact waterfall for the highest-conviction non-base scenario.
7. Scenario EPS paths vs consensus.
8. Monitoring panel: current readings vs thresholds for the leading indicators.

Save all charts as PNGs.

## Phase 8: Output Creation

Honor the selected output format. When no format is selected or the run is ambiguous, default to **PDF** — this is a narrative-plus-evidence analysis. All formats must present the same underlying dataset and conclusions.

### PDF Report (default)

A professional research report with this section order:

1. Executive summary — the 3-6 channels that matter, headline net-of-hedge sensitivities, the scenario skew, and the single most important thing to monitor.
2. Exposure map and channel ranking — including the "What does NOT matter" table.
3. Channel deep dives — one section per channel: exposure evidence, transmission beta with lag and confidence, the stated-vs-realized sensitivity reconciliation (Item 7A and management guidance vs the statistical estimate, with the guidance hit-rate), hedging attenuation, management quotes, and Guidepoint/Carbon Arc corroboration where available.
4. Historical episodes.
5. Forward scenarios and what's priced in — scenario table, per-channel bridges, asymmetry assessment.
6. Monitoring dashboard — indicators, current readings, thresholds, cadence.
7. Methodology, sources, and disclosures — data windows, statistical caveats, sample-size limits.

### XLSX

Workbook with sheets: Executive Summary; Exposure Map; Channel Scorecard; Transmission Analysis (full correlation/lag tables and the stated-vs-realized reconciliation); Hedging Detail; Historical Episodes; Scenarios (with per-channel impact bridges as live formulas driven by editable macro assumptions); What's Priced In; Monitoring; Macro Data; Company Data; Sources & Methodology. Follow house workbook formatting: Calibri; dark teal #1B474D headers with white text; currency as `$#,##0` with unit-bearing headers; percentages as `0.0%`; blue text for hardcoded inputs, formulas black; freeze panes on tables; source notes on every sheet. Derived values must be live Excel formulas so scenario assumptions can be flexed. After building, run the recalculation script `python skills/office/xlsx/scripts/recalc.py <output_file>` and fix all formula errors before sharing.

### PDF Presentation

Slide-style landscape PDF per the presentation block below: one insight per slide, following the report section order with the channel scorecard and scenario bridge as the core exhibits.

### Dashboard

Private interactive dashboard with panels for the exposure map, channel scorecard, per-channel transmission detail (chart + beta + hedge status), episode explorer, scenario toggles with live P&L impact, and the monitoring panel with current readings vs thresholds.

## Phase 9: Conclusion

Answer the core question directly in the response:

1. **What matters**: The ranked channels with net-of-hedge sensitivity per unit macro move and confidence.
2. **What does not matter**: The rejected channels and why — be direct.
3. **Where the risk is now**: Which scenario the current macro/geopolitical setup most resembles, and the estimated impact vs consensus.
4. **What is priced in**: Whether consensus and the multiple already reflect the base case, and where the asymmetry sits.
5. **What to monitor**: The top 3-5 leading indicators with thresholds and cadence, plus scheduled geopolitical events.
6. **What would change the view**: The 2-3 datapoints that would invalidate the channel ranking or scenario skew.

Be direct about uncertainty: small samples, unstable rolling correlations, and regime breaks (a company that re-shored its supply chain in 2023 should not be scored on its 2018 tariff beta without adjustment — say so). Share the selected output file or deployed dashboard and present the conclusion in the response.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When the `data_source` selection includes any of `daloopa`, `factset`, or `morningstar`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:
1. Make raw figures clickable wherever the provider returns a URL, deep link, report link, document reference, filing link, cell-level reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source/source-note cells where feasible, and include a `Sources & Traceability` or `Source Map` sheet with provider, company/security/entity, metric, period, as-of timestamp, provider metric/series/document ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, KPI tile, chart datapoint, tooltip, or detail drawer that displays a raw provider figure must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Daloopa document, filing, and company-series links/references; FactSet entity, metric, document, and any returned URL/deep link; Morningstar security, datapoint, report, and URL references.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity/security identifier, metric or series ID/name, period, as-of timestamp, and document/report identifier where available, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures. Derived calculations should link or reference the source cells/figures used in the calculation.

---

## Output format: PDF (Presentation)

When the user selects output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF. Do NOT produce the standard portrait memo; this format replaces it.

### Page setup
- Orientation: landscape
- Page size: US Letter landscape (11" x 8.5") or widescreen 16:9 (13.333" x 7.5") — default to 16:9 for a modern deck feel
- Margins: 0.5"–0.75" on all sides
- One logical slide per page

### Slide anatomy
- Title bar at top: concise, insight-led headline (e.g., "Revenue grew 23% in Q4" not "Revenue Overview"). 24–32 pt, bold.
- Optional subtitle/deck name and slide number in a thin footer.
- Body: a single clear idea per slide. Prefer tables, charts, and labeled visuals over long prose. Bullets ≤ 5 per slide, ≤ 12 words each.
- Leave generous whitespace. Do not pack a slide edge-to-edge with text.

### Typography and style
- Sans-serif throughout (Calibri or Arial). Body 14–18 pt, captions 10–12 pt.
- Single accent color plus neutrals. No decorative graphics, clip art, or stock imagery.
- Numeric values right-aligned and use tabular figures. Percentages, currency, and units formatted consistently across the deck.
- Charts: direct-label data, minimize gridlines, ≤ 5 series, encode meaning with color rather than decoration.

### Recommended slide order (adapt to the workflow)
1. Cover — title, subject entity, date, author/firm.
2. Executive summary — 3–5 bullets with the core takeaway.
3. Key metrics / scorecard table.
4. Core analysis slides — one idea per slide, each with a headline insight.
5. Supporting exhibits — comps, scenarios, market maps, etc.
6. Risks / watch items.
7. Recommendation or next steps (omit explicit buy/sell calls where the workflow prohibits them).
8. Appendix — methodology, source list, disclosures.

### Quality bar
- Every slide must answer: "so what?" in the title.
- Fact-check every number against its provider-of-record among the selected data sources.
- Verify no text overflow, wrapping mid-word, or low-contrast color combinations before delivery.
- Output is intended for external distribution; treat it as client-ready.

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

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## MANDATORY QA REVISIONS (v2, 2026-07-21) — these override any conflicting guidance above

1. **Financial number formatting (all outputs)**: Follow standard finance sign and numbering conventions. Abbreviate large values — never write out every digit of a billion-scale number in text, tables, or slides. Default unit is $ in millions with thousands separators (e.g., "$3,423M" or "$3.4B", never "$3,423,192,847"). State the unit once per table/exhibit header ("$ in millions unless otherwise noted") rather than repeating full figures per cell. Negative values in parentheses, e.g., (412). Multiples as 0.0x; percentages to one decimal; per-share amounts in dollars and cents.
2. **Source quality bar**: Cite only professional-grade sources: company filings (10-K/10-Q/8-K, S-1, proxy), earnings transcripts, investor-relations materials, connected premium data providers, primary regulatory/statistical agencies, and top-tier financial press (WSJ, FT, Bloomberg, Reuters). NEVER cite or rely on Zacks, Motley Fool, Seeking Alpha, Simply Wall St, GuruFocus, Benzinga, StockTwits, aggregator blogs, SEO content farms, or similar unprofessional sources — neither in prose nor in citation lists. If an aggregator merely relays another outlet's reporting (e.g. "Benzinga, citing The Information"), cite the original outlet directly instead; never cite the aggregator, even as a relay.
3. **Spreadsheet standards (any XLSX deliverable)**:
   - Hide gridlines on every sheet (Excel: View > uncheck Gridlines / Alt+W,V,G; openpyxl: `ws.sheet_view.showGridLines = False`).
   - Financial-model color convention: blue font = hardcoded inputs/assumptions; black font = formulas and same-sheet references; green font = links pulling from other sheets.
   - Summary/output tabs must contain NO hardcoded numbers (no blue on the summary page) — every figure must be a formula or cell reference linked to the underlying data/calculation tabs.
   - Never bury constants inside formulas as in-cell calculations (e.g., a black cell containing `=1234*0.25` that references no other cells). Every driver lives in its own labeled input cell (blue), and formulas reference cells only.

## Attached materials

Any files supplied through the kickoff form arrive as attachments on this turn and are
downloaded into the workspace. Read them before starting external research and treat them
as primary source input. If no files were attached, proceed using the available finance
and data connectors plus web research, and say so rather than asking the user to re-upload.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `office/pdf`, `office/pptx`, `office/xlsx`, `website-building/webapp`.
