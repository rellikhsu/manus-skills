---
name: perplexity
description: Perplexity Finance workflows for public-company research, market screening, valuation support, earnings analysis, competitive landscape, management credibility, macro impact, and investment-thesis tracking. Use when the user asks for any of these workflows and read the narrowest child skill first.
---

# Perplexity Finance Skills Collection

Use the narrowest child skill under this namespace for the requested public-market or investment-research workflow. The child skills were exported from the user's Perplexity Finance workspace and preserved with their original instructions and input schemas.

For NVO and other biopharma companies, combine these workflows with the local `biopharma-loe-valuation` and `valuation-model-governance` skills. Treat every finance connector, alternative-data provider, expert-call source, market quote, estimate, and pipeline claim as conditional on actual connector availability and a verified as-of date.

The `finance-screener-workflow-fast` child contains an unexecuted script that expects DuckDB and an external `finance_analyst` tool; inspect the runtime before using it.
