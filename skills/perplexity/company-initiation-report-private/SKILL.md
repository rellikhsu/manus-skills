---
name: "perplexity:company-initiation-report-private"
description: "Create an investor-ready private-company initiation deck covering funding, ownership, unit economics, revenue quality, runway, governance, scenarios, valuation, diligence gaps, and decision-relevant risks."
metadata:
  owners: [daniel-wang-pplx]
  team: capabilities
  source_workflow: company-initiation-report-private
  perplexity:
    display_name: Private company initiation report
---
# Company Initiation Report (Private)

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `company_name` (Company name)
- `scope` (Research scope) Options: `all` (All core sections); `business_model` (Business model & market); `funding_cap_table` (Funding, ownership & preference stack); `financials` (Revenue quality, unit economics, burn & runway); `governance` (Governance & board); `valuation` (Valuation triangulation); `scenarios` (Scenarios); `risks_gaps` (Risks & diligence gaps).

OPTIONAL — assume the default (or omit) unless the user specifies:
- `website` (Company website) No default — omit silently if the user does not provide it.
- `stage` (Stage) Options: `auto` (Auto-detect); `seed_series_a` (Seed / Series A); `series_b_growth` (Series B–C / Growth); `late_stage` (Late stage / Pre-IPO). Default: `auto`.
- `evaluation_context` (Evaluation context) — Shapes emphasis (e.g., secondary purchases weight the preference stack and secondary marks more heavily). Options: `general` (General coverage initiation); `primary_round` (Evaluating a primary round); `secondary_purchase` (Evaluating a secondary purchase); `pre_ipo` (Pre-IPO / crossover coverage). Default: `general`.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `pitchbook` (PitchBook); `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `pitchbook`, `perplexity_finance`, `factset`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: if the default sources leave a data domain with no usable coverage (connector absent or no data for the entity), silently attempt the remaining supported sources for this skill (Daloopa, Morningstar) under the same connected-only rule before settling for built-in Perplexity Finance alone, and record the escalation in the sourcing note.
- `output_format` (Output format) Options: `pdf_presentation` (PDF (Presentation)); `pdf` (PDF); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf_presentation`.
- `peers` (Comparable companies) No default — omit silently if the user does not provide it.
- `key_debates` (Key debates to address) No default — omit silently if the user does not provide it.
- `context_file` (Upload materials) Ask the user to attach the file(s) in chat. No default — omit silently if the user does not provide it.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Company Initiation Report (Private)

Produce a foundational initiation report on a private company for an institutional investor. The core question: what is this business actually worth across plausible outcomes, how confident can we be in each input, and what evidence would change that view? Private companies are disclosure-limited, so this workflow is built around triangulation and confidence tiering — every material figure must be sourced, cross-checked, and labeled by reliability. Do not frame the work as any single investor's style, and do not issue a buy/sell/invest recommendation; deliver evidence, valuation triangulation, scenarios, and diligence gaps so the reader can form their own view.

## Evidence and confidence tiering (applies to every phase)

Tag every material figure in the report with one of three confidence tiers, shown next to the figure or in a tier column in tables:
- **Disclosed** — stated by the company or a primary/official source: press release, company blog, statutory filing (Form D, Companies House accounts, EU registry filings), audited financials in uploaded materials, or verbatim executive statement with named speaker and date.
- **Reported** — attributed to credible journalism or a named data provider (e.g., Bloomberg, WSJ, FT, Reuters, The Information, PitchBook, Forge) but not confirmed by the company. Name the outlet and publication date.
- **Estimated** — derived by you (or a third party) from indirect signals. Show the estimation method and inputs inline (e.g., "headcount × loaded cost benchmark," "comps multiple × reported ARR").

Triangulation rules:
1. Any load-bearing figure (revenue/ARR, valuation, capital raised, burn, headcount) requires at least two independent sources, or an explicit `single source` flag.
2. When sources conflict, show both figures with dates, state which you weight higher and why (recency, source track record, proximity to primary disclosure), and carry the preferred figure forward.
3. Never present an estimate with false precision. Use ranges for estimated figures and show the exact reported figure (never "~") for disclosed/reported ones.
4. If a section cannot be supported by evidence, state the limitation plainly. Never fabricate figures, round terms, investors, or links.
5. Record a corroboration count for every load-bearing private-market claim (e.g., `corroborated ×3`) and carry it into the source map. Syndicated or company-seeded coverage of the same announcement counts as one source, not several — trace reported figures back to the originating outlet before counting.

## Phase 0: Setup and entity resolution

1. Resolve the company unambiguously: legal/trading name, website, HQ, sector, founding year. Private-company name collisions are common — confirm identity via the website and at least one funding record before pulling any data. If the user supplied a website, treat it as the anchor.
2. Confirm the company is private. If it has completed an IPO, direct listing, or SPAC merger, tell the user and offer the public-company initiation workflow instead.
3. Derive all as-of parameters from the run date. Save raw tabular pulls (funding rounds, secondary prices, comps data) to a working directory before analysis.
4. Read any uploaded materials (decks, data-room excerpts, prior notes) first; treat user-provided figures as Disclosed-tier unless internally inconsistent, and reconcile external findings against them.

## Phase 1: Data collection — layered private-data sweep

Work through the layers in order; each layer fills gaps and cross-checks the previous one.

1. **Private-market data tools first.** Pull the company's record from the private-company finance tool (Forge data): secondary market price history, implied secondary valuation, funding round history, total capital raised, and any recorded marks. Record as-of dates for every price or mark.
2. **Selected data sources (one or more, collected at intake).** `data_source` is a set of one or more sources collected at intake — options: PitchBook, Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, Carbon Arc, and Guidepoint; defaults: PitchBook, Perplexity Finance, FactSet, Carbon Arc, and Guidepoint. Every premium provider is bring-your-own-license: for each selected source, check whether its connector is connected. If a source is selected but not connected, continue without it and add one line to the report's sourcing note — “<Provider> was selected but is not connected; connecting it would add <the specific value for this report — e.g., PitchBook: verified round terms, deal-level valuations, investor and board data; Guidepoint: former-employee and customer interviews on the target; Carbon Arc: demand/transaction signals to test growth claims>.” Never stall or fail the run over an unavailable premium source; the built-in Perplexity Finance tools are the always-available baseline.
   Assign a provider-of-record per data domain and state it under each exhibit: **PitchBook is provider-of-record for funding rounds, valuations, cap-table/ownership data, and investors** whenever selected and connected — reconcile layer 1 (Forge) against it and note discrepancies; for the public comps, fundamentals/KPI history follow Daloopa > FactSet > Morningstar > built-in, and consensus estimates FactSet > built-in; Carbon Arc is provider-of-record for alt-data demand signals and Guidepoint for expert qualitative evidence. These universes are complementary, not redundant: PitchBook covers the private target and private peers while FactSet/Daloopa/Morningstar cover the listed comps, so a complete report draws on both sides. Cross-validate every load-bearing figure wherever provider coverage overlaps; where providers disagree materially, show both values and explain the basis difference (definition, as-of date, methodology) — never silently average. One table column or time series = one provider basis; never splice providers within a series without an explicit footnote at the splice point.
3. **Primary disclosures.** Company website, press releases, product pages, pricing pages, engineering/company blog, and statutory filings where the geography provides them (Form D in the US; full statutory accounts from UK Companies House and many EU/APAC registries — pull these whenever the company has entities there, as they are often the only audited financials available).
4. **Credible reporting.** Funding, revenue, and valuation reporting from major outlets and specialist press. Cite outlet and date for each figure.
5. **Institutional marks.** Where mutual funds or crossover investors hold the company, check reported fund marks (fund reports/N-PORT-derived data) as an independent valuation signal.
6. **Expert evidence (Guidepoint, when selected and connected).** Pull recent expert interviews on the company AND its category: former employees (organizational health, how revenue is really recognized, churn and pipeline reality), customers (win/loss reasons, pricing paid, renewal intent), and competitors' operators (where the target wins and loses deals). Run reverse-references — interviews about other companies in the category that mention the target. For a private company this is often the only inside-view evidence available: quote with expert role and call date, tier it Reported, weight calls under ~12 months old above older ones, and flag any single-expert claim that lacks corroboration.
7. **Alt-data signals (Carbon Arc, when selected and connected).** Where Carbon Arc has coverage of the private company, pull demand/transaction signals (transaction volume, spend-panel, web/app demand series) and always benchmark the company series against its category trend so company-specific momentum is separated from market beta. Reconcile against reported or estimated revenue growth — an alt-data series that contradicts claimed ARR growth is a finding, not noise; show both. Where direct company coverage is absent, use category-level series as an independent check on the Phase 2 market-growth and TAM claims.
8. **Public-comp cross-document reads.** Read the closest listed competitors' 10-Ks and earnings transcripts for mentions of the private target or its category: named-competitor references, pricing and win/loss commentary, market-growth statements, and segment results in the overlapping category. These are Disclosed-tier evidence about the market and Reported-tier evidence about the target, and often the most reliable outside-in read on competitive dynamics.
9. **Operating signals.** Job postings (hiring velocity, functions, locations), headcount trend (LinkedIn-derived where available), product launches and release cadence, app-store/traffic data where relevant, customer reviews (G2, Capterra), and notable customer or partnership announcements. These feed burn, growth, and traction estimates — label everything derived from them Estimated.
10. Build a source log as you go: figure, value, tier, source, URL, as-of date, and corroboration count. This becomes the appendix source map.

## Phase 2: Business model, market, and competitive position

1. Describe what the company sells, to whom, and how it monetizes: product lines, pricing model, revenue model (subscription/ARR, usage, transaction take-rate, hardware, services mix), and go-to-market motion.
2. Market: TAM/SAM with stated methodology (bottom-up preferred), growth rate, and the structural change creating the opportunity. Distinguish hard data from directional estimates.
3. Competitive position: top 3–7 competitors (public and private), the company's wedge and differentiation, switching costs, network or data effects, and incumbent response risk. Where private competitors are cited, apply the same tiering to their figures. Where public competitors overlap, cite their 10-K competition sections and transcript commentary (Phase 1, layer 8) as outside-in evidence on share shifts and pricing.

## Phase 3: Funding history, ownership, and the preference stack

1. **Round-by-round funding table** (from earliest to latest): round name, close date, amount raised, pre/post-money valuation, price per share where known, lead and notable participating investors, and confidence tier per cell. Show total capital raised and compare it to the sum of rounds; investigate gaps (debt, secondaries, unannounced rounds).
2. **Ownership / cap-table view.** A precise cap table is almost never public — build an estimated ownership map instead: founders/management, employee pool (ESOP), and major investor blocks by round, using round sizes and standard dilution math. Label the whole exhibit Estimated, state assumptions (e.g., 10–20% option pool refreshes, no secondary transfers unless reported), and show a sanity check that implied stakes sum to ~100%.
3. **Preference stack and structural seniority.** This is mandatory: headline post-money valuation can materially overstate what common or junior-preferred shares are worth. Document, or where undisclosed assume and flag:
   - Liquidation preference multiples and participation rights by series (default assumption if undisclosed: 1x non-participating, flagged Estimated).
   - Seniority order (pari passu vs stacked), cumulative preferred dividends, and any structured terms from late rounds (ratchets, IPO price guarantees, PIK features, warrants) — late-stage "flat" rounds frequently hide structure; check reporting on the most recent rounds specifically.
   - Total preference overhang in dollars, and the exit value below which common shareholders and each preference layer are impaired.
4. Note any down rounds, recapitalizations, extension/bridge rounds, tender offers, or reported secondary programs, and what they signal.

## Phase 4: Financial condition — revenue quality, unit economics, burn, and runway

1. **Revenue and growth.** Best-evidence revenue or ARR with tier labels; be precise about the metric definition (GAAP revenue vs ARR vs annualized run-rate vs bookings vs GMV — never mix them silently; if only GMV is reported, estimate net revenue via take-rate). Build a revenue trajectory from all datapoints found (each with date, tier, source).
2. **Revenue quality.** Assess: recurring vs one-time mix, contract duration and prepayment, customer concentration, logo vs net revenue retention signals, pricing power evidence, and any signs of low-quality revenue (heavy discounting, channel stuffing, related-party or circular revenue — flag vendor-financing or investor-as-customer arrangements explicitly).
3. **Unit economics.** Where evidence permits: gross margin (disclosed or benchmarked to business model), CAC/payback signals, contribution margin per unit/order/seat, and the trajectory. If nothing is disclosed, anchor benchmark ranges to the closest public comps' disclosed figures — gross margin, S&M as a % of revenue, and retention metrics from their filings and transcripts — rather than generic business-model averages; name the anchor comps and label the result Estimated.
4. **Burn and runway.** Estimate net burn via at least two methods and reconcile: (a) capital raised minus reported cash cushion vs time elapsed since the last raise; (b) headcount × fully loaded cost benchmark minus estimated gross profit. Present monthly net burn range, implied runway from the last known raise date, and the implied timing of the next financing need. Cross-check against hiring pace (accelerating hiring with short runway is a red flag; layoffs signal burn correction). Present runway as a sensitivity grid, not a point estimate — low/mid/high burn × with/without the estimated gross-profit offset — with the implied next-raise window under each cell. Where selected, corroborate with Guidepoint commentary on hiring, layoffs, or sales attainment and with the Carbon Arc demand trend: a decelerating demand series shortens the credible runway even when headline burn looks stable.
5. Path to profitability: management statements on breakeven (quote, speaker, date) vs your arithmetic.

## Phase 5: Governance, board, and control

1. Board composition (investor, founder, independent seats) and any known super-voting/dual-class founder control.
2. Investor protective provisions and rights where reported (board consent items, drag-along, pro-rata, information rights).
3. Management quality: founder/CEO track record, executive turnover in the last 24 months (departures of CFO/CRO/COO are decision-relevant), and Glassdoor-style signals as soft evidence. Where Guidepoint is selected, former-employee interviews are the strongest available evidence on the causes of executive turnover and on culture; quote role and call date.
4. Related-party issues, litigation, regulatory exposure, and any reported audit or accounting concerns.

## Phase 6: Valuation triangulation

Value the company three independent ways, then reconcile:
1. **Last-round anchor.** Most recent post-money valuation, its date, and staleness. Adjust the anchor for what has changed since: growth delivered vs implied expectations, sector multiple compression/expansion since that date, and any structure in the round that inflates headline value. Then reverse-engineer what the mark assumes: compute the implied revenue/ARR multiple at the post-money on best-evidence figures, and the growth-and-exit-multiple path a new investor at that price would need to earn a conventional venture return over 3–5 years. Set those required assumptions against current sector base rates (public-comp multiples, recent exit multiples) and state plainly whether the mark is priced for perfection, roughly in line, or conservative.
2. **Secondary and institutional marks.** Latest secondary price and implied valuation from the private-market tool, expressed as a premium/discount to the last round; mutual fund marks where available. Note liquidity and volume caveats — thin secondary prints are weak evidence.
3. **Comps-implied.** Select 4–8 public comparables via two routes and merge them: the built-in peer tools for the conventional comp set, plus a quantitative screen for listed companies with similar growth, gross-margin, and revenue-model profiles even when they sit outside the obvious category (and precedent private/M&A transactions where relevant). Pull current forward and trailing multiples with the finance tools — FactSet consensus where selected and connected, built-in estimates otherwise — and mine the comps' filings and transcripts for the unit-economics anchors (gross margin, retention, S&M efficiency) that feed the Phase 4 benchmarks. Apply the multiples to the best-evidence revenue/ARR estimate, and apply an explicit, justified private-company adjustment (illiquidity, information risk, typically a 20–35% discount unless justified otherwise). Show the full bridge: metric × multiple × adjustment = implied EV/equity value, with tier labels on each input.
4. **Reconciliation table**: the three (or more) valuation reads side by side, divergence in %, and your explanation of why they differ and which read carries the most evidentiary weight today.
5. **Preference-adjusted view.** Translate the enterprise/equity value range into what it implies for common stock and junior preferred given the Phase 3 preference stack: at each scenario exit value, show proceeds per layer. State plainly where headline valuation is misleading for anyone not holding senior preferred.

## Phase 7: Scenarios

Build three scenarios over a 3–5 year horizon — upside, base, downside — each with: the operating path (growth, margin), exit route (IPO, strategic M&A, remains private with further raises, down round/recap), exit-value math, probability weight (must sum to 100%), and implied outcomes for senior preferred vs junior preferred vs common. Include the structural downside case where the preference stack absorbs most value. State the 2–3 assumptions each scenario is most sensitive to.

## Phase 8: Debates, diligence gaps, and risks

1. **Key debates** — address each user-supplied debate head-on with the evidence gathered; where the user supplied none, identify the 2–4 questions that will determine the outcome, and state what the evidence currently supports.
2. **Diligence gap register** — the decision-critical items that could not be verified from outside: exact financials, churn/NRR, cap-table terms, customer contracts, litigation status. For each: why it matters, what artifact would resolve it (data-room document, management question, reference call), and priority (high/medium/low). This section is mandatory — a private initiation that hides its blind spots is worse than none.
3. **Decision-relevant risks** — top 5, ranked by expected impact, each with the observable signal that would confirm it is materializing and a monitoring cadence.

## Phase 9: Output creation

Default output is **PDF (Presentation)** — an investor-ready deck. Honor the selected `output_format`; all formats present the same underlying dataset, exhibits, and tier labels.

- **PDF (Presentation)** — slide order: (1) cover; (2) executive summary with the valuation triangulation range and confidence statement; (3) company & business model; (4) market & competition; (5) funding history table; (6) ownership & preference stack (including the exit-waterfall exhibit); (7) revenue quality & unit economics; (8) burn & runway; (9) governance; (10) valuation triangulation & reconciliation; (11) scenarios & preference-adjusted outcomes; (12) key debates; (13) diligence gap register; (14) risks & monitoring; (15) appendix: methodology, source map with tiers, disclosures.
- **PDF (memo)** — portrait memo in the same section order, with the funding table, valuation reconciliation, waterfall, and diligence register as full-width exhibits.
- **XLSX** — sheets: `Summary`, `Funding History`, `Cap Table (Est.)`, `Preference Stack & Waterfall`, `Revenue & Burn Build`, `Comps`, `Valuation Triangulation`, `Scenarios`, `Diligence Gaps`, `Sources & Traceability`. Derived values as live formulas; tier label column on every data sheet.
- **Dashboard** — panels mirroring the deck sections with a valuation-triangulation headline module, funding timeline, waterfall chart, and a filterable diligence-gap and source-map table.

## Conclusion

End with a direct answer to the core question: the defensible valuation range and where within it the evidence points, the confidence level and the single largest source of uncertainty, what new evidence would most change the view (next disclosed metric, next round terms, secondary print), and the 3–5 signals to monitor with cadence. No buy/sell or invest/pass recommendation.

## Provider Traceability Requirement (Daloopa / FactSet / Morningstar)

When the selected `data_source` values include any of `daloopa`, `factset`, or `morningstar`, raw data figures sourced from the selected provider must be traceable back to the originating provider/source artifact.

Requirements:
1. Make raw figures clickable wherever the provider returns a URL, deep link, report link, document reference, filing link, cell-level reference, or data-page link.
2. In PDF, DOCX, PPTX, Markdown, or memo outputs, hyperlink the figure itself or an adjacent source marker.
3. In XLSX outputs, add hyperlinks to the raw data cells or adjacent source/source-note cells where feasible, and include a `Sources & Traceability` or `Source Map` sheet with provider, company/security/entity, metric, period, as-of timestamp, provider metric/series/document ID, and URL/deep link.
4. In dashboard/web outputs, every table cell, KPI tile, chart datapoint, tooltip, or detail drawer that displays a raw provider figure must expose a click target or link to the provider/source page where available.
5. Preserve provider-native references: Daloopa document, filing, and company-series links/references; FactSet entity, metric, document, and any returned URL/deep link; Morningstar security, datapoint, report, and URL references.
6. If no clickable provider URL/deep link is returned for a datapoint, do not fabricate one. Instead show the provider name, entity/security identifier, metric or series ID/name, period, as-of timestamp, and document/report identifier where available, and explicitly mark `no provider URL returned`.
7. This traceability requirement applies only to raw/provider-sourced figures. Derived calculations should link or reference the source cells/figures used in the calculation.
8. Apply the same discipline to the other providers where used: preserve PitchBook deal and company-profile references, Carbon Arc series/dataset identifiers with as-of dates, and Guidepoint interview identifiers with expert role and call date; where no link is returned, mark `no provider URL returned` per rule 6.

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
- Fact-check every number against its provider-of-record among the selected data sources.
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

## Attached materials

Any files supplied through the kickoff form arrive as attachments on this turn and are
downloaded into the workspace. Read them before starting external research and treat them
as primary source input. If no files were attached, proceed using the available finance
and data connectors plus web research, and say so rather than asking the user to re-upload.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `research-report`, `office/pdf`, `office/pptx`, `office/xlsx`, `website-building/webapp`.
