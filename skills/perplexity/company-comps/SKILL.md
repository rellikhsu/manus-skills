---
name: "perplexity:company-comps"
description: "Build a trading comps table with EV/Revenue, EV/EBITDA, P/E, growth rates, and margins for a company and its peer group."
metadata:
  perplexity:
    display_name: Company comps
    display_desciption: Spread trading comps for a company and its peer group
    connectors:
      - id: factset_mcp
        reason: Optional datasource for financial metrics
      - id: daloopa
        reason: Optional datasource for financial metrics

---
# Company Comps

Build a professional trading comps table for the specified companies, sourced exclusively from the user-selected data provider.

## Phase 0: Data Source Routing (MANDATORY FIRST STEP)

The user selects exactly ONE data source via `{{data_source}}`. All financial data in the output must come from that source — do not mix providers. If a figure is unavailable from the selected source, leave the cell blank and annotate "n/a — not available in {source}". Do NOT silently substitute from another provider.

Provider routing:

| Source | Primary tool | Availability |
|---|---|---|
| `perplexity_finance` | Finance tools / public markets data available in Computer; load `finance/finance-markets` for public company data lookups | Available where public-market coverage exists |
| `factset` | `factset_mcp` MCP connector — `FactSet_Metrics` → `FactSet_Fundamentals` / `FactSet_EstimatesConsensus` / `FactSet_GlobalPrices` / `FactSet_EntityReference` | Connected |
| `daloopa` | `daloopa` MCP connector — `discover_companies` → `discover_company_series` → `get_company_fundamentals` | Connected (historicals/filings-based; limited forward consensus — use for reported financials) |
| `morningstar` | `morningstar` MCP connector — `morningstar-id-lookup-tool` → `morningstar-data-tool` / `morningstar-analyst-research-tool` | Use if connected; otherwise pause and ask the user to connect/provide export or confirm fallback |
| `pitchbook` | PitchBook connector or user-provided PitchBook export | Use if connected; otherwise pause and ask the user to connect/provide export or confirm fallback |
| `sp_global` | S&P Capital IQ / Market Intelligence | No MCP connector — pause and ask the user to provide a Capital IQ export, or confirm fallback to web search against spglobal.com / capitaliq.com domains |
| `lseg` | LSEG Workspace / Refinitiv Eikon | No MCP connector — pause and ask the user to provide an LSEG export, or confirm fallback to web search against lseg.com / refinitiv.com domains |

For `sp_global` and `lseg`: before proceeding, surface the connector gap to the user and confirm the fallback path. Do not silently substitute another provider.

## Phase 1: Peer Group

1. Parse the input companies. If only one company is provided, auto-select 5–8 comparable peers based on sector, business model, size, and growth profile.
2. When using FactSet, use `FactSet_EntityReference` for peer identification. When using Morningstar, use `morningstar-screener-tool`. When using Daloopa, use `discover_companies` to validate coverage.
3. Finalize the peer group selection and confirm every ticker has coverage in the selected source before proceeding.

## Phase 2: Data Collection (Single-Source Discipline)

1. For each company, gather from the SELECTED source only: market cap, enterprise value, revenue (LTM and NTM where supported), EBITDA, net income, FCF, share price, shares outstanding, consensus estimates.
2. For FactSet: call `FactSet_Metrics` first to resolve metric codes, then `FactSet_Fundamentals` for reported and `FactSet_EstimatesConsensus` for forward.
3. For Daloopa: forward consensus is limited — flag NTM fields as "n/a — Daloopa (filings-based)" unless reported in guidance. Pull historicals via `get_company_fundamentals`.
4. For Morningstar: use `morningstar-data-tool` with resolved datapoint IDs; supplement with `morningstar-analyst-research-tool` for forward views.
5. For PitchBook: use connected PitchBook tools or the user-provided PitchBook export only. If no connector/export is available, ask the user before any fallback.
6. Calculate all selected metrics: EV/Revenue, EV/EBITDA, P/E, revenue growth (YoY), gross margin, EBITDA margin, net margin, FCF yield, Rule of 40.
7. Capture as-of timestamps and any click-through URLs returned by the provider (e.g., Morningstar report URLs, Daloopa document/filing links, FactSet entity/document IDs, PitchBook profile/export references).

## Phase 3: Table Construction

1. Build the comps table with companies as rows and metrics as columns.
2. Include mean, median, high, and low summary statistics.
3. Highlight the primary company if doing a peer comparison.
4. Format numbers appropriately (multiples to 1 decimal, percentages to 1 decimal, currency in millions/billions). Never use "~" before figures — use exact values.

## Phase 4: Source Attribution (REQUIRED)

Every data cell must carry attribution. Apply these rules:

1. **Header block** of the output must state: "Data source: {Provider Name}. All figures sourced from {Provider} as of {timestamp}."
2. **Per-row attribution column** (Excel: dedicated "Source" column; markdown: footnoted references) containing:
   - **Underlying filing citation** where the provider exposes it (e.g., "10-Q FY25 Q2, filed 2025-08-05" from Daloopa `search_documents` or FactSet document metadata).
   - **Click-through URL** to the provider's source document or data page where available:
     - Daloopa: document URLs returned by `search_documents` / `get_company_fundamentals`
     - Morningstar: analyst report URLs from `morningstar-analyst-research-tool`
     - FactSet: entity/document identifiers and any URLs returned by the API
     - PitchBook: profile, company, document, or export references returned by the connector/export
     - S&P Global / LSEG: deep-link URLs if provided in the user's export
3. **Estimate vs. reported flag**: mark every cell as "Reported" or "Consensus ({provider})" so the banker can distinguish.
4. **As-of date** per metric column (e.g., "Prices as of {date}", "Consensus as of {date}").
5. If a provider does not expose a click-through URL for a given datapoint, cite the underlying filing (form type, period, filing date) instead. Never fabricate URLs.

## Phase 5: Delivery

1. Deliver in the requested format (Excel, markdown, or both). For Excel, place attribution in an adjacent column and include a "Sources & Methodology" tab listing every provider call made, timestamp, and click-through URLs.
2. Include a brief narrative (≤150 words) on where the primary company trades relative to peers and any notable outliers. Analyst-grade density; no filler.
3. Include a "Data Gaps" section enumerating any cells left blank and the reason (coverage gap in selected source, metric not available, etc.).
4. Do NOT include buy/sell recommendations.

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
are not: `finance/finance-markets`, `office/xlsx`, `office/pdf`, `office/pptx`, `data/visualization`, `website-building/webapp`.
