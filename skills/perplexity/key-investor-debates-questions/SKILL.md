---
name: key-investor-debates-questions
description: "Identify the highest-sensitivity investor debates for a public company, map bull/base/bear and disconfirming evidence, quantify KPI and valuation impact, summarize the last 8 quarters of sentiment/setup, and generate specific management questions for public Q&A and private 1:1 meetings."
metadata:
  perplexity:
    display_name: "Key investor debates questions"
---
# Key Investor Debates & Questions

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `ticker` (Stock ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `debate_focus` (Debates or theses to stress-test) — Optional. Your candidate debates will be ranked against everything mined from transcripts and estimates — and displaced if the evidence says so. No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `morningstar`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (PitchBook) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Key Investor Debates & Questions

Identify the handful of unresolved investor debates that actually drive a public company's valuation, map each one rigorously (falsifiable framing, bull/base/bear, disconfirming evidence, quantified KPI and valuation impact), read the sentiment and positioning setup over the last 8 quarters, and produce specific, non-googleable diligence questions for management. Do not frame the work as any single investor's style. The core question is: which 3-5 disagreements, if resolved, would move this stock the most — and what evidence or questioning would resolve them?

## Analytical Standard

1. **Valuation sensitivity over media volume**: Rank debates by how much they move the estimate lines and the multiple, not by how often they appear in headlines. A debate that dominates financial media but moves FY+1 EPS by 1% is not a key debate.
2. **Falsifiability**: Every debate must reduce to one sentence that observable data can confirm or refute. If it cannot be falsified, it is a narrative, not a debate — say so and exclude it.
3. **What's priced in**: For each debate, back out the market's embedded expectation from the current multiple, consensus estimates, and estimate dispersion before assessing bull/bear asymmetry.
4. **Disconfirming-evidence discipline**: Every side of a debate has at least one datapoint it must explain away. Surface the strongest such datapoint for bull, base, and bear — not a strawman.
5. **Quote-backed transcript claims**: Any claim about what management said or what analysts keep asking must carry a verbatim quote, speaker name, and quarter/date.
6. **Evidence weighting**: Reconcile conflicting evidence explicitly and state which carries more weight and why. Distinguish leading indicators from coincident ones. Call out debates that look important narratively but show weak evidence of valuation sensitivity.
7. **Question quality bar**: Management questions must be specific, anchored in disclosed figures, and designed to elicit information not already in filings, transcripts, or sell-side notes. No softballs; no questions whose answer is googleable.
8. **Uncertainty honesty**: State sample-size limits, data gaps (e.g., short interest coverage), and where the setup read is inference rather than measurement. Never fabricate a datapoint.

## Phase 1: Setup and Data Collection

Use finance tools first for all market and company data. Resolve the ticker with the ticker lookup tool before any ticker-dependent pull; if multiple listings match, use the primary public listing unless the user's context indicates otherwise. Derive all as-of parameters from the run date. Save all raw tabular pulls as CSVs to a `finance_data/` working directory before analysis.

### Data sources (one or more, collected at intake)

`data_source` is a set of one or more sources collected at intake. Options: Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc (alt data), and Guidepoint (expert calls); the default selection is all of these except PitchBook. Premium providers are bring-your-own-license, so handle availability without stalling:

1. **BYOL check**: For each selected premium source, check whether its connector is connected. If selected but not connected, proceed without it and add one line to the methodology/sourcing note naming what connecting it would add to this analysis — e.g., "Guidepoint was selected but is not connected; connecting it would add expert-call testimony from customers, channel partners, and former employees to arbitrate each debate." Never fail or stall the run over an unavailable premium source; Perplexity Finance built-in tools are the always-available baseline.
2. **Provider of record per domain**: Assign each data domain to the strongest selected-and-connected provider and state the assignment on every exhibit: fundamentals and KPI history — Daloopa > FactSet > Morningstar > built-in; consensus estimates, dispersion, and revisions — FactSet > built-in; multiples and peer valuation — FactSet > Morningstar > built-in; private-company comparables where a debate involves private competitors — PitchBook > built-in; alt-data demand/transaction signals — Carbon Arc; expert qualitative evidence — Guidepoint.
3. **Complementary streams, not redundancy**: Independence of evidence is the point of this skill — sell-side numbers (FactSet), reported fundamentals (Daloopa/Morningstar), practitioner testimony (Guidepoint), and observed demand (Carbon Arc) let each side of a debate be tested with evidence the other side does not control. Cross-validate every load-bearing figure across two selected providers where coverage overlaps; where providers disagree materially, show both values and explain the basis difference — never silently average.
4. **Series integrity**: One table column or one time series = one provider basis. Never splice providers within a series without an explicit footnote at the splice point.

Collect, covering at least the last 8 completed quarters (extend to 12 where cheap to do so):

1. **Price history**: Daily adjusted close and volume for a window spanning the last 8 quarters plus 3 months of lead-in, via the OHLCV history tool. Never use general web search for historical prices. Pull the latest quote for the as-of header.
2. **Earnings history**: Last 8 quarters of EPS and revenue actuals vs. consensus, surprise magnitudes, and one-day post-earnings price moves.
3. **Transcripts and earnings artifacts**: The last 8 earnings call transcripts (verbatim), keeping prepared remarks and analyst Q&A separable — the Q&A sections are the primary raw material for debate mining. Also collect each quarter's earnings press release and earnings presentation; gaps between what the deck emphasizes and what Q&A dwells on are debate signals.
4. **Consensus estimates**: Current forward consensus for revenue, EPS, EBITDA/operating income, and FCF for FY+1 and FY+2, including high/low/mean dispersion where available, plus the revision path of FY+1 revenue and EPS consensus across the last 8 quarters. When FactSet is selected and connected, pull analyst-level dispersion (high/low/mean, and standard deviation where returned) and the revision trend per estimate line — dispersion width and revision divergence are the most direct measure of where sell-side disagreement is widest, and feed the Phase 2 ranking directly.
5. **Analyst research**: Ratings mix (buy/hold/sell counts), price target mean/high/low vs. current price, and rating/target changes over the last 8 quarters.
6. **Sentiment**: Ticker-level sentiment via the ticker sentiment tool; note the market sentiment backdrop where relevant.
7. **Ownership**: Institutional holders — top holders, quarter-over-quarter position changes, new and exited positions, and concentration. Note the reporting lag on 13F-derived data.
8. **Segments and KPIs**: Segment revenue and company-specific KPIs (ARPU, NRR, GMV, units, backlog, etc.) via the segments tool for the KPI-impact quantification.
9. **Valuation**: Multiple time series (P/E, EV/Revenue, EV/EBITDA, P/FCF as relevant) via the company ratios tool, plus current multiples for 4-5 closest peers via the peers tool for relative framing.
10. **Short interest**: Pull short interest and days-to-cover from finance tools where available; otherwise use exchange-published short interest data via web search with inline citations. If unavailable for the listing, state the limitation — do not estimate.
11. **Filings**: The latest 10-K plus the 10-Qs covering the last 8 quarters, recent 8-Ks, and the proxy where governance or compensation touches a debate. Read across documents: risk-factor language added or dropped, changes to the stated competitor set, KPI definitions changed or disclosures discontinued, and segment re-statements — each is evidence that management is managing a debate.
12. **Guidance base rates**: Management's guidance for each of the last 8 quarters vs. subsequent actuals, per guided line — beat/met/missed counts and average magnitude — used when weighing management's side of any debate.
13. **Guidepoint expert calls (when selected and connected)**: Recent expert interviews on the target and its closest peers, plus reverse-references — experts interviewed about other companies who discuss the target. For every expert datapoint used, record the expert's vantage (customer, channel partner, former employee, competitor), the call date, and how many independent calls corroborate the claim.
14. **Carbon Arc alt data (when selected and connected)**: Demand/transaction signals for the company and its comps that map to the KPIs the debates turn on. Establish each signal's historical relationship to the reported KPI over the available quarters before using its latest reading as evidence.

Use public web sources only after finance tools are insufficient (e.g., short interest, buyside-consensus color, event context), and cite them inline. Prefer primary sources: SEC filings, exchange data, IR materials, earnings transcripts.

## Phase 2: Debate Identification and Ranking

### Q&A mining

1. Across the last 8 transcripts, extract every analyst question and tag it by topic. What analysts keep asking quarter after quarter is the live debate set.
2. Score each topic on: frequency (how many quarters it appears), persistence (still being asked in the most recent 2 quarters), escalation (question sharpness increasing), and management evasiveness (deflection, non-answers, changed disclosure). Support evasiveness claims with verbatim quotes.
3. **Answer evolution and contradiction sweep**: For each recurring topic, track how management's answer has evolved across the 8 quarters — quote the earliest and most recent answers side by side and characterize the drift (more specific, more hedged, re-scoped, metric quietly swapped). Separately flag every place the Q&A record contradicts or hedges the same quarter's prepared remarks or presentation: a confident prepared claim followed by a qualified Q&A answer is one of the strongest live-debate signals.

### Corroborating signals

4. Cross-check the mined topics against: sell-side rating dispersion and price-target spread (wide spread = live disagreement), consensus estimate dispersion (high-low range vs. mean on FY+1 revenue/EPS), the direction and volatility of estimate revisions, and post-earnings reaction asymmetry (which topics coincided with the largest moves). With FactSet connected, go line by line: the estimate lines with the widest high/low dispersion and with diverging revisions (some analysts raising while others cut) should each map to a mined debate — a wide-dispersion line with no mined debate means the transcripts missed one; add it to the candidate list. Where Guidepoint is connected, note which candidates experts with ground truth have directly addressed; where Carbon Arc is connected, note which candidates have a live alt-data signal capable of settling or sharpening them before the next print — resolvability raises a debate's practical priority at equal valuation sensitivity.

### Valuation-sensitivity ranking

5. Build a candidate list of 6-10 debates. For each, identify: (a) the estimate line it moves (revenue growth, gross margin, opex, EPS, FCF, or a specific segment/KPI line), (b) the multiple it moves and why (growth durability, margin quality, terminal-value risk), and (c) a rough bull-minus-bear implied value spread: apply plausible bull and bear outcomes to the affected estimate line, pair each with a defensible multiple, and compute the implied price range vs. the current price. Show the arithmetic with exact figures and as-of dates.
6. Rank strictly by the implied value spread — valuation sensitivity, not media volume. Explicitly name 1-2 heavily discussed topics that rank low and say why (small estimate impact, already priced in, or unfalsifiable).
7. Select the top 3-5 debates. If the user supplied debates to stress-test, evaluate them within this same ranking; if one fails to rank, say so directly and show what displaced it.

## Phase 3: Debate Mapping (repeat for each selected debate)

For each of the top 3-5 debates, produce a structurally identical block:

1. **The debate in one falsifiable sentence**: A single statement resolvable by observable data within a stated horizon (e.g., "NRR stabilizes at or above 110% by Q4 FY2026" — not "the company has strong customer loyalty").
2. **Bull / base / bear positions**: What each side believes, the 2-3 strongest pieces of evidence each cites (quote-backed where transcript-derived), and which investor constituency plausibly holds each view given the positioning data. Lead with the single best datapoint each side cites — the one piece of evidence that side would defend under cross-examination — and marshal bull and bear evidence from independent streams (reported figures/filings, transcript record, sell-side estimates, Guidepoint testimony, Carbon Arc signals). Flag explicitly when both sides cite the same datapoint read differently: that debate resolves on interpretation, not new data.
3. **Disconfirming evidence**: For each of bull, base, and bear, the single strongest datapoint that side must explain away, and the quality of the available explanation.
4. **Independent-stream arbitration (when Guidepoint / Carbon Arc selected)**: State who holds ground truth on this debate — customers, channel partners, former employees, competitors — and what the Guidepoint call record from those vantages says, with call dates and corroboration counts (one uncorroborated call is color, not evidence; label it as such). Then state whether a Carbon Arc signal bears on the debate: the signal, its historical fit to the disputed KPI, the latest reading vs. what consensus implies, and whether it can settle or sharpen the debate before the next print. Where expert testimony and alt data point opposite ways, weigh them explicitly rather than picking silently. Also summarize the management-record read from the Phase 2 sweep: how management's answer to this question has evolved over the 8 quarters, and any prepared-remarks/Q&A contradictions.
5. **Quantified KPI and valuation impact**: The estimate line and period the debate moves; bull/base/bear values for that line with the reasoning; the multiple each scenario supports (grounded in the company's own multiple history and peer multiples); the implied price per scenario; and what the current price implies is priced in. Exact figures only — never "~" — with as-of dates on all market data. Include the guidance base rate on the affected line (how often management hit its prior guides for that line over the last 8 quarters) and weight management's framing accordingly.
6. **Resolution path**: The specific upcoming datapoints that will move the debate (earnings line items, KPI disclosures, filings, product/regulatory events), with expected dates from the earnings schedule and a note on which direction each outcome cuts. Close the block with one line naming the single observable that resolves the debate: the metric, the threshold, the source, and the date it becomes visible.

## Phase 4: Management Diligence Questions

Generate a question bank organized by debate, split into two tiers:

1. **Public earnings-call Q&A questions** (2-3 per debate): Appropriate to ask on the record, but still sharp — anchored to a specific disclosed number, forcing management to quantify a driver, reconcile an inconsistency between statements/quarters, or commit to a mechanism. Reference the exact figure and period being probed.
2. **Private 1:1 / NDR questions** (2-3 per debate): Sharper questions on mechanism, unit economics, competitive dynamics, capital-allocation logic, and decision frameworks that management can discuss without selectively disclosing material nonpublic information. Frame questions Reg FD-aware: probe how management thinks and what already-public data implies, not undisclosed results.

Standards for every question: (a) non-googleable — verify the answer is not already in the last 8 transcripts, recent filings, or the collected data; (b) specific — cite the number, segment, or quote it is anchored to; (c) annotated — one line on which debate it informs, what a strong answer sounds like, and what an evasive answer would signal. No questions management can answer with prepared talking points. Explicitly avoid softballs ("How do you think about the opportunity...").

## Phase 5: Sentiment and Setup — Last 8 Quarters

1. **Positioning**: Institutional ownership trend over the available quarters — top-holder adds/trims, notable new/exited positions, concentration change; distinguish index/passive from active where discernible. Note 13F lag. Short interest level and trend with days-to-cover where available.
2. **Estimate-revision direction**: The path of FY+1 revenue and EPS consensus across the last 8 quarters — rising, falling, or inflecting, and when.
3. **Post-earnings reactions**: A table of the last 8 prints: EPS/revenue surprise, guidance direction where available, and one-day price reaction. Read the asymmetry: does the setup punish in-line results (crowded long), reward modest beats (skepticism), or ignore beats (debate lives elsewhere)?
4. **Sentiment and sell-side stance**: Current sentiment reading, ratings mix, and mean price target vs. price; note where buyside expectations likely sit relative to published sellside numbers when reactions diverge from surprise direction. Where Guidepoint is connected, contrast field-level expert tone with the sell-side stance — practitioner pessimism against sell-side optimism (or the reverse) is itself a setup datapoint.
5. **Annotated price history**: Build an annotated price chart over the 8-quarter window using the same methodology as the house Annotated Stock Price Chart skill: adjusted close from the OHLCV history tool (never web-sourced prices); select events objectively — all 8 earnings dates, the largest absolute one-day moves, gap moves, volume spikes, and major rating/target changes; 6-10 annotations with short on-chart labels and a detailed event timeline beneath (date, event, exact price reaction, causal explanation, source); distinguish confirmed facts from plausible market interpretation and avoid implying causality where evidence only supports correlation.
6. **Setup verdict**: One paragraph — is the name a crowded long, crowded short, or genuinely contested; which debate the current setup is most exposed to; and what the reaction function into the next print likely looks like.

## Phase 6: Output Creation

Honor the selected `output_format`. Default to PDF when ambiguous — the analysis is narrative- and judgment-heavy. All formats must present the same underlying dataset and section content.

### PDF (portrait memo — default)

Section order: (1) Executive summary — the #1 debate, the setup verdict, and the 3 highest-value questions; (2) Debate stack-rank table — debate, falsifiable statement, estimate line moved, bull/bear implied price spread, resolution date, and which side the independent evidence streams currently favor; (3) One section per debate (Phase 3 blocks); (4) Question bank — per debate, public-Q&A and private-1:1 questions side by side with annotations; (5) Sentiment & setup — positioning, revisions, reaction table, annotated price chart with event timeline; (6) Conclusion (Phase 7); (7) Methodology, data as-of dates, and sources — including the provider-of-record assignment per exhibit and the one-line sourcing notes for any selected-but-unconnected providers.

### XLSX

Sheets: `Executive Summary`, `Debate Stack-Rank` (ranking table with sensitivity arithmetic), one `Debate 1..n` detail sheet per debate (scenario table with live formulas for implied prices), `Question Bank`, `Setup - 8Q History` (reactions, revisions, ownership, short interest time series), `Price & Events` (price data with event flags and embedded annotated chart), `Sources & Methodology`. Apply house workbook formatting: Calibri; dark teal #1B474D headers with white text; currency `$#,##0` with unit-bearing headers; percentages `0.0%`; blue text for hardcoded inputs, formulas black; freeze panes; source notes on every sheet. Derived values (implied prices, spreads) must be live Excel formulas. After building, run the recalculation script `python skills/office/xlsx/scripts/recalc.py <output_file>` and fix all formula errors before sharing.

### PDF (Presentation)

One insight per slide following the deck standards below: cover; executive summary; debate stack-rank; one slide per debate (falsifiable statement as the headline, scenario table as the exhibit); question bank (one slide per tier); setup and annotated chart; conclusion; appendix.

### Dashboard

Private interactive dashboard with: debate cards (expandable to full Phase 3 blocks), sensitivity table with scenario toggles, question bank with debate filters, 8-quarter setup panel (reactions, revisions, ownership), interactive annotated price chart with hover event details, and methodology notes. Deploy and provide the link.

Charts (all formats): DPI 150, figsize 12x7, seaborn-v0_8-whitegrid, palette #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553. Titles state the insight, not the data (e.g., `Estimate Revisions Turned Negative Two Quarters Before the De-rating`).

## Phase 7: Conclusion

Answer the core question directly:

1. **The debate that matters most**: Name it, state the falsifiable sentence, and show its valuation sensitivity vs. the rest of the stack.
2. **What's priced in**: The market's embedded expectation on each key debate, derived from current multiples, consensus, and positioning.
3. **Where the asymmetry sits**: Which debate offers the widest gap between what's priced and what the evidence supports, and in which direction.
4. **What would change the view**: The 2-3 specific datapoints that would resolve or flip the top debate.
5. **Monitoring plan**: For each debate — the metric, the threshold that matters, the source, and the check cadence, tied to the upcoming catalyst calendar with dates.

Be direct about uncertainty: where evidence conflicts, say which side carries more weight and why; where data is missing (short interest, buyside positioning), say so plainly.

Share the output file or deployed dashboard and present the conclusion in the response.

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When `data_source` is `daloopa`, `factset`, or `morningstar`, or when `data_sources` includes any of `daloopa`, `factset`, or `morningstar`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

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

### Quality bar
- Every slide must answer: "so what?" in the title.
- Fact-check every number against its provider of record among the selected data sources.
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
4. **Methodology correction (supersedes any conflicting step above)**: Do NOT derive debates or implied valuation per share from sell-side price targets or the high/low of sell-side reports. Published price targets without access to the underlying models, rationale, and revisions are not evidence and must not anchor any exhibit. Instead:
   a. **Transcript Q&A mining is the primary proxy**: what analysts ask about most, and most persistently, across the last 8 earnings transcripts.
   b. **Industry valuation-driver framework**: start from what structurally drives valuation for stocks in this industry (e.g., ARR/NRR for software; AUV and same-store-sales growth for restaurants; combined ratio for insurers), then assess how each driver applies to this specific business.
   c. **Key driver analysis**: measure how the stock has actually moved after beats/misses on specific KPIs (map post-earnings reactions to which metric surprised) to establish empirically which lines the market prices.
   d. **Framing**: a key debate qualitatively lays out both sides of a large force that will have downstream effects on these KPIs/metrics — not a myopic restatement of a common industry metric ("the key debate for CRWD is ARR" is wrong: ARR matters for every software company; the debate is the force acting on it).
5. Consensus estimate dispersion/revisions may corroborate a debate ONLY when sourced from a connected professional provider (e.g., FactSet) — never from free aggregator sites.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `office/pdf`.
