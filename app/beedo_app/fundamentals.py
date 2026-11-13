"""Company fundamentals for EGX stocks: data from TradingView's market scanner, rated with standard rules.

The whole market (about 300 stocks) comes back in one request, so every number can be compared with
its peers (same industry, or sector, or the market). Rules are deliberately simple and shown to the user.
"""
import json, statistics, threading, time, urllib.request

SCAN_URL = "https://scanner.tradingview.com/egypt/scan"
COLS = {  # our key -> TradingView column
    "symbol": "name", "name": "description", "sector": "sector", "industry": "industry", "close": "close",
    "market_cap": "market_cap_basic", "pe": "price_earnings_ttm", "pb": "price_book_ratio",
    "roe": "return_on_equity", "net_margin": "net_margin", "debt_to_equity": "debt_to_equity",
    "eps_growth": "earnings_per_share_diluted_yoy_growth_ttm", "revenue_growth": "total_revenue_yoy_growth_ttm",
    "dividend_yield": "dividends_yield_current",
    # shown as key figures (not rated)
    "eps": "earnings_per_share_basic_ttm", "ps": "price_sales_current", "ev_ebitda": "enterprise_value_ebitda_ttm",
    "roa": "return_on_assets", "gross_margin": "gross_margin", "operating_margin": "operating_margin",
    "current_ratio": "current_ratio", "total_debt": "total_debt", "free_cash_flow": "free_cash_flow_ttm",
    "revenue": "total_revenue", "net_income": "net_income",
    "high_52w": "price_52_week_high", "low_52w": "price_52_week_low", "beta": "beta_1_year",
    "volatility_1m": "Volatility.M", "perf_1m": "Perf.1M", "perf_3m": "Perf.3M", "perf_ytd": "Perf.YTD", "perf_1y": "Perf.Y",
    "avg_volume": "average_volume_30d_calc",
}
BANKS = {"Regional Banks", "Major Banks"}
CACHE_SECONDS = 1800
_cache = {"at": 0.0, "rows": None}
_lock = threading.Lock()


def market(force=False):
    """All EGX stocks with their fundamentals, cached for 30 minutes."""
    with _lock:
        if not force and _cache["rows"] and time.time() - _cache["at"] < CACHE_SECONDS:
            return _cache["rows"]
    body = json.dumps({"filter": [{"left": "type", "operation": "equal", "right": "stock"},
                                  {"left": "exchange", "operation": "equal", "right": "EGX"}],
                       "columns": list(COLS.values()), "range": [0, 1000]}).encode()
    req = urllib.request.Request(SCAN_URL, data=body, headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r).get("data") or []
    except Exception as e:
        raise ConnectionError(f"Could not download company fundamentals from TradingView: {e}") from e
    rows = [dict(zip(COLS, d["d"])) for d in data]
    if not rows:
        raise ConnectionError("TradingView returned no company data.")
    with _lock:
        _cache.update(at=time.time(), rows=rows)
    return rows


# ---------- peers ----------
def _median(rows, key):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    return round(statistics.median(vals), 2) if len(vals) >= 4 else None


def peer_medians(row, rows):
    """Medians from the narrowest group with at least 4 values: industry, then sector, then the whole market."""
    out = {}
    for key in ("pe", "pb", "roe", "net_margin", "debt_to_equity", "eps_growth", "revenue_growth", "dividend_yield"):
        for label, group in (("industry", [r for r in rows if row.get("industry") and r.get("industry") == row["industry"]]),
                             ("sector", [r for r in rows if row.get("sector") and r.get("sector") == row["sector"]]),
                             ("market", rows)):
            m = _median(group, key)
            if m is not None:
                out[key] = {"median": m, "group": label}
                break
    return out


# ---------- standard rules ----------
GOOD, FAIR, POOR = 2, 1, 0
LABEL = {GOOD: "Good", FAIR: "Fair", POOR: "Poor"}


def _rule(key, title, value, score, why, unit=""):
    return {"key": key, "title": title, "value": value, "unit": unit, "score": score,
            "label": LABEL.get(score, "No data"), "why": why}


def rate(row, rows):
    """Standard rules, each scored Good / Fair / Poor. Banks skip margin and debt rules, which don't fit how banks work."""
    bank = row.get("industry") in BANKS
    peers = peer_medians(row, rows)
    med = lambda k: (peers.get(k) or {}).get("median")
    rules = []

    pe, m = row.get("pe"), med("pe")
    if pe is None:
        rules.append(_rule("pe", "P/E (valuation)", None, None, "No earnings data"))
    elif pe <= 0:
        rules.append(_rule("pe", "P/E (valuation)", pe, POOR, "Loss-making over the last 12 months"))
    else:
        s = GOOD if (pe <= 10 or (m and pe <= 0.8 * m)) else POOR if (pe > 30 or (m and pe > 1.5 * m)) else FAIR
        rules.append(_rule("pe", "P/E (valuation)", pe, s, {GOOD: "Cheap for its earnings", FAIR: "Fairly valued", POOR: "Expensive for its earnings"}[s]))

    pb, m = row.get("pb"), med("pb")
    if pb is None:
        rules.append(_rule("pb", "P/B (price vs book value)", None, None, "No book-value data"))
    else:
        cheap, dear = (1.0, 2.5) if bank else (1.5, 5.0)
        s = GOOD if pb <= cheap or (m and pb <= 0.7 * m) else POOR if pb > dear and not (m and pb <= m) else FAIR
        rules.append(_rule("pb", "P/B (price vs book value)", pb, s, {GOOD: "Low price for its assets", FAIR: "Normal price for its assets", POOR: "High price for its assets"}[s]))

    roe = row.get("roe")
    if roe is None:
        rules.append(_rule("roe", "Return on equity", None, None, "No profitability data"))
    else:
        s = GOOD if roe >= 15 else FAIR if roe >= 8 else POOR
        rules.append(_rule("roe", "Return on equity", roe, s, {GOOD: "Earns well on shareholders' money (15%+)", FAIR: "Moderate returns (8-15%)", POOR: "Weak returns (under 8%)"}[s], "%"))

    if not bank:
        nm, m = row.get("net_margin"), med("net_margin")
        if nm is None:
            rules.append(_rule("net_margin", "Net profit margin", None, None, "No margin data"))
        else:
            s = GOOD if nm >= 10 or (m and nm >= 1.2 * m and nm > 0) else FAIR if nm >= 3 else POOR
            rules.append(_rule("net_margin", "Net profit margin", nm, s, {GOOD: "Keeps a healthy share of sales as profit", FAIR: "Thin but positive margins", POOR: "Little or no profit on sales"}[s], "%"))

        de = row.get("debt_to_equity")
        if de is None:
            rules.append(_rule("debt_to_equity", "Debt to equity", None, None, "No debt data"))
        else:
            s = GOOD if de <= 0.5 else FAIR if de <= 1.5 else POOR
            rules.append(_rule("debt_to_equity", "Debt to equity", de, s, {GOOD: "Low debt (0.5 or less)", FAIR: "Moderate debt (up to 1.5)", POOR: "High debt (over 1.5)"}[s]))

    # Egypt's high inflation lifts nominal growth, so "good" growth starts at 20%
    eg = row.get("eps_growth")
    if eg is None:
        rules.append(_rule("eps_growth", "Earnings growth (yearly)", None, None, "No growth data"))
    else:
        s = GOOD if eg >= 20 else FAIR if eg >= 0 else POOR
        rules.append(_rule("eps_growth", "Earnings growth (yearly)", eg, s, {GOOD: "Strong growth (20%+, above inflation)", FAIR: "Growing, but slower than inflation", POOR: "Earnings are falling"}[s], "%"))

    rg = row.get("revenue_growth")
    if rg is not None:
        s = GOOD if rg >= 20 else FAIR if rg >= 0 else POOR
        rules.append(_rule("revenue_growth", "Revenue growth (yearly)", rg, s, {GOOD: "Sales growing strongly (20%+)", FAIR: "Sales growing slowly", POOR: "Sales are shrinking"}[s], "%"))

    dy = row.get("dividend_yield")
    if dy:  # a bonus only: many good EGX companies reinvest instead of paying out
        s = GOOD if dy >= 4 else FAIR
        rules.append(_rule("dividend_yield", "Dividend yield", dy, s, "Pays a solid dividend (4%+)" if s == GOOD else "Pays a small dividend", "%"))

    scored = [r for r in rules if r["score"] is not None]
    core = [r for r in scored if r["key"] in ("pe", "pb", "roe", "net_margin", "debt_to_equity", "eps_growth")]
    if len(core) < 3:
        quality = {"label": "Not enough data", "level": None, "score": None,
                   "why": "TradingView has too few reported figures for this company to rate it."}
    else:
        pct = round(100 * sum(r["score"] for r in scored) / (2 * len(scored)))
        level = 2 if pct >= 70 else 1 if pct >= 45 else 0
        quality = {"label": ["Weak", "Fair", "Strong"][level], "level": level, "score": pct,
                   "why": f"{sum(1 for r in scored if r['score'] == GOOD)} good, {sum(1 for r in scored if r['score'] == FAIR)} fair and "
                          f"{sum(1 for r in scored if r['score'] == POOR)} poor out of {len(scored)} checks"}
    return {"symbol": row["symbol"], "name": row.get("name"), "sector": row.get("sector"), "industry": row.get("industry"),
            "bank": bank, "market_cap": row.get("market_cap"), "rules": rules, "quality": quality, "peers": peers,
            "figures": {k: row.get(k) for k in COLS if k not in ("symbol", "name", "sector", "industry")}}


def for_symbol(symbol):
    rows = market()
    row = next((r for r in rows if r["symbol"] == symbol.upper()), None)
    if not row:
        return {"symbol": symbol.upper(), "quality": {"label": "Not enough data", "level": None, "score": None,
                "why": "TradingView has no company data for this code."}, "rules": [], "peers": {}}
    return rate(row, rows)


def verdict(quality_level, rung):
    """Combines the business (quality) with the course's technical signal (rung -3..+3)."""
    if quality_level is None:
        return {"tone": "neutral", "short": "No rating", "text": "No fundamentals rating: rely on the technical signal, and keep positions small."}
    if quality_level == 2:
        if rung >= 2: return {"tone": "good", "short": "Best setup", "text": "Best setup: a strong company with a buy signal."}
        if rung >= 0: return {"tone": "neutral", "short": "Watch", "text": "Strong company, but no buy signal yet: put it on your watchlist and wait."}
        return {"tone": "warn", "short": "Wait", "text": "Strong company in a falling trend: wait for the chart to turn before buying."}
    if quality_level == 1:
        if rung >= 2: return {"tone": "neutral", "short": "Acceptable", "text": "Acceptable: a fair company with a buy signal. Consider a smaller position."}
        if rung >= 0: return {"tone": "neutral", "short": "No edge", "text": "Fair company with no clear signal: no edge right now."}
        return {"tone": "warn", "short": "Stay out", "text": "Fair company in a falling trend: stay out for now."}
    if rung >= 2: return {"tone": "warn", "short": "Speculative", "text": "Speculative: the chart says buy but the business is weak. Use a small size, or skip it."}
    return {"tone": "bad", "short": "Avoid", "text": "Avoid: a weak business without a buy signal."}
