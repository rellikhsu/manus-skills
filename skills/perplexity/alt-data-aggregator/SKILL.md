---
name: "perplexity:alt-data-aggregator"
description: "Enter a ticker and get a consolidated alternative-data read from Carbon Arc for the company, its industry, and its closest comps. Pulls every relevant Carbon Arc signal available for the names (transactions, demand, digital engagement, hiring and more), benchmarks the target's trajectory against industry and comp-set trends, reconciles alt-data signals against reported KPIs and consensus expectations, and flags divergences that may signal inflections before they appear in reported results. Exhibit-led output with dated, source-attributed series."
metadata:
  owners: [daniel-wang-pplx]
  team: capabilities
  source_workflow: alt-data-aggregator
  perplexity:
    display_name: Alt data aggregator
---
# Alt Data Aggregator

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `ticker` (Company ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `comps_override` (Comparable companies (optional)) — Leave blank to derive 4-6 comps automatically with rationale for each. No default — omit silently if the user does not provide it.
- `scope` (Scope) — Which benchmarking layers to include. All three by default. Options: `company` (Company); `industry` (Industry); `comps` (Comps). Default: `company`, `industry`, `comps`.
- `data_source` (Data sources) — Select every data provider this run should draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `carbon_arc` (Carbon Arc (alt data)); `perplexity_finance` (Perplexity Finance (built-in)); `daloopa` (Daloopa); `factset` (FactSet). Default: `carbon_arc`, `perplexity_finance`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Daloopa, FactSet) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.
- `lookback_window` (Lookback window) Options: `6_months` (6 months); `12_months` (12 months); `24_months` (24 months); `36_months` (36 months). Default: `24_months`.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Alt Data Aggregator

Build a consolidated alternative-data read for one company, its industry, and its closest comps. Core question: are observable transaction, demand, digital-engagement, and hiring signals tracking above, below, or in line with reported KPIs and consensus — and where do divergences suggest an inflection before it appears in reported results? Output is exhibit-led: dated, source-attributed series, not prose summaries of them.

## Data Sources (selection, BYOL)

`data_source` is a set of one or more sources collected at intake. Options: Carbon Arc (alt data), Perplexity Finance (built-in), Daloopa, FactSet; defaults: Carbon Arc + Perplexity Finance. Premium providers are bring-your-own-license: check each selected provider's connection at run start.

1. **Carbon Arc is the core engine of this skill.** If connected, it is provider-of-record for all alt-data signals. If selected but NOT connected, say so prominently — first line of the executive summary and again in the sourcing note — and state exactly what connecting unlocks for this run: observed transaction/spend, demand, digital-engagement, app/web-usage, hiring, and other coverage-dependent series for the target, industry, and comps, benchmarked and reconciled against reported KPIs and consensus. Then still deliver the best built-in baseline (Phases 1 and 3: reported KPIs, consensus and revisions, peer trends). Never stall, fail the run, or fabricate alt-data series.
2. Other selected-but-unconnected providers: continue with one sourcing-note line naming what connecting would add (Daloopa: filing-linked KPI history; FactSet: deeper consensus and revision detail).
3. Provider-of-record per domain, stated per exhibit: alt data → Carbon Arc; fundamentals/KPI history → Daloopa > FactSet > built-in; consensus → FactSet > built-in.
4. One series = one provider basis; no splices without a footnote. Cross-validate load-bearing figures across overlapping providers; show material disagreements with the basis difference — never silently average.
5. A signal observes a panel, not the KPI: always distinguish Carbon Arc signals from consensus, guidance, and reported actuals. Link signals wherever Carbon Arc returns a URL or dataset reference; if none, show provider, entity, signal, period, as-of, and dataset ID — never fabricate links. Frame signals as directional unless historical fit supports a point estimate.

## Phase 0: Setup, Comp Set, and Coverage Discovery

1. Resolve the ticker first; pull profile, segments, fiscal calendar. Derive as-of parameters from the run date; apply the selected lookback (default 24 months) to every series. Honor `scope` (company / industry / comps; all by default) — skipped scopes are omitted, not silently emptied.
2. Comps: use a user override verbatim. Otherwise derive from (a) the built-in peer tool, (b) competitors named in the latest 10-K/20-F, (c) a same-industry screen on revenue scale and growth/margin profile; reconcile to 4–6 comps with one-line rationale each. Industry = the target's primary-revenue industry; note where segments span industries.
3. **Coverage discovery — never assume datasets.** Query Carbon Arc at runtime to enumerate what it actually exposes for the target, each comp, and the industry — every signal family it returns (transactions, demand, engagement, hiring, pricing, foot traffic, etc.) — recording entity mapping, frequency, history depth, reporting lag, and latest data date. Build a coverage matrix: rows = entities, columns = signal families, cells = dataset ID + history + as-of, or "no coverage".
4. Graceful non-coverage: if the target lacks a signal family, say so and use industry- or comp-level series only as clearly labeled proxies — never as company observations. If Carbon Arc has no coverage for the name at all, state this prominently and run the built-in baseline mode.

## Phase 1: Reported Baseline and Expectations

Save raw pulls as CSVs to a working directory before analysis. For target and each comp: (1) last 8–12 quarters of revenue, segment revenue, and company-specific KPIs (e.g., units, ARPU, MAU/DAU, GMV, subscribers) via the segment/KPI tool, not the statements tool; (2) consensus revenue/EPS/KPI estimates for the next two quarters and current fiscal year, plus revision direction and magnitude; (3) latest guidance from the most recent transcript and press release, verbatim where load-bearing; (4) relevant industry aggregates via the macro tools; (5) price performance and post-earnings reactions over the lookback, to calibrate what is priced in.

## Phase 2: Signal Assembly and Standardization

Per covered entity × signal family in scope: pull the full lookback at native frequency; compute calendar-aligned YoY %, QoQ where meaningful, and an index (=100 at lookback start). Stamp every series with provider, dataset ID, entity mapping, frequency, last data date, and panel/methodology caveats; flag any panel or methodology change inside the window — a panel break is not a demand inflection. Map each series onto the target's fiscal calendar so quarter-to-date aggregation is exact.

## Phase 3: Benchmarking — Company vs Industry vs Comps

1. Trajectory: per signal family, target YoY trend vs industry aggregate vs comp median/range, plus the growth spread (target minus comp median) and its trend.
2. Share shift: where transaction/demand data permits, target share of the comp-set total over time.
3. Momentum: trailing 3-month vs 12-month trend per series; flag trend breaks and second-derivative shifts; separate company-specific inflections (target moves, comps do not) from industry-wide moves.
4. Classify each signal as historically leading, coincident, or lagging its KPI — leading signals carry the thesis weight.

## Phase 4: Reconciliation — Alt-Data Signal vs Reported KPI vs Consensus

The core discipline, per reported KPI with a plausible signal proxy:

1. **Signal-to-KPI map**: pair signal to KPI; state honestly what fraction of the KPI base (geography, channel, customer mix) the signal observes.
2. **Historical fit**: over overlapping reported quarters, correlation of signal growth vs KPI growth, direction hit rate, average tracking error — exact figures with sample size; no overclaiming below 6 overlapping quarters.
3. **In-flight read**: quarter-to-date signal growth vs the same fiscal period a year ago vs consensus KPI growth. Present a range unless historical fit supports a point estimate — no false precision.
4. **Divergence flags**: CONFIRMS / DIVERGES POSITIVE / DIVERGES NEGATIVE / INCONCLUSIVE, with confidence High/Medium/Low scored on historical fit, coverage of the KPI base, history depth, corroboration across independent signal families, and known distortions.
5. **False-positive controls**: before flagging, test price-vs-volume mix, calendar effects (holiday shift, extra week, promo comps), panel drift, channel-mix shift into unobserved channels, and M&A effects. Call out signals that look important narratively but show weak or unstable fit.
6. Where signal families disagree, explain the likely basis difference and which evidence carries more weight for that KPI — never average the disagreement away.

## Phase 5: Exhibits

Every exhibit carries dated series, as-of stamps, and per-series provider attribution. Fixed list so runs are structurally identical:

1. **Signal Coverage Matrix** — coverage per entity, with history depth and latest data date.
2. **Target Trajectory Panel** — one dated chart per covered signal family.
3. **Benchmark Panel** — target vs industry vs comp median per family, plus growth-spread series.
4. **Signal-to-KPI Reconciliation Table** — historical-fit statistics per pair.
5. **Current-Quarter Divergence Table** — QTD signal read vs consensus vs guidance, with flag and confidence.
6. **Inflection Watchlist** — divergences to monitor, each with threshold and next data-update date.

Chart titles state the insight (e.g., "Card spend decelerated below comp median in May"), not the data.

## Output Format

All formats present the same dataset. `pdf` (default): portrait memo — executive summary (with the Carbon Arc connection callout when applicable), Exhibits 1–6 with interpretation, methodology and sources. `pdf_presentation`: landscape deck per the block below. `xlsx`: sheets — Summary, Coverage Matrix, Signal Series, Benchmarks, Reconciliation, Divergence Flags, Sources & Traceability. `dashboard`: panels mirroring Exhibits 1–6 with entity selector, series toggles, and per-datapoint source links.

## Conclusion

Answer directly: is the target tracking above, below, or in line with consensus and its comp set on observable data; the two or three highest-confidence divergences and their implication for upcoming prints; what appears priced in; what would change the read (specific falsifiers); and a monitoring plan — which series, at what cadence, with what thresholds.

## Provider Traceability Requirement (Daloopa / FactSet)

When the selected `data_source` values include `daloopa` or `factset`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:
1. Make raw figures clickable wherever the provider returns a URL, deep link, report link, document reference, filing link, cell-level reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source/source-note cells where feasible, and include a `Sources & Traceability` or `Source Map` sheet with provider, company/security/entity, metric, period, as-of timestamp, provider metric/series/document ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, KPI tile, chart datapoint, tooltip, or detail drawer that displays a raw provider figure must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Daloopa document, filing, and company-series links/references; FactSet entity, metric, document, and any returned URL/deep link.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity/security identifier, metric or series ID/name, period, as-of timestamp, and document/report identifier where available, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures. Derived calculations should link or reference the source cells/figures used in the calculation.

---

## Output format: PDF (Presentation)

When output_format = "pdf_presentation", produce a client-ready slide deck delivered as a landscape PDF; this replaces the portrait memo. Page setup: widescreen 16:9 (13.333" x 7.5") preferred, 0.5"–0.75" margins, one logical slide per page. Slide anatomy: insight-led headline in the title bar, 24–32 pt bold (e.g., "Card spend decelerated below comp median in May", not "Spend Overview"); one clear idea per slide; prefer tables, charts, and labeled visuals over prose; ≤ 5 bullets per slide, ≤ 12 words each; generous whitespace. Typography: sans-serif throughout (Calibri or Arial), body 14–18 pt, captions 10–12 pt; single accent color plus neutrals, no decorative graphics; numeric values right-aligned with tabular figures and consistent units; charts direct-labeled, minimal gridlines, ≤ 5 series. Slide order: cover; executive summary (with the Carbon Arc connection callout when applicable); signal coverage matrix; core exhibit slides — trajectory, benchmarks, reconciliation, divergence flags — one idea per slide; inflection watchlist / monitoring plan; appendix with methodology, source list, and disclosures. Quality bar: every slide title answers "so what?"; fact-check every number against the selected data sources; verify no text overflow, mid-word wrapping, or low-contrast colors; treat the deck as client-ready for external distribution.

---

## PDF Formatting and Private Artifact Standards

Apply whenever the output includes `pdf` or `pdf_presentation`:

1. Alignment: left-align section titles and body text to the same content edge (center titles only on a cover page); captions, source notes, and exhibit titles share the same left grid.
2. Layout grid: one consistent margin and content grid across the entire PDF; every title, paragraph, table, and chart snaps to it.
3. Table sizing: primary tables share one overall width — full text width in portrait, same exhibit width and left edge per slide in presentations; with fewer columns, keep total width and adjust column proportions rather than shrinking the table.
4. Chart sizing: consistent width, height, left edge, and caption/source placement across comparable pages unless a deliberate full-page exhibit is required.
5. Numeric formatting: right-align numbers in tables; keep units, decimals, currency, percentages, and date formats consistent throughout.
6. Private internal artifacts: never show internal workspace artifacts in any user-facing output — workspace or sandbox paths, temporary or cache filenames, raw provider/API response files, logs, intermediate CSV/JSON/parquet/XLSX exports, extraction screenshots, notebook/script names, or any `file://`, `/home/user/workspace`, `/tmp`, or sandbox-only references. Omit them or replace with user-safe source labels.
7. Allowed references: user-provided filenames and public or provider-native source URLs may be cited; do not confuse legitimate source citations with private internal artifacts.
8. Final visual/privacy QA before delivery: aligned titles and body, consistent table widths and chart dimensions, aligned captions and source notes, no text overflow or mid-word wrapping, no cramped or misaligned exhibits, no internal artifact exposure.

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
