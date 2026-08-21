---
name: peer-earnings-read-through
description: "Analyze recent peer earnings transcripts to isolate industry themes and translate them into target-company implications with confidence and transmission mechanisms."
metadata:
  perplexity:
    display_name: "Peer earnings read-through"
---
# Peer Earnings Read-Through

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `target_company` (Target company)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `peer_companies` (Peer basket (optional)) — Leave blank to have the basket built automatically with rationale for each peer. No default — omit silently if the user does not provide it.
- `focus_areas` (Focus areas) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Morningstar, PitchBook) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Peer Earnings Read-Through

Analyze the most recent earnings calls and results of a target company's peer set to isolate industry-level themes and translate them into specific, dated, confidence-rated implications for the target. The core investor question: what have peers already told the market that the target's next print will confirm or contradict — and through what mechanism? This is not a comps valuation exercise and not a summary of peer quarters; every peer datapoint must earn its place by changing the expected trajectory of a target P&L line, KPI, or guidance posture.

## Phase 0: Setup and Data Sources

1. Resolve the target company to a name and ticker before any ticker-dependent pull. If ambiguous, resolve to the most liquid primary listing and state the choice.
2. Derive all as-of parameters from the run date. Record the run date/time prominently; every transcript quote and market figure in the output carries its own date.
3. Pull the target's next scheduled earnings date (earnings schedule tool). This date anchors the entire analysis: read-throughs are framed as "what should show up in the target's [specific fiscal quarter] print on [date]."
4. `data_source` is a set of one or more sources collected at intake: the user may pick any combination of Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc (alt data), and Guidepoint (expert calls); the default set is Perplexity Finance, FactSet, Daloopa, Carbon Arc, and Guidepoint. Premium providers are bring-your-own-license: for each selected source, check whether its connector is actually connected. If a source is selected but not connected, proceed without it and add exactly one line to the deliverable's sourcing note naming what it would have added to this read-through — e.g., "Guidepoint was selected but is not connected; connecting it would add expert calls on the peers that reference the target and its shared demand pools." Never stall or fail the run over an unavailable premium source; Perplexity Finance built-in tools plus primary public sources (filings, IR releases, official transcripts) are the always-available baseline. Never use low-quality aggregators.
5. Assign a provider of record per data domain from the selected-and-connected set, and state it on every exhibit: fundamentals and KPI history — Daloopa > FactSet > Morningstar > built-in; consensus estimates and revisions — FactSet > built-in; private-company data (if a private peer or customer matters) — PitchBook > built-in; fund/ETF holdings analytics — Morningstar > built-in; alt-data demand/transaction signals — Carbon Arc; expert qualitative evidence — Guidepoint. Selected sources are complementary, not redundant: use overlapping coverage to cross-validate every load-bearing figure (any number an executive-summary read-through depends on) across at least two providers where coverage exists. Where providers disagree materially, show both values and explain the basis difference (definition, calendarization, restatement) — never silently average. One table column or one time series = one provider basis; never splice providers within a series without an explicit footnote at the splice point.
6. Save all raw tabular pulls (peer lists, earnings histories, segment data, quote logs) as CSVs in a working directory before analysis so figures are auditable.

## Phase 1: Peer Basket Construction

If the user supplied a peer basket, use it as given; validate each ticker resolves and note (without overriding) any peer whose relevance seems weak. If no basket was supplied, construct one:

1. Start from the finance peer tool (`finance_company_peers`) for the target, then apply judgment. Classification-based peers (same SIC/GICS) are a starting point, not the answer. For read-through purposes, **suppliers, customers, and channel partners are often more informative than same-industry peers** — a chip supplier's bookings commentary can front-run an OEM's revenue; a big-box retailer's inventory posture can front-run a CPG company's sell-in. Deliberately consider four buckets:
   - Direct competitors (same end market, substitutable products)
   - Upstream suppliers to the target or to the target's industry
   - Downstream customers / channel partners / distributors
   - Demand-adjacent bellwethers (companies exposed to the same end-demand pool or spending budget, even in a different sector)
   Source candidates from more than the obvious names, using three sweeps: (a) **10-K competitor sets** — the "Competition" sections of the target's 10-K and of candidate peers' 10-Ks; a company that names the target as a competitor belongs on the candidate list even if the target does not name it back; (b) **supply-chain disclosures** — customer-concentration disclosures (customers >10% of revenue), named suppliers and partners in 10-Ks, 8-Ks, and IR materials, on both the target's side and candidates' side; (c) a **quantitative same-driver screen** via the built-in screener/peer tools — same end market with similar growth/margin profile, plus companies whose revenue or KPI history co-moves with the target's key drivers. This surfaces non-obvious read-through names that classification codes and habit miss.
2. Target 6–10 peers. For each, record: ticker, relationship bucket, one-line rationale for why its commentary transmits to the target, and its two most recent earnings call dates.
3. Exclude peers whose most recent call predates the target's own most recent call by more than one full quarter unless they are uniquely informative (state why if kept).
4. Present the final basket as a **Basket Rationale table** early in the output: peer, relationship type, transmission relevance, latest call date, days since call. State explicitly which peers were user-provided vs. constructed.
5. Note in the output (one line) that formal valuation-oriented peer selection is covered by the separate Comparable Companies skill; this basket is optimized for information transmission, not multiple comparability.

## Phase 2: Evidence Collection (per peer)

For each peer in the basket:

1. **Full artifact set per print:** for each of the peer's two most recent prints, collect the **press release, the earnings presentation/slide deck, and the transcript — both prepared remarks AND Q&A** (transcript tool; earnings schedule/history tools to confirm call dates). Treat Q&A as first-class evidence, not an appendix: read-through signal disproportionately lives in Q&A answers about demand, pricing, and inventory that management did not volunteer in prepared remarks; tag every quote in the register as prepared-remarks or Q&A. Presentations often carry segment/KPI detail and guidance bridges absent from the release. Two prints per peer establishes a delta — what changed in tone, guidance, and emphasis between the prior call and the latest one is often more informative than the level.
2. **Results context:** pull actuals vs. consensus and post-earnings stock reaction (earnings history tool) for the same two quarters, and segment/KPI detail (segments tool) where the read-through runs through a specific segment (e.g., only the peer's datacenter segment is relevant to the target). Do not use consolidated financials where a segment is the true transmission channel.
3. **Quote discipline:** every claim attributed to a peer must be backed by a verbatim quote with speaker name, role, fiscal quarter referenced, and **call date**. Log quotes in a structured quote register: peer, quarter, call date, speaker, artifact (prepared remarks / Q&A / presentation / press release / expert call), verbatim quote, theme tag(s), direction (positive/negative/neutral for the theme), specificity (quantified / directional / vague).
4. **Staleness (as-of discipline):** compute days elapsed between each call date and the run date. Flag any commentary older than **70 days as stale**; in fast-moving markets (semis, energy, freight, anything mid-cycle-turn) flag at **45 days**. Stale quotes may still be used for trend context but must be visibly labeled and cannot anchor a High-confidence read-through on their own. A demand comment from 10 weeks ago is a historical datapoint, not a current signal.
5. If a transcript is unavailable for a peer (e.g., recent IPO, foreign issuer without English transcript), state the gap, use the press release and prepared-remarks documents from IR as fallback, and note the lower evidentiary weight. Never fabricate quotes.
6. **Guidepoint (when selected and connected):** pull recent expert calls on the PEERS, not only the target. Reverse-references are the highest-value read-through evidence: an expert discussing a peer who mentions the target by name, its share position, or the demand pool both companies sell into. Also pull expert calls on the shared customer set or channel where they exist. Log expert evidence in the quote register with call date, the expert's vantage point (former employee, customer, channel partner), and the same staleness flags as transcripts. Expert testimony that corroborates a peer's public commentary can raise a theme's confidence one notch; expert testimony that contradicts it caps confidence at Medium and must be surfaced in the conflicts section.
7. **Carbon Arc (when selected and connected):** pull cross-company alt-data demand/transaction signals for the target, each peer where covered, and the shared end market. For every candidate industry signal, answer explicitly: does the TARGET's own alt-data trend confirm or diverge from the peer's reported trend? Confirmation upgrades confidence; divergence is a finding in itself — say whether it implies share shift or a timing lag, and report it rather than smoothing it. Before relying on any alt-data series, reconcile it against the peer's reported KPI for the quarters where both exist and state the historical fit.

## Phase 3: Theme Extraction — Anecdote vs. Signal

Extract commentary across these seven standing theme categories (add sector-specific categories where warranted, but always cover these):

1. Demand commentary (order trends, pipeline, win rates, end-market tone)
2. Pricing (realized price, discounting, pass-through, pricing power language)
3. Inventory / backlog / book-to-bill (channel inventory, destocking/restocking, backlog cover)
4. Capex intentions (peer's own capex plans and any customer-capex commentary)
5. Customer behavior (deal elongation, budget scrutiny, seat/usage trends, trade-down)
6. Geographic and segment divergences (regions or segments inflecting differently)
7. Guidance direction (raise / maintain / cut; guide philosophy changes; visibility language)

For each theme, build a **corroboration matrix**: rows = themes, columns = peers, cells = direction (+ / − / mixed / not mentioned) with the supporting quote reference. Then apply the evidence standard:

- **Mentioned by one peer = anecdote.** Report it, but label it peer-idiosyncratic until corroborated. Ask explicitly: is this a company-specific issue (share loss, execution, one-off comp) masquerading as an industry theme?
- **Corroborated by two peers = emerging signal**, especially if the peers sit in different basket buckets (a supplier and a competitor saying the same thing is stronger than two competitors).
- **Corroborated by three or more peers, same direction = industry signal.** Track and report the mention count and net direction for every theme.
- Weight quantified statements above directional ones, and directional above vague; weight the latest call above the prior call; weight unprompted prepared-remarks disclosure and specific Q&A answers above analyst-led framing the management merely accepted.
- Actively reject false positives: call out themes that sound narratively important but have weak evidence (one vague mention, stale quote, or a peer with an obvious idiosyncratic motive to spin).
- Where a peer's own beat/miss and stock reaction contradict its qualitative tone (upbeat call, stock down 8%), note it — the market's reaction to a peer print is itself read-through evidence.
- **Company-specific vs. industry-wide, decided explicitly:** for every peer surprise (beat/miss, guide change, or notable tone shift), write down both competing explanations — company-specific (share gain/loss, execution, one-off comps, mix, self-inflicted) and industry-wide (demand, pricing, inventory cycle, shared cost inputs) — and state which one the evidence supports, citing the discriminating datapoint (a supplier corroborating the same trend argues industry-wide; a direct competitor printing the opposite result argues share shift). Only industry-wide explanations transmit to the target directly; company-specific ones transmit only through the competitive-substitution mechanism, with the sign inverted. Do this separation per surprise, in the output, not just implicitly.

## Phase 4: Target Translation — Mechanism, Direction, Magnitude, Timing, Confidence

This is the payoff phase. Open the section with a **Read-Through Map table** — one row per read-through, columns: peer datapoint (with source and date) → shared driver / transmission mechanism → quantified implication for the specific target KPI (direction and magnitude with the arithmetic shown, or "direction only") → timing (which target print) → confidence rating. The map is the skeleton the reader scans first; the entry blocks below carry the quotes and full reasoning, in the same row order. For each industry signal (and any high-stakes anecdote worth flagging), produce a read-through entry with all six elements:

1. **Theme and evidence:** the signal, mention count, net direction, and the two or three strongest dated quotes.
2. **Transmission mechanism:** state exactly WHY the peer statement maps to the target — name the mechanism explicitly. Standard mechanisms: shared customers or customer budgets; shared supply chain (common suppliers, input costs, lead times); competitive substitution (peer strength may be target weakness — direction can invert); pricing umbrella (peer price moves reset the market's price expectations); shared macro/geographic exposure; channel inventory transmission (destocking upstream hits shipments downstream with a lag). If no credible mechanism exists, say so and drop the read-through — correlation of narratives is not a mechanism.
3. **Mapped target line item / KPI:** the specific P&L line, segment, or KPI where the effect should appear (e.g., "Data Center segment revenue," "gross margin via memory input costs," "NRR via seat contraction"), not just "revenue."
4. **Direction and magnitude:** direction for the target (note where competitive substitution inverts the sign), and magnitude where estimable — sized from the peer's quantification, the target's revenue mix, or historical elasticity between the two (e.g., "peer cited high-single-digit ASP decline; at the target's 30% exposure to that product line, roughly a 200–300 bps revenue headwind"). Show the arithmetic. If magnitude is not estimable, say "direction only" rather than inventing precision.
5. **Timing:** which target print the effect should show up in (next quarter's results, next quarter's guide, or 2+ quarters out), reflecting fiscal-calendar offsets and typical lags in the transmission channel (channel inventory effects lag; pricing umbrella effects can be immediate in guidance language).
6. **Confidence rating with rationale:** High / Medium / Low, justified against four criteria: corroboration count, mechanism directness, quote freshness, and specificity/quantification. A single stale, vague, uncorroborated mention can never exceed Low. For each entry also state the falsifier: what evidence (a datapoint, a peer print still to come, a target disclosure) would kill or confirm this read-through before the target reports.

Also state, briefly, **what is already priced in**: check the target's consensus revision trend and recent stock performance relative to the peer news flow (estimates and price tools). A well-telegraphed peer signal the target has already de-rated on is not an edge; flag which read-throughs appear priced vs. unpriced.

## Phase 5: Read-Through Conflicts

Include a dedicated section wherever peers disagree on a theme (one raises on demand, another cuts). For each conflict:

1. Present both sides with dated quotes.
2. Adjudicate which side carries more weight for the target and why: recency, proximity of the peer's business to the target's (a peer sharing the target's exact customer set outranks a distant bellwether), quantification, and each peer's guidance credibility (check their last 4 quarters of guide-vs-actual via earnings history).
3. If the conflict is genuinely unresolvable, say so, state what the disagreement implies (e.g., share shift between the two peers rather than an industry trend), and define what upcoming datapoint resolves it.

## Phase 6: Output

Honor the selected `output_format`; all formats present the same underlying dataset. **Default is the PDF memo** when ambiguous.

Standard section order (all formats):
1. Header — target, ticker, run date/time, target's next earnings date, basket size, data sources used (provider of record per domain; one-line notes for any selected-but-unconnected providers).
2. Executive summary — the 3–5 read-throughs that matter most, each with direction, target line item, timing, and confidence in one line.
3. Basket Rationale table (Phase 1.4).
4. Peer print scoreboard — per peer: latest quarter result vs. consensus, guide action (raise/maintain/cut), post-print stock reaction, call date, staleness flag.
5. Theme corroboration matrix with mention counts and net direction.
6. Read-Through Map table followed by the read-through entries (Phase 4) — one block per theme, ordered by decision relevance to the target, not by mention count.
7. Company-specific vs. industry-wide adjudication for each peer surprise (Phase 3).
8. Read-through conflicts (Phase 5).
9. Anecdote watchlist — uncorroborated single-peer items worth monitoring, clearly labeled as anecdote.
10. Conclusion — direct answer to the core question: net, do peer prints point to upside, downside, or mixed risk into the target's next print; which read-throughs appear priced in; the monitoring plan (remaining peer prints on the calendar before the target reports, with dates, and which theme each will confirm or refute).

Format specifics:
- `pdf`: portrait memo, tightly edited, tables for the scoreboard and matrix, exact figures throughout (never "~"), every quote dated.
- `xlsx`: sheets — Summary, Basket Rationale, Peer Scoreboard, Quote Register, Theme Matrix, Read-Through Map, Read-Throughs, Conflicts, Sources & Traceability.
- `dashboard`: panels mirroring the section list, with quote-level tooltips (quote, speaker, call date, staleness flag) on matrix cells and read-through cards.
- `pdf_presentation`: follow the PDF (Presentation) block below; one read-through per slide with an insight-led headline.

Never expose internal implementation details (workspace paths, tool mechanics) in user-facing output. Do not give buy/sell/hold recommendations or price targets; the deliverable is the read-through map, its confidence structure, and the monitoring plan.

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

## Output format: PDF (Presentation)

When the user selects output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF. Do NOT produce the standard portrait memo; this format replaces it.

### Page setup
- Orientation: landscape
- Page size: US Letter landscape (11" x 8.5") or widescreen 16:9 (13.333" x 7.5") — default to 16:9 for a modern deck feel
- Margins: 0.5"–0.75" on all sides
- One logical slide per page

### Slide anatomy
- Title bar at top: concise, insight-led headline (e.g., "Three peers flagged channel destocking — a Q3 shipment headwind" not "Inventory Overview"). 24–32 pt, bold.
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

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `office/pdf`, `office/pptx`, `office/xlsx`, `data/visualization`, `website-building/webapp`.
