---
name: update-investment-thesis
description: "Update an existing investment thesis or memo by tracking dated developments against each thesis pillar, milestone, scenario, and falsifier."
metadata:
  perplexity:
    display_name: "Update investment thesis"
---
# Update Investment Thesis

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `thesis_file` (Existing thesis or memo) Ask the user to attach the file(s) in chat.

OPTIONAL — assume the default (or omit) unless the user specifies:
- `ticker` (Ticker) No default — omit silently if the user does not provide it.
- `as_of_date` (Memo as-of date override) — Developments are tracked from this date to today. Defaults to the date on the memo, or the latest dated datapoint inside it. No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `morningstar`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (PitchBook) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Update Investment Thesis

Update an existing investment thesis or memo by tracking every dated development since the memo was written against each thesis pillar, assumption, milestone, scenario, and falsifier. The core question for the investor: is the original thesis on track, drifting, or falsified — and is the reason to own (or avoid) the position today still the reason written in the memo? Do not frame the work as any single investor's style; the quality comes from disciplined decomposition of the memo, an exhaustive dated evidence ledger, honest pillar-by-pillar verdicts, and explicit anti-anchoring checks.

## Analytical Standard

1. **Evidence-first, memo-second**: The memo defines what to test; it does not define what is true. Evaluate each new development as if reviewing the situation fresh, then compare that fresh read to the memo's claims.
2. **Anti-anchoring discipline**: The single biggest failure mode in thesis maintenance is rationalizing — reinterpreting bad news as noise and good news as confirmation. Every "weakens" or "breaks" judgment must be stated as bluntly as every "confirms." Where evidence is genuinely mixed, say so and identify which side carries more weight and why.
3. **Thesis-creep detection**: If the position now rests on a different rationale than the memo's (e.g., the memo argued margin expansion, but the current bull case is a new product cycle), flag it explicitly. A quietly replaced rationale is a new thesis, not an updated one — and it deserves fresh underwriting, not inherited conviction.
4. **Falsifiability**: Every pillar must have at least one falsifier with a measurable threshold by the end of the run — either taken from the memo or inferred and labeled as inferred.
5. **Completeness check**: Developments that touch no pillar are not discarded. They go to a New Information section, because a material development the memo has no slot for is evidence the thesis was incomplete.
6. **Exactness**: Show the exact figure, never "~". Every number carries a source and an as-of date. Transcript claims require a verbatim quote with speaker and quarter. Never fabricate links, quotes, or figures; where data is missing, state the limitation and proceed.

## Phase 1: Parse the Memo into a Structured Thesis

Read the uploaded memo in full before pulling any data.

1. **Identify the subject**: Extract the company, ticker, and listing. If the user supplied a ticker, verify it matches the memo's subject; if they conflict, flag the conflict and use the user's ticker. Resolve the ticker with the finance ticker lookup tool before any data pull. If the subject is a private company, note it and follow the private-company adaptations below.
2. **Establish the as-of date** (the anchor for "what has happened since"), in priority order: (a) the user-provided as-of/lookback input; (b) an explicit date on the memo (title page, header, footer); (c) the latest dated datapoint referenced inside the memo (last quarter discussed, last price cited). State which method was used and the exact date chosen. If only a quarter is inferable, use the day after that quarter's earnings release.
3. **Extract the thesis skeleton** into five structured lists, quoting or closely paraphrasing memo language and citing the memo section for each item:
   - **Pillars**: the 3–6 core claims the thesis stands on (e.g., "NRR stays above 120%", "competitor X cannot match unit economics", "management redeploys FCF into buybacks").
   - **Assumptions**: the quantified inputs beneath the pillars — growth rates, margin trajectories, market size, pricing, share count, exit multiple, discount rate. Record the exact figures the memo used.
   - **Milestones**: dated or dateable events the memo expected (product launches, margin inflection quarters, contract wins, regulatory decisions, capital returns), each with its expected timing.
   - **Scenarios and price targets**: bull/base/bear (or equivalent) values, probabilities if given, the valuation method behind each, and the memo-date reference price.
   - **Falsifiers**: the memo's stated "what would change my view" conditions with thresholds.
4. **Infer missing elements — and say so**: If the memo lacks explicit falsifiers (common), derive at least one falsifier per pillar from the pillar's own logic (e.g., a pillar of "pricing power" implies a falsifier of "gross margin declines for two consecutive quarters ex-mix"). Label every inferred item `[inferred — not in original memo]`. Do the same for missing milestones or undated scenarios. Never present inferred content as the author's.
5. **Record the baseline**: memo-date stock price, market cap, relevant multiples, and consensus NTM revenue/EPS as of the memo date where recoverable. This baseline is what all deltas are measured against.

## Phase 2: Build the Dated Development Ledger

Gather every material development between the as-of date and the run date. Use finance tools first; derive all as-of parameters from the run date; save raw tabular pulls as CSVs to a working directory before analysis.

### Data sources (one or more, collected at intake)

`data_source` is a set of one or more sources collected at intake. Options: Perplexity Finance (built-in, always available), FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc (alt data), and Guidepoint (expert calls); defaults are all of these except PitchBook. Premium providers are bring-your-own-license: for each selected source, check whether its connector is connected. If a selected source is not connected, proceed without it and add exactly one line to the deliverable's sourcing note naming what connecting it would have added to this update (e.g., "FactSet was selected but is not connected; connecting it would add as-of-date consensus and a clean estimate-revision path since the memo"). Never stall or fail the run over an unavailable premium source — the built-in finance tools are the baseline.

Assign a provider of record per data domain from the selected-and-connected set, and state it beneath each exhibit: fundamentals and KPI history — Daloopa > FactSet > Morningstar > built-in; consensus and estimate revisions — FactSet > built-in; private-company rounds, marks, and cap tables — PitchBook > built-in private-company tool; fund/ETF holdings and analytics — Morningstar > built-in; alt-data demand/transaction signals — Carbon Arc; expert qualitative evidence — Guidepoint. Selected sources are complementary, not redundant: cross-validate every load-bearing figure — any number that flips a pillar verdict or trips a falsifier — against a second independent source where one is available. Where providers disagree materially on the same figure, show both values and explain the basis difference (fiscal calendar, adjusted vs GAAP, point-in-time vs restated); never silently average. One time series or table column = one provider basis; never splice providers mid-series without a footnote at the splice point.

Use public web sources only after finance tools are insufficient, cite them inline, and prefer primary sources (SEC filings, earnings transcripts, IR materials, company disclosures, official statistics) over commentary.

Collect, at minimum, these categories (1–8 always; 9–10 when the corresponding source is selected and connected):

1. **Earnings prints and guidance**: Every quarterly report in the window — revenue, EPS, operating income/EBITDA, FCF, and key KPI actuals versus consensus, using the earnings history tool. For each print in the window, pull the complete artifact set — earnings press release, earnings presentation, and the full transcript, reading prepared remarks and Q&A as separate evidence (guidance and framing live in the prepared remarks; stress, hedging, and dodged questions surface in Q&A). Extract guidance (ranges, midpoints, raises/cuts/reaffirmations) and verbatim management statements that bear on any pillar, with speaker and quarter, and flag where a Q&A answer hedges or contradicts the prepared script. Compute management's guidance hit rate across the window (and prior guides where recoverable) — beat / met / missed per guided metric — as the base rate for weighting current guidance in Phase 4. Note post-earnings one-day moves.
2. **Estimate revisions**: Current consensus forward estimates (revenue, EPS, EBITDA, FCF, relevant KPIs) versus the closest recoverable consensus at the as-of date. Quantify the revision in absolute and percentage terms per fiscal year. When FactSet is selected and connected it is the provider of record here: pull the as-of-date (or closest recoverable point-in-time) consensus and the full revision path since, including estimate-count and dispersion changes where returned. If as-of consensus is not recoverable, reconstruct direction from revision history or state the limitation.
3. **Filings and corporate events**: 10-K/10-Q/8-K (or local equivalents) filed in the window — M&A, divestitures, restructurings, impairments, capital raises, buyback/dividend changes, auditor or accounting changes, litigation, covenant events. Date each and cite the filing.
4. **Management and board changes**: CEO/CFO/segment-head departures and hires, board turnover, notable insider buying or selling (insider transactions tool — distinguish 10b5-1 scheduled sales from discretionary trades), and shifts in institutional ownership from the holders tool: top-holder position changes, notable entries and exits, and concentration change since the as-of date.
5. **Competitive and industry events**: Peer earnings read-throughs (peer tool for the 4–5 closest comparables) — read every peer print in the window specifically against the thesis's shared drivers (demand, pricing, share, input costs) and record whether each peer datapoint corroborates or contradicts the pillar it touches; supplement self-declared comps with a quantitative screen for same-industry companies with similar growth/margin profiles, since the most informative read-through may come from a company the memo never named. Also competitor product launches and pricing actions, share-shift datapoints, supply/demand shifts, and regulatory or policy changes touching the industry.
6. **Macro shifts**: Only the macro variables the memo's driver logic actually depends on (rates, FX, commodity inputs, end-market indicators), pulled from macro history tools — as-of-date level versus current level, with the change quantified.
7. **Price action versus benchmark**: Total price change from as-of date to run date for the stock, a market benchmark, a sector proxy, and the peer basket. Decompose the stock move into estimate change versus multiple change (multiple bridge) where data permits — this reveals how much of the developments the market has already priced.
8. **Sell-side signal**: Rating and price-target changes in the window from the analyst research tool — used as evidence of narrative shift, not as truth.
9. **Expert-call evidence (Guidepoint, when selected)**: Treat expert interviews conducted since the as-of date as a distinct new-evidence stream answering one question per pillar: has channel and customer reality moved since the memo was written? Pull calls on the company and its closest peers, plus reverse-references — experts interviewed about other companies who mention the subject — and extract dated, attributed observations on demand, pricing, competitive displacement, and execution. Enter each material observation as its own ledger row with the expert's vantage point (customer, channel partner, competitor, former employee). Weight expert claims below filed actuals but above sell-side commentary.
10. **Alt-data trajectory (Carbon Arc, when selected)**: Pull demand/transaction signals for the company and its category covering the window and plot them against the specific KPI assumptions the memo made — is the alt-data trajectory since the as-of date running ahead of, in line with, or behind the path the thesis requires? Calibrate the signal by reconciling it against reported KPIs for the overlapping quarters, state the known coverage bias, and enter material divergences as ledger rows; these are often the earliest pillar-level evidence available ahead of the next print.

Every ledger entry must carry: date, category, one-sentence description, quantified magnitude, and source. If the window exceeds roughly three years, note that the memo is stale enough that a full re-underwrite may be more appropriate than an update, then proceed — covering every earnings print but prioritizing the most material items in other categories.

**Private-company adaptation**: If the subject is private, replace categories 1–2 and 7–8 with: funding rounds, secondary-market price marks and implied valuations (private company info tool), disclosed KPIs or leaked/reported financials (labeled as such), investor mark changes, and public-comparable multiple moves as a valuation proxy. State clearly which figures are company-disclosed versus reported versus estimated.

## Phase 3: Map Developments to the Thesis

This mapping is the analytical core. For each ledger entry:

1. Assign it to the specific pillar(s), assumption(s), milestone(s), or falsifier(s) it touches — by name, not by vague theme.
2. Score its direction per element touched: **confirms** / **weakens** / **breaks** / **neutral**, with a one-to-three-sentence evidence statement quantifying the impact (e.g., "Q2 NRR printed 108% vs the memo's ≥120% assumption — weakens Pillar 2 and trips inferred falsifier F2a").
3. **Falsifier tripwire check**: Test every falsifier (original and inferred) against the ledger. A tripped falsifier must be stated plainly — it cannot be argued around; if the analyst believes the falsifier itself was mis-specified, say so explicitly and treat that as a thesis revision, not an excuse.
4. **Milestone scorecard**: Mark each milestone met / missed / delayed / pending, with the evidence and date. Repeated delays are a weakening signal in their own right, not neutral.
5. **New Information section**: Collect every material development that maps to no pillar. For each, answer: does this reveal a blind spot the memo should have covered (thesis incomplete — propose the missing pillar or risk), or is it genuinely immaterial to the investment case (say why)? Do not silently drop unmapped items.
6. Apply a materiality filter throughout: exclude routine noise (immaterial press releases, minor PT tweaks) from the main ledger, but state the filter used.

## Phase 4: Verdicts

1. **Per-pillar verdict**: For each pillar, weigh its confirms/weakens/breaks entries and rule **intact / strengthened / impaired / broken**. Show the evidence trail — the ruling must be reproducible from the ledger. Where entries conflict, identify which evidence carries more weight (filed actuals outrank management framing; multi-quarter trends outrank single prints; leading indicators outrank coincident ones) and reject narratively loud items with weak evidence. For each pillar, name the single best supporting datapoint and the single best disconfirming datapoint — exact figure, date, and source for each; if no genuine disconfirming datapoint exists, say so explicitly rather than manufacturing balance. Weight management guidance by the hit-rate base rate computed in Phase 2 — a team that missed its last three guides earns less benefit of the doubt than one that has beaten every one.
2. **Fresh-eyes test** (anti-anchoring): In one paragraph, state what an analyst with no prior position would conclude from the assembled evidence alone, before rereading the memo. If the fresh-eyes read and the memo-anchored read diverge, present both and explain the gap — the divergence itself is a finding.
3. **Thesis-creep audit**: State in one sentence the memo's original reason to own (or short/avoid), and in one sentence the strongest case today. If they differ materially, flag thesis creep and state that the new rationale requires fresh underwriting rather than inherited conviction.
4. **Scenario and price-target refresh**: Mark each memo scenario still-valid or stale. Where the evidence justifies it, show old → new for the key assumptions and resulting scenario values, with the specific ledger entries driving each change. Do not silently move targets; every change needs a stated cause. If the memo's valuation method is no longer appropriate, say so and explain.
5. **What is priced in**: Using the Phase 2 multiple bridge and estimate-revision data, assess how much of the net development the market has already absorbed — and therefore whether the update changes the forward risk/reward, not just the narrative. Make the comparison explicit: state the growth/margin path the current multiple and consensus imply, set it against both the memo's assumptions and the fresh-eyes read, and rule whether the expectations gap the thesis depended on has widened, narrowed, or closed. A thesis can be analytically intact and still be dead as an investment if the market has fully caught up — say which case this is.
6. **Overall verdict**: Rule the thesis **on track / drifting / falsified**, with a confidence level and the two or three decisive pieces of evidence. "Drifting" requires naming what is drifting (timing, magnitude, or mechanism). "Falsified" is required — not optional — if a core pillar is broken or an original falsifier tripped without a documented, evidence-based revision.

## Phase 5: Refreshed Milestones, Falsifiers, and Monitoring Plan

1. **Refreshed milestones**: Roll forward the milestone list — carry unresolved items with updated expected dates, add new milestones surfaced by the ledger (upcoming prints, product events, regulatory dates from the earnings calendar and filings), and retire completed ones.
2. **Refreshed falsifiers**: Tighten or add falsifiers so every surviving pillar has at least one measurable tripwire with an explicit threshold and a time bound expressed as a calendar date or a named print ("by the FQ3 report on <date>"), not "medium term". Preserve the original/inferred/new labels.
3. **Monitoring plan**: A table of signal, source, threshold that matters, check cadence, next check date (anchored to real calendar events — the next earnings date from the earnings calendar, known regulatory or product dates), and which pillar it guards — practical enough to run quarterly without rereading the full memo.

## Phase 6: Output — Redline-Style Delta Memo

Honor the selected output format. Default to PDF (portrait memo) when ambiguous: this is a narrative judgment document. All formats must present the same underlying dataset.

**Redline convention (all formats)**: For every updated element, show the original memo language (or figure) and the updated language side by side or as labeled `Original:` / `Update:` pairs, with the status tag — STANDS, REVISED, BROKEN, or NEW. The reader must be able to see exactly what changed and what stands without opening the original memo.

### PDF memo (default)

Section order:
1. Header — company, ticker, memo as-of date (and how it was established), run date, window covered, overall verdict.
2. Verdict box — on track / drifting / falsified, one-paragraph rationale, confidence, fresh-eyes divergence note if any.
3. Thesis scorecard — one table: each pillar, memo claim (abbreviated), verdict, decisive evidence, falsifier status.
4. Development ledger — the dated table (date, category, development, magnitude, pillar touched, direction, source).
5. Pillar-by-pillar redline — per pillar: original claim, evidence for/against with quotes and figures, verdict, refreshed falsifier.
6. Milestone scorecard and New Information section (with proposed new pillars/risks where the thesis was incomplete).
7. Scenario refresh — old → new table with causes; what is priced in.
8. Thesis-creep audit and refreshed monitoring plan.
9. Appendix — methodology, as-of conventions, source list.

### XLSX

Sheets: Verdict Summary; Thesis Scorecard; Development Ledger (filterable, one row per development with mapping and direction columns); Pillar Detail; Milestones & Falsifiers; Scenario Refresh (old/new assumptions as live formulas where practical); Monitoring Plan; Sources & Traceability. Apply house workbook formatting (Calibri; dark teal #1B474D headers with white text; blue hardcoded inputs; frozen panes; source notes on every sheet) and run the recalculation check before sharing.

### PDF presentation

One idea per slide: verdict; scorecard; the 3–5 highest-impact developments (one each); scenario refresh; monitoring plan; appendix. Insight-led headlines ("Pillar 2 broken: NRR printed 108% vs 120% assumption", not "NRR Update").

### Dashboard

Panels: verdict banner; pillar status cards with drill-down to evidence; interactive development timeline mapped to pillars; milestone tracker; scenario old/new comparison; monitoring table. Every displayed figure needs a tooltip with value, date, and source.

## Conclusion

End the response (regardless of format) by directly answering: Is the thesis on track, drifting, or falsified? What is the single most important thing that changed since the memo? Does the position rest on the original rationale or a replaced one? What are the top three signals to watch next, with thresholds and dates? Be direct about uncertainty and data gaps; a verdict of "drifting, low confidence, pending the next print" is acceptable — a hedged non-answer is not.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When the `data_source` selection includes any of `daloopa`, `factset`, or `morningstar`, raw data figures sourced from those providers must be traceable back to the originating provider/source artifact.

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
- Title bar at top: concise, insight-led headline (e.g., "Revenue grew 23% in Q4" not "Revenue Overview"). 24–32 pt, bold.
- Optional subtitle/deck name and slide number in a thin footer.
- Body: a single clear idea per slide. Prefer tables, charts, and labeled visuals over long prose. Bullets ≤ 5 per slide, ≤ 12 words each.
- Leave generous whitespace. Do not pack a slide edge-to-edge with text.

### Typography and style
- Sans-serif throughout (Calibri or Arial). Body 14–18 pt, captions 10–12 pt.
- Single accent color plus neutrals. No decorative graphics, clip art, or stock imagery.
- Numeric values right-aligned and use tabular figures. Percentages, currency, and units formatted consistently across the deck.
- Charts: direct-label data, minimize gridlines, ≤ 5 series, encode meaning with color rather than decoration.

### Quality bar
- Every slide must answer: "so what?" in the title.
- Fact-check every number against its provider of record among the selected data sources.
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

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## MANDATORY QA REVISIONS (v2, 2026-07-21) — these override any conflicting guidance above

1. **Financial number formatting (all outputs)**: Follow standard finance sign and numbering conventions. Abbreviate large values — never write out every digit of a billion-scale number in text, tables, or slides. Default unit is $ in millions with thousands separators (e.g., "$3,423M" or "$3.4B", never "$3,423,192,847"). State the unit once per table/exhibit header ("$ in millions unless otherwise noted") rather than repeating full figures per cell. Negative values in parentheses, e.g., (412). Multiples as 0.0x; percentages to one decimal; per-share amounts in dollars and cents.
2. **Source quality bar**: Cite only professional-grade sources: company filings (10-K/10-Q/8-K, S-1, proxy), earnings transcripts, investor-relations materials, connected premium data providers, primary regulatory/statistical agencies, and top-tier financial press (WSJ, FT, Bloomberg, Reuters). NEVER cite or rely on Zacks, Motley Fool, Seeking Alpha, Simply Wall St, GuruFocus, Benzinga, StockTwits, aggregator blogs, SEO content farms, or similar unprofessional sources — neither in prose nor in citation lists. If an aggregator merely relays another outlet's reporting (e.g. "Benzinga, citing The Information"), cite the original outlet directly instead; never cite the aggregator, even as a relay.
3. **Spreadsheet standards (any XLSX deliverable)**:
   - Hide gridlines on every sheet (Excel: View > uncheck Gridlines / Alt+W,V,G; openpyxl: `ws.sheet_view.showGridLines = False`).
   - Financial-model color convention: blue font = hardcoded inputs/assumptions; black font = formulas and same-sheet references; green font = links pulling from other sheets.
   - Summary/output tabs must contain NO hardcoded numbers (no blue on the summary page) — every figure must be a formula or cell reference linked to the underlying data/calculation tabs.
   - Never bury constants inside formulas as in-cell calculations (e.g., a black cell containing `=1234*0.25` that references no other cells). Every driver lives in its own labeled input cell (blue), and formulas reference cells only.
4. **Required file upload**: The existing thesis file is mandatory input. At intake, explicitly ask the user to upload it. If no file is attached, do not proceed with the update — ask for the upload and wait. Inline-pasted thesis text explicitly provided by the user may substitute for the file.

## Attached materials

Any files supplied through the kickoff form arrive as attachments on this turn and are
downloaded into the workspace. Read them before starting external research and treat them
as primary source input. If no files were attached, proceed using the available finance
and data connectors plus web research, and say so rather than asking the user to re-upload.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `document-review`, `office/pdf`.
