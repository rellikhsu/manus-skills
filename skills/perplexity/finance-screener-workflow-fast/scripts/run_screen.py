#!/usr/bin/env python3
"""Deterministic single-entry fast-mode screener runner.

Full parity with the perplexity.ai/finance/screener fast path. This script is
the ONLY supported entry point for fast-mode requests: it ensures DuckDB is
importable (installing and transparently re-execing once if needed), calls
`finance_analyst` itself (via the `external-tool` CLI), downloads the parquet
tables it needs, compiles a typed JSON screen specification into deterministic
DuckDB SQL using a metric registry, executes the query, and prints machine
-readable telemetry followed by a Markdown table.

Invocation (the only bash call the agent should make for fast-mode screens):

    python3 scripts/run_screen.py --spec-json '<json>' [--output PATH]

or

    python3 scripts/run_screen.py --spec-file spec.json [--output PATH]

The DuckDB bootstrap deliberately runs before the `finance_analyst` call and
before any parquet download: the cold-sandbox path re-execs this process, so
network work completed beforehand would be discarded and repeated.

No agent-authored SQL, no manual `describe_external_tools`/`call_external_tool`
calls, and no manual schema inspection are needed or allowed for any request
that fits the supported spec below. See SKILL.md and
references/metric-registry.md for the exact contract.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.1"
RUNNER_VERSION = "3.3.2"

# ---------------------------------------------------------------------------
# DuckDB bootstrap (transparent, in-process re-exec — no second agent call)
# ---------------------------------------------------------------------------


_DUCKDB_MODULE: Any = None
_DUCKDB_READY_SECONDS: float = 0.0


def duckdb_bootstrap_was_reexec() -> bool:
    """True when this process is the post-re-exec child of a cold bootstrap.

    In that case the parent process's pip-install and interpreter-startup
    time happened before this process existed and is therefore NOT included
    in any timing this process reports.
    """
    return os.environ.get("_SCREENER_DUCKDB_BOOTSTRAPPED") == "1"


def load_duckdb():
    """Import DuckDB, installing and re-executing once when absent.

    ORDERING CONTRACT: this must be called before the `finance_analyst`
    external-tool call and before any parquet download. The cold-sandbox
    path re-execs the whole process via os.execve, which restarts main()
    from scratch; if any network work had already completed it would be
    thrown away and repeated, doubling the two most expensive phases of a
    run. Bootstrapping first makes a cold start cost one pip install, not a
    duplicated finance_analyst call plus a duplicated full download.

    Idempotent: the resolved module is cached, so the early bootstrap in
    main() followed by run()'s own defensive call neither re-imports nor
    re-installs.
    """
    global _DUCKDB_MODULE, _DUCKDB_READY_SECONDS
    if _DUCKDB_MODULE is not None:
        return _DUCKDB_MODULE
    start = time.monotonic()
    try:
        import duckdb  # type: ignore
    except ModuleNotFoundError:
        if duckdb_bootstrap_was_reexec():
            # Already tried once in this exec chain; do not loop forever.
            raise
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--disable-pip-version-check",
                "duckdb>=1.3,<2",
            ],
            check=True,
        )
        # A fresh sandbox may not expose newly installed site-packages to the
        # already-running interpreter. Re-exec transparently so the original
        # command continues without an agent-visible retry or second call.
        env = dict(os.environ)
        env["_SCREENER_DUCKDB_BOOTSTRAPPED"] = "1"
        os.execve(sys.executable, [sys.executable, *sys.argv], env)
        # os.execve replaces the process image, so this is unreachable in
        # practice; reaching it means the re-exec itself failed to take
        # effect and continuing would run the screen without DuckDB.
        raise RuntimeError(
            "DuckDB bootstrap re-exec did not replace the process image."
        )
    _DUCKDB_MODULE = duckdb
    _DUCKDB_READY_SECONDS += time.monotonic() - start
    return duckdb


# ---------------------------------------------------------------------------
# Metric registry
# ---------------------------------------------------------------------------
# Every metric maps to a SQL expression evaluated against the CTEs built by
# build_ctes(). Expressions reference CTE aliases: cp (company_profiles),
# qt (quotes), ttm_income (TTM + prior-TTM income statement), ttm_cf (TTM cash
# flow), bs (latest balance-sheet snapshot). All expressions are fixed strings
# from this registry; user input only selects keys, operators, and numeric
# thresholds. No user string is ever interpolated into an expression.

METRIC_REGISTRY: dict[str, dict[str, Any]] = {
    "price": {
        "expr": "qt.price",
        "needs": {"quotes"},
        "unit_family": "currency",
        "definition": "Latest quote price (quotes.price).",
    },
    "market_cap": {
        "expr": "qt.market_cap",
        "needs": {"quotes"},
        "unit_family": "currency",
        "definition": "Latest market capitalization, DOUBLE (quotes.market_cap).",
    },
    "pe_trailing": {
        "expr": "qt.market_cap / NULLIF(ttm_income.ttm_net_income, 0)",
        "needs": {"quotes", "income_statement"},
        "definition": (
            "Trailing P/E = market cap / TTM net income (income_statement "
            "quarters ranked 1-4). NULL when TTM net income <= 0. When used "
            "in a filter or as the sort metric, the compiler automatically "
            "adds `ttm_income.ttm_net_income > 0` so negative-earnings rows "
            "(which would otherwise satisfy e.g. 'P/E < 11' trivially via a "
            "negative ratio) are excluded rather than silently mis-passing. "
            "Market cap (the numerator) is always positive, so no second "
            "guard is needed here."
        ),
        "guards": ["ttm_income.ttm_net_income > 0"],
        "unit_family": "multiple",
    },
    "ev_ebitda": {
        "expr": (
            "(qt.market_cap + COALESCE(bs.total_debt, 0) "
            "- COALESCE(bs.cash_and_cash_equivalents, 0)) "
            "/ NULLIF(ttm_income.ttm_ebitda, 0)"
        ),
        "needs": {"quotes", "income_statement", "balance_sheet"},
        "definition": (
            "EV/EBITDA = (market cap + latest total_debt - latest "
            "cash_and_cash_equivalents) / TTM EBITDA (sum of income_statement"
            ".ebitda over quarters ranked 1-4). Balance-sheet items use the "
            "single latest reported quarter snapshot, not summed. When "
            "filtered/sorted, the compiler adds two guards: "
            "`ttm_income.ttm_ebitda > 0` (so negative-EBITDA rows don't "
            "trivially satisfy 'below X' filters via a negative multiple) "
            "AND `(qt.market_cap + COALESCE(bs.total_debt, 0) - "
            "COALESCE(bs.cash_and_cash_equivalents, 0)) > 0` (enterprise "
            "value itself must be positive -- a cash-rich, low-debt company "
            "can have negative EV, which with positive EBITDA produces a "
            "negative multiple that would otherwise trivially pass e.g. "
            "'EV/EBITDA < 10'; both numerator and denominator sign must be "
            "positive for the ratio to be meaningful)."
        ),
        "guards": [
            "ttm_income.ttm_ebitda > 0",
            "(qt.market_cap + COALESCE(bs.total_debt, 0) "
            "- COALESCE(bs.cash_and_cash_equivalents, 0)) > 0",
        ],
        "unit_family": "multiple",
    },
    "fcf_yield": {
        "expr": "ttm_cf.ttm_fcf / NULLIF(qt.market_cap, 0)",
        "needs": {"quotes", "cash_flow"},
        "unit_family": "percentage",
        "definition": (
            "FCF yield = TTM free_cash_flow (sum of cash_flow.free_cash_flow "
            "over quarters ranked 1-4) / market cap. Market cap is always "
            "positive so no denominator guard is needed; a negative yield "
            "correctly reflects negative TTM FCF."
        ),
    },
    "revenue_growth_yoy_ttm": {
        "expr": (
            "CASE WHEN ttm_income.prior_quarter_count = 4 "
            "THEN (ttm_income.ttm_revenue - ttm_income.prior_ttm_revenue) "
            "/ NULLIF(ABS(ttm_income.prior_ttm_revenue), 0) END"
        ),
        "needs": {"income_statement"},
        "unit_family": "percentage",
        "definition": (
            "TTM revenue YoY growth = (TTM revenue - prior-year TTM revenue) "
            "/ |prior-year TTM revenue|. TTM = quarters ranked 1-4; "
            "prior-year TTM = quarters ranked 5-8. NULL unless 8 quarters of "
            "history exist."
        ),
    },
    "net_income_growth_yoy_ttm": {
        "expr": (
            "CASE WHEN ttm_income.prior_quarter_count = 4 "
            "THEN (ttm_income.ttm_net_income - ttm_income.prior_ttm_net_income) "
            "/ NULLIF(ABS(ttm_income.prior_ttm_net_income), 0) END"
        ),
        "needs": {"income_statement"},
        "unit_family": "percentage",
        "definition": (
            "TTM net-income YoY growth, same quarter-ranking convention as "
            "revenue_growth_yoy_ttm. NULL unless 8 quarters of history exist."
        ),
    },
    "gross_margin_ttm": {
        "expr": "ttm_income.ttm_gross_profit / NULLIF(ttm_income.ttm_revenue, 0)",
        "needs": {"income_statement"},
        "definition": (
            "TTM gross_profit / TTM revenue. When filtered/sorted, the "
            "compiler adds `ttm_income.ttm_revenue > 0`: TTM revenue can be "
            "negative in this dataset (restatements/write-downs), and "
            "negative revenue combined with negative gross profit produces "
            "a spuriously positive margin (double-negative sign flip) that "
            "would trivially pass a 'high margin' filter."
        ),
        "guards": ["ttm_income.ttm_revenue > 0"],
        "unit_family": "percentage",
    },
    "operating_margin_ttm": {
        "expr": "ttm_income.ttm_operating_income / NULLIF(ttm_income.ttm_revenue, 0)",
        "needs": {"income_statement"},
        "definition": (
            "TTM operating_income / TTM revenue. Same "
            "`ttm_income.ttm_revenue > 0` guard as gross_margin_ttm and for "
            "the same double-negative sign-flip reason."
        ),
        "guards": ["ttm_income.ttm_revenue > 0"],
        "unit_family": "percentage",
    },
    "net_margin_ttm": {
        "expr": "ttm_income.ttm_net_income / NULLIF(ttm_income.ttm_revenue, 0)",
        "needs": {"income_statement"},
        "definition": (
            "TTM net_income / TTM revenue. Same "
            "`ttm_income.ttm_revenue > 0` guard as gross_margin_ttm and for "
            "the same double-negative sign-flip reason (confirmed in this "
            "dataset: negative-revenue, negative-net-income rows otherwise "
            "produce net margins as high as +993%)."
        ),
        "guards": ["ttm_income.ttm_revenue > 0"],
        "unit_family": "percentage",
    },
    "positive_net_income": {
        "expr": "(ttm_income.ttm_net_income > 0)",
        "needs": {"income_statement"},
        "boolean": True,
        "unit_family": "boolean",
        "definition": "TTM net income > 0.",
    },
    "positive_fcf": {
        "expr": "(ttm_cf.ttm_fcf > 0)",
        "needs": {"cash_flow"},
        "boolean": True,
        "unit_family": "boolean",
        "definition": "TTM free cash flow > 0.",
    },
    "debt_to_equity": {
        "expr": "bs.total_debt / NULLIF(bs.total_stockholders_equity, 0)",
        "needs": {"balance_sheet"},
        "definition": (
            "Latest balance-sheet total_debt / total_stockholders_equity "
            "(single latest reported quarter snapshot). When "
            "filtered/sorted, the compiler adds "
            "`bs.total_stockholders_equity > 0`: a company with negative "
            "equity (accumulated deficit exceeding paid-in capital) divides "
            "a positive total_debt by a negative number and produces a "
            "negative D/E ratio that would trivially pass a 'low leverage' "
            "filter despite being financially distressed, not conservatively "
            "levered."
        ),
        "guards": ["bs.total_stockholders_equity > 0"],
        "unit_family": "multiple",
    },
    "current_ratio": {
        "expr": "bs.total_current_assets / NULLIF(bs.total_current_liabilities, 0)",
        "needs": {"balance_sheet"},
        "definition": (
            "Latest balance-sheet total_current_assets / "
            "total_current_liabilities. When filtered/sorted, the compiler "
            "adds `bs.total_current_liabilities > 0`: a reported zero or "
            "negative current-liabilities figure is a data-quality artifact "
            "in this dataset, not a real balance-sheet state, and would "
            "otherwise produce an undefined or sign-flipped ratio."
        ),
        "guards": ["bs.total_current_liabilities > 0"],
        "unit_family": "multiple",
    },
    "cash": {
        "expr": "bs.cash_and_cash_equivalents",
        "needs": {"balance_sheet"},
        "unit_family": "currency",
        "definition": "Latest balance-sheet cash_and_cash_equivalents.",
    },
    "total_debt": {
        "expr": "bs.total_debt",
        "needs": {"balance_sheet"},
        "unit_family": "currency",
        "definition": "Latest balance-sheet total_debt.",
    },
    "dividend_yield_ttm": {
        "expr": (
            "(-1 * ttm_cf.ttm_common_dividends_paid) / NULLIF(qt.market_cap, 0)"
        ),
        "needs": {"quotes", "cash_flow"},
        "unit_family": "percentage",
        "definition": (
            "APPROXIMATION: TTM common dividends paid (cash_flow, quarters "
            "ranked 1-4; stored as a cash outflow, so negated) / market cap. "
            "There is no dedicated dividend-yield field in this database; "
            "this proxies trailing shareholder-yield-on-cost, not a "
            "forward/announced yield."
        ),
    },
    "payout_ratio_ttm": {
        "expr": (
            "(-1 * ttm_cf.ttm_common_dividends_paid) "
            "/ NULLIF(ttm_income.ttm_net_income, 0)"
        ),
        "needs": {"income_statement", "cash_flow"},
        "definition": (
            "APPROXIMATION: TTM common dividends paid (cash-flow statement) "
            "/ TTM net income. When filtered/sorted, the compiler adds "
            "`ttm_income.ttm_net_income > 0`: a company paying dividends "
            "while posting a TTM net loss produces a negative payout ratio "
            "that would trivially pass a 'low payout ratio' filter despite "
            "not being a sustainably low payout (dividends are not covered "
            "by earnings at all)."
        ),
        "guards": ["ttm_income.ttm_net_income > 0"],
        "unit_family": "percentage",
    },
    "eps_ttm": {
        "expr": "ttm_income.ttm_net_income / NULLIF(qt.shares_outstanding, 0)",
        "needs": {"quotes", "income_statement"},
        "unit_family": "plain",
        "definition": (
            "APPROXIMATION: TTM net income / latest shares_outstanding "
            "(quotes). income_statement.eps is a VARCHAR per-period EPS "
            "field, not summable across quarters; this recomputes a TTM EPS "
            "proxy from TTM net income and the current share count rather "
            "than summing reported per-quarter EPS."
        ),
    },
    "share_count_change_yoy": {
        "expr": (
            "CASE WHEN ttm_income.prior_quarter_count = 4 "
            "AND ttm_income.current_quarter_count = 4 "
            "THEN (ttm_income.avg_shares_current - ttm_income.avg_shares_prior) "
            "/ NULLIF(ABS(ttm_income.avg_shares_prior), 0) END"
        ),
        "needs": {"income_statement"},
        "unit_family": "percentage",
        "definition": (
            "APPROXIMATION: % change in average weighted_average_shs_out "
            "between the current TTM window (quarters ranked 1-4) and the "
            "prior-year TTM window (quarters ranked 5-8). Positive = "
            "dilution, negative = buybacks. NULL unless 8 quarters exist."
        ),
    },
}

# Columns always available for filtering/sorting alongside the metric
# registry above (kept separate because they are identifiers, not numeric
# screening metrics with an operator contract).
STANDARD_BUNDLE_COLUMNS = [
    ("ticker", "cp.symbol"),
    ("company", "cp.company_name"),
    ("industry", "cp.industry"),
    ("price", "qt.price"),
    ("market_cap", "qt.market_cap"),
    ("pe_trailing", METRIC_REGISTRY["pe_trailing"]["expr"]),
    ("pct_change", "qt.changes_percentage"),
    ("volume", "qt.volume"),
    ("revenue_growth_yoy_ttm", METRIC_REGISTRY["revenue_growth_yoy_ttm"]["expr"]),
    ("net_margin_ttm", METRIC_REGISTRY["net_margin_ttm"]["expr"]),
]

OPERATORS = {"lt", "lte", "gt", "gte", "eq", "between"}
SQL_OPERATORS = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">=", "eq": "="}

REQUIRED_TABLES_BASE = {"company_profiles", "quotes"}

MAX_LIMIT = 1000
MAX_DISPLAY_ROWS = 25

TOOL_OUTPUT_GLOB_DIR = Path(
    "/home/user/workspace/current_session_context/tool_calls/call_external_tool"
)


# ---------------------------------------------------------------------------
# Spec validation
# ---------------------------------------------------------------------------

UNIVERSE_FIELDS = {
    "sectors",
    "industries",
    "countries",
    "exchanges",
    "currency",
    "tickers",
    "market_cap_min",
    "market_cap_max",
    "active_only",
    "exclude_etfs_funds",
    "exclude_non_common",
}

TOP_LEVEL_FIELDS = {
    "universe",
    "filters",
    "sort",
    "limit",
    "display_rows",
    "sector_percentile_rank",
    "columns",
}

FILTER_FIELDS = {"metric", "op", "value", "low", "high"}
SORT_FIELDS = {"metric", "direction"}


class SpecError(ValueError):
    """Raised for any spec validation failure. Message is agent-facing."""


def _reject_unknown(obj: dict, allowed: set, where: str) -> None:
    unknown = set(obj.keys()) - allowed
    if unknown:
        raise SpecError(
            f"Unknown field(s) in {where}: {sorted(unknown)}. "
            f"Allowed: {sorted(allowed)}."
        )


# ---------------------------------------------------------------------------
# Unit-aware value parsing
#
# Every numeric spec value (universe.market_cap_min/max, filter value/low/
# high) may be given either as a bare JSON number (preserved as the existing
# canonical unit for full backward compatibility) or as a human-readable
# string. Parsing is metric-aware: which string forms are accepted depends
# on the metric's `unit_family` (currency/scale, percentage, multiple, or
# boolean). Parsing is strict and deterministic -- ambiguous, malformed, or
# wrong-family strings are rejected with an actionable SpecError rather than
# guessed at. See references/metric-registry.md "Unit-aware value parsing"
# for the full user-facing contract and worked examples.
# ---------------------------------------------------------------------------

_SCALE_SUFFIXES = {
    "k": 1_000.0,
    "m": 1_000_000.0,
    "mm": 1_000_000.0,
    "mn": 1_000_000.0,
    "b": 1_000_000_000.0,
    "bn": 1_000_000_000.0,
    "t": 1_000_000_000_000.0,
    "tn": 1_000_000_000_000.0,
}

# 3-letter ISO currency codes we accept as an explicit prefix/suffix on
# currency-family values. The code itself is not converted (no FX lookup) --
# it is only a passthrough label to accept forms like "USD 20B"; the value
# is otherwise taken at face value in the spec's implied unit
# (universe.currency), consistent with the rest of the fast-mode path which
# does not perform currency conversion.
_CURRENCY_CODES = {"USD", "EUR", "GBP", "JPY", "CNY", "INR", "CAD", "AUD", "CHF", "HKD"}
_CURRENCY_SYMBOLS = {"$": "USD", "\u20ac": "EUR", "\u00a3": "GBP", "\u00a5": "JPY"}


def _reject_non_finite(value: float, where: str) -> float:
    if math.isnan(value) or math.isinf(value):
        raise SpecError(f"{where}: value must be finite (got {value}).")
    return value


def _strip_currency_marker(text: str, where: str) -> str:
    """Remove a leading/trailing currency symbol or ISO code, commas, and
    surrounding whitespace. Raises on an unknown currency code so we never
    silently accept an unsupported currency label.

    A leading sign is preserved across a currency symbol, so both "-$5M"
    and "$-5M" strip down to "-5M" (both are natural ways to write a
    negative currency amount).
    """
    stripped = text.strip()
    sign = ""
    if stripped[:1] in "+-":
        sign, stripped = stripped[0], stripped[1:].strip()
    # Leading currency symbol, e.g. "$500M"
    for symbol in _CURRENCY_SYMBOLS:
        if stripped.startswith(symbol):
            stripped = stripped[len(symbol) :].strip()
            break
    else:
        # Leading or trailing 3-letter ISO code, e.g. "USD 20B" / "20B USD"
        m = re.match(r"^([A-Za-z]{3})\s+(.+)$", stripped)
        if m and m.group(1).upper() in _CURRENCY_CODES:
            stripped = m.group(2).strip()
        else:
            m = re.match(r"^(.+)\s+([A-Za-z]{3})$", stripped)
            if m and m.group(2).upper() in _CURRENCY_CODES:
                stripped = m.group(1).strip()
            elif re.search(r"[A-Za-z]{3}", stripped) and re.search(
                r"^[A-Za-z\s]+$", re.sub(r"[0-9.,\-+kmbtKMBT]", "", stripped)
            ):
                # Leftover alphabetic content that isn't a known ISO code or
                # scale suffix -- reject rather than guess.
                pass  # handled by the caller's suffix parsing / final check
    if sign and stripped[:1] not in "+-":
        stripped = sign + stripped
    return stripped


def _parse_currency_value(raw: Any, where: str) -> float:
    """Parse a currency/scale value for market_cap_min/max, price, market_cap,
    cash, total_debt. Accepts a bare number (canonical: already in the raw
    unit, e.g. dollars) or a string such as "$500M", "USD 20B", "2.5bn",
    "1,250,000", with K/M/B/T (case-insensitive) scale suffixes."""
    if isinstance(raw, bool):
        raise SpecError(f"{where}: expected a currency amount, got a boolean.")
    if isinstance(raw, (int, float)):
        return _reject_non_finite(float(raw), where)
    if not isinstance(raw, str):
        raise SpecError(
            f"{where}: expected a number or a currency string (e.g. '$500M'), "
            f"got {type(raw).__name__}."
        )
    text = raw.strip()
    if not text:
        raise SpecError(f"{where}: empty string is not a valid currency value.")
    if "%" in text:
        raise SpecError(
            f"{where}: '{raw}' looks like a percentage, but this field is a "
            "currency amount (e.g. '$500M', '20000000000'). Percent signs are "
            "not valid here."
        )
    if re.search(r"\bx\b", text, re.IGNORECASE) or re.fullmatch(
        r"[0-9.,\s+-]*[0-9]x", text, re.IGNORECASE
    ):
        raise SpecError(
            f"{where}: '{raw}' looks like a multiple (e.g. '30x'), but this "
            "field is a currency amount."
        )
    text = _strip_currency_marker(text, where)
    text = text.replace(",", "")
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*([A-Za-z]{0,2})", text)
    if not match:
        raise SpecError(
            f"{where}: '{raw}' is not a recognized currency value. Use a "
            "plain number (e.g. 500000000), or a string like '$500M', "
            "'USD 20B', '2.5bn', with an optional K/M/B/T scale suffix."
        )
    number_part, suffix = match.groups()
    number = float(number_part)
    if suffix:
        multiplier = _SCALE_SUFFIXES.get(suffix.lower())
        if multiplier is None:
            raise SpecError(
                f"{where}: '{raw}' has an unrecognized scale suffix "
                f"'{suffix}'. Supported suffixes: K, M, B, T (case-insensitive; "
                "MM/MN/BN/TN also accepted)."
            )
        number *= multiplier
    return _reject_non_finite(number, where)


def _parse_percentage_value(raw: Any, where: str) -> float:
    """Parse a percentage-family value (growth, margins, yields, payout
    ratio, share-count change). Accepts a bare number (canonical: already a
    decimal fraction, e.g. 0.10 for 10%) or a string such as "10%",
    "-5.5%", "150 bps", "150bps". Bps are divided by 10,000; percents by 100.
    """
    if isinstance(raw, bool):
        raise SpecError(f"{where}: expected a percentage, got a boolean.")
    if isinstance(raw, (int, float)):
        return _reject_non_finite(float(raw), where)
    if not isinstance(raw, str):
        raise SpecError(
            f"{where}: expected a decimal number or a percentage string "
            f"(e.g. '10%'), got {type(raw).__name__}."
        )
    text = raw.strip()
    if not text:
        raise SpecError(f"{where}: empty string is not a valid percentage value.")
    if "$" in text or re.search(r"\b(usd|eur|gbp|jpy)\b", text, re.IGNORECASE):
        raise SpecError(
            f"{where}: '{raw}' looks like a currency amount, but this field "
            "is a percentage (e.g. '10%', or a decimal fraction like 0.10)."
        )
    if re.search(r"\bx\b", text, re.IGNORECASE):
        raise SpecError(
            f"{where}: '{raw}' looks like a multiple (e.g. '30x'), but this "
            "field is a percentage."
        )
    bps_match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*bps", text, re.IGNORECASE)
    if bps_match:
        return _reject_non_finite(float(bps_match.group(1)) / 10_000.0, where)
    pct_match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*%", text)
    if pct_match:
        return _reject_non_finite(float(pct_match.group(1)) / 100.0, where)
    # A bare numeric string with no unit is rejected for percentage-family
    # metrics: unlike currency/multiple families, a plain string number here
    # is genuinely ambiguous ("10" could mean 10% or 10.0 as a decimal
    # fraction = 1000%) and this exact ambiguity caused the misconversion
    # this feature was built to prevent. Require an explicit '%'/'bps' unit
    # on any string; bare JSON numbers (handled above) remain the unambiguous
    # canonical-decimal-fraction path.
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        raise SpecError(
            f"{where}: '{raw}' is a bare numeric string with no unit, which "
            "is ambiguous for a percentage field (it could mean "
            f"{text}% or the decimal fraction {text}). Use a JSON number "
            f"({text} means {text} as a decimal fraction, i.e. "
            f"{float(text) * 100:g}%), or an explicit string like '{text}%' "
            "or '{n} bps'."
        )
    raise SpecError(
        f"{where}: '{raw}' is not a recognized percentage value. Use a "
        "decimal-fraction number (e.g. 0.10 for 10%), or a string like "
        "'10%', '-5.5%', or '150 bps'."
    )


def _parse_multiple_value(raw: Any, where: str) -> float:
    """Parse a multiple-family value (pe_trailing, ev_ebitda, debt_to_equity,
    current_ratio). Accepts a bare number (canonical: already the multiple,
    e.g. 30 for 30x) or a string such as "30x", "1.5x"."""
    if isinstance(raw, bool):
        raise SpecError(f"{where}: expected a multiple, got a boolean.")
    if isinstance(raw, (int, float)):
        return _reject_non_finite(float(raw), where)
    if not isinstance(raw, str):
        raise SpecError(
            f"{where}: expected a number or a multiple string (e.g. '30x'), "
            f"got {type(raw).__name__}."
        )
    text = raw.strip()
    if not text:
        raise SpecError(f"{where}: empty string is not a valid multiple value.")
    if "%" in text:
        raise SpecError(
            f"{where}: '{raw}' looks like a percentage, but this field is a "
            "multiple (e.g. '30x', or a plain number like 30)."
        )
    if "$" in text or re.search(r"\b(usd|eur|gbp|jpy)\b", text, re.IGNORECASE):
        raise SpecError(
            f"{where}: '{raw}' looks like a currency amount, but this field "
            "is a multiple (e.g. '30x', or a plain number like 30)."
        )
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*[xX]?", text)
    if not match:
        raise SpecError(
            f"{where}: '{raw}' is not a recognized multiple value. Use a "
            "plain number (e.g. 30) or a string like '30x' / '1.5x'."
        )
    return _reject_non_finite(float(match.group(1)), where)


def _parse_plain_value(raw: Any, where: str) -> float:
    """Parse a plain numeric metric (currently only eps_ttm). No unit
    strings are recognized; numeric strings are accepted for convenience but
    must be unambiguous plain numbers with no unit suffix."""
    if isinstance(raw, bool):
        raise SpecError(f"{where}: expected a number, got a boolean.")
    if isinstance(raw, (int, float)):
        return _reject_non_finite(float(raw), where)
    if isinstance(raw, str) and re.fullmatch(r"\s*[+-]?\d+(?:\.\d+)?\s*", raw):
        return _reject_non_finite(float(raw), where)
    raise SpecError(
        f"{where}: '{raw}' is not a recognized plain numeric value. This "
        "metric does not accept currency/percentage/multiple unit strings."
    )


_UNIT_PARSERS = {
    "currency": _parse_currency_value,
    "percentage": _parse_percentage_value,
    "multiple": _parse_multiple_value,
    "plain": _parse_plain_value,
}


def _parse_unit_aware_value(raw: Any, unit_family: str, where: str) -> float:
    """Dispatch to the correct family parser. `unit_family` must be one of
    the keys in _UNIT_PARSERS (never 'boolean' -- boolean metrics are
    validated separately and never pass through this function)."""
    parser = _UNIT_PARSERS.get(unit_family)
    if parser is None:
        raise SpecError(f"{where}: metric has no numeric unit family to parse.")
    return parser(raw, where)


def validate_spec(spec: dict) -> dict:
    """Validate and normalize a typed screen specification.

    Raises SpecError with an explicit message on any unknown field, unknown
    metric, unknown operator, or out-of-range value. Returns a normalized
    copy with defaults applied.
    """
    if not isinstance(spec, dict):
        raise SpecError("Spec must be a JSON object.")
    _reject_unknown(spec, TOP_LEVEL_FIELDS, "top-level spec")

    normalized: dict[str, Any] = {}

    universe = spec.get("universe", {})
    if not isinstance(universe, dict):
        raise SpecError("universe must be an object.")
    _reject_unknown(universe, UNIVERSE_FIELDS, "universe")

    norm_universe: dict[str, Any] = {
        "sectors": _validate_str_list(universe.get("sectors"), "universe.sectors"),
        "industries": _validate_str_list(
            universe.get("industries"), "universe.industries"
        ),
        "countries": _validate_str_list(
            universe.get("countries"), "universe.countries"
        ),
        "exchanges": _validate_str_list(
            universe.get("exchanges"), "universe.exchanges"
        ),
        "currency": universe.get("currency", "USD"),
        "tickers": _validate_str_list(universe.get("tickers"), "universe.tickers"),
        "market_cap_min": _validate_unit_value_or_none(
            universe.get("market_cap_min"), "currency", "universe.market_cap_min"
        ),
        "market_cap_max": _validate_unit_value_or_none(
            universe.get("market_cap_max"), "currency", "universe.market_cap_max"
        ),
        "active_only": bool(universe.get("active_only", True)),
        "exclude_etfs_funds": bool(universe.get("exclude_etfs_funds", True)),
        "exclude_non_common": bool(universe.get("exclude_non_common", True)),
    }
    if not isinstance(norm_universe["currency"], str) or not norm_universe["currency"]:
        raise SpecError("universe.currency must be a non-empty string.")
    if (
        norm_universe["market_cap_min"] is not None
        and norm_universe["market_cap_max"] is not None
        and norm_universe["market_cap_min"] > norm_universe["market_cap_max"]
    ):
        raise SpecError("universe.market_cap_min must be <= market_cap_max.")
    normalized["universe"] = norm_universe

    filters = spec.get("filters", [])
    if not isinstance(filters, list):
        raise SpecError("filters must be an array.")
    norm_filters = []
    for i, flt in enumerate(filters):
        if not isinstance(flt, dict):
            raise SpecError(f"filters[{i}] must be an object.")
        _reject_unknown(flt, FILTER_FIELDS, f"filters[{i}]")
        metric = flt.get("metric")
        if metric not in METRIC_REGISTRY:
            raise SpecError(
                f"filters[{i}].metric '{metric}' is not a supported metric. "
                f"Supported: {sorted(METRIC_REGISTRY)}."
            )
        op = flt.get("op")
        if op not in OPERATORS:
            raise SpecError(
                f"filters[{i}].op '{op}' is not supported. Supported: "
                f"{sorted(OPERATORS)}."
            )
        is_boolean = METRIC_REGISTRY[metric].get("boolean", False)
        unit_family = METRIC_REGISTRY[metric].get("unit_family")
        if op == "between":
            if is_boolean:
                raise SpecError(
                    f"filters[{i}]: boolean metric '{metric}' does not "
                    "support op 'between'."
                )
            low = flt.get("low")
            high = flt.get("high")
            if low is None or high is None:
                raise SpecError(
                    f"filters[{i}]: 'between' requires both low and high."
                )
            low = _parse_unit_aware_value(low, unit_family, f"filters[{i}].low")
            high = _parse_unit_aware_value(high, unit_family, f"filters[{i}].high")
            if low > high:
                raise SpecError(
                    f"filters[{i}]: low must be <= high (got low={low!r} > "
                    f"high={high!r} after normalization -- check for reversed "
                    "bounds or a unit mismatch between low and high)."
                )
            norm_filters.append({"metric": metric, "op": op, "low": low, "high": high})
        else:
            if is_boolean:
                value = flt.get("value", True)
                if not isinstance(value, bool):
                    raise SpecError(
                        f"filters[{i}]: metric '{metric}' is boolean; value "
                        "must be true or false."
                    )
                if op != "eq":
                    raise SpecError(
                        f"filters[{i}]: boolean metric '{metric}' only "
                        "supports op 'eq'."
                    )
                norm_filters.append({"metric": metric, "op": op, "value": value})
            else:
                value = _parse_unit_aware_value(
                    flt.get("value"), unit_family, f"filters[{i}].value"
                )
                norm_filters.append({"metric": metric, "op": op, "value": value})
    normalized["filters"] = norm_filters

    sort = spec.get("sort")
    if sort is None:
        normalized["sort"] = None
    else:
        if not isinstance(sort, dict):
            raise SpecError("sort must be an object.")
        _reject_unknown(sort, SORT_FIELDS, "sort")
        metric = sort.get("metric")
        if metric not in METRIC_REGISTRY and metric not in {
            c for c, _ in STANDARD_BUNDLE_COLUMNS
        }:
            raise SpecError(
                f"sort.metric '{metric}' is not a supported metric or column."
            )
        direction = sort.get("direction", "desc")
        if direction not in {"asc", "desc"}:
            raise SpecError("sort.direction must be 'asc' or 'desc'.")
        normalized["sort"] = {"metric": metric, "direction": direction}

    limit = spec.get("limit", 400)
    limit = _validate_int(limit, "limit")
    if not 1 <= limit <= MAX_LIMIT:
        raise SpecError(f"limit must be between 1 and {MAX_LIMIT}.")
    normalized["limit"] = limit

    display_rows = spec.get("display_rows", 25)
    display_rows = _validate_int(display_rows, "display_rows")
    if not 0 <= display_rows <= MAX_DISPLAY_ROWS:
        raise SpecError(f"display_rows must be between 0 and {MAX_DISPLAY_ROWS}.")
    normalized["display_rows"] = display_rows

    normalized["sector_percentile_rank"] = bool(
        spec.get("sector_percentile_rank", False)
    )

    columns = spec.get("columns", [])
    if not isinstance(columns, list):
        raise SpecError("columns must be an array.")
    for i, col in enumerate(columns):
        if col not in METRIC_REGISTRY:
            raise SpecError(
                f"columns[{i}] '{col}' is not a supported metric. Supported: "
                f"{sorted(METRIC_REGISTRY)}."
            )
    normalized["columns"] = list(dict.fromkeys(columns))  # de-dup, preserve order

    return normalized


def _validate_str_list(value, where: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise SpecError(f"{where} must be an array of strings.")
    return value


def _validate_number(value, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpecError(f"{where} must be a number.")
    return float(value)


def _validate_number_or_none(value, where: str):
    if value is None:
        return None
    return _validate_number(value, where)


def _validate_unit_value_or_none(value, unit_family: str, where: str):
    if value is None:
        return None
    return _parse_unit_aware_value(value, unit_family, where)


def _validate_int(value, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SpecError(f"{where} must be an integer.")
    return value


# ---------------------------------------------------------------------------
# SQL compilation
# ---------------------------------------------------------------------------


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _sql_literal_list(values: list[str]) -> str:
    return "(" + ", ".join(_sql_literal(v) for v in values) + ")"


NON_COMMON_EXCLUSION_CLAUSE = """cp.company_name NOT ILIKE '%warrant%'
  AND cp.company_name NOT ILIKE '%preferred%'
  AND cp.company_name NOT ILIKE '%depositary%'
  AND cp.company_name NOT ILIKE '%debenture%'
  AND cp.company_name NOT ILIKE '%parrs%'
  AND cp.company_name NOT ILIKE '% units'
  AND cp.company_name NOT ILIKE '% unit'
  AND cp.company_name NOT ILIKE '%PFD%'
  AND NOT regexp_matches(cp.company_name, '(?i)\\d+(\\.\\d+)?\\s*%\\s*(senior |sr\\.? |fixed rate |subordinated )*(notes?|bonds?)\\b')
  AND NOT regexp_matches(cp.symbol, '(WW|WS|WT)$')
  AND NOT (
    regexp_matches(cp.symbol, 'W$')
    AND EXISTS (
      SELECT 1 FROM company_profiles AS cp2
      WHERE cp2.symbol = regexp_replace(cp.symbol, 'W$', '')
        AND cp2.company_name = cp.company_name
    )
  )
  AND NOT (
    regexp_matches(cp.symbol, 'U$')
    AND EXISTS (
      SELECT 1 FROM company_profiles AS cp2
      WHERE cp2.symbol = regexp_replace(cp.symbol, 'U$', '')
        AND cp2.company_name = cp.company_name
    )
  )"""
# Notes on this proxy:
# - There is no dedicated security-type column in company_profiles, so
#   non-common securities (warrants, SPAC units, preferred/depositary
#   shares, debt-like instruments) are excluded by name-pattern and
#   symbol-suffix heuristics, mirroring the prior fast-mode preset.
# - The trailing-W (warrant) and trailing-U (unit) symbol-suffix checks only
#   fire when a sibling security with the same company_name and the base
#   symbol (suffix stripped) also exists, to avoid excluding tickers that
#   merely end in W or U by coincidence (e.g. a company literally named
#   ending in U with no sibling record).


def required_tables_for(spec: dict) -> set[str]:
    tables = set(REQUIRED_TABLES_BASE)
    for flt in spec["filters"]:
        tables |= METRIC_REGISTRY[flt["metric"]]["needs"]
    if spec["sort"] and spec["sort"]["metric"] in METRIC_REGISTRY:
        tables |= METRIC_REGISTRY[spec["sort"]["metric"]]["needs"]
    for col in spec["columns"]:
        tables |= METRIC_REGISTRY[col]["needs"]
    # Standard bundle always needs income_statement (pe_trailing, rev yoy,
    # net margin) in addition to company_profiles + quotes.
    tables |= {"company_profiles", "quotes", "income_statement"}
    return tables


def build_ctes(tables: set[str]) -> tuple[list[str], set[str]]:
    """Build only the CTEs required by the requested tables. Returns
    (cte_sql_blocks, cte_aliases_available)."""
    ctes: list[str] = []
    aliases: set[str] = set()

    if "income_statement" in tables:
        ctes.append(
            """ranked_income_quarters AS (
  SELECT
    symbol,
    TRY_CAST(date AS DATE) AS filing_date,
    TRY_CAST(revenue AS DOUBLE) AS revenue,
    TRY_CAST(gross_profit AS DOUBLE) AS gross_profit,
    TRY_CAST(operating_income AS DOUBLE) AS operating_income,
    TRY_CAST(net_income AS DOUBLE) AS net_income,
    TRY_CAST(ebitda AS DOUBLE) AS ebitda,
    TRY_CAST(weighted_average_shs_out AS DOUBLE) AS weighted_average_shs_out,
    ROW_NUMBER() OVER (
      PARTITION BY symbol ORDER BY TRY_CAST(date AS DATE) DESC
    ) AS quarter_rank
  FROM income_statement
  WHERE period IN ('Q1', 'Q2', 'Q3', 'Q4')
    AND TRY_CAST(date AS DATE) IS NOT NULL
)"""
        )
        ctes.append(
            """ttm_income AS (
  SELECT
    symbol,
    SUM(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN net_income END)
      AS ttm_net_income,
    SUM(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN revenue END)
      AS ttm_revenue,
    SUM(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN gross_profit END)
      AS ttm_gross_profit,
    SUM(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN operating_income END)
      AS ttm_operating_income,
    SUM(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN ebitda END)
      AS ttm_ebitda,
    AVG(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN weighted_average_shs_out END)
      AS avg_shares_current,
    SUM(CASE WHEN quarter_rank BETWEEN 5 AND 8 THEN net_income END)
      AS prior_ttm_net_income,
    SUM(CASE WHEN quarter_rank BETWEEN 5 AND 8 THEN revenue END)
      AS prior_ttm_revenue,
    AVG(CASE WHEN quarter_rank BETWEEN 5 AND 8 THEN weighted_average_shs_out END)
      AS avg_shares_prior,
    COUNT(CASE WHEN quarter_rank BETWEEN 1 AND 4 THEN 1 END)
      AS current_quarter_count,
    COUNT(CASE WHEN quarter_rank BETWEEN 5 AND 8 THEN 1 END)
      AS prior_quarter_count
  FROM ranked_income_quarters
  WHERE quarter_rank BETWEEN 1 AND 8
  GROUP BY symbol
)"""
        )
        aliases.add("ttm_income")

    if "cash_flow" in tables:
        ctes.append(
            """ranked_cf_quarters AS (
  SELECT
    symbol,
    TRY_CAST(date AS DATE) AS filing_date,
    TRY_CAST(free_cash_flow AS DOUBLE) AS free_cash_flow,
    TRY_CAST(common_dividends_paid AS DOUBLE) AS common_dividends_paid,
    ROW_NUMBER() OVER (
      PARTITION BY symbol ORDER BY TRY_CAST(date AS DATE) DESC
    ) AS quarter_rank
  FROM cash_flow
  WHERE period IN ('Q1', 'Q2', 'Q3', 'Q4')
    AND TRY_CAST(date AS DATE) IS NOT NULL
)"""
        )
        ctes.append(
            """ttm_cf AS (
  SELECT
    symbol,
    SUM(free_cash_flow) AS ttm_fcf,
    SUM(common_dividends_paid) AS ttm_common_dividends_paid,
    COUNT(*) AS quarter_count
  FROM ranked_cf_quarters
  WHERE quarter_rank BETWEEN 1 AND 4
  GROUP BY symbol
)"""
        )
        aliases.add("ttm_cf")

    if "balance_sheet" in tables:
        ctes.append(
            """latest_bs AS (
  SELECT *
  FROM (
    SELECT
      symbol,
      TRY_CAST(date AS DATE) AS filing_date,
      TRY_CAST(total_debt AS DOUBLE) AS total_debt,
      TRY_CAST(total_stockholders_equity AS DOUBLE) AS total_stockholders_equity,
      TRY_CAST(total_current_assets AS DOUBLE) AS total_current_assets,
      TRY_CAST(total_current_liabilities AS DOUBLE) AS total_current_liabilities,
      TRY_CAST(cash_and_cash_equivalents AS DOUBLE) AS cash_and_cash_equivalents,
      ROW_NUMBER() OVER (
        PARTITION BY symbol ORDER BY TRY_CAST(date AS DATE) DESC
      ) AS bs_rank
    FROM balance_sheet
    WHERE TRY_CAST(date AS DATE) IS NOT NULL
  )
  WHERE bs_rank = 1
)"""
        )
        aliases.add("bs")

    return ctes, aliases


def compile_sql(spec: dict) -> str:
    """Compile a validated spec into deterministic DuckDB SQL.

    Every table/column name and SQL fragment originates from the metric
    registry or fixed templates below; the only values ever interpolated
    from the spec are: sanitized string literals (via _sql_literal) and
    numbers that have already been validated as int/float by validate_spec.
    No agent-authored SQL, and no raw string concatenation of user-controlled
    identifiers, is used.
    """
    tables = required_tables_for(spec)
    ctes, cte_aliases = build_ctes(tables)

    universe = spec["universe"]

    select_cols = list(STANDARD_BUNDLE_COLUMNS)
    seen = {c for c, _ in select_cols}
    for col in spec["columns"]:
        if col not in seen:
            select_cols.append((col, METRIC_REGISTRY[col]["expr"]))
            seen.add(col)
    # Filters/sort referencing a metric not already selected should still be
    # selectable for transparency, but per spec keep output to standard
    # bundle + requested columns only (filters need not be projected).

    if spec["sector_percentile_rank"]:
        rank_targets = [c for c in spec["columns"]] or (
            [spec["sort"]["metric"]] if spec["sort"] else []
        )
        for metric in rank_targets:
            if metric in METRIC_REGISTRY:
                alias = f"{metric}_sector_pctile"
                if alias not in seen:
                    expr = (
                        f"PERCENT_RANK() OVER (PARTITION BY cp.sector "
                        f"ORDER BY {METRIC_REGISTRY[metric]['expr']})"
                    )
                    select_cols.append((alias, expr))
                    seen.add(alias)

    select_clause = ",\n  ".join(f"{expr} AS {name}" for name, expr in select_cols)

    joins = ["FROM company_profiles AS cp", "JOIN quotes AS qt USING (symbol)"]
    if "ttm_income" in cte_aliases:
        joins.append("JOIN ttm_income USING (symbol)")
    if "ttm_cf" in cte_aliases:
        joins.append("LEFT JOIN ttm_cf USING (symbol)")
    if "bs" in cte_aliases:
        joins.append("LEFT JOIN latest_bs AS bs USING (symbol)")

    where_clauses: list[str] = []
    if universe["active_only"]:
        where_clauses.append("cp.is_actively_trading = 'true'")
    where_clauses.append(f"cp.currency = {_sql_literal(universe['currency'].upper())}")
    if universe["exclude_etfs_funds"]:
        where_clauses.append("cp.is_etf = 'false'")
        where_clauses.append("cp.is_fund = 'false'")
    if universe["sectors"]:
        where_clauses.append(f"cp.sector IN {_sql_literal_list(universe['sectors'])}")
    if universe["industries"]:
        where_clauses.append(
            f"cp.industry IN {_sql_literal_list(universe['industries'])}"
        )
    if universe["countries"]:
        where_clauses.append(
            f"cp.country IN {_sql_literal_list(universe['countries'])}"
        )
    if universe["exchanges"]:
        where_clauses.append(
            f"cp.exchange IN {_sql_literal_list(universe['exchanges'])}"
        )
    if universe["tickers"]:
        where_clauses.append(f"cp.symbol IN {_sql_literal_list(universe['tickers'])}")
    if universe["market_cap_min"] is not None:
        where_clauses.append(f"qt.market_cap >= {universe['market_cap_min']}")
    if universe["market_cap_max"] is not None:
        where_clauses.append(f"qt.market_cap <= {universe['market_cap_max']}")
    if universe["exclude_non_common"]:
        where_clauses.append(NON_COMMON_EXCLUSION_CLAUSE)
    if "ttm_income" in cte_aliases:
        where_clauses.append("ttm_income.current_quarter_count = 4")
    where_clauses.append("qt.market_cap IS NOT NULL")

    # Deterministic ratio-sanity guards: applied automatically whenever a
    # metric with a registered `guards` list is filtered or sorted on. Each
    # guard clause is added at most once even if shared by several active
    # metrics (e.g. ttm_income.ttm_net_income > 0 is shared by pe_trailing
    # and payout_ratio_ttm). These prevent double-negative or
    # negative-denominator sign flips (e.g. negative EBITDA / negative
    # enterprise value, or negative equity) from making a distressed
    # company look attractively cheap/low-levered.
    applied_guards: set[str] = set()
    active_metrics = {flt["metric"] for flt in spec["filters"]}
    if spec["sort"] and spec["sort"]["metric"] in METRIC_REGISTRY:
        active_metrics.add(spec["sort"]["metric"])
    for metric in active_metrics:
        for guard in METRIC_REGISTRY[metric].get("guards", []):
            if guard not in applied_guards:
                where_clauses.append(guard)
                applied_guards.add(guard)

    for flt in spec["filters"]:
        metric_def = METRIC_REGISTRY[flt["metric"]]
        expr = metric_def["expr"]
        if flt["op"] == "between":
            where_clauses.append(f"({expr}) BETWEEN {flt['low']} AND {flt['high']}")
        elif metric_def.get("boolean"):
            where_clauses.append(f"({expr}) = {str(flt['value']).upper()}")
        else:
            op = SQL_OPERATORS[flt["op"]]
            where_clauses.append(f"({expr}) {op} {flt['value']}")

    where_clause = "\nWHERE " + "\n  AND ".join(where_clauses)

    order_clause = ""
    if spec["sort"]:
        metric = spec["sort"]["metric"]
        direction = "ASC" if spec["sort"]["direction"] == "asc" else "DESC"
        # Sort by the already-projected alias when available, else by
        # registry expression so we never require an extra join.
        if metric in seen:
            order_expr = metric
        else:
            order_expr = METRIC_REGISTRY[metric]["expr"]
        order_clause = f"\nORDER BY {order_expr} {direction} NULLS LAST"

    limit_clause = f"\nLIMIT {spec['limit']}"

    cte_clause = "WITH " + ",\n".join(ctes) + "\n" if ctes else ""
    sql = (
        f"{cte_clause}SELECT\n  {select_clause}\n"
        + "\n".join(joins)
        + where_clause
        + order_clause
        + limit_clause
    )
    return sql.strip()


READ_ONLY_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|COPY|ATTACH|INSTALL|LOAD|"
    r"PRAGMA|EXPORT|IMPORT|CALL)\b",
    flags=re.IGNORECASE,
)


def validate_read_only(sql: str) -> str:
    cleaned = sql.strip().rstrip(";").strip()
    if not re.match(r"^(WITH|SELECT)\b", cleaned, flags=re.IGNORECASE):
        raise ValueError("SQL must begin with WITH or SELECT.")
    forbidden = READ_ONLY_FORBIDDEN.search(cleaned)
    if forbidden:
        raise ValueError(f"Read-only SQL required; found {forbidden.group(1)}.")
    return cleaned


# ---------------------------------------------------------------------------
# finance_analyst invocation (programmatic, via external-tool CLI)
# ---------------------------------------------------------------------------


def call_finance_analyst(query: str) -> dict:
    """Call finance_analyst via the external-tool CLI and return the parsed
    JSON payload with top-level 'content' and 'data_files'."""
    proc = subprocess.run(
        [
            "external-tool",
            "call",
            json.dumps(
                {
                    "source_id": "finance",
                    "tool_name": "finance_analyst",
                    "arguments": {"query": query},
                }
            ),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"finance_analyst call failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"finance_analyst returned non-JSON output: {proc.stdout[:500]}"
        ) from exc
    # Some environments wrap the payload under a "result" key; normalize.
    if "data_files" not in payload and "result" in payload:
        payload = payload["result"]
    if "data_files" not in payload:
        raise RuntimeError(
            "finance_analyst response missing 'data_files'. Keys: "
            f"{list(payload.keys())}"
        )
    return payload


def default_query_for_tables(tables: set[str]) -> str:
    ordered = [
        t
        for t in [
            "company_profiles",
            "quotes",
            "income_statement",
            "balance_sheet",
            "cash_flow",
        ]
        if t in tables
    ]
    return (
        "Provide read access to the following raw tables for a structured "
        "SQL screen I will run myself: " + ", ".join(ordered) + ". "
        "I do not need you to write or run any SQL yourself; I only need the "
        "underlying parquet data files for these tables."
    )


# ---------------------------------------------------------------------------
# Download with one automatic InvalidToken retry (no agent-visible retry)
# ---------------------------------------------------------------------------


class InvalidTokenError(RuntimeError):
    pass


def _download_one(table: str, url: str, destination: Path) -> tuple[str, Path]:
    target = destination / f"{table}.parquet"
    try:
        urllib.request.urlretrieve(url, target)
    except urllib.error.HTTPError as exc:
        if exc.code == 400:
            body = exc.read().decode("utf-8", errors="ignore")
            if "InvalidToken" in body or "InvalidToken" in str(exc):
                raise InvalidTokenError(table) from exc
        raise
    return table, target


def download_tables(
    requested: list[str], available: dict[str, str], cache: Path
) -> dict[str, Path]:
    cache.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=min(6, max(1, len(requested)))) as executor:
        jobs = {
            executor.submit(_download_one, table, available[table], cache): table
            for table in requested
        }
        for job in as_completed(jobs):
            table, path = job.result()
            paths[table] = path
    return paths


def download_tables_with_retry(
    requested: list[str], query: str
) -> tuple[dict[str, Path], dict[str, Any]]:
    """Download required tables. On S3 InvalidToken, transparently call
    finance_analyst exactly one more time in-process and retry exactly once.
    No agent-visible retry — this is all inside a single bash invocation."""
    telemetry: dict[str, Any] = {
        "finance_tool_calls": 0,
        "download_retry_count": 0,
        "finance_tool_elapsed_seconds": 0.0,
        "download_elapsed_seconds": 0.0,
    }

    t0 = time.monotonic()
    payload = call_finance_analyst(query)
    telemetry["finance_tool_calls"] += 1
    telemetry["finance_tool_elapsed_seconds"] += round(time.monotonic() - t0, 3)

    available = {item["table_name"]: item["url"] for item in payload["data_files"]}
    missing = [t for t in requested if t not in available]
    if missing:
        raise RuntimeError(
            f"finance_analyst did not return required table(s): {', '.join(missing)}. "
            f"Available: {sorted(available)}."
        )

    cache = Path("/home/user/workspace/.finance_screener_cache")
    t1 = time.monotonic()
    try:
        paths = download_tables(requested, available, cache)
    except InvalidTokenError:
        telemetry["download_retry_count"] += 1
        t2 = time.monotonic()
        payload = call_finance_analyst(query)
        telemetry["finance_tool_calls"] += 1
        telemetry["finance_tool_elapsed_seconds"] += round(time.monotonic() - t2, 3)
        available = {
            item["table_name"]: item["url"] for item in payload["data_files"]
        }
        missing = [t for t in requested if t not in available]
        if missing:
            raise RuntimeError(
                "finance_analyst retry did not return required table(s): "
                f"{', '.join(missing)}."
            )
        paths = download_tables(requested, available, cache)
    telemetry["download_elapsed_seconds"] = round(time.monotonic() - t1, 3)

    return paths, telemetry


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_cell(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        magnitude = abs(value)
        if magnitude >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        if magnitude >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        if magnitude >= 1_000:
            return f"{value:,.0f}"
        return f"{value:,.4f}" if magnitude < 1 else f"{value:,.2f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(columns: list[str], rows: list[tuple]) -> str:
    lines = ["| " + " | ".join(columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        lines.append("| " + " | ".join(format_cell(v) for v in row) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_spec(args) -> tuple[dict, dict]:
    """Load, parse, and validate the spec.

    Returns a (normalized_spec, original_spec) tuple. original_spec is the
    raw, pre-normalization JSON object exactly as supplied by the caller
    (units/strings intact), so it can be included in telemetry alongside
    the normalized spec for auditability.
    """
    if args.spec_json:
        raw = args.spec_json
    elif args.spec_file:
        raw = Path(args.spec_file).read_text(encoding="utf-8")
    else:
        raise SpecError("Either --spec-json or --spec-file is required.")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecError(f"Spec is not valid JSON: {exc}") from exc
    return validate_spec(parsed), parsed


def run(spec: dict, output_path: str, original_spec: dict | None = None) -> dict:
    total_start = time.monotonic()

    # DuckDB must be importable before any network work happens. On a cold
    # sandbox load_duckdb() installs it and os.execve re-execs this process;
    # doing that here (rather than after the download, as v3.3 did) means the
    # discarded pre-exec work is only spec parsing and SQL compilation, never
    # a finance_analyst call or a full parquet download. Normally already
    # resolved and cached by main() before run() is entered.
    duckdb = load_duckdb()

    tables = sorted(required_tables_for(spec))
    sql = compile_sql(spec)
    sql = validate_read_only(sql)

    query = default_query_for_tables(set(tables))
    paths, dl_telemetry = download_tables_with_retry(tables, query)

    connection = duckdb.connect()
    for table in tables:
        safe_table = re.sub(r"[^a-zA-Z0-9_]", "", table)
        parquet_path = str(paths[table]).replace("'", "''")
        connection.execute(
            f"CREATE VIEW {safe_table} AS SELECT * FROM read_parquet('{parquet_path}')"
        )

    query_start = time.monotonic()
    cursor = connection.execute(sql)
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    query_elapsed = round(time.monotonic() - query_start, 3)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sql_output = output.with_suffix(".sql")
    sql_output.write_text(sql + ";\n", encoding="utf-8")
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    shown = rows[: spec["display_rows"]]
    total_elapsed = round(time.monotonic() - total_start, 3)

    telemetry = {
        "schema_version": SCHEMA_VERSION,
        "runner_version": RUNNER_VERSION,
        "total_rows": len(rows),
        "displayed_rows": len(shown),
        "output_csv_path": str(output),
        "generated_sql_path": str(sql_output),
        "finance_tool_elapsed_seconds": dl_telemetry["finance_tool_elapsed_seconds"],
        "download_elapsed_seconds": dl_telemetry["download_elapsed_seconds"],
        "query_elapsed_seconds": query_elapsed,
        "total_elapsed_seconds": total_elapsed,
        # Wall time this process spent making DuckDB importable (~0 when it
        # was already installed). On a cold sandbox the pip install happens
        # in the PARENT process, which then os.execve re-execs; that parent's
        # install and startup time is not observable here, so it is excluded
        # from both this field and total_elapsed_seconds.
        # duckdb_bootstrap_reexec flags exactly that case.
        "duckdb_ready_seconds": round(_DUCKDB_READY_SECONDS, 3),
        "duckdb_bootstrap_reexec": duckdb_bootstrap_was_reexec(),
        "finance_tool_calls": dl_telemetry["finance_tool_calls"],
        "download_retry_count": dl_telemetry["download_retry_count"],
        "tables_used": tables,
        "dataset_metadata": {
            "source": "finance_analyst (source_id=finance)",
            "tables": tables,
        },
        "normalized_spec": spec,
        "original_spec": original_spec,
    }

    print(json.dumps(telemetry))
    print(render_markdown(columns, shown))
    return telemetry


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic fast-mode finance screener runner."
    )
    spec_group = parser.add_mutually_exclusive_group(required=True)
    spec_group.add_argument("--spec-json", help="Inline JSON screen specification.")
    spec_group.add_argument("--spec-file", help="Path to a JSON screen spec file.")
    parser.add_argument(
        "--output",
        default="/home/user/workspace/screen.csv",
        help="Output CSV path (a sibling .sql file is also written).",
    )
    args = parser.parse_args()

    try:
        spec, original_spec = load_spec(args)
    except SpecError as exc:
        print(json.dumps({"error": "spec_validation_failed", "message": str(exc)}))
        return 2

    try:
        # Bootstrap DuckDB before run() does anything expensive. Spec
        # validation above is deliberately first: it is pure CPU, so an
        # invalid spec still exits 2 promptly without paying for a pip
        # install, while a cold-sandbox re-exec still lands strictly before
        # the finance_analyst call and the parquet download.
        load_duckdb()
        run(spec, args.output, original_spec=original_spec)
    except Exception as exc:  # noqa: BLE001 - surface any runtime failure clearly
        print(json.dumps({"error": "runtime_failure", "message": str(exc)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
