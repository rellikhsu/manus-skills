---
name: "perplexity:market-map"
description: "Research an industry vertical, categorize companies by sub-segment, stage, and funding, and produce a visual market map."
metadata:
  perplexity:
    display_name: "Market map"
---
# Market Map

Research an industry vertical and produce a comprehensive market map categorizing all relevant companies.
Premium data connectors (CBInsights, Statista, PitchBook, Crunchbase) are available and should be used when accessible.

## Phase 1: Market Taxonomy

1. Research the industry using broad searches: "[industry] market map", "[industry] landscape", "[industry] startups", "[industry] companies", industry reports, and analyst coverage.
2. Define 4-8 logical sub-segments or categories that partition the market.
3. For each sub-segment, define clear inclusion criteria (what types of companies belong).

## Phase 2: Company Research (Two-Pass)

### Pass 1: Broad Discovery
1. For each sub-segment, research and identify companies using multiple strategies in parallel:
   - Web search: "[segment] companies", "[segment] startups", "[segment] tools"
   - Competitor/alternative lists: "alternatives to [known company in segment]"
   - Investor portfolios and accelerator batches (YC, a16z, Sequoia, etc.)
   - Premium connectors when available (PitchBook, CB Insights, Crunchbase)
   - Industry reports, analyst notes, conference speaker lists
2. Use wide_research for batch company lookups when the list exceeds 10.
3. For each company, gather ALL of the following into a canonical table:
   - Company name
   - Segment (primary sub-segment assignment)
   - Description (3-5 sentence product/business summary — what the company actually builds, who it sells to, and the core technical approach. Must be self-contained and never truncated with "..." — if the source text is long, rewrite it into a complete summary.)
   - Why interesting (2-4 sentences on differentiation, wedge, or thesis: unique technical approach, notable customers or design partners, unusual go-to-market, or category-defining position)
   - Founder background (names + prior companies, PhD lab, or domain credentials for each named founder when disclosed)
   - Founded year
   - HQ location
   - Funding stage (Pre-Seed, Seed, Series A, etc., or Bootstrapped/Stealth)
   - Total funding raised (with currency)
   - Round history (each disclosed round: stage, date, amount, lead investor)
   - Key investors (lead investors first, then notable participating funds and strategic/corporate investors)
   - Est. revenue / ARR (if discoverable)
   - Est. growth rate (if discoverable)
   - Disclosed metrics & traction (any of: named customers/logos, pilots, deployments, units shipped, GMV, users/MAU, contracts signed, partnerships, YoY growth — with source and date for each)
   - Employee count
   - Website URL
   - Source URLs (at least one verifiable source per company)

### Pass 2: Gap Analysis & Verification
1. Review the company list by segment. Flag any segment with fewer than 5 companies for additional targeted research.
2. Run cross-reference searches: "[industry] startups 2024 2025 2026", "[industry] emerging companies", "new [industry] tools" to catch recently launched companies.
3. Stealth verification: For any company or founder labeled "stealth", search "[founder name]" startup OR founded OR company OR CEO to verify they haven't publicly launched. Reclassify any who have.
4. Source verification: Spot-check that source URLs resolve and support the claimed data points. Flag low-confidence entries.

## Phase 3: Output & Delivery

CRITICAL: Regardless of output format, every deliverable MUST include:
  (a) The full canonical company table with ALL fields from Phase 2, with Segment as a filterable column
  (b) Source URLs per company
  (c) A summary narrative with market themes and white space opportunities

### Format-specific rendering:

- **Web:** Deploy an interactive page. The primary view is a filterable/sortable data table with Segment as the default grouping. Add a visual map view (grid/treemap grouped by segment) as a secondary view. Clicking a company opens a detail modal that shows the FULL long-form description, the "why interesting" narrative, founder background, complete round history, full investor list, and any disclosed metrics/traction — none of these fields may be truncated in the modal. The table itself may show a shortened description, but the modal is the canonical full view.

- **Slide:** Produce a polished deck with:
  Slide 1: Title + scope
  Slide 2: Visual market map (companies organized by segment in color-coded panels)
  Slide 3+: Detailed company table(s) grouped by segment, showing ALL canonical fields. Split across multiple slides if needed for readability.
  Final slide: Market observations, white space analysis, and consolidated source list.

- **Spreadsheet:** Produce a formatted Excel file with:
  Tab 1: Full company table with Segment as the first data column (enabling auto-filter by segment)
  Tab 2: Summary by segment (company count, total funding, avg metrics)
  Tab 3: Market narrative and white space analysis

All formats must present the same underlying dataset. No format should drop columns that another format includes.

### Source URL formatting (per output type):
- **Web:** Render sources as markdown links: [Source Name](url)
- **Slide:** Display as plain-text citations (e.g., "Source: Crunchbase, PitchBook") with full URLs on a consolidated sources slide.
- **Spreadsheet:** Write source URLs as plain URLs only — never use markdown link syntax like [text](url) in cell values. If multiple sources exist for one company, separate them with a line break or semicolon. Use openpyxl's cell.hyperlink property to make URLs clickable when possible.
