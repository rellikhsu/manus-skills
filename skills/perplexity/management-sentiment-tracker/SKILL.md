---
name: management-sentiment-tracker
description: "Track quote-backed shifts in management language across earnings transcripts, MD&A, and material risk-factor changes over time, then connect them to subsequent KPI and financial outcomes where feasible."
metadata:
  perplexity:
    display_name: "Management sentiment tracker"
---
# Management Sentiment Tracker

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `ticker` (Stock ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `lookback_window` (Lookback window) Options: `4-quarters` (Last 4 quarters); `8-quarters` (Last 8 quarters); `12-quarters` (Last 12 quarters); `16-quarters` (Last 16 quarters). Default: `8-quarters`.
- `analysis_scope` (Sources to analyze) — Leave empty to analyze all three sources. Options: `transcripts` (Earnings transcripts (prepared remarks & Q&A)); `mdna` (MD&A drafting changes (10-Q/10-K)); `risk_factors` (Material risk-factor changes). No default — omit silently if the user does not provide it.
- `focus_topics` (Focus topics) No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Daloopa, Morningstar, Carbon Arc, Guidepoint) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF memo); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX quote register); `dashboard` (Dashboard). Default: `pdf`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Management Sentiment Tracker

Track how management's language has shifted over time — across earnings call prepared remarks, analyst Q&A, MD&A drafting, and risk-factor disclosures — and determine whether those shifts carry investment signal. The core question is: what is management saying differently now versus before, is every claimed shift provable with verbatim quotes, and have similar language changes historically preceded changes in reported fundamentals? Do not frame the work as any single investor's style; the quality comes from disciplined text comparison, a strict quote-backed evidence standard, and honest linkage of language to outcomes.

## Scope Boundary

This skill is the qualitative sibling of the Management KPI & Credibility Tracker. That skill scores the numbers: guidance ranges, KPI commitments, milestones, and time-bound forward statements versus revisions and actuals. This skill tracks the language: hedging, confidence, emphasis, evasion, and drafting changes. Keep the boundary crisp — do not rebuild a guidance-vs-actuals scorecard here. Numeric outcomes appear in this analysis only in Phase 5, where they test whether a language shift was informative. If the user wants the full numeric credibility scorecard, point them to the Management KPI & Credibility Tracker; the two are designed to be run together.

## Phase 0: Setup and Corpus Collection

Use finance tools first. Resolve the ticker before any ticker-dependent pull, derive all as-of parameters from the run date, and save raw pulls to a `finance_data/` working directory before analysis. Data sourcing follows the selection rules below.

### Data sources (one or more, collected at intake)

`data_source` is a set of one or more sources collected at intake: Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, Carbon Arc (alt data), and Guidepoint (expert calls); the defaults are Perplexity Finance and FactSet. Every premium source is bring-your-own-license. For each selected source, check whether its connector is connected; if a source is selected but not connected, proceed without it and add one line to the deliverable's sourcing note naming what it would have added for this analysis (e.g., "Daloopa was selected but is not connected; connecting it would add filing-linked KPI history for the outcome-linkage tests"). Never stall or fail a run over an unavailable premium source — the built-in finance tools are the always-available baseline.

Assign a provider of record per data domain and state it on every exhibit that uses that domain: transcripts and filings — the built-in earnings transcript tool and SEC EDGAR are the corpus of record regardless of selections; consensus estimates, revisions, and surprise history for Phase 5 — FactSet when selected and connected, otherwise built-in; fundamentals and KPI history for the outcome linkage — Daloopa > FactSet > Morningstar > built-in. Where two selected-and-connected providers cover the same load-bearing Phase 5 figure (an actual, a consensus number, a surprise), cross-check it across both; if they disagree materially, show both values and explain the basis difference (as-reported vs adjusted, calendarization, currency) — never silently average. One table column or one time series = one provider basis; never splice providers mid-series without a footnote at the splice point.

Two non-default sources extend the evidence base when selected: Guidepoint adds expert-call evidence on how former employees, customers, and industry practitioners perceive this management team's credibility — an outside check on whether the language shifts you flag are noticed and believed by people who deal with the company. Carbon Arc adds alt-data demand and transaction signals as a reality check against tone — upbeat prepared remarks while alt-data demand decelerates (or fresh caution while demand holds) is itself a rankable divergence for Phase 6; reconcile Carbon Arc signals against reported KPIs before treating them as outcomes in Phase 5.

1. **Window**: Use the user-selected lookback window; default to the last 8 reported quarters. The corpus is every earnings call transcript in the window plus every 10-Q and 10-K filed in the window, and the last pre-window filing of each type as the comparison base.
2. **Transcripts**: Pull verbatim earnings call transcripts with the earnings transcript tool. For each call, separate prepared remarks from Q&A and tag every passage with speaker name and role (CEO, CFO, other executives, operator, analyst with firm). Prepared remarks are lawyered and rehearsed; evasiveness lives in Q&A — the two must be analyzed separately throughout.
3. **Filings**: Pull MD&A and Risk Factors sections from 10-Qs and 10-Ks via SEC EDGAR. For non-US filers, use the closest analogs (Operating and Financial Review in annual/interim reports, 20-F Item 3.D and Item 5) and note that semiannual reporting reduces sample density.
4. **Outcome data (for Phase 5 only)**: Pull earnings history (actuals vs consensus and surprises), segment revenue and KPIs via the segment tool, quarterly financials, consensus estimate history, and the next earnings date from the earnings schedule tool.
5. **Document inventory**: Produce a table listing every document collected — type, fiscal period, event/filing date, source — and every document that could not be retrieved. State gaps plainly; never fabricate a quote, a transcript, or a filing excerpt. If a transcript or filing is missing, mark affected analyses as limited rather than interpolating.
6. If the user supplied focus topics, treat them as priority lenses for every phase, but still surface material shifts outside them.

Use public web sources only after finance tools and EDGAR are insufficient, and cite them inline. Prefer primary sources: filings, transcripts, IR materials, company disclosures.

## Phase 1: Transcript Language Analysis — Prepared Remarks vs Q&A

Run every analysis in this phase twice — once on prepared remarks, once on Q&A — and report the two tracks separately, because divergence between the scripted and unscripted track is itself a finding. Quantify that divergence per quarter — e.g., Q&A hedging density minus prepared-remarks hedging density — so a widening scripted-vs-unscripted gap shows up as a trend series rather than an impression; scripted confidence paired with rising unscripted hedging is the classic tell.

1. **Hedging-language density**: Count hedging constructions per 1,000 words, per quarter, per track, and per speaker (CEO vs CFO at minimum). Use a stated lexicon — e.g., "we believe", "we think", "roughly", "approximately", "should", "could", "may", "we'll see", "it's early", "assuming", "to the extent", "hopefully", "cautiously" — and disclose the exact lexicon and normalization in the methodology section. Report the trend and the largest single-quarter changes.
2. **Confidence markers**: Track the density of specific, checkable forward statements (numbers, dates, named milestones, "we will" commitments) versus vague optimism ("well positioned", "excited about the opportunity"). A shift from quantified commitments to adjectives is a downgrade in disclosure quality even when tone stays positive.
3. **Topic dwell time**: Allocate each call's words across a consistent topic map (segments, products, geographies, margins, capital allocation, macro, and the user's focus topics). Track share-of-airtime by topic per quarter: what got materially more or less airtime, which topics were newly introduced, and which quietly disappeared. Distinguish management-initiated dwell (prepared remarks) from analyst-forced dwell (Q&A).
4. **New vs retired vocabulary**: Identify terms and phrases that first appear or permanently vanish in the window, with first/last appearance quarter (e.g., "record backlog" retired, "elongated sales cycles" introduced). Ignore one-off word choices; flag only vocabulary changes that persist or coincide with a topic shift.
5. **Non-answers and deflections**: Match every analyst question to its answer and classify each response: answered directly, answered partially, deflected (answered a different question), declined ("we don't guide to that", "we're not going to comment"), or reframed. For every flagged non-answer, log the verbatim question with analyst name and firm, the verbatim response with speaker, and the date. Track repeat-question patterns — the same topic deflected across multiple consecutive quarters is a stronger signal than any single dodge. Also note when management stops answering a question it previously answered.
6. **Speaker divergence**: Flag quarters where CEO and CFO language diverges (e.g., CFO adds hedges while CEO stays promotional), with quotes from each.

## Phase 2: MD&A Drafting Changes (10-Q / 10-K)

Compare each filing against the prior comparable filing (10-Q vs the same fiscal quarter's 10-Q a year earlier and vs the immediately preceding 10-Q; 10-K vs prior 10-K). Look for meaningful drafting changes, not formatting noise:

1. Changes in causal attribution — what management says drove results, and whether attributions shift from company-specific strengths to external factors (or the reverse).
2. Added or deleted qualifiers and caveats around trends ("increased" becoming "increased modestly, primarily due to…"; "we expect growth" becoming "we expect growth, subject to…").
3. Dropped claims — growth statements, demand characterizations, competitive-position assertions present in prior filings and now absent.
4. New forward-looking caution: liquidity language, covenant references, customer-concentration wording, impairment triggers, going-concern-adjacent phrasing.
5. Changes in how key metrics are defined, framed, or sequenced within MD&A when they alter emphasis.

Explicitly ignore: section reordering, pagination and formatting differences, mechanical period-number updates, safe-harbor and legal boilerplate refreshes, and synonym swaps with no semantic content. Every flagged change must be shown as a before/after verbatim excerpt with document, section, and filing date.

## Phase 3: Risk-Factor Delta

Report only three categories, and apply a decision-relevance test to each: would this change a valuation input, a debate position, or a monitoring item for an investor? If not, exclude it.

1. **New risks** — genuinely new exposures, not restyled generic risks.
2. **Materially reworded risks** — changes that alter probability, severity, or specificity. The highest-priority flag is hypothetical-to-actual conversion: "could adversely affect" becoming "has adversely affected", or a generic risk acquiring named customers, products, jurisdictions, or proceedings.
3. **Removed risks** — deletions can signal resolution or repositioning; state which reading the surrounding disclosure supports.

Explicitly suppress boilerplate churn: sector-wide macro/cyber/regulatory language updates that mirror peer filings, legal-standard refreshes, and cosmetic rewording. State in the output how many total risk-factor edits were observed and how many survived the decision-relevance filter, so the reader knows the suppression was applied rather than the filings being static.

## Phase 4: Evidence Standard (applies to every phase)

1. Every claimed language shift must be quote-backed: before/after verbatim excerpts, with speaker (for transcripts) or document section (for filings), document identity, and date or fiscal quarter. A shift that cannot be shown in quotes does not go in the report.
2. No unsupported sentiment scores. Never present a standalone "sentiment: 6.2/10" or "tone: negative" rating as a finding.
3. Quantitative text metrics — hedge-word counts, dwell-time percentages, answer-rate statistics, any sentiment deltas — are supporting evidence only, presented beneath the quotes they corroborate, with methodology stated (lexicon, normalization, topic map, classification rules). They are never the headline.
4. Quote excerpts must be long enough to be fair — no clipping that reverses meaning. Preserve ellipses honestly.
5. Where evidence is thin (one ambiguous quote, a single quarter), say so and downweight the finding rather than dressing it up.

## Phase 5: Language-to-Outcome Linkage

Test whether this management team's language shifts have been informative, using the outcome data from Phase 0:

1. For each material historical shift, identify the financial line or KPI it most plausibly concerns, then check subsequent reported outcomes with exact figures: did new caution on topic X precede a miss, deceleration, guide-down, or estimate cut on X? Did new specificity or confidence precede a beat or guide-up? Record the lead time in quarters.
2. Build a linkage table: shift (quarter flagged, one-line description, anchor quote reference) → linked metric → subsequent outcome (exact reported figure vs consensus or prior trend, with dates) → lead time → verdict: confirmed, contradicted, or unresolved.
3. Be statistically honest. A handful of shifts is an anecdote base, not a sample; report hit rates but state the n, and reject narratively appealing links where timing or magnitude does not actually support them. Distinguish language that led outcomes from language that merely accompanied already-visible deterioration. Then use the hit rate (with its n) as an explicit calibration input for Phase 6: state whether this team's language shifts have historically been leading, coincident, or uninformative, and weight the current quarter's unresolved shifts accordingly — new caution from a team whose caution has reliably led misses deserves more weight than the same words from a team whose language has never led outcomes.
4. Where the user has also run the Management KPI & Credibility Tracker, reconcile: language findings should be read alongside the numeric guide-vs-actual record, and conflicts between the two (e.g., cautious language but consistent beats) should be called out rather than smoothed over.
5. **Forward watch items**: Every current unresolved shift becomes a watch item with the specific metric to monitor, the threshold or disclosure that would confirm or refute the signal, and the next checkpoint (next earnings date or filing). These are the actionable output of the skill.

## Phase 6: Ranking by Investment Relevance

Rank all findings — transcript shifts, MD&A changes, risk-factor deltas — in a single scorecard using explicit criteria: magnitude of the language change; persistence across quarters; corroboration across sources (a shift appearing in Q&A, MD&A, and risk factors outranks a single-source shift); historical signal value of similar shifts from this management team (Phase 5); materiality of the linked financial line to the investment case; and market awareness — check analyst research and ticker sentiment tools (and Guidepoint expert commentary, when selected and connected) to note whether the shift is already a live sell-side topic or still unnoticed, since unnoticed shifts carry more variant-perception value. Explicitly call out popular "tone reads" circulating in commentary that the textual evidence does not support.

## Phase 7: Output Creation

Honor the selected output format. Default to a PDF memo when ambiguous, because the deliverable is narrative and quote-driven. All formats present the same underlying dataset.

Include 3–5 charts in every format, following the chart standards: DPI 150, figsize 12x7, seaborn-v0_8-whitegrid, palette #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553, insight-stating titles. Standard chart set: (1) topic dwell-time shares by quarter (stacked area, prepared remarks and Q&A distinguished); (2) hedging density per 1,000 words by quarter, prepared remarks vs Q&A as separate series; (3) direct-answer rate in Q&A by quarter; (4) timeline overlaying flagged language shifts on the subsequent earnings-surprise record.

### PDF memo (default)

Portrait memo with this section order:

1. Executive summary — the top 3–5 language shifts and what each means for the investment debate.
2. Language Shift Scorecard — the ranked findings table with rank rationale.
3. Transcript analysis — prepared remarks vs Q&A tracks, dwell-time chart, hedging/confidence trends, evasiveness log highlights with verbatim question/answer pairs.
4. MD&A drafting changes — before/after excerpts with commentary.
5. Risk-factor delta — new / reworded / removed, with suppression statistics.
6. Language-to-outcome linkage — the linkage table and honest hit-rate discussion.
7. Forward watch items — metric, threshold, checkpoint for each unresolved shift.
8. Methodology and limitations — lexicons, topic map, classification rules, corpus gaps.
9. Exhibits appendix — full quote tables: every cited excerpt with before/after text, speaker or section, document, and date, keyed to the finding it supports.

### XLSX (quote register)

When XLSX is selected, build a workbook with these sheets: `Summary` (ranked scorecard and navigation); `Quote Register` (one row per excerpt: finding ID, document type, fiscal period, date, speaker or section, verbatim excerpt, before/after pair ID, classification, decision-relevance note); `Q&A Evasiveness Log` (question, analyst and firm, response classification, verbatim response, repeat-question flag); `Topic Dwell Time`; `Hedging & Confidence Metrics`; `MD&A Deltas`; `Risk Factor Deltas`; `Outcome Linkage`; `Watch Items`; `Sources & Methodology`. Apply house workbook formatting: Calibri; dark teal #1B474D headers with white text; percentages as `0.0%`; freeze panes on tables; source notes on every sheet; derived metric cells as live formulas where practical.

### PDF presentation and dashboard

For `pdf_presentation`, follow the PDF (Presentation) block below with the memo's section order adapted to one insight per slide. For `dashboard`, build a private interactive dashboard with panels for the scorecard, dwell-time and hedging trend charts, an expandable Q&A evasiveness log, a searchable quote explorer, the outcome-linkage table, and watch items; every charted datapoint's tooltip should carry the underlying quote reference.

## Phase 8: Conclusion

End with a direct answer to the core question: has management's language changed, in what direction, and has this team's language historically been informative? State what the market already appears to have absorbed versus which shifts remain unnoticed, what would change the view (the specific disclosures or results that would confirm or refute each open signal), and the monitoring plan — which upcoming call topics, filings, and metrics to check, at what cadence. Be direct about uncertainty: small corpora, missing transcripts, and ambiguous drafting changes must be labeled as such, and conflicting evidence should be reconciled with a statement of which evidence carries more weight.

Share the selected output file or dashboard and present the conclusion in the response.

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When the `data_source` selection includes `daloopa`, `factset`, or `morningstar`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:
1. Make raw figures clickable wherever the provider returns a URL, deep link, report link, document reference, filing link, cell-level reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source/source-note cells where feasible, and include a `Sources & Traceability` or `Source Map` sheet with provider, company/security/entity, metric, period, as-of timestamp, provider metric/series/document ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, KPI tile, chart datapoint, tooltip, or detail drawer that displays a raw provider figure must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Daloopa document, filing, and company-series links/references; FactSet entity, metric, document, and any returned URL/deep link; Morningstar security, datapoint, report, and URL references.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity/security identifier, metric or series ID/name, period, as-of timestamp, and document/report identifier where available, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures. Derived calculations should link or reference the source cells/figures used in the calculation.

## Output format: PDF (Presentation)

When the user selects output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF. Do NOT produce the standard portrait memo; this format replaces it.

### Page setup
- Orientation: landscape
- Page size: US Letter landscape (11" x 8.5") or widescreen 16:9 (13.333" x 7.5") — default to 16:9 for a modern deck feel
- Margins: 0.5"–0.75" on all sides
- One logical slide per page

### Slide anatomy
- Title bar at top: concise, insight-led headline (e.g., "CFO hedging doubled in Q&A since Q2" not "Language Overview"). 24–32 pt, bold.
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
3. Language Shift Scorecard table.
4. Core analysis slides — one shift per slide, each with its before/after quotes and headline insight.
5. Supporting exhibits — dwell time, hedging trends, evasiveness log, outcome linkage.
6. Watch items.
7. Appendix — quote tables, methodology, source list, disclosures.

### Quality bar
- Every slide must answer: "so what?" in the title.
- Fact-check every number against its provider of record.
- Verify no text overflow, wrapping mid-word, or low-contrast color combinations before delivery.
- Output is intended for external distribution; treat it as client-ready.

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
4. **Supporting web app**: In addition to the PDF report, build and deploy a supporting interactive web app presenting the sentiment analysis. All charts must be genuinely interactive (hover tooltips, series toggles, time-range selection where sensible) and numerically consistent with the PDF. QA the deployed app yourself before delivering: load it in a browser, interact with every chart, verify data correctness and rendering, and fix any issues before sharing the link.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `investment-research`, `finance/finance-markets`, `office/pdf`, `office/xlsx`, `website-building/webapp`.
