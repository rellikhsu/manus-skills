---
name: "perplexity:industry-overview"
description: "Build an investor-ready industry overview deck covering market definition, segmentation, sizing, profit pools, value chain, growth drivers, cyclicality, regulation, economics, and investor implications."
metadata:
  perplexity:
    display_name: "Industry overview"
---
# Industry Overview

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `industry` (Industry or market)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `anchor_company` (Anchor company or ticker (optional)) No default — omit silently if the user does not provide it.
- `geography` (Geographic scope) Options: `global` (Global); `north-america` (North America); `europe` (Europe); `asia-pacific` (Asia-Pacific); `middle-east-africa` (Middle East & Africa); `latin-america` (Latin America); `india` (India). Default: `global`.
- `horizon` (Analysis horizon) Options: `1_2y` (1–2 years); `3_5y` (3–5 years); `5y_plus` (5+ years). Default: `3_5y`.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `morningstar`, `pitchbook`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: all supported sources for this skill are already default-enabled; when a data domain has no usable premium coverage, fall back to built-in Perplexity Finance and record the gap in the sourcing note.
- `output_format` (Output format) Options: `pdf_presentation` (PDF (Presentation)); `pdf` (PDF); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf_presentation`.
- `focus_areas` (Focus areas) — Leave blank for full coverage; select to deepen specific sections. Options: `sizing` (Market sizing); `profit_pools` (Profit pools & value chain); `growth_drivers` (Growth drivers); `cyclicality` (Cyclicality); `regulation` (Regulation); `economics` (Industry economics). No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Industry Overview

Produce an investor-ready overview of the market an industry (or a specific company) operates in: how the market is defined and segmented, how big it really is and how fast it is growing, where the economics accrue across the value chain, what drives growth and how durable those drivers are, and what all of this implies for investors. The core question this analysis answers: is this an attractive market to have exposure to, where in it, and what evidence would change that view?

**Scope boundary.** This skill covers the MARKET, not the players. Industry structure metrics (concentration, business-model archetypes, barriers to entry) are in scope because they describe the market; individual-company positioning depth — market-share battles, moat comparisons, player-by-player profiles, head-to-head product analysis — is explicitly out of scope and belongs to the sibling "Competitive Landscape" skill. Keep any company mentions strictly as sizing or economics evidence, and close the deliverable with a one-line handoff pointing to Competitive Landscape for player-level work. State this scope explicitly in the deliverable itself — one line on the executive-summary or scope page, e.g., "This overview analyzes the market — sizing, growth, structure, and economics. For company-level competitive positioning and share dynamics, see the Competitive Landscape skill." — so the reader is never caught off guard by the absence of company-vs-company competitive depth.

## Phase 0: Scope and setup

1. Parse the inputs. If an anchor company or ticker is provided, resolve the ticker first, then pull the company profile and its segment disclosures so the market definition is grounded in what the company actually sells — not in a generic sector label.
2. Write a one-sentence market definition before any sizing: products/services included, adjacencies explicitly excluded, geographic scope, and the span of the value chain covered. Every size, growth rate, and profit-pool figure in the deliverable must conform to this definition; if a source uses a different definition, restate or exclude it and say so.
3. Derive all as-of dates and lookback windows from the run date. Save every raw tabular pull (macro series, segment revenues, financials, screens) as CSV files in a working directory (e.g., `finance_data/`) before analysis.
4. Data sources. `data_source` is a set of one or more sources collected at intake (options: Perplexity Finance built-in, FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc, Guidepoint; all seven are selected by default). Premium providers are bring-your-own-license: for each selected provider, check whether its connector is actually connected. If a provider is selected but not connected, proceed without it and add one line to the deliverable's sourcing note — "<Provider> was selected but is not connected; connecting it would add <the specific value for this overview: PitchBook — private entrants, funding, and valuations for the participant landscape; Carbon Arc — observed demand/transaction signals to test the growth narrative; Guidepoint — practitioner evidence on structure, pricing, and channels; Daloopa — filing-traceable segment/KPI history; FactSet — consensus estimates and quantitative screens; Morningstar — independent fundamentals and fund-holdings context>." Never stall or fail a run over an unavailable provider; the built-in finance tools are the always-available baseline.
5. Provider-of-record per data domain. Assign each domain to the strongest selected-and-connected provider and state the provider per exhibit: fundamentals and segment/KPI history — Daloopa > FactSet > Morningstar > built-in; consensus estimates — FactSet > built-in; private-company data (rounds, valuations, entrants) — PitchBook > built-in private-company tool; alt-data demand/transaction signals — Carbon Arc; expert qualitative evidence — Guidepoint; macro series — built-in macro tools. Providers cover complementary universes: FactSet-screened publics plus PitchBook privates together span the full participant landscape; Carbon Arc corroborates or challenges reported growth; Guidepoint supplies practitioner context filings cannot. Cross-validate every load-bearing figure (sizing inputs, segment revenues, profit-pool margins) across at least two providers where coverage overlaps; where providers disagree materially, show both values and explain the basis difference — never silently average. One table column or one time series = one provider basis; never splice providers within a series without an explicit footnote at the splice point.
6. Use public web sources only after finance tools are insufficient, and prefer primary sources — SEC/regulator filings, earnings transcripts, IR materials, official statistics agencies, trade associations with published methodology. Never rely on low-quality aggregators, and never treat a market-research-shop press release as a primary source.

## Phase 1: Market definition and segmentation

1. Build the taxonomy along 2–3 segmentation lenses (typically product/service, customer or end-market, and geography). Choose one primary lens for the deliverable and state why it is the most decision-relevant cut.
2. Define 4–8 segments under the primary lens that are mutually exclusive and collectively exhaustive against the Phase 0 definition, each with one-line inclusion criteria. Flag where the anchor company (if any) participates.
3. Assemble the evidence base by triangulating three discovery routes so the participant landscape spans public AND private: (a) self-declared competitor sets — read the competition sections of the 10-Ks/annual reports of the 2–3 most obvious participants and harvest every named competitor; (b) quantitative same-industry screens — screen the public-equity SQL database (or FactSet screens when selected and connected) for companies matching the industry's revenue-growth and margin profile that self-declared sets miss, supplemented by the finance peer tool; (c) private entrants and disruptors — PitchBook (when selected and connected) for funded private players, recent entrants, and disruptive business models, with funding round, latest valuation, and lead investors; fall back to the built-in private-company tool otherwise. Reconcile the three lists and make an explicit include/exclude call on any company appearing on only one route. Target 8–20 public companies with material exposure. Pull their segment disclosures (segment revenue and KPIs such as units, GMV, ARPU) with the segments tool across roughly the last 8 quarters (10-K plus 10-Qs), noting segment re-statements and restating history to the current basis where possible — these disclosures are the backbone of supply-side sizing and profit-pool math in Phases 2–3. This list is evidence, not a set of company profiles; do not expand it into positioning analysis.
4. Carry the private players from route (c) forward only insofar as they affect market size, the Phase 2 gross-up, or value-chain economics — their aggregate funding and disclosed revenue signals also calibrate the private/unlisted share assumption in Approach B.
5. **Participant reference table (required exhibit)**: distill the reconciled participant list into one controlled reference table — one row per relevant player (roughly 8–15 rows; every included player must matter to the market's size, structure, or economics), with columns for: player name; a one-line description of what it does in this market; headquarters location; ownership/funding status (public with ticker, subsidiary with parent, or private with latest round, amount raised, and lead investors where disclosed); latest annual revenue or best-available revenue signal ($ with unit, estimates flagged as estimates); and the value-chain step or segment it plays in. Keep it strictly factual and market-descriptive — no moat scores, no share battles, no positioning commentary (that depth belongs to Competitive Landscape). Cite a source for every row. This table appears exactly once in the deliverable, in the market structure / participants section, and every output format must include it.

## Phase 2: Market sizing with an explicit build

**Sizing discipline (non-negotiable):** never present a single sell-side or market-research-firm headline number as fact. Every market size shown must expose its build — the formula, each assumption, and each assumption's source. Third-party research figures (Gartner, IDC, Statista, Grand View, etc.) may be used only as cross-checks, labeled with the firm, publication date, and their stated market definition.

1. **Approach A — bottom-up build (preferred).** Size the market as units × price, customers × annual spend, or an equivalent driver decomposition appropriate to the industry. Source every input: unit counts from official statistics or company disclosures, pricing from disclosed ASPs/ARPU or primary pricing pages, penetration from macro or census data. Show the arithmetic in a visible table.
2. **Approach B — supply-side aggregation.** Sum the in-scope revenue of the public evidence base from segment disclosures (restated to the Phase 0 definition), then gross up for private and unlisted participants with an explicitly stated share assumption and its basis. This approach doubles as a floor: the market cannot be smaller than observable in-scope revenue.
3. **Approach C — top-down macro cross-check.** Anchor to relevant macro aggregates using the macro snapshot and macro history tools (e.g., GDP components, industry production, retail sales, construction spend, healthcare expenditure, capex series across 196 countries) and apply a penetration or share-of-wallet ratio with a stated source.
4. **Approach D — observed-demand cross-check (Carbon Arc, when selected and connected).** Pull industry-level demand/transaction trend series for the market and its major segments and test whether observed volume/spend growth is consistent with the growth the sizing narrative assumes. Where the observed signal diverges from narrative TAM/CAGR claims by more than a few points, treat it as a challenge to be explained — coverage or panel bias versus genuinely different demand — not as noise, and carry any unresolved gap into the Phase 6 consensus critique.
5. **Reconciliation (required).** Reconcile at least two independent approaches. Present the range and a midpoint or preferred point estimate, state which approach carries more weight and why, and if the spread between approaches exceeds 25%, flag it prominently and explain the source of divergence (definition mismatch, gross-up assumption, double counting). If only one approach is feasible, state that limitation explicitly rather than manufacturing false precision. Always reconcile top-down or third-party market-size claims against the bottom-up sum of participant in-scope revenue from Approach B: if a quoted figure exceeds the grossed-up participant revenue sum by more than the stated private/unlisted share can plausibly explain, say so plainly — that is usually TAM inflation, and it changes the investment conclusion.
6. Distinguish TAM / SAM / SOM where the request concerns a specific company's opportunity, and call out TAM inflation directly when common quoted figures embed unrealistic scope.
7. **Growth.** Compute the historical 5-year CAGR from the evidence base (segment revenues, macro series, official statistics) rather than quoting one. Build a forward 3–5 year growth view as base/bull/bear scenarios tied to the Phase 4 drivers, with each scenario's key assumption deltas shown. Size segments individually where evidence supports it; mark low-confidence segment estimates as such. Where third-party research firms published prior forecasts for this market, compare at least one against the realized outturn as a base rate for how much to discount current projections.

## Phase 3: Value chain and profit pools

1. Map the value chain in 4–8 steps from inputs to end customer, naming the archetypal participant type at each step (again, types — not player profiles).
2. Quantify the revenue pool and profit pool (operating profit dollars) at each step using the public evidence base: pull financials and ratio time series for representative companies at each step, compute median operating margin, ROIC, and capital intensity per step, and scale to the step's revenue pool. State the sample used per step.
3. Explain WHY economics accrue where they do — scarcity of a critical input, IP or process knowledge, regulatory position, switching costs, network effects at the layer level, or bargaining-power asymmetries between steps.
4. Show profit-pool migration: how the distribution of profit across steps has shifted over the last 5–10 years (with figures), and the direction of travel with the mechanism driving it. Call out steps where revenue is large but profit is structurally thin.

## Phase 4: Growth drivers, headwinds, and durability

1. Identify the 3–5 drivers that explain most of the market's growth. Decompose growth into volume, price, and mix where data allows, and attribute an approximate contribution per driver with the evidence behind it.
2. Run a durability test on each driver: classify it as secular, cyclical, or one-off; state the evidence for durability (adoption curves, demographics, regulation, replacement cycles); and state what would break it — every driver must carry a falsifiable kill condition.
3. Build a headwinds/tailwinds table with direction, quantified magnitude where possible, time frame, and confidence. Explicitly reject drivers that look important narratively but show weak evidence in the data — name them and say why they were excluded.
4. **Macro linkage.** Use macro history to test how the industry's growth co-moves with candidate macro series (rates, GDP, consumer spending, industrial production, energy prices, FX) over 10+ years. Distinguish leading from coincident indicators, and state where apparent relationships are too noisy or short-sampled to trust.
5. **Earnings-season sweep.** Pull the latest quarterly transcripts (prepared remarks AND Q&A) and earnings presentations for the 6–10 largest public participants and extract what each said about the same demand environment: demand characterization, pricing commentary, order/backlog or pipeline trends, and guidance direction. Tabulate the agreements and contradictions in one exhibit; where participants describe the same market differently, determine whether the divergence is mix, geography, or segment exposure — or a participant losing share — and state which read the rest of the evidence supports. Cross-check the collective management narrative against the Carbon Arc observed-demand signal where available.

## Phase 5: Cyclicality, regulation, and industry economics

1. **Cyclicality vs secularity.** Quantify peak-to-trough revenue and margin swings across the past two industry cycles using the evidence base and macro series. State where the industry sits in the current cycle and the evidence for that read. Decompose recent growth into its cyclical and secular components — this is often the single most mispriced judgment about an industry.
2. **Regulation.** Summarize the current regulatory regime by major geography, pending or proposed changes with expected timing, and the quantified exposure (what share of the market or profit pool each change touches). Cite regulator or legislative primary sources. Include historical regulatory shocks and how the market absorbed them.
3. **Industry economics scorecard.** Assemble a table covering: pricing power evidence (realized price/mix trends), industry median and dispersion of gross and operating margins, aggregate ROIC versus an estimated cost of capital, capital intensity (capex/revenue), working-capital character, barriers to entry, top-5 revenue concentration and its 5-year trend (a structure metric only — do not extend into share-battle analysis), M&A/consolidation cadence, and dominant business-model archetypes (subscription, transactional, licensing, services) with their economic implications.
4. **Expert evidence (Guidepoint, when selected and connected).** Search recent expert interviews on the industry and its major participants for practitioner views on industry structure, pricing discipline (are increases sticking, is discounting spreading), share shifts among participant types, and channel dynamics (direct vs distribution mix, inventory positions, promotional intensity). Use these views to pressure-test the pricing-power and concentration reads in the scorecard, and check reverse references — experts interviewed about adjacent markets who comment on this one. Every expert claim used must be quote-backed with the expert's role and interview date, labeled as qualitative single-source evidence, and corroborated or explicitly contrasted with the quantitative record; never let a single expert quote overturn a data series on its own.

## Phase 6: Investor implications and conclusion

Answer the core question directly:
1. Is this an attractive market, and specifically where — which value-chain steps and segments combine growth with defensible economics, and which are structurally value-poor despite headline growth.
2. The 2–4 key industry-level debates, with the strongest evidence on each side and which side the evidence currently favors.
3. What appears priced in at the sector level: compare current sector-level valuation multiples to their 5–10 year history in one exhibit, without extending into single-stock calls.
4. Where the consensus could be wrong: state the prevailing industry narrative — the growth rate, cycle read, and structural-winner assumptions embedded in sell-side sector research and the earnings-sweep tone — then identify the 1–2 places the assembled evidence most disagrees with it (top-down sizes the bottom-up revenue sum cannot support, secular growth that decomposes as mostly cyclical, observed demand running below management narratives, expert checks contradicting reported pricing discipline). For each, specify the observable evidence — specific data series, filing disclosures, or expert-check findings — that would confirm or refute the variant view within the analysis horizon.
5. What would change the view — the falsifiable conditions from Phase 4 plus any sizing or cyclicality assumptions that dominate the conclusion.
6. A monitoring dashboard: 5–8 metrics with source, current reading, threshold that would trigger a re-underwrite, and check cadence.
7. Close with the handoff: for player-level positioning, share dynamics, and moat comparisons within this market, run the Competitive Landscape skill.

## Phase 7: Output creation

Honor the selected `output_format`. All formats must present the same underlying dataset — no format drops exhibits another includes. When the format is ambiguous, default to the presentation deck.

**Core exhibit set (all formats):** market definition and segmentation map; sizing build tables for each approach plus the reconciliation bridge (waterfall from each approach to the preferred estimate); segment size/growth table; value-chain profit-pool bar chart (revenue vs profit share by step); growth-driver decomposition chart; headwinds/tailwinds table; earnings-sweep agreements/contradictions table; cyclicality time series with cycle annotations; regulatory map table; industry economics scorecard; monitoring dashboard. Charts: DPI 150, figsize 12x7, seaborn-v0_8-whitegrid, palette #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553; titles state the insight, not the data.

- **PDF (Presentation) — default.** 14–18 slides in this order: (1) cover; (2) executive summary — the market call in 3–5 bullets; (3) market definition and segmentation; (4) sizing build and reconciliation; (5) segment sizes and growth; (6) growth outlook scenarios; (7) value chain map; (8) profit pools and migration; (9) growth drivers and durability; (10) headwinds/tailwinds and the earnings-season sweep; (11) cyclicality and cycle position; (12) regulation; (13) industry economics scorecard; (14) investor implications and debates; (15) monitoring dashboard; (16) appendix — sizing methodology, definitions, source list, and the sourcing note (provider-of-record per domain; providers selected but not connected and what they would add).
- **PDF (memo).** Portrait report with the same section order as the phases, executive summary first, exhibits inline at full text width.
- **XLSX.** Sheets: `Summary`, `Market Sizing` (all approaches with live formulas for each build), `Segments`, `Profit Pools`, `Growth Drivers`, `Earnings Sweep`, `Cyclicality & Macro`, `Regulation`, `Economics Scorecard`, `Monitoring`, `Sources & Traceability`. Derived values must be live formulas, not hardcoded snapshots.
- **Dashboard.** Panels: market size and growth (with the reconciliation range shown, not a single number), segment treemap, profit-pool chart, driver/headwind board, cyclicality chart, economics scorecard, monitoring metrics with thresholds. Every raw figure exposes its source on click or hover.

Every figure carries its source and as-of date; show exact figures, never "~". Every format includes the sourcing note listing the provider-of-record per data domain and any selected-but-unconnected providers with what connecting them would add. Where data is missing, state the limitation — do not fabricate or interpolate silently.

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
- Title bar at top: concise, insight-led headline (e.g., "Profit pools are migrating downstream" not "Value Chain Overview"). 24–32 pt, bold.
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
- Fact-check every number against its provider-of-record.
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
4. **Slide alignment QA (mandatory before delivery)**: Render every slide to an image and visually inspect it. Images and adjacent text boxes must sit on the same horizontal level (top edges aligned) with consistent spacing; fix any element that is misaligned, overlapping, or floating at an odd offset, then re-render and re-check until clean.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `office/pdf`, `office/pptx`, `office/xlsx`, `website-building/webapp`.
