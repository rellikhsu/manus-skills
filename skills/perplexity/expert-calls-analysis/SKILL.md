---
name: "perplexity:expert-calls-analysis"
description: "Surfaces and synthesizes recent Guidepoint expert-call transcripts for a target company and its comps. Identifies the most relevant interviews (customers, competitors, channel partners, former employees), extracts quote-backed themes on demand, pricing, competitive dynamics and execution, separates corroborated signal from single-source anecdote, tracks how expert tone has shifted across quarters, and maps findings to the target's KPIs and live investor debates — every claim tied to a dated interview."
metadata:
  perplexity:
    display_name: "Expert calls analysis"
---
# Expert Calls Analysis

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `company` (Company or ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `peers` (Comp set override) — Leave blank to have the comp set built automatically with rationale for each peer. No default — omit silently if the user does not provide it.
- `focus_themes` (Focus themes) — Leave empty to let the evidence rank the themes. Options: `demand` (Demand); `pricing` (Pricing); `competition` (Competition); `execution` (Execution / management); `product` (Product); `channel` (Channel). No default — omit silently if the user does not provide it.
- `lookback_window` (Lookback window) Options: `6_months` (Last 6 months); `12_months` (Last 12 months); `18_months` (Last 18 months); `24_months` (Last 24 months). Default: `12_months`.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Guidepoint is the expert-call engine of this skill; providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `guidepoint` (Guidepoint (expert calls)); `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet). Default: `guidepoint`, `perplexity_finance`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (FactSet) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Expert Calls Analysis

Surface and synthesize recent expert-call evidence on a target company and its comps to answer the core investor question: what do the people closest to the business — customers, competitors, channel partners, former employees — believe about demand, pricing, competitive dynamics, and execution that filings and earnings calls do not yet show, and does that evidence confirm or contradict what is priced in? Guidepoint expert-call transcripts are the primary engine. Do not frame the work as any single investor's style. This is not a digest of interviews: every claim ties to a dated interview and expert role, every theme carries an explicit corroboration count, and every finding maps to a target KPI or a live investor debate.

## Evidence Standard

1. **Every claim dated and attributed.** Any statement derived from an expert call carries the interview date and the expert's role descriptor (e.g., "former regional sales VP at [competitor], interviewed 2026-04-18"). Verbatim quotes wherever the claim is load-bearing. No floating assertions.
2. **Corroboration counts.** Every theme states n — interviews supporting / contradicting / mixed out of the total reviewed (e.g., "supported in 5 of 14; contradicted in 1"). One interview is an anecdote; two is an emerging signal; three or more in the same direction is a corroborated signal. Cross-role corroboration (a customer and a channel partner independently agreeing) outweighs same-role corroboration.
3. **Single-source flags.** Any claim resting on one interview is visibly labeled `single-source` everywhere it appears, and the output includes a dedicated single-source watchlist rather than letting anecdotes blend into the narrative.
4. **Role-aware weighting.** Customers and channel partners are strongest on demand, pricing, and sell-through; former employees are strongest on execution and product reality but carry staleness (weight internal claims by departure date, not interview date) and potential axe-grinding; competitors are structurally biased — competitor praise of the target is strong signal, competitor criticism weak signal. State the weighting applied when it changes a conclusion.
5. **Specificity over vibes.** Rank quantified statements (win rates, discount percentages, churn) above directional, and directional above vague. Actively reject false positives: name themes that sound narratively important but rest on vague or stale commentary.
6. **Experts are evidence, not truth.** Expert samples are small and non-random. Triangulate every load-bearing expert claim against reported data — segment KPIs, consensus — and state whether it confirms, front-runs, or contradicts the reported trend. Where reported figures disagree, show both and weigh them; never present expert consensus as fact.
7. **Compliance.** Never solicit, infer, or build conclusions on material nonpublic information. If a transcript appears to contain company-specific MNPI (unreleased figures, undisclosed contract terms), exclude that passage and note the exclusion generically.

## Phase 0: Setup and Source Routing

1. Resolve the company to a name and ticker with the ticker lookup tool before any ticker-dependent pull; for private companies, use the private-company profile tool and note the data limitations. The company is the only required input — everything else is derivable.
2. Derive all as-of parameters from the run date. Default lookback: trailing 12 months of interviews; honor the `lookback_window` override. Record the run date and window in the output header.
3. `data_source` is a set of one or more sources collected at intake (options: Guidepoint, Perplexity Finance, FactSet; defaults: Guidepoint + Perplexity Finance). Premium sources are bring-your-own-license. For each selected source, check whether its connector is connected, then route:
   - **Guidepoint (core engine).** All expert-interview surfacing, transcripts, and quotes. If selected and connected, run the full expert-call workflow (Phases 2-5). If NOT connected (or not selected), state this prominently — as the first line of the deliverable's sourcing note and in the response — with one line on what connecting it unlocks for this skill: dated expert-interview transcripts across customers, competitors, channel partners, and former employees of the target and its comps, enabling corroboration counts and quarter-by-quarter tone tracking. Then run the public-evidence fallback (see Fallback Mode below). Never stall the run over an unconnected source.
   - **FactSet (if selected and connected):** provider of record for consensus estimates, revisions, and fundamentals context in Phase 5; preserve FactSet document/entity references. If selected but not connected, add one sourcing-note line: "FactSet was selected but is not connected; connecting it would add consensus and estimate-revision detail for the KPI and debate mapping."
   - **Perplexity Finance (always-available baseline):** ticker resolution, quotes, financials, segment KPIs, estimates, earnings transcripts, peers, earnings schedule.
   - One exhibit = one provider basis; where providers disagree materially on a figure, show both and explain the basis difference — never silently average. State the provider per exhibit.
4. Save all raw pulls — interview inventories, quote registers, KPI series — as CSVs in a working directory before analysis so every figure and quote is auditable.

## Phase 1: Target Grounding and Comp Set

1. **Peer set.** If the user supplied peers, use them as given (validate each resolves; note, without overriding, any that look weakly relevant). Otherwise derive 4-8 comps: start from the finance peer tool, then cross-check against the competitor set the company itself names in its latest 10-K (Item 1/1A) or equivalent filing — self-declared competitors often differ from classification-based peers and are exactly the companies whose expert calls carry read-through. Include 1-2 private competitors where central to the competitive story (note the thinner data). One-line rationale per comp.
2. **Grounding data.** Pull the target's segment revenue and KPIs (segments tool — ARPU, NRR, GMV, units, backlog as applicable), FY+1/FY+2 consensus for revenue and EPS with dispersion where available, the last 4 earnings-call transcripts (Q&A separable — raw material for Phase 5 debate mapping), earnings history (surprises, post-earnings moves), and the next scheduled earnings date, which anchors the "when would this evidence show up" framing.

## Phase 2: Interview Surfacing and Selection

Search Guidepoint across three concentric rings, restricted to the lookback window:

1. **Direct coverage:** interviews about the target itself — customers, former employees, competitors, channel partners/distributors, suppliers, industry consultants.
2. **Comp coverage:** interviews about each Phase 1 comp — for industry read-through and the reverse-reference sweep below.
3. **Reverse-references:** interviews nominally about OTHER companies in which the target is mentioned. Experts speaking about a different subject are often less guarded — treat unprompted target mentions as high-value evidence and tag them `reverse-reference`.

Build an **interview inventory**: interview date, subject company, expert role category (current/former customer, competitor, channel partner, former employee, supplier, consultant), seniority and recency (for formers: departure date), themes touched, direct vs. reverse-reference, and a relevance score. Rank by: direct target coverage > reverse-reference > industry-level; expert proximity (decision-maker > observer); recency; and marginal role diversity (a 12th customer adds less than a first channel partner). Select the most relevant interviews for deep reading — typically 10-25 depending on coverage — and state both counts ("38 identified in window; 16 read in full"). If target coverage is thin (fewer than ~5 relevant interviews), say so plainly, widen the window with an explicit note, and lean on comp and reverse-reference evidence rather than overreading a tiny sample.

## Phase 3: Theme Extraction and Corroboration

Extract evidence against six standing theme categories: **demand** (pipeline, win rates, budget tone, usage/expansion), **pricing** (realized price, discounting, pricing power), **competition** (share shifts, displacement wins/losses), **execution/management** (leadership quality, attrition, roadmap delivery), **product** (product reality vs. marketing, gaps), and **channel** (partner economics, inventory, sell-through vs. sell-in). If the user selected focus themes, go deepest there but still scan all six and surface anything material outside the selection; if none were selected, rank themes by evidence strength — corroboration count, specificity, recency — and lead with the strongest.

1. **Quote register.** For every extracted datapoint log: interview date, expert role, subject company, verbatim quote, theme tag(s), direction for the target, specificity (quantified/directional/vague), and direct vs. reverse-reference. Ships as an appendix or sheet.
2. **Corroboration matrix.** Themes as rows, interviews as columns, cells showing direction. Compute n supporting / contradicting / mixed per theme and apply the anecdote → emerging → corroborated ladder, noting cross-role corroboration explicitly.
3. **Contradictions.** Where experts disagree, present both sides with dated quotes and adjudicate on proximity, recency, specificity, and structural bias; state the verdict and confidence. Never average away a live disagreement — a genuine expert split on a load-bearing question is itself a finding.

## Phase 4: Tone Trajectory Across Quarters

1. Bucket the reviewed interviews by calendar quarter across the lookback window. For each theme with sufficient coverage, score expert tone per quarter on a -2 to +2 scale, each score backed by the underlying quotes, and chart the trajectory.
2. Show n per quarter on every trajectory exhibit and refuse to over-read sparse cells — a one-interview quarter is a datapoint, not a trend. Where coverage is too thin for quarterly bucketing, say so and present an earlier-half vs. later-half comparison instead.
3. Flag inflections: quarters where tone turned, and whether the turn preceded, coincided with, or followed the reported KPI trend and stock move over the same period. Expert tone that leads reported numbers is the highest-value output of this skill; identify it explicitly where the evidence supports it, and say so honestly where it does not.

## Phase 5: KPI and Debate Mapping

1. **KPI map.** For each corroborated signal (and any high-stakes single-source claim worth flagging), name the specific target line it should show up in — segment revenue, NRR, gross margin, unit volume, attach rate, backlog — the direction, the plausible timing (which upcoming print), and whether the expert evidence confirms, front-runs, or contradicts the reported trend and consensus. Use exact reported figures with periods; never "~".
2. **Live debates.** Identify the 3-5 live investor debates from the last 4 transcripts' recurring analyst Q&A topics, consensus estimate dispersion, and recent rating/target changes. For each: what the expert evidence says, which side it supports, with what n and the 1-2 strongest dated quotes — and name the debates on which the expert record is silent or too thin to adjudicate. Silence on a hot debate is worth reporting.
3. **What would change the view.** For the strongest signals, state the falsifier: the reported datapoint or future interview evidence that would overturn the expert read.

## Fallback Mode (Guidepoint not connected)

Deliver the best available analysis from public expert-adjacent evidence, labeled prominently and repeatedly as **public-transcript evidence — NOT expert-call data**: (a) the target's last 4-8 earnings-call Q&A sections (analyst pressure points, management evasions); (b) comp and supplier/customer earnings transcripts that mention the target or its market — the public analog of reverse-references; (c) industry conference and analyst-day transcripts from primary sources. Run the same discipline — dated attributed quotes, corroboration counts across companies, tone trajectory by quarter, KPI and debate mapping — while stating its limits: public speakers are promotional and lawyered, and there is no customer or former-employee vantage. Include the one-line note on what connecting Guidepoint unlocks. Never present fallback output as expert-call synthesis.

## Phase 6: Output Creation

Honor the selected `output_format`; default to PDF when ambiguous — the deliverable is judgment- and quote-heavy. All formats present the same underlying dataset: coverage header (mode, interviews identified/read, date range, role mix), executive summary (3-5 strongest signals with n counts and dates), interview inventory, theme sections with quotes and corroboration counts, tone trajectory exhibits, KPI and debate map, contradictions and single-source watchlist, conclusion, methodology.

- **PDF (portrait memo — default):** sections in the order above; the mode banner (expert-call vs. public-evidence fallback) sits at the top of page 1.
- **XLSX:** sheets — `Executive Summary`, `Interview Inventory`, `Quote Register`, `Corroboration Matrix`, `Tone by Quarter`, `KPI & Debate Map`, `Single-Source Watchlist`, `Sources & Methodology`. House formatting: Calibri; dark teal #1B474D headers with white text; percentages `0.0%`; blue text for hardcoded inputs, formulas black; freeze panes on tables; hide gridlines on report-facing sheets; source notes on every sheet. Derived counts and scores as live formulas where practical.
- **PDF (Presentation):** follow the deck standards below — cover; coverage and mode; executive summary; one slide per major theme (corroboration count in the headline); tone trajectory; KPI and debate map; watchlist; conclusion; appendix.
- **Dashboard:** panels for theme cards (expandable to quotes), corroboration matrix, tone trajectory with quarter filters, interview inventory with role filters, KPI/debate map, and methodology; deploy and provide the link.

Charts: DPI 150, figsize 12x7, seaborn-v0_8-whitegrid, palette #20808D, #A84B2F, #1B474D, #BCE2E7, #944454, #FFC553. Titles state the insight (e.g., `Customer Tone Turned Negative Two Quarters Before Reported NRR`), not just the data.

## Phase 7: Conclusion

Answer the core question directly: (1) the single strongest corroborated expert signal, its n, and whether the market appears to price it; (2) where expert evidence contradicts consensus or reported optics, and which side the weight of evidence favors; (3) the most interesting single-source anecdote worth monitoring but not acting on; (4) tone trajectory verdict — improving, deteriorating, or mixed — and against which KPI to test it; (5) a monitoring plan: what to watch in the next print (with date), and what future expert evidence would confirm or falsify the read. Be blunt about sample size: state total n and role mix wherever a conclusion rests on it.

Share the output file or deployed dashboard and present the conclusion in the response.

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## Provider Traceability Requirement (Guidepoint / FactSet)

When `data_source` includes `guidepoint` or `factset`, raw figures and quotes sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:
1. Make raw figures and quotes clickable wherever the provider returns a URL, deep link, transcript link, document reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure/quote itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source-note cells where feasible, and include a `Sources & Methodology` or `Source Map` sheet with provider, company/entity, metric or interview reference, period or interview date, as-of timestamp, provider document/interview ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, quote card, KPI tile, chart datapoint, or detail drawer displaying a raw provider figure or quote must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Guidepoint interview/transcript IDs, interview dates, and expert role descriptors with any returned transcript links; FactSet entity, metric, document, and any returned URL/deep link.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity identifier, metric/series or interview ID, period or interview date, and as-of timestamp, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures and quotes. Derived calculations should reference the source figures used.

---

## Output format: PDF (Presentation)

When the user selects output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF. Do NOT produce the standard portrait memo; this format replaces it.

### Page setup
- Orientation: landscape
- Page size: US Letter landscape (11" x 8.5") or widescreen 16:9 (13.333" x 7.5") — default to 16:9 for a modern deck feel
- Margins: 0.5"–0.75" on all sides
- One logical slide per page

### Slide anatomy
- Title bar at top: concise, insight-led headline (e.g., "Customers report lengthening sales cycles" not "Demand Overview"). 24–32 pt, bold.
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
- Fact-check every number against the selected data sources.
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
4. **Connector gate (supersedes the BYOL non-stalling rule for this skill only)**: This skill's core evidence base is expert-call transcripts. At the very start — before any research or extended reasoning — check whether Guidepoint (or another expert-network connector) is connected. If not, STOP and surface this to the user: state that Guidepoint is not connected, explain what it would add, and ask whether to (a) connect it, (b) proceed using only public expert-call proxies, or (c) cancel. Proceed only after the user chooses. (An explicit user instruction in the initial request choosing option (b) satisfies this gate.)

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `office/pdf`, `office/pptx`, `office/xlsx`, `data/visualization`, `website-building/webapp`.
