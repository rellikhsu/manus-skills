---
name: "perplexity:management-kpi-credibility-tracker"
description: "Track management guidance, KPI commitments, milestones, and time-bound forward-looking statements against revisions and actual outcomes in an auditable XLSX."
metadata:
  perplexity:
    display_name: "Management KPI credibility tracker"
---
# Management KPI & Credibility Tracker

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `ticker` (Stock ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `lookback` (Lookback window) Options: `4-quarters` (Last 4 quarters); `8-quarters` (Last 8 quarters); `12-quarters` (Last 12 quarters); `16-quarters` (Last 16 quarters). Default: `8-quarters`.
- `commitment_scope` (Commitment types to track) — Leave empty to track all commitment types. Options: `financial-guidance` (Financial guidance (revenue, EPS, margins, FCF)); `kpi-targets` (Operating KPI targets (users, units, NRR, ARPU)); `milestones` (Milestones (launches, approvals, capacity)); `capital-allocation` (Capital allocation (buybacks, dividends, deleveraging)); `long-term-targets` (Long-term / investor-day targets). No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `daloopa` (Daloopa); `factset` (FactSet); `morningstar` (Morningstar); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `daloopa`, `factset`, `carbon_arc`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Morningstar, Guidepoint) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `xlsx` (XLSX); `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `dashboard` (Dashboard). Default: `xlsx`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Management KPI & Credibility Tracker

Build a quantitative, time-series record of every commitment a management team has made — guidance items, KPI targets, milestones, and time-bound forward-looking statements — and score each one against the subsequent actual outcome. Do not frame the work as any single investor's style. The core question is: how much should an investor trust this management team's forward statements, in which direction does the team systematically bias (sandbag or overpromise), and how does the team behave when it is about to miss?

This is an evidence ledger, not a narrative exercise. Every scored outcome must trace back to a verbatim quote or a filed disclosure on one side and a reported actual on the other. The single highest-signal finding is the quietly-dropped commitment — a target that stops being mentioned without ever being formally withdrawn — so the workflow includes a mandatory completeness check that guarantees no extracted commitment is silently lost.

## Phase 1: Setup and Data Collection

Use finance tools first for market and company data. Resolve the ticker before any ticker-dependent pull, derive all as-of parameters from the run date, and save raw tabular pulls as CSVs to a `finance_data/` working directory before analysis. `data_source` is a set of one or more sources collected at intake: the user may choose any combination of Perplexity Finance (`perplexity_finance`, built-in), Daloopa (`daloopa`), FactSet (`factset`), Morningstar (`morningstar`), Carbon Arc (`carbon_arc`, alt data), and Guidepoint (`guidepoint`, expert calls); the defaults are `perplexity_finance`, `daloopa`, `factset`, and `carbon_arc`. Every premium provider is bring-your-own-license, so for each selected source check whether its connector is actually connected. If a source is selected but not connected, continue without it and add exactly one line to the deliverable's sourcing note naming what it would have added to this run — e.g., "Daloopa was selected but is not connected; connecting it would add a filing-linked, as-reported guidance and actuals history with per-figure source links for the register." Never stall or fail the run over an unavailable premium source; the built-in Perplexity Finance tools are the always-available baseline.

Assign a provider-of-record per data domain from the selected-and-connected sources and state it on every exhibit and sheet: guidance-vs-actual history, fundamentals, and KPI actuals — Daloopa > FactSet > Morningstar > built-in; consensus estimates and revisions — FactSet > built-in; alt-data demand/transaction signals — Carbon Arc; expert qualitative evidence — Guidepoint. These sources are complementary, not redundant: Daloopa anchors what management actually printed, FactSet shows what the Street believed, Carbon Arc shows what demand is doing right now, Guidepoint explains why. Cross-validate every load-bearing figure in the register (guided values, actuals, deltas feeding the scorecard) across at least two sources where coverage overlaps; where providers disagree materially, show both values and explain the basis difference — never silently average. One register column or time series = one provider basis; never splice providers within a series without an explicit footnote at the splice point.

1. **Lookback window**: Use the user-selected lookback; default is the last 8 quarters of earnings events. The window defines which prints you mine for commitments. Commitments made inside the window whose due dates fall after the most recent actual are tracked as `Open` — never scored prematurely.
2. **Transcripts**: Pull the earnings call transcript for every quarter in the lookback window using the earnings transcript tool. These are the primary commitment source: prepared remarks and Q&A both count. Management often guides verbally in Q&A — a CFO answering "we'd expect that to be roughly flat sequentially" has issued guidance that will never appear in the press release — so mine Q&A exchanges for numbers, dates, and hedged commitments with the same rigor as prepared remarks. If a transcript for a quarter is unavailable, state the gap and fall back to the earnings press release and prepared-remarks documents from investor relations.
3. **Shareholder letters and guidance disclosures**: For companies that publish shareholder letters, guidance tables in earnings press releases, investor-day targets, or 8-K guidance updates, collect these for the same window from IR pages and SEC filings (cite each inline). Sweep all three guidance artifact classes for every print — the press release (and its guidance table), the earnings presentation/slide deck (outlook slides often carry ranges, bridges, and KPI targets the release omits), and the transcript's prepared remarks and Q&A — and record which artifact each commitment came from; a discrepancy between the deck and the spoken guide is itself register-worthy. Mid-quarter guidance revisions (pre-announcements, conference updates, withdrawn guidance 8-Ks) must be captured — they are revision events, not new commitments.
4. **Public filings (commitment sweep)**: In addition to transcripts and guidance artifacts, mine the periodic SEC filings themselves for commitments over the same window: 10-K/10-Q MD&A outlook and liquidity/capital-resources sections (stated targets, capital-allocation, cost-program, and margin commitments), 8-Ks beyond guidance updates (restructuring plans, material agreements, management changes that reset accountability), and the proxy statement (DEF 14A) for the incentive-plan metrics and targets management is actually paid on. Register any commitment that appears only in a filing exactly as if it had been spoken on a call, tagged with document type, section, and filing date, and cite each filing inline. Cross-check guidance against the proxy's incentive targets — a guide set above (or below) the bonus-plan threshold is a credibility datapoint; flag divergences in the register.
5. **Actuals**: Pull EPS and revenue actuals versus consensus, surprise magnitude, and post-earnings one-day moves from the earnings history tool for the window plus the four quarters after the window start (so early-window guidance has actuals to match). Pull segment revenue and operating KPIs (ARPU, subscribers, DAU/MAU, GMV, units, bookings, NRR, backlog, or the company's sector-specific equivalents) from the segments tool, and non-GAAP actuals (adjusted EPS, adjusted EBITDA, FCF) from the adjusted metrics tool. Pull quarterly statements from the company financials tool for margin, capex, and buyback actuals. When Daloopa is selected and connected, it is the provider-of-record for the guidance-vs-actual history: pull its filing-linked, as-reported series for every guided metric — the guides, the revisions, and the printed actuals — covering at least ~8 quarters and more where the history exists (extend before the lookback start so early-window guides have actuals and prior-guide context). Use Daloopa's per-figure source links to anchor the register's guided and actual values, and score against as-reported figures, not later restatements — commitments are judged against the numbers management actually printed at the time, with restatements noted separately.
6. **Consensus context**: Pull consensus estimates as of each guidance date where available, so each guide can be positioned versus the Street (guiding above/below consensus is part of revision behavior). When FactSet is selected and connected, it is the provider-of-record for consensus: for each guidance event, capture the consensus level immediately before the guide, the size and speed of the post-guide estimate revision, and where consensus settled relative to the guide (converged to it, above it, or discounting it). This measures whether the Street believed management — a guide the sell side immediately fades is itself a credibility datapoint; log it per guidance event so Phase 5 can analyze it.
7. **Calendar**: Pull the earnings schedule to anchor every print to an exact date and to identify the next upcoming print for the monitoring section.
8. **Carbon Arc alt-data (when selected)**: pull demand/transaction signals for the company and its closest comps covering both (a) past quarters, to backtest how well the signal tracked reported KPIs before trusting it forward, and (b) the current, still-open guidance period. The core question is trajectory versus the current guide: is the in-quarter signal tracking ahead of or behind what the guide implies? Record the implied ahead/behind read with mapping assumptions and panel-coverage caveats stated; it feeds the current-guide analysis in Phases 5 and 7 and can corroborate or challenge a suspect reported actual in Phase 3.
9. **Guidepoint expert evidence (when selected)**: pull recent expert-call takeaways on the company and its close peers that touch guided topics — demand tone, capacity or launch timelines, regulatory odds — including reverse-references where experts on other companies mention the target. Use them as qualitative context on whether specific `Open` commitments look achievable and to explain quiet-drop clusters; expert opinion never overrides a ledger-scored outcome.

Use public web sources only after finance tools are insufficient; prefer SEC filings, earnings transcripts, IR materials, and official company disclosures, and cite them inline. Never use low-quality aggregators.

## Phase 2: Commitment Extraction — Build the Register

Read every transcript, letter, and guidance disclosure in the window and extract EVERY item in scope. Do not sample or summarize; the register's value is completeness. Extract:

1. **Quantitative guidance**: next-quarter and full-year ranges or point estimates for revenue, EPS (state GAAP vs non-GAAP basis), gross/operating margin, EBITDA, operating income, FCF, capex, opex, tax rate, share count, and any guided KPI. Record low, midpoint, and high; for point guides, record the point as midpoint. For "at least" / "exceed" language, record the floor and flag the open-ended top.
2. **KPI commitments**: subscriber/user/unit targets, store or capacity openings, NRR/retention targets, take-rate or ARPU trajectories, cost-savings run-rates — anything management committed to with a number and a period.
3. **Milestones**: product launches, regulatory submissions/approvals, plant/datacenter completions, geographic launches, partnership or integration dates, deleveraging or ratings targets, buyback/dividend commitments.
4. **Time-bound forward-looking statements**: any statement of the form "we expect X by Q4", "on track to double Y by fiscal 2026", "will exceed Z this year", "remain confident we'll reach…". If it has (a) a claim and (b) an explicit or inferable due period, it belongs in the register.

For every commitment record, capture all of the following — no exceptions:

- **Verbatim quote** (exact words, no paraphrase; ellipses allowed only for length, never to change meaning)
- **Speaker and title** (e.g., CFO Jane Doe); note whether prepared remarks or Q&A
- **Print/date made**: the earnings event or disclosure it came from and its exact date
- **Commitment type** taxonomy: `financial-guidance`, `kpi-target`, `milestone`, `capital-allocation`, `long-term-target`
- **Metric and basis** (e.g., non-GAAP diluted EPS; constant-currency revenue growth — flag FX-adjusted bases explicitly)
- **Guided value/range** (low/mid/high, or the qualitative milestone description)
- **Due period/date** (fiscal quarter, fiscal year, or explicit date; note when the due period is inferred rather than stated)
- **Firmness**: `explicit` (numeric, dated) vs `soft` (directional, hedged — "roughly", "aiming for"). Soft commitments are tracked but scored separately; do not let hedged language inflate or deflate the hit rate silently.

Assign each commitment a stable ID (e.g., `TICKER-2025Q2-07`) so revisions and outcomes chain to it. When the same target is restated in later prints, log those as revision events against the original ID, not as new commitments — this chain is what makes quiet drops detectable.

Honor the user's selected commitment scope: extract all categories, but if the user narrowed scope, score and report only the selected categories and note the exclusion in methodology.

## Phase 3: Outcome Matching

For every commitment whose due period has a reported actual:

1. **EPS/revenue guidance** → match against the earnings history actuals for the due period (respecting GAAP vs non-GAAP basis; use the adjusted metrics tool for non-GAAP). Record the actual, the print and date on which the actual was reported, the delta versus guidance midpoint (absolute and %), and position versus the range (above high / within / below low).
2. **Segment and operating KPIs** → match against the segments tool and adjusted metrics tool for the due period. If a KPI is disclosed only in the press release or 10-Q/10-K, pull it from the filing and cite it.
3. **Milestones** → verify against filings, press releases, and subsequent transcripts: did the event happen by the due date? Record the evidence (filing/announcement and date) or its absence.
4. **Basis integrity**: never score a constant-currency guide against a reported-currency actual, or a non-GAAP guide against a GAAP actual, without an explicit reconciliation note. If the bases cannot be reconciled, mark the outcome `unverifiable` with the reason — do not force a score.
5. If an actual is genuinely unavailable (metric discontinued, disclosure changed), state the limitation. A discontinued disclosure that coincides with a deteriorating metric is itself a finding — flag it.
6. **Definition-change flags**: when management re-bases a KPI — redefines "active user", changes segment composition, switches gross to net, shifts fiscal-period boundaries, or changes the non-GAAP adjustment set — flag every affected commitment. Score against the definition in force when the commitment was made if the data allows; otherwise mark `unverifiable — definition changed` and record both definitions with their effective dates. A re-basing that conveniently converts a would-be miss into a `Met` is a red flag: call it out explicitly, and count definition changes as their own line in the Phase 5 scorecard.

## Phase 4: Status Scoring and the Completeness Check

Score every commitment with exactly one status:

- **Beat** — actual above the high end (or milestone delivered early)
- **Met** — actual within the guided range (or milestone delivered on time); for point guides, within a stated tolerance (default ±1% for revenue-scale metrics, ±1 cent for EPS; state the tolerance in methodology)
- **Missed** — actual below the low end (or milestone not delivered by the due date and not formally moved)
- **Pushed Out** — management explicitly moved the due date before it passed; record old and new dates and the quote making the change
- **Withdrawn** — formally withdrawn or replaced, with the withdrawal quote/filing and date
- **Quietly Dropped** — see below
- **Open** — due period not yet reported; no score

**Quietly-dropped detection (mandatory completeness check).** This is the highest-signal output and it must be systematic, not incidental:

1. Build a mention matrix: commitments as rows, every subsequent print in the window as columns. For each cell record `reaffirmed`, `revised`, `resolved` (actual reported / milestone hit), `withdrawn`, or `absent` — with the supporting quote for any non-absent cell.
2. A commitment is **Quietly Dropped** when it goes absent for two or more consecutive prints without resolution or formal withdrawal, and either its due date has passed or intervening disclosures make achievement implausible. Record the last-mention date and quote — the silence gap is the evidence.
3. **Reconciliation**: every commitment extracted in Phase 2 must appear in the final register with a terminal status or `Open`. Count extracted vs scored + open; if the counts do not tie, find the lost rows before proceeding. No commitment may be silently omitted because matching was hard — hard-to-match commitments get `unverifiable` with an explanation, never deletion.

Also log **revision events** as their own record type: each time a guide is raised, lowered, reaffirmed, or narrowed, capture date, prior mid, new mid, direction, magnitude, and quarters remaining until the due period.

## Phase 5: Credibility Scorecard Analytics

Compute, with exact figures and stated sample sizes:

1. **Hit rate by type**: Beat+Met as % of scored commitments, broken out by commitment type, by metric (revenue, EPS, margin, KPI, milestone), by horizon (next-quarter vs full-year vs multi-year), and by firmness (explicit vs soft). Show numerators and denominators — a 100% hit rate on 3 observations is not a track record, and you must say so. Treat these as base rates per KPI and per horizon: the operative outputs are statements like "hit 7 of 8 next-quarter revenue guides but 1 of 4 multi-year KPI targets", because the metric- and horizon-specific base rate is what gets applied to the current guide in item 9.
2. **Sandbagging / overpromise bias**: for quantitative guides, the distribution of (actual − guidance midpoint) / |midpoint|. Report mean, median, and the share of outcomes above the high end vs below the low end, per metric. A consistent +2–4% revenue beat pattern is sandbagging; investors should model guidance with that haircut/uplift — state the implied adjustment explicitly. Distinguish a stable bias (predictable, usable) from an erratic one (low information content). Test whether the bias is systematic rather than incidental: report sign-consistency (share of quarters beating the midpoint) alongside mean/median and dispersion, and say plainly when the sample is too small to distinguish bias from noise.
3. **Revision behavior**: for every guide-down, how many quarters before the due period did it come, and was it one clean cut or repeated drip-cuts on the same target? Late, repeated guide-downs are the classic low-credibility signature; early single cuts preserve credibility. For guide-ups, note whether raises exceed the amount already beaten (true raise vs mechanical flow-through).
4. **Quiet-drop and push-out rates**: quietly-dropped + pushed-out as % of all non-open commitments, and which topics they cluster in — clustering reveals where the business is actually struggling before the P&L shows it. Include the definition-change count from Phase 3 here: which KPIs were re-based, when, and whether the re-basing coincided with deteriorating performance on the old definition.
5. **Trend**: rolling 4-quarter hit rate and bias across the window. Is credibility improving or deteriorating? Tie inflections to events (new CFO, segment reorganization, macro shock) with transcript evidence.
6. **Speaker attribution** where meaningful: CEO vs CFO statements can differ systematically in ambition; report only if the sample supports it.
7. **Composite credibility score (0–100)** with fixed weights so runs are comparable: hit rate 40; bias stability and magnitude 20; quiet-drop/push-out penalty 20; guide-down timeliness 10; milestone delivery 10. Show the sub-scores and arithmetic. The score is a summary, not a verdict — the register rows are the evidence.
8. **Market reaction context** (secondary): using post-earnings moves from earnings history, note whether the market already prices this team's bias (e.g., muted reaction to routine sandbagged beats). When FactSet consensus history is available, add the Street-belief read: per guide, did estimates converge to the guide, sit above it, or discount it — and when guide and consensus diverged, which one the actual validated. A persistent guide-vs-consensus gap that consensus keeps winning quantifies how much the market already haircuts this team.
9. **Credibility-weighted read of the current guide**: for every `Open` guide, produce an expected actual by applying the metric- and horizon-specific base rate and median bias adjustment from items 1–2 to the guide midpoint, and state the implied range. Where Carbon Arc is selected, reconcile this against the in-quarter alt-data trajectory (ahead/behind the guide); where FactSet is selected, position it against current consensus. Show the inputs separately, then the combined read — e.g., "guide mid $2.10B; base-rate/bias-adjusted $2.16B; alt-data tracking modestly ahead; consensus $2.14B; credibility-weighted read $2.15–2.18B" — and flag disagreements loudly: a habitual sandbagger whose alt-data is tracking behind the guide is the highest-alert combination this workflow can produce.

Call out explicitly where the evidence is thin, where statuses rest on judgment (inferred due dates, basis reconciliations), and which findings would not survive one or two reclassifications. Do not present narrative impressions of management as findings — only the ledger counts.

## Phase 6: Output Creation

Honor the selected `output_format`. When ambiguous or unspecified, default to XLSX — the analysis is data-heavy and must remain auditable. All formats present the same underlying dataset.

### Excel Workbook (primary)

Build a professional workbook with openpyxl. Every derived figure (deltas, hit rates, bias stats, composite score) must be a live Excel formula referencing the register rows, not a hardcoded snapshot, so the workbook stays auditable. Sheets, in order:

1. **Executive Summary**: composite score with sub-scores; headline hit rates; bias direction and implied guidance adjustment; count of quietly-dropped and pushed-out commitments with the top 3 highest-signal rows quoted; the credibility-weighted read of the current guide (with the alt-data ahead/behind read where Carbon Arc is selected); trend verdict; navigation links.
2. **Commitment Register**: one row per commitment — ID, date made, source print/document, speaker & title, verbatim quote, type, metric & basis, firmness, guided low/mid/high (or milestone description), due period, actual, actual print & date, delta vs mid ($/units and %), range position, status, and source reference (link where available). Freeze the header, add autofilter, and conditional-format status (Beat/Met green-family, Missed/Quietly Dropped red-family, Pushed Out/Withdrawn amber).
3. **Revision Timeline**: one row per revision event — commitment ID, date, prior mid, new mid, direction, magnitude %, quarters to due period, quote.
4. **Mention Matrix**: commitments × subsequent prints with reaffirmed/revised/resolved/withdrawn/absent cells — the completeness-check evidence.
5. **Credibility Scorecard**: hit-rate tables by type/metric/horizon/firmness with n's, bias distribution stats, revision-timing table, Street-belief table (guide vs consensus per event, where FactSet is selected), definition-change log, rolling trend, composite score build-up, and the current-guide read build-up.
6. **Quietly Dropped & Watchlist**: every quietly-dropped and pushed-out commitment with last-mention date, silence gap, and what to listen for on the next call; plus all `Open` commitments due at the next 1–2 prints.
7. **Methodology & Sources**: extraction rules, scoring definitions and tolerances, basis-reconciliation notes, reconciliation counts (extracted = scored + open + unverifiable), sample-size caveats, data dictionary, provider-of-record assignments per exhibit, provider traceability, and the sourcing note listing any selected-but-unconnected providers and what connecting each would add.

Workbook formatting: Calibri font; dark teal #1B474D headers with white text; currency as `$#,##0` with unit-bearing headers such as `Revenue ($M)`; percentages as `0.0%`; blue text for hardcoded inputs, formulas black; freeze panes on tables; hide gridlines on report-facing sheets; column A width 3 margin on report sheets; source notes on every sheet. After building, run the recalculation script: `python skills/office/xlsx/scripts/recalc.py <output_file>` and fix all formula errors before sharing.

### Charts (all formats)

Create matplotlib charts with DPI 150, figsize 12x7, seaborn-v0_8-whitegrid style, palette #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553. Titles state the insight (e.g., `Management Sandbagged Revenue by a Median 2.8% Over 8 Quarters`, not `Guidance vs Actuals`):

1. Guide-vs-actual delta distribution (histogram or dot plot per metric, range shown).
2. Hit rate by commitment type with n labels.
3. Rolling 4-quarter hit rate and bias trend.
4. Guide-down timing chart (quarters-before-due for each cut).
5. Commitment status waterfall or stacked composition over time, quietly-dropped highlighted.
6. Current-guide exhibit: guide range vs credibility-weighted expected print vs consensus vs in-quarter alt-data trajectory (include only the series whose sources are selected and connected).

### PDF Report

Concise memo: composite score and verdict, the scorecard tables, the chart package, the top quietly-dropped exhibits with quotes, and methodology with source citations. Include the full commitment register as an appendix table.

### PDF Presentation

Slide-style PDF, one insight per page with headline takeaway, using the same charts and tables (see the PDF Presentation block below).

### Dashboard

Private interactive dashboard: scorecard tiles, filterable commitment register, mention-matrix heatmap, bias distribution chart, revision timeline, quietly-dropped watchlist cards, and methodology panel, with source links on raw figures.

## Phase 7: Conclusion

Answer the core question directly:

1. **Credibility verdict**: the composite score, the headline hit rate, and the direction and stability of bias — in one or two sentences an investor can act on.
2. **How to use it in modeling**: the explicit haircut or uplift to apply to this team's guidance by metric (e.g., "model revenue at guide-mid +2.5%, EPS at high end; treat multi-year KPI targets as aspirational — 1 of 4 delivered").
3. **What's priced in**: whether the market already trades this team's bias, based on reaction patterns.
4. **Highest-signal findings**: the quietly-dropped and drip-cut items, quoted, and what they imply about where the business is under pressure.
5. **What to monitor**: the specific `Open` commitments due at the next print, the exact language to listen for (reaffirmation vs silence), the thresholds that would resolve each to Beat/Met/Missed, and the credibility-weighted expected print for each from Phase 5 (with the alt-data ahead/behind read where available).
6. **What would change the view**: the 2–3 observations (e.g., two consecutive clean guides after a CFO change, formal withdrawal replacing silence) that would materially raise or lower the credibility assessment.

Be direct about uncertainty and sample size. If the window contains a regime change (new management, major M&A, restatement), report pre- and post-change scorecards separately rather than blending them.

Share the selected output file or deployed dashboard and present the conclusion in the response.

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When the `data_source` selection (or a `data_sources` list) includes any of `daloopa`, `factset`, or `morningstar`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

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

## MANDATORY QA REVISIONS (v2, 2026-07-21) — these override any conflicting guidance above

1. **Financial number formatting (all outputs)**: Follow standard finance sign and numbering conventions. Abbreviate large values — never write out every digit of a billion-scale number in text, tables, or slides. Default unit is $ in millions with thousands separators (e.g., "$3,423M" or "$3.4B", never "$3,423,192,847"). State the unit once per table/exhibit header ("$ in millions unless otherwise noted") rather than repeating full figures per cell. Negative values in parentheses, e.g., (412). Multiples as 0.0x; percentages to one decimal; per-share amounts in dollars and cents.
2. **Source quality bar**: Cite only professional-grade sources: company filings (10-K/10-Q/8-K, S-1, proxy), earnings transcripts, investor-relations materials, connected premium data providers, primary regulatory/statistical agencies, and top-tier financial press (WSJ, FT, Bloomberg, Reuters). NEVER cite or rely on Zacks, Motley Fool, Seeking Alpha, Simply Wall St, GuruFocus, Benzinga, StockTwits, aggregator blogs, SEO content farms, or similar unprofessional sources — neither in prose nor in citation lists. If an aggregator merely relays another outlet's reporting (e.g. "Benzinga, citing The Information"), cite the original outlet directly instead; never cite the aggregator, even as a relay.
3. **Spreadsheet standards (any XLSX deliverable)**:
   - Hide gridlines on every sheet (Excel: View > uncheck Gridlines / Alt+W,V,G; openpyxl: `ws.sheet_view.showGridLines = False`).
   - Financial-model color convention: blue font = hardcoded inputs/assumptions; black font = formulas and same-sheet references; green font = links pulling from other sheets.
   - Summary/output tabs must contain NO hardcoded numbers (no blue on the summary page) — every figure must be a formula or cell reference linked to the underlying data/calculation tabs.
   - Never bury constants inside formulas as in-cell calculations (e.g., a black cell containing `=1234*0.25` that references no other cells). Every driver lives in its own labeled input cell (blue), and formulas reference cells only.
4. **Quote sourcing**: Every verbatim management statement must carry its source: document type (earnings call transcript, 10-K, investor day, press release), the date/quarter, and a citation link. No unsourced quotes anywhere in the deliverable.
5. **No overall headline score**: Do NOT compute or present an aggregate/overall management credibility score — it is ambiguous and unhelpful. Per-KPI hit rates plus commentary are the scoring ceiling of this deliverable.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `office/xlsx`.
