---
name: competitive-landscape
description: "Build an investor-grade analysis of market structure and company positioning, mapping peers, strategic groups, share shifts, moats, unit economics, and implications for growth, margins, and valuation."
metadata:
  perplexity:
    display_name: "Competitive landscape"
---
# Competitive Landscape

# Form Input Reference

Inputs arrive pre-filled through this skill's input form and are injected into the opening request via the query template. Never re-ask for anything the form collected. A blank or empty placeholder value means the user omitted that optional input — skip it silently and apply the documented default behavior below.

REQUIRED — must have before starting:
- `company` (Focal company or ticker)

OPTIONAL — assume the default (or omit) unless the user specifies:
- `market_scope` (Market or segment scope) — Leave blank to analyze the arena driving the largest share of the focal company's revenue. No default — omit silently if the user does not provide it.
- `competitors` (Competitor set) No default — omit silently if the user does not provide it.
- `share_basis` (Share metric basis) — The metric used for market share and share-shift math. Options: `auto` (Auto (industry convention)); `revenue` (Revenue); `units_volume` (Units / volume); `gmv_tpv` (GMV / TPV); `subscribers_users` (Subscribers / users). Default: `auto`.
- `lookback` (Lookback window) Options: `3_years` (3 years + latest LTM); `5_years` (5 years + latest LTM); `10_years` (10 years + latest LTM). Default: `3_years`.
- `data_source` (Data sources) — Select every data provider you want this run to draw on. Providers you have not connected are skipped gracefully and noted, so connecting them enriches the output. Perplexity Finance is always available. Options: `perplexity_finance` (Perplexity Finance (built-in)); `factset` (FactSet); `daloopa` (Daloopa); `morningstar` (Morningstar); `pitchbook` (PitchBook); `carbon_arc` (Carbon Arc (alt data)); `guidepoint` (Guidepoint (expert calls)). Default: `perplexity_finance`, `factset`, `daloopa`, `morningstar`, `pitchbook`, `carbon_arc`, `guidepoint`. Each premium source is used only if its connector is connected; otherwise skip it silently and record in the sourcing note what connecting it would have added. Escalation rung: all supported sources for this skill are already default-enabled; when a data domain has no usable premium coverage, fall back to built-in Perplexity Finance and record the gap in the sourcing note.
- `output_format` (Output format) Options: `pdf` (PDF); `pdf_presentation` (PDF (Presentation)); `xlsx` (XLSX); `dashboard` (Dashboard). Default: `pdf`.
- `additional_context` (Additional context) No default — omit silently if the user does not provide it.

Everywhere the rest of this prompt refers to a selected, chosen, or provided input, it means the value supplied through the form.

---

# Competitive Landscape

Build an investor-grade analysis of the players and competitive forces in a market: who competes, in which strategic groups, who is gaining or ceding share (with sourced numbers, not vibes), whose advantages are durable, and what that means for the growth, margins, and valuation of the focal company or segment. The core question this answers: is the focal company's competitive position getting stronger or weaker, and is that trajectory priced in?

Scope discipline: this analysis is about PLAYERS and conduct, not the market itself. Keep market sizing, TAM build-ups, and demand-driver work to a brief context paragraph — if the user primarily wants the market itself, that is the sibling "Industry Overview" skill; if they want a visual directory of companies by sub-segment and funding stage, that is the sibling "Market Map" skill. Everything here must serve the competitive question.

## Phase 0: Setup and Data Source Routing

1. Parse the request: focal company (or explicit multi-company arena with no protagonist), market/segment scope, competitor set if named, share metric basis, lookback window, selected data sources, output format.
2. Resolve the focal company's ticker with the ticker lookup tool before any ticker-dependent pull. If the focal company is private, resolve it through the private-company tool (funding history, latest primary and secondary marks, disclosed metrics) and note that public-market tools will apply only to its listed competitors.
3. Define the competitive arena precisely in one sentence — product category, customer segment, and geography (e.g., "cloud data warehousing for large enterprises, global" not "software"). Every inclusion/exclusion decision downstream references this definition. If the focal company competes in multiple distinct arenas, analyze the arena matching the user's stated scope; if no scope is given, choose the arena that drives the largest share of the focal company's revenue and say so explicitly.
4. Derive all as-of parameters from the run date. Default lookback: last 3 fiscal years plus the latest LTM/last-4-quarters period for share work (extend to 5 or 10 years when the user selects a longer window and data supports it); last 8 quarters of transcripts for conduct evidence.
5. `data_source` is a set of one or more sources collected at intake — options: Perplexity Finance (built-in), FactSet, Daloopa, Morningstar, PitchBook, Carbon Arc (alt data), Guidepoint (expert calls); all seven are selected by default. Route it as follows:
   - **BYOL check.** Premium providers are bring-your-own-license. For each selected source, check whether its connector is connected. If selected but not connected: proceed without it and add one line to the deliverable's sourcing note — "<Provider> was selected but is not connected; connecting it would add <its specific value to this landscape — e.g., PitchBook: private-competitor rounds, marks, and revenue triangulation inputs; Guidepoint: practitioner win/loss and pricing evidence; Carbon Arc: demand signals showing who is actually gaining; Daloopa: filing-linked segment/KPI history for the share math>." Never stall or fail over an unavailable premium source — the built-in finance tools are the always-available baseline.
   - **Provider of record per data domain**, stated on every exhibit that uses it: fundamentals & segment/KPI history: Daloopa > FactSet > Morningstar > built-in; consensus estimates & revisions: FactSet > built-in; private-company data (rounds, marks, secondaries): PitchBook > built-in private-company tool; fund/ownership analytics: Morningstar > built-in; alt-data demand/transaction signals: Carbon Arc; expert qualitative evidence (pricing, win/loss, channel checks): Guidepoint.
   - **Complementary universes, not redundancy.** A real landscape is mixed: FactSet/Daloopa cover the listed players, PitchBook covers the privates, Carbon Arc measures demand across both, Guidepoint explains the why behind the numbers. Where selected providers overlap, cross-validate every load-bearing figure (share numerators, denominators, margins); where they disagree materially, show both values and explain the basis difference (calendarization, segment definition, restatement vintage) — never silently average.
   - **Series integrity.** One table column / one time series = one provider basis; never splice providers within a series without an explicit footnote at the splice point.
   - Save every raw tabular pull as CSV in a working directory (e.g., `finance_data/`) before analysis, tagged with its provider of record, so all computed shares and deltas are reproducible from saved inputs.
6. Public web sources come ONLY after finance tools are insufficient (typically: private-company revenue triangulation, third-party market share studies, pricing pages, regulatory filings of foreign or private players). Prefer primary sources — filings, earnings transcripts, IR decks, official statistics, regulator publications — and cite each inline. Never rely on low-quality aggregators.

## Phase 1: Peer Set and Strategic Groups

1. Build the player list. Start from the user's named competitors verbatim (include every one; drop none). If the set is not fully specified, triangulate discovery from five independent channels — no single channel is trusted alone:
   a. **Filed competitor sets, both directions**: the focal company's 10-K "Competition" section AND each candidate's own 10-K. The asymmetries are informative — a giant the target names who does not name the target back is an aspirational comp; a smaller player who names the target is an attacker. Record who-names-whom in a cross-reference table and carry the asymmetries into the strategic-group read.
   b. **Peer transcripts**: search the last 8 quarters of earnings transcripts of adjacent companies for mentions of the focal company — a company that discusses the target on its calls competes with it in practice, whatever the filings say.
   c. **Guidepoint reverse-references** (when selected+connected): experts interviewed about OTHER companies who mention the target unprompted; recurring reverse-mentions surface competitors the target's own disclosures underweight.
   d. **Quantitative screen**: same-industry companies whose revenue growth and gross/EBIT margin profiles fall within a stated band of the focal company's — self-declared comps miss the economically similar players. Flag any screen hit absent from channels a–c and decide inclusion against the arena definition, stating the call.
   e. **PitchBook** (when selected+connected): private companies in the arena by vertical and keyword — funded privates the filings never name; fall back to the built-in private-company tool otherwise.
   Then correct the union manually. The finance peer tool may seed channel d, but its output reflects index/sector adjacency, not arena overlap: add players the channels miss (foreign listings, divisions of diversified parents) and remove companies that don't actually compete in the defined arena — state each removal and why.
2. Target 6–12 players covering, where identifiable, at least ~80% of arena revenue or volume; list a "long tail" line for the remainder rather than ignoring it. Include private players — do not build a public-only landscape when the arena's most important competitor is private.
3. For each player, record: name, ticker or ownership status (public / private-VC / private-PE / subsidiary of X), arena-relevant business description (1 sentence), and how much of the parent's total revenue the arena represents (a focused pure-play behaves differently from a giant's side business — flag this asymmetry explicitly, using the segment tool to isolate arena-relevant revenue for diversified players).
4. Assign strategic groups: cluster players by the two dimensions that actually govern competition in this arena (e.g., price point x product breadth, integration depth x customer segment, scale x specialization). Name each group, state its inclusion criteria, and identify which group the focal company competes in and which groups can invade it. 3–5 groups is typical; do not force clusters where the arena is genuinely homogeneous.
5. Fix the arena's 3–5 battleground metrics — the measures investors and operators actually benchmark on (e.g., SaaS: ARR growth, NRR, Rule of 40; payments: TPV, take rate; marketplaces: GMV, take rate, repeat rate; carriers: units, load factor, cost per unit). Use these same metrics consistently for every player in every subsequent phase.

## Phase 2: Share and Share-Shift (Reproducible Math)

This phase must produce numbers a reader can recompute. No unsourced share claims, no "gaining share" without a basis.

1. Declare the share basis up front and use it consistently: the metric (revenue, units, GMV/TPV, ARR, subscribers, capacity, etc.), the currency and unit, and the period convention (fiscal years calendarized to the nearest calendar year, or trailing-4-quarter windows). Honor the user's `share_basis` selection; if `auto`, pick the basis the industry itself uses and justify the choice in one sentence.
2. Build the numerator series: for each player and each period in the lookback, pull the arena-relevant figure — total company revenue only for pure-plays; the segment tool's segment revenue or KPI series (GMV, units, ARPU x users, etc.) for diversified players; disclosed or triangulated figures for privates (Phase 2.5). Convert non-USD reporters at the average rate for each period and note the rates used. Cross-validate each load-bearing numerator from a second selected provider where coverage overlaps (e.g., Daloopa segment series vs. FactSet); reconcile discrepancies >2% in a footnote rather than averaging.
3. Build the denominator two ways where possible, and label which one each share number uses:
   - **Relative share**: sum of the tracked players' figures. Fully reproducible; understates the long tail. Preferred for share-SHIFT analysis.
   - **Absolute share**: a third-party or company-cited market size. Cite the source, vintage, and definition; flag any definitional mismatch with the arena.
4. Compute share per player per period and share shift in basis points over the full lookback and over the most recent year. Present the complete table: raw figures, denominator, share, and delta — with a source for every raw cell and estimate flags `[E]` where applicable. Missing data shows as "n/a" with the reason, never blank and never interpolated silently.
5. Sanity checks before drawing conclusions: shares sum to 100% (relative basis); no player's implied growth contradicts its reported growth; fiscal-year misalignments >1 quarter are flagged; any share move >300 bps in a single year is traced to a specific driver (M&A, contract win/loss, price action, new product, exit) with a cited event — unexplained large moves are treated as possible data errors, not findings.
6. Distinguish organic share shift from acquired share: where M&A occurred in the window, show share shift both as-reported and pro-forma (acquirer + target combined historically) so the organic trajectory is visible.
7. Carbon Arc corroboration (when selected+connected): pull relative demand/transaction-signal trajectories across the competitor set on a common basis and set them against the computed reported-share shifts — the alt-data read on who is actually gaining, ahead of and between filings. Where signals and reported share diverge (e.g., demand signals show the target slipping while reported share holds), state the divergence, the likely cause (pricing, mix shift, panel/channel coverage), and which read Phase 6 should weight. Present signal-based shares as a separate corroborating exhibit with panel-coverage caveats — never splice them into the reported-share series.

### Phase 2.5: Private Players — Triangulation With Confidence Tiers

For each private player, estimate the arena figure and tag it with a confidence tier; carry the tier through every table that uses the number:

- **Tier 1 — Disclosed**: company-published audited or press-released figures (revenue, ARR, GMV), or a listed parent's segment disclosure. Use as-is with citation.
- **Tier 2 — Reported/Provider**: private-market provider data (funding rounds, valuation marks, secondary prices from the private-company tool), credible press reporting of specific figures, or sell-side estimates. Cite outlet/provider and date.
- **Tier 3 — Triangulated**: your own estimate from at least two independent legs — e.g., disclosed customer count x estimated ACV; headcount x revenue-per-employee of the closest public comp; valuation mark ÷ prevailing arena revenue multiple; disclosed growth rate applied to a last-known revenue. Show the triangulation arithmetic and present a range, not a point.

Never present Tier 2/3 numbers with the same confidence as reported figures. If a private player is material (plausibly >10% relative share) and only Tier 3 data exists, run the share-shift conclusions at both ends of the estimate range and state whether the verdict survives.

## Phase 3: Moat Assessment Per Player (Evidence-Graded)

Rate every player — not just the focal company — on the five moat sources. A moat claim is an empirical claim; grade the evidence, don't assert.

1. Moat sources to assess: **switching costs** (integration depth, contractual lock-in, retraining/data-migration cost, observed churn/retention), **network effects** (cross-side vs same-side, local vs global, measurable density advantage), **scale economies** (unit-cost or R&D/fixed-cost spread at volume; minimum efficient scale vs player sizes), **brand/intangibles** (pricing premium actually achieved, proprietary data, patents), **regulatory barriers** (licenses, approvals, certifications, tariff/local-content protection).
2. For each player x source, assign strength (Strong / Moderate / Weak / None) AND an evidence grade:
   - **Verified**: quantified disclosure or observable market outcome — retention/NRR figures, realized price increases that stuck, cost-per-unit gaps, win rates, regulatory license counts.
   - **Corroborated**: management claims consistent with independent evidence (customer commentary, competitor transcripts, third-party surveys, Guidepoint expert interviews — always with the corroboration count, e.g., "3 of 4 experts").
   - **Asserted**: management or press narrative only. Asserted-only claims cannot support a Strong rating.
3. Run the disconfirming check for every Strong rating: what evidence would falsify it, and does any exist (rising churn, price cuts, share loss to a smaller entrant, gross margin erosion)? Call out moats that look important narratively but show weak evidence — brand and "ecosystem" claims are the usual offenders.
4. Distinguish current state from trajectory: is each moat widening, stable, or eroding, and on what evidence (e.g., NRR trend, pricing-power trend, relative R&D/capex capacity)?
5. Summarize in a moat scoreboard (players x five sources, strength + grade + one-line evidence citation each) and identify the arena's decisive moat source — the one that historically separates winners from losers here.

## Phase 4: Unit Economics and Financial Quality Comparison

1. Pull margin and return series for all public players over the lookback via the ratios tool: gross margin, EBIT/EBITDA margin, FCF margin, ROIC/ROE, plus S&M and R&D intensity where relevant. Same fiscal-period convention as Phase 2; flag exceptions.
2. Compare disclosed unit economics on the Phase 1 battleground metrics — NRR, CAC payback, take rate, ARPU, cost per unit, LTV proxies — from segment KPIs, filings, and IR materials. Only compare like-for-like definitions; where companies define a metric differently (e.g., NRR inclusion rules), state the difference rather than forcing a ranking. Mark "not disclosed" honestly — a sparse but honest table beats a complete fabricated one.
3. Interpret dispersion structurally: does the margin gap between leaders and laggards reflect scale (test: margin vs arena revenue), mix, pricing power, or accounting choices? Connect each explanation back to the Phase 3 moat evidence — margins are the moat's financial fingerprint, and a "Strong moat" rating with deteriorating relative margins is a contradiction to resolve, not ignore.
4. Where adjusted metrics matter (adj EBITDA, adj EPS, FCF definitions), use the adjusted-metrics capability and note material adjustment differences between players.
5. Pull consensus estimate-revision trends for every public player (provider of record: FactSet when connected, built-in estimates otherwise): relative revision momentum across the set is the market's running read on who is winning. Note where revisions contradict your share math or the Carbon Arc signals — that disagreement is an input to the Phase 6 what's-priced-in call, not noise to smooth over.

## Phase 5: Pricing Dynamics, Conduct, and Entry Vectors

1. Diagnose competitive conduct: is this arena behaving **rationally** (price discipline, stable/rising gross margins, capacity growth tracking demand, competitors publicly declining unprofitable business) or as a **share war** (list-price cuts, discounting escalation, promotional intensity, capacity racing ahead of demand, "investing in price" language)? Support the verdict with: gross margin trajectories across players (Phase 4), pricing actions with dates and magnitudes, and verbatim transcript quotes (speaker, company, quarter) from the last 8 quarters on pricing, discounting, and competitive response — sweep prepared remarks AND Q&A, plus earnings presentations, press releases, and recent 8-Ks where pricing actions or contract wins/losses are disclosed. Note conduct inflections mid-window — a rational arena turning irrational is often the single most valuation-relevant finding.
2. Expert-call pricing and win/loss evidence (Guidepoint, when selected+connected): pull recent interviews on the focal company AND its main competitors covering realized pricing, discounting depth, win/loss outcomes, and switching behavior. Treat each interview as one data point, not a verdict: report every load-bearing claim with its corroboration count and dates ("3 of 4 experts, Mar–Jun, report vendor X discounting 15–20% on renewals; 1 disputes"). Single-expert claims are flagged as uncorroborated and cannot alone support a conduct verdict or a moat re-grade; before relying on any expert claim, cross-check it against gross-margin trajectories, transcript language, and (where available) Carbon Arc demand signals, and state which corroborates.
3. Map entry and disruption vectors. Inventory the barriers implied by Phase 3, then scan for what could route around them: funded new entrants (use private-market funding data — capital flooding into the arena is a leading indicator of future price pressure), adjacent giants with distribution advantages, substitutes and technology discontinuities that reset the basis of competition, vertical integration by customers or suppliers, and regulatory change that lowers or raises barriers. For each material vector: likelihood (high/medium/low), earliest credible impact window, which incumbents are most exposed, and the evidence.
4. Record recent strategic conduct that changes structure: M&A in the arena (acquirer, target, date, value, multiple with methodology, strategic logic), major partnerships/exclusives, and capacity or capex announcements.

## Phase 6: Synthesis — Implications for the Focal Company

Answer the core question directly; every claim must trace to a prior phase.

1. **Position verdict**: is the focal company gaining, holding, or ceding share (state the bps, basis, and period), and is its decisive moat widening or eroding (cite the grade and evidence)?
2. **Growth implication**: arena growth ± the focal company's share trajectory implies a revenue growth band. Compare it against consensus revenue estimates for the next 2 fiscal years. State whether consensus embeds share gains, share stability, or share loss — and whether the landscape evidence supports that embedded assumption.
3. **Margin implication**: given the conduct diagnosis (rational vs share war), relative scale trajectory, and entry pressure, are the focal company's gross and operating margins structurally biased up, flat, or down? Cross-check against consensus margin estimates.
4. **Valuation implication**: does the focal company's relative multiple vs the peer set (from Phase 4 pulls plus current quotes) already pay for the competitive position you found? Identify the variant perception — where your landscape read differs from what consensus and the multiple imply.
5. **Who wins and why**: name the player(s) best positioned to gain share over the next 2–3 years and the player(s) most likely to cede it, with the causal mechanism doing the work (which decisive moat, cost position, demand-signal trajectory, or conduct advantage) — a ranked call, not a hedge across everyone. State the confidence level and 2–3 falsifiers specific to this call (distinct from the focal-company signposts below): observable events or data prints, with thresholds, that would flip the winner call. If the evidence genuinely cannot separate winners, say so and name the evidence that would.
6. **Falsifiers and monitoring**: 3–5 specific, quantified signposts with thresholds and cadence (e.g., "relative share on the declared basis, checked each earnings season — two consecutive quarters of >50 bps loss breaks the thesis"; "gross margin gap to nearest competitor narrowing below X pts"; "new-entrant funding above $Y in the arena"). Include the single piece of evidence that would most change the verdict.
7. Be direct about uncertainty: small player counts, Tier 3 estimates, definitional mismatches, and short windows all limit confidence — state which conclusions are robust to those limits and which are not.

## Phase 7: Output Creation

Honor the selected `output_format`; default to PDF when ambiguous (this is a narrative-plus-exhibits analysis). All formats present the same underlying dataset: the player roster (with the who-names-whom cross-reference), share/share-shift table with sources and confidence tiers, moat scoreboard, unit-economics comparison, conduct evidence, entry vectors, and the synthesis. Exhibit titles state insights, not topics ("Focal Co. ceded 240 bps of relative revenue share over FY23–FY25", not "Market Share").

- **XLSX** — sheets in order: (1) Verdict & Read Me — position verdict, implications, monitoring plan, methodology notes; (2) Players & Strategic Groups; (3) Share & Share Shift — raw figures per player per period, denominator, computed shares and bps deltas as live formulas, basis and period stated in the header, confidence tier and source per raw cell; (4) Moat Scoreboard; (5) Unit Economics & Margins; (6) Conduct & Pricing Evidence — dated actions, transcript quotes, and expert-call claims with corroboration counts (plus a Demand Signals exhibit where Carbon Arc was used); (7) Entry & Disruption Vectors; (8) Sources & Traceability. Derived values must be live formulas so share math stays auditable.
- **PDF (memo)** — portrait memo in the Phase 1→6 order, opening with a one-page executive summary (verdict, share trajectory, moat call, the three implications, top signposts), tables and charts embedded at the relevant section.
- **PDF (Presentation)** — apply the PDF (Presentation) block below; recommended order: cover; executive summary; arena & strategic groups; share-shift exhibit; moat scoreboard; unit economics comparison; conduct & pricing; entry vectors; implications for growth/margins/valuation; monitoring signposts; appendix (methodology, triangulation math, sources).
- **Dashboard** — panels: position verdict banner; share-trend chart with basis/period selector; moat scoreboard heat map; margin/unit-economics comparison; conduct evidence feed with dated quotes and expert corroboration counts; demand-signal trend panel where Carbon Arc was used; entry-vector watch list; monitoring signposts with thresholds. Every raw figure exposes its source on click.

Chart standards where charts are produced: titles state the insight; label data directly; ≤5 series per chart; annotate share charts with the basis and period; never plot Tier 3 point estimates without their range.

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

---

End the response with: This is research and analysis only, not personalized financial advice. Consult a qualified financial advisor before making investment decisions.

## MANDATORY QA REVISIONS (v2, 2026-07-21) — these override any conflicting guidance above

1. **Financial number formatting (all outputs)**: Follow standard finance sign and numbering conventions. Abbreviate large values — never write out every digit of a billion-scale number in text, tables, or slides. Default unit is $ in millions with thousands separators (e.g., "$3,423M" or "$3.4B", never "$3,423,192,847"). State the unit once per table/exhibit header ("$ in millions unless otherwise noted") rather than repeating full figures per cell. Negative values in parentheses, e.g., (412). Multiples as 0.0x; percentages to one decimal; per-share amounts in dollars and cents.
2. **Source quality bar**: Cite only professional-grade sources: company filings (10-K/10-Q/8-K, S-1, proxy), earnings transcripts, investor-relations materials, connected premium data providers, primary regulatory/statistical agencies, and top-tier financial press (WSJ, FT, Bloomberg, Reuters). NEVER cite or rely on Zacks, Motley Fool, Seeking Alpha, Simply Wall St, GuruFocus, Benzinga, StockTwits, aggregator blogs, SEO content farms, or similar unprofessional sources — neither in prose nor in citation lists. If an aggregator merely relays another outlet's reporting (e.g. "Benzinga, citing The Information"), cite the original outlet directly instead; never cite the aggregator, even as a relay.
3. **Spreadsheet standards (any XLSX deliverable)**:
   - Hide gridlines on every sheet (Excel: View > uncheck Gridlines / Alt+W,V,G; openpyxl: `ws.sheet_view.showGridLines = False`).
   - Financial-model color convention: blue font = hardcoded inputs/assumptions; black font = formulas and same-sheet references; green font = links pulling from other sheets.
   - Summary/output tabs must contain NO hardcoded numbers (no blue on the summary page) — every figure must be a formula or cell reference linked to the underlying data/calculation tabs.
   - Never bury constants inside formulas as in-cell calculations (e.g., a black cell containing `=1234*0.25` that references no other cells). Every driver lives in its own labeled input cell (blue), and formulas reference cells only.
4. **Explicit unit labeling (every figure, every exhibit)**: No naked numbers. Every growth or change rate carries a % sign ("+23.1%", never "23.1"); every market-share or revenue-share figure is written as a percentage with the % sign ("20.8%", never "20.8"); every dollar value carries a $ sign and unit ("$412M", "$1.2B"); margins always carry the % sign ("18.4%", never "18.4"). Any multi-year annualized growth rate must be labeled as CAGR — "19% CAGR (2021–2025)" — never "19% / yr", "19% per year", or an unlabeled rate. This applies to every slide, chart axis, chart data label, table cell, KPI callout, and prose sentence, including summary and share-comparison slides. Before delivering, sweep every exhibit for naked numbers: a share table showing bare "20.8"/"23.1", a revenue column without $ signs, or a growth/margin column without % signs fails QA and must be fixed before delivery.

## Supporting skills

Load the following skills when they are available in this environment, and skip any that
are not: `finance/finance-markets`, `investment-research`, `office/xlsx`, `office/pdf`, `office/pptx`, `data/visualization`, `website-building/webapp`.
