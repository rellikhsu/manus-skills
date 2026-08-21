---
name: lbo
description: "Build a fully linked XLSX leveraged buyout model for public-to-private or private-company transactions with debt schedules, cash sweep, returns, sensitivities, covenants, and validation."
metadata:
  perplexity:
    display_name: "LBO"
---
# LBO

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `target` (Target company) — Public ticker/name for a take-private, or a private company name. Attach financials below for private targets.

OPTIONAL — assume the default (or omit) unless the user specifies:
- `deal_type` (Deal type) Options: `auto` (Auto-detect); `public_to_private` (Public-to-private); `private` (Private target). Default: `auto`.
- `offer_premium` (Offer premium (public targets)) — Premium to the current share price. Default 30% if blank, stated as an assumption. No default — omit silently if the user does not provide it.
- `entry_multiple` (Entry multiple or price (private targets / override)) — Entry EV/EBITDA or a fixed enterprise value. If blank for private targets, derived from peer trading multiples with an explicit note. No default — omit silently if the user does not provide it.
- `hold_period` (Hold period) Options: `3` (3 years); `5` (5 years); `7` (7 years). Default: `5`.
- `leverage` (Target leverage) — Total leverage in turns of LTM EBITDA, with tranche split if you have one. Default 5.0–5.5x if blank. No default — omit silently if the user does not provide it.
- `debt_structure` (Debt tranches) — Default if blank: revolver (undrawn) + TLB + senior notes. Rates built as base rate + spread from current market data. Options: `revolver` (Revolver (undrawn, commitment fee)); `tla` (Term Loan A (amortizing)); `tlb` (Term Loan B (1% amortization, cash sweep)); `senior_notes` (Senior notes (bullet)); `mezz_pik` (Mezzanine with PIK toggle). No default — omit silently if the user does not provide it.
- `rollover_equity` (Rollover equity) — Management or seller equity rolled into the deal, tracked as a separate class through exit. No default — omit silently if the user does not provide it.
- `exit_multiple` (Exit multiple) — Default: exit at the entry multiple. Any assumed expansion is flagged prominently in the returns story. No default — omit silently if the user does not provide it.
- `reference_files` (Reference documents) Ask the user to attach the file(s) in chat. No default — omit silently if the user does not provide it.
- `context` (Additional context) No default — omit silently if the user does not provide it.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `daloopa` (Daloopa); `factset` (FactSet); `morningstar` (Morningstar); `pitchbook` (PitchBook). Default: `perplexity_finance`, `daloopa`, `factset`, `pitchbook`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Morningstar) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `xlsx` (XLSX); `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `dashboard` (Dashboard). Default: `xlsx`.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Leveraged Buyout Model

Build a fully linked, formula-driven Excel LBO model for the specified target — a public company being taken private or a private company — and answer the sponsor's core questions: what does the deal pay at entry, can the capital structure service itself through the hold, and what IRR and MOIC does the equity earn at exit, driven by what? The workbook must recalculate live when any assumption changes, and every returns claim must trace to sourced inputs.

## Core Rules

1. Every projected or derived cell must contain an Excel formula, never a Python-computed constant. Hardcodes are permitted only for sourced historical values and explicit user/editable assumptions, and both must be visually distinguished (blue font) and cited.
2. Do not silently convert missing or null source values into zero. If a required input is unavailable, source it, estimate it with an explicit confidence flag, or disclose the gap — never fabricate.
3. Show exact figures with as-of dates; never approximate with "~". Every market data point carries its pull date.
4. Editable assumptions drive the model. A user must be able to change the offer premium, leverage, margin ramp, or exit multiple on the assumptions tabs and watch sources & uses, the debt waterfall, covenants, and returns update without touching any other cell.
5. No unintended circular references and zero formula errors after recalculation. The interest circularity treatment in Phase 4 is mandatory and must be documented in the workbook.
6. Do not create charts unless explicitly requested; the model is table-based.
7. Never expose internal implementation details (workspace paths, tool mechanics, intermediate files) in the workbook or the memo. Output must be exec-ready.

## Phase 0: Scope the Transaction

1. Classify the target:
   - **Public-to-private**: the target trades publicly. Resolve the ticker first, confirm listing venue, currency, and fiscal year-end.
   - **Private**: no listed equity. Determine whether the user supplied financials (uploaded databook, CIM, prior model) or whether financials must be triangulated.
   - If `deal_type` is auto, classify from the ticker lookup result and state the classification.
2. Fix model parameters: presentation currency and units (state $M or local-currency M in headers), hold period (default 5 years; also compute returns for exits in every year of the hold), transaction close assumed at the most recent balance sheet date unless the user specifies otherwise, and annual projection cadence.
3. Parse user inputs for offer premium, entry multiple, target leverage, debt structure, rollover equity, and exit multiple. Where blank, apply the defaults defined in the phases below and label each default as a stated assumption in the workbook — never as fact.

## Phase 1: Data Collection

Use finance tools first for all market and company data; save raw tabular pulls to a working directory before analysis. `data_source` is a set of one or more sources collected at intake — options: Perplexity Finance (built-in), Daloopa, FactSet, Morningstar, PitchBook; defaults: Perplexity Finance, Daloopa, FactSet, PitchBook — and the run should draw on every selected source. Premium providers are bring-your-own-license: for each selected source, check whether its connector is connected. If selected but not connected, continue without it and add one line to the Methodology sourcing notes — "<Provider> was selected but is not connected; connecting it would add <what it adds to this model, e.g. filing-traceable historical fundamentals (Daloopa), the consensus operating trajectory (FactSet), sponsor precedent deal terms (PitchBook)>" — and never stall the run; the built-in finance tools are the always-available baseline. Assign a provider of record per data domain from the selected-and-connected set and state it in each sheet's source notes: historical fundamentals and KPI history — Daloopa > FactSet > Morningstar > built-in; consensus forward estimates — FactSet > built-in; sponsor precedent buyout terms — PitchBook; live quotes and macro rates — built-in tools. Cross-check the load-bearing entry inputs (LTM EBITDA, net debt, fully diluted shares) against a second selected provider where coverage overlaps; where providers disagree materially, show both values with the basis difference (e.g., adjusted vs reported EBITDA) — never silently average. One historical series = one provider basis; never splice providers within a row without a footnote at the splice point. Use public web sources only after these are insufficient, and prefer primary sources (filings, earnings releases, transcripts, IR materials); cite them.

### Public targets

1. Pull the current share price, market cap, and as-of timestamp with the quotes tool. Record the exact price and timestamp — this anchors the offer price.
2. Pull 3 fiscal years plus LTM of income statement, balance sheet, and cash flow data (company financials tool), adjusted/non-GAAP EBITDA (adjusted metrics tool), consensus forward revenue and EBITDA (estimates tool), and leverage/margin ratio history (company ratios tool). When Daloopa is selected and connected it is the provider of record for these historicals — pull its as-reported and adjusted series with filing-level references and use built-in tools only to fill gaps, footnoted. When FactSet is selected and connected it is the provider of record for the consensus operating trajectory (forward revenue, EBITDA, margins, and capex where covered) that anchors the base case.
3. Build the fully diluted share count using the **treasury stock method at the offer price**: basic shares outstanding plus in-the-money option and warrant dilution net of assumed buyback proceeds, plus unvested RSUs, from the latest 10-K/10-Q share tables when finance tools do not carry instrument-level detail. Show the TSM calculation as live formulas on the transaction assumptions tab, with the option/RSU inputs cited to the filing.
4. Identify existing debt (by instrument where disclosed), cash, and any preferred/NCI that affects the equity-to-enterprise bridge. Where findable, ground the debt picture in the actual credit documents — credit agreements and indentures filed as 8-K/10-K exhibits: maturities, pricing, call protection/make-whole, covenant packages, and change-of-control puts — and cite the filing; these terms drive the refinancing cost at close and whether any tranche can economically remain outstanding. Default assumption is all existing debt is refinanced at close.
5. Pull peer trading multiples (peers + ratios tools) to contextualize the entry multiple. When PitchBook is selected and connected, also pull sponsor precedent buyouts in the target's sector — entry EV/EBITDA, total leverage, and structure for recent comparable LBOs — to calibrate the entry multiple, leverage default, and tranche split; cite the specific precedent deals used (sponsor, target, close date, multiple, leverage) on the Transaction Assumptions sheet and in the memo.

### Private targets

1. If reference documents are uploaded (CIM, databook, financial statements), treat them as the primary source and extract revenue, EBITDA, capex, working capital, and debt directly, citing page/section.
2. If not, triangulate: press releases and news of prior funding or M&A, the private company info tool (funding history, marks, secondary prices), industry benchmarks from public comparables, and any disclosed metrics (headcount, unit volumes, ARR). Every triangulated figure carries a **confidence flag — High / Medium / Low —** in a dedicated column on the assumptions tab, with the basis stated (e.g., "Low — revenue inferred from disclosed ARR growth and press-reported headcount").
3. If EBITDA cannot be established even at Low confidence, stop and deliver a structured input request listing the minimum data needed (LTM revenue, EBITDA or margin, capex, existing debt) rather than a model built on invented numbers.

### Financing market data

1. Pull the current base rate for the deal currency from the macro snapshot tool — term SOFR or the closest available short-term benchmark for USD, and the equivalent benchmark for other currencies — with the exact value and as-of date. All floating tranche pricing is built as **base + spread** referencing this cell.
2. Set tranche spreads from current leveraged-credit conditions when reliable market color is available (cite it) — preferring observed pricing from credit agreements of recent comparable sponsor deals (8-K exhibits) or PitchBook precedent terms, citing the deal; otherwise apply standard structuring ranges as explicit editable assumptions (e.g., revolver S+225–275, TLA S+250–300, TLB S+350–450 with 0–75 bps floor, senior notes fixed at TLB + 150–250 bps, mezzanine 11–13% with PIK option). Mark every spread blue and note its basis.

## Phase 2: Entry Valuation and Sources & Uses

Build a **Transaction Assumptions** sheet followed by a **Sources & Uses** sheet, all formula-linked.

1. **Entry price.**
   - Public: offer price per share = current price × (1 + offer premium). Default premium 30% if unspecified (state it as a default; typical take-private premia run 20–40%). Equity purchase price = offer price × TSM fully diluted shares. Enterprise value = equity purchase price + refinanced debt − cash acquired (adjust for preferred/NCI where present). Show the implied entry EV/EBITDA on LTM and forward EBITDA next to peer trading multiples — and the PitchBook sponsor precedents where pulled — so the user sees the premium paid versus the market and versus what sponsors have actually paid.
   - Private: entry EV = entry multiple × LTM EBITDA (user-provided multiple, or default to the peer trading median with an explicit note that private targets typically transact at a discount to public comps).
2. **Fees**: financing fees by tranche (default 2.0–2.5% of funded debt, capitalized and amortized over tranche tenor) and transaction/advisory fees (default 1.5–2.0% of EV), both editable.
3. **Uses**: equity purchase price, refinancing of existing net debt, transaction fees, financing fees, and minimum cash funded to the balance sheet.
4. **Sources**: each debt tranche sized in turns of LTM EBITDA per the target leverage (default if unspecified: total leverage 5.0–5.5x split TLB ~3.5–4.0x, senior notes ~1.5x, revolver undrawn at close), **rollover equity** if specified (management or seller rollover, shown as a distinct source and tracked as a separate equity class through exit), and **sponsor equity as the plug** = total uses − debt − rollover. Show sponsor equity as % of total capitalization (flag if below ~30% — thin equity cushions are a credit-committee concern).
5. **Check row**: Sources − Uses = 0, conditionally formatted red if nonzero.

## Phase 3: Operating Model

Build the projection engine on an **Operating Model** sheet driven entirely by an editable assumptions block.

1. **Revenue build**: use the most granular sourced driver structure available — segment growth, unit × price, or consolidated growth — with per-year editable growth rates. Anchor years 1–2 of the base case to consensus estimates for public targets (cite them); fade growth toward a sustainable terminal rate by exit. Where management has published guidance or medium-term targets (guidance ranges, investor-day plans), also record a **management case** alongside the consensus-anchored **street case** — same driver structure, different growth/margin assumptions, deltas stated and each case's source cited. Default the base case to street; the deal-thesis margin ramp belongs to the management/upside case unless the user directs otherwise.
2. **Margin bridge**: gross margin and opex ratios per year building to EBITDA, with an explicit EBITDA margin row. Where the deal thesis includes margin expansion, express it as stepwise assumption changes (bps per year) so the bridge from entry margin to exit margin is visible and editable — not a hardcoded exit EBITDA.
3. **Below EBITDA**: D&A (% of revenue or capex-linked), capex (% of revenue, sourced from history), working capital via DSO/DIO/DPO or NWC % of revenue delta, cash taxes at an assumed effective rate applied to EBT (EBT = EBITDA − D&A − interest from the debt schedule; use zero-floor on cash taxes when EBT is negative and note that NOL mechanics are simplified).
4. Compute **cash flow available for debt service**: EBITDA − cash taxes − capex − increase in NWC − mandatory amortization feeds the sweep in Phase 4.
5. All historical anchor figures blue and cited; all projections formulas.

## Phase 4: Debt Schedule

Build one roll-forward block per tranche on a **Debt Schedule** sheet: beginning balance → draws → mandatory amortization → cash sweep → (PIK accrual) → ending balance, plus cash interest and fees.

1. **Tranches**: revolver (undrawn at close unless specified; include a **commitment fee on the undrawn balance**, default 0.375–0.50%), TLA (amortizing, e.g., 5%/yr) and/or TLB (1%/yr mandatory amortization) per the selected structure, senior notes (bullet, no sweep unless specified), and mezzanine with a **PIK toggle**: a Y/N input that switches interest between cash pay and accrual added to principal (`ending balance = beginning + PIK interest − repayments`). Include only the tranches in the user's structure or the Phase 2 default; do not pad the model with unused tranches.
2. **Interest circularity — mandatory approach, document it**: use a non-iterative **average-balance approximation**. Compute each tranche's interest on the average of (a) the beginning balance and (b) the beginning balance less scheduled mandatory amortization; the discretionary cash sweep reduces only the ending balance and therefore affects the **following** period's interest. This breaks the interest→cash flow→paydown→interest loop, so the workbook requires no iterative calculation and recalculates cleanly. State this convention, and its direction of bias (slightly overstates interest in heavy-sweep years, conservative for returns), on the Methodology sheet. Do not use Excel iterative calculation.
3. **Cash sweep**: sweep % of excess free cash flow (default 100%, editable) applied in priority order — revolver first, then TLA, then TLB, then (only if permitted) notes/mezz. Every paydown formula uses MIN/MAX guards so no balance goes negative and no sweep exceeds available cash. If free cash flow is negative, draw the revolver (capped at the commitment; flag a liquidity shortfall if the cap binds).
4. Total debt, net debt, and cash roll-forward rows sum the tranches; beginning balances tie to Sources & Uses at close and to prior-period endings thereafter.

## Phase 5: Credit Metrics and Covenant Headroom

On a **Credit & Covenants** sheet, compute per year: total and net leverage (Debt/EBITDA), interest coverage (EBITDA/cash interest), and fixed charge coverage ((EBITDA − capex)/(cash interest + mandatory amortization)). Set assumed covenant levels — user-provided, or defaults of net leverage covenant at closing leverage + 0.75x with annual step-downs, and minimum interest coverage 2.0x — clearly labeled as assumptions. Show **headroom** rows (covenant minus actual, and cushion %) with conditional formatting: red on breach, amber within 15% cushion. Identify the tightest year and metric explicitly.

## Phase 6: Exit and Returns

On a **Returns Analysis** sheet:

1. **Exit value**: exit EV = exit multiple × exit-year LTM EBITDA. Default exit multiple = entry multiple (flag prominently whenever the base case assumes multiple expansion — returns that depend on paying less than you sell for deserve scrutiny). Exit equity = exit EV − net debt at exit; split between sponsor and rollover equity pro rata to invested amounts (adjust if the user specifies a different rollover structure).
2. **IRR and MOIC by exit year**: a table computing sponsor IRR and MOIC for an exit at the end of every year of the hold period, using IRR() over the full signed cash flow series (equity outflow negative at close, any interim distributions positive, exit proceeds positive) and MOIC = total proceeds / total invested. Highlight the target hold year.
3. **Value-creation attribution** for the base exit year, as an additive bridge that ties exactly:
   - EBITDA growth = (exit EBITDA − entry EBITDA) × entry multiple
   - Multiple expansion = (exit multiple − entry multiple) × exit EBITDA
   - Deleveraging = entry net debt − exit net debt (plus any interim distributions)
   - The three components must sum to exit equity − entry equity via live formulas, with a tie-out check row. Express each as % of total value created.
4. State the returns verdict: does the base case clear a 20% gross IRR / 2.0x MOIC sponsor hurdle (or the user's hurdle), and which attribution component carries the deal.

## Phase 7: Sensitivities

On a **Sensitivities** sheet, formula-driven (no Excel data tables):

1. **Entry × exit multiple grid** for IRR and for MOIC: odd dimensions (5×5), axes symmetric around base case, mixed references so every cell varies; the center cell must equal the model's live base-case output (this is the wiring proof) and is highlighted.
2. **Leverage sensitivity**: IRR/MOIC at closing leverage of base −1.0x, −0.5x, base, +0.5x, +1.0x, holding entry price constant (equity plug absorbs the difference). Flag rows where the covenant check in Phase 5 would breach.
3. **Margin cases**: base / downside / upside operating cases (base = the street case; upside default: the management case where one was built, otherwise +200 bps and full margin plan; downside default: revenue growth −300 bps per year and no margin expansion) with IRR, MOIC, minimum covenant cushion, and peak revolver draw per case.

## Phase 8: Workbook Construction and Formatting

Sheet order (omit only sheets that are genuinely inapplicable): **Dashboard** (deal snapshot: entry price and multiple, S&U summary, leverage, base IRR/MOIC, attribution split, tightest covenant — all cross-sheet formula links, no frozen panes), **Transaction Assumptions**, **Sources & Uses**, **Operating Model**, **Debt Schedule**, **Credit & Covenants**, **Returns Analysis**, **Sensitivities**, **Methodology** (data sources with dates accessed, the provider-of-record map per domain, any selected-but-not-connected provider notes, TSM inputs, triangulation basis and confidence flags for private targets, interest convention statement, defaults applied, limitations).

House formatting: Calibri; dark teal `#1B474D` section headers with white bold text; blue font for hardcoded inputs and editable assumptions, black for same-sheet formulas, green for cross-sheet references; yellow fill reserved for the key editable assumptions only; currency `#,##0` with unit-bearing labels (e.g., `Revenue ($M)`); percentages `0.0%`; multiples `0.0x`; MOIC `0.00x`; negatives in parentheses; zeros may display as `-`; right-aligned numerics; freeze panes on statement tables; hide gridlines on report-facing sheets; column A as a narrow margin on report sheets; a source-notes column on every sheet carrying data. Every hardcoded assumption needs source or basis, date, and URL/provider reference where available.

## Phase 9: Validation

Do not deliver until all checks pass or limitations are explicitly disclosed:

1. Sources = Uses exactly; sponsor equity plug is the balancing item.
2. Every debt roll-forward ties (beginning + draws + PIK − amortization − sweep = ending); no tranche balance negative in any period; revolver never exceeds commitment; sweep respects priority order.
3. Fully diluted shares reconcile to the TSM inputs (public deals); offer premium recomputes from the quoted price cell.
4. Interest ties to the documented average-balance convention; no circular references anywhere in the workbook.
5. Attribution bridge sums exactly to equity value creation; sensitivity center cells equal live base-case outputs; every sensitivity cell differs and moves in the expected direction.
6. Covenant conditional formatting fires correctly on a test perturbation, then restore base inputs.
7. Recalculate the workbook with the standard recalc script; zero formula errors (#REF!, #DIV/0!, #VALUE!, #NAME?).
8. Formula audit: no projected cell contains a pasted constant; color coding consistent; spot-check 3–5 historical values against the selected data source.

## Phase 10: Delivery

1. Deliver the workbook (after the Excel integrity check below) plus a **short summary memo of the returns story** in the response: entry (price, premium or multiple, leverage, sponsor check), the debt paydown path and tightest covenant year, base-case IRR/MOIC with the attribution split (EBITDA growth vs multiple expansion vs deleveraging), what the deal needs to believe (the two or three assumptions the returns are most sensitive to, quantified from Phase 7), and what would change the view (e.g., "below 4.5x entry leverage the deal no longer clears 20% IRR without multiple expansion").
2. Disclose every default applied, every triangulated input with its confidence flag, and any data limitations. Do not claim precision the sourcing does not support.

## Output Formats

Honor the selected `output_format`; all formats present the same underlying model outputs. Default is XLSX (this is a model-building skill).

- **XLSX** (primary): the full workbook per Phase 8, plus the returns-story memo in the response text.
- **PDF**: a portrait memo — transaction summary, sources & uses table, operating case summary, debt paydown and covenant table, returns and attribution, sensitivity grids, methodology — with the workbook still attached as the underlying model.
- **PDF (Presentation)**: per the presentation block below — cover; deal snapshot; sources & uses; operating case; debt paydown & covenants; returns & attribution; sensitivities; risks & what-to-believe; appendix/methodology — with the workbook attached.
- **Dashboard**: panels for deal snapshot, S&U, paydown path, covenant headroom, returns by exit year, attribution, and sensitivity grids, all traceable to sources; workbook attached.

## Output format: PDF (Presentation)

When the user selects output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF. Do NOT produce the standard portrait memo; this format replaces it.

### Page setup
- Orientation: landscape
- Page size: US Letter landscape (11" x 8.5") or widescreen 16:9 (13.333" x 7.5") — default to 16:9 for a modern deck feel
- Margins: 0.5"–0.75" on all sides
- One logical slide per page

### Slide anatomy
- Title bar at top: concise, insight-led headline (e.g., "Deleveraging drives 60% of value creation" not "Returns Overview"). 24–32 pt, bold.
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
are not: `finance/finance-markets`, `investment-research`, `office/xlsx`, `office/pdf`, `office/pptx`, `website-building/webapp`.
