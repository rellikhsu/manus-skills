---
name: pre-earnings-brief
description: "Prepare for earnings with consensus estimates, key metrics, historical surprises, and reaction scenarios."
metadata:
  perplexity:
    display_name: "Pre-earnings brief"
---
# Pre-earnings Brief

Generate a comprehensive pre-earnings analysis report for the specified company or companies.

## Phase 1: Company Identification

1. Parse the input to identify ticker symbols or company names.
2. Determine the upcoming earnings date for each company.
3. Use the selected `data_source` as the authoritative source for financial figures and estimates whenever available, including Perplexity Finance, FactSet, Daloopa, Morningstar, PitchBook, or Carbon Arc; if a selected source is unavailable or incomplete, state the limitation and supplement with cited public sources.

## Phase 2: Research (per company)

For each company, research and compile:

### Consensus Estimates
- Revenue, EPS, and key segment estimates from Wall Street consensus
- Range of estimates (high/low/mean)
- Recent estimate revisions and direction of revisions

### Key Metrics to Watch
- Identify 5-8 critical KPIs specific to the company (e.g., subscriber count, ARPU, cloud growth rate)
- Prior quarter actuals and consensus expectations
- Management guidance from prior quarter
- When `data_source` is `carbon_arc`, use Carbon Arc naturally as an early-signal layer for company KPIs ahead of earnings, prioritizing observable KPI trend indicators, directional inflections, and signal-vs-consensus context rather than forcing it into every metric.

### Historical Beat/Miss Patterns
- Last 4-8 quarters of EPS and revenue beats/misses
- Average magnitude of surprise
- Stock price reaction on earnings day (historical pattern)

### Market Impact Scenarios
- Bull case: What would drive a positive reaction
- Base case: What consensus likely implies and what would count as in-line
- Bear case: What would drive a negative reaction
- Key risks and catalysts

## Phase 3: Report Delivery

1. Compile into a structured report with per-company sections.
2. Include a summary table of key estimates across all companies.
3. All data must include source citations with URLs.
4. Respect the selected `output_format`:
   - `pdf`: produce a polished portrait PDF memo.
   - `pdf_presentation`: produce a client-ready landscape PDF slide deck using the section below.
   - `xlsx`: produce an Excel workbook with summary tables, assumptions, KPI history, estimate revisions, scenarios, and a source log.
   - `dashboard`: produce an interactive dashboard with company selector, estimate tables, historical beat/miss views, KPI cards, scenario panels, and source links.

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

## Carbon Arc Early-Signal Guidance

When `data_source` is `carbon_arc`, use Carbon Arc as an early-signal source for company KPIs ahead of earnings. Treat Carbon Arc data as a way to assess whether observable KPI trends are tracking above, below, or in line with consensus and management commentary. Use it naturally where it has coverage and explanatory power, especially for demand indicators, usage trends, traffic, transactions, customer activity, channel checks, or other KPI proxies relevant to the company.

Requirements:
1. Distinguish Carbon Arc early signals from Wall Street consensus estimates, company guidance, and reported actuals.
2. Where Carbon Arc returns a URL, report link, dataset link, metric reference, or source artifact, hyperlink or label the signal in the same manner as other provider-sourced figures.
3. If Carbon Arc does not return a clickable provider URL for a signal, do not fabricate one. Show Carbon Arc as the provider and include the company/entity, KPI or signal name, period, as-of timestamp, and dataset or metric identifier where available.
4. Avoid overstating precision. Frame Carbon Arc outputs as directional early signals unless the returned dataset explicitly supports a point estimate.

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
- Fact-check every number against the selected data_source.
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

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`.
