"""Company fundamentals for EGX stocks: data from TradingView's market scanner, rated with standard rules.

The whole market (about 300 stocks) comes back in one request, so every number can be compared with
its peers (same industry, or sector, or the market). Rules are deliberately simple and shown to the user.
"""
import json, os, statistics, sys, threading, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # sibling import under python -I
import analyze  # noqa: E402,F401  (sets up root certificates for HTTPS)

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


def _scan(body):
    req = urllib.request.Request(SCAN_URL, data=json.dumps(body).encode(), headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return [d["d"] for d in json.load(r).get("data") or []]
    except Exception as e:
        raise ConnectionError(f"Could not reach TradingView: {e}") from e


def health(index, stocks):
    """index: (close, change %, SMA50, SMA200, RSI); stocks: [(close, change %, SMA50, SMA200)].
    Score: index above SMA200 and SMA50 (+1 each, below -1 each), share of stocks above their SMA50 (>=60% +1, <=40% -1)."""
    close, chg, s50, s200, rsi = index
    pct = lambda ok, xs: round(100 * sum(map(ok, xs)) / len(xs)) if xs else None
    above50 = pct(lambda r: r[0] > r[2], [r for r in stocks if None not in (r[0], r[2])])
    above200 = pct(lambda r: r[0] > r[3], [r for r in stocks if None not in (r[0], r[3])])
    up = sum(1 for r in stocks if (r[1] or 0) > 0); down = sum(1 for r in stocks if (r[1] or 0) < 0)
    score = (1 if close > s200 else -1) + (1 if close > s50 else -1) + \
            (1 if above50 is not None and above50 >= 60 else -1 if above50 is not None and above50 <= 40 else 0)
    label = "Healthy" if score >= 2 else "Weak" if score <= -2 else "Mixed"
    return {"label": label, "score": score, "egx30": round(close, 2), "egx30_change": round(chg or 0, 2),
            "egx30_sma50": round(s50, 2), "egx30_sma200": round(s200, 2), "egx30_rsi": round(rsi, 1) if rsi is not None else None,
            "above_sma50_pct": above50, "above_sma200_pct": above200, "advancers": up, "decliners": down, "stocks": len(stocks)}


MIN_INDUSTRY = 3  # fewer stocks than this: breadth means little, so no label


def industries(stocks):
    """stocks: [(close, change %, SMA50, SMA200, sector, industry)] -> one row per industry, healthiest first.
    Score: share above SMA50 and share above SMA200 (>=60% +1 each, <=40% -1 each). 2 = Healthy, -2 = Weak."""
    groups = {}
    for r in stocks:
        groups.setdefault((r[5] or "Other", r[4] or ""), []).append(r)
    out = []
    for (ind, sec), rs in groups.items():
        h = health((1, 0, 0, 0, None), rs)  # dummy index: only the breadth figures are used here
        a50, a200 = h["above_sma50_pct"], h["above_sma200_pct"]
        side = lambda p: 0 if p is None else 1 if p >= 60 else -1 if p <= 40 else 0
        score = side(a50) + side(a200)
        chg = [r[1] for r in rs if r[1] is not None]
        label = "Too few stocks" if len(rs) < MIN_INDUSTRY else "Healthy" if score >= 2 else "Weak" if score <= -2 else "Mixed"
        out.append({"industry": ind, "sector": sec, "stocks": len(rs), "label": label, "score": score,
                    "above_sma50_pct": a50, "above_sma200_pct": a200, "advancers": h["advancers"], "decliners": h["decliners"],
                    "avg_change": round(sum(chg) / len(chg), 2) if chg else None})
    out.sort(key=lambda x: (x["label"] == "Too few stocks", -x["score"], -(x["above_sma50_pct"] or 0)))
    return out


def market_health():
    """EGX30 against its 50- and 200-day averages, breadth of every EGX stock, and the same breadth per industry
    (TradingView, end of day)."""
    idx = _scan({"symbols": {"tickers": ["EGX:EGX30"]}, "columns": ["close", "change", "SMA50", "SMA200", "RSI"]})
    stocks = _scan({"filter": [{"left": "type", "operation": "equal", "right": "stock"},
                               {"left": "exchange", "operation": "equal", "right": "EGX"}],
                    "columns": ["close", "change", "SMA50", "SMA200", "sector", "industry"], "range": [0, 1000]})
    if not idx or None in idx[0][:4] or not stocks:
        raise ConnectionError("TradingView returned no EGX30 or market data.")
    return {**health(idx[0], stocks), "industries": industries(stocks)}


# ---------- snapshot: when Yahoo has no daily history (or a frozen one) ----------
SMA_LENGTHS = (5, 6, 8, 9, 10, 13, 15, 20, 21, 30, 50, 100, 200)  # what TradingView's scanner offers (no 18)
NOT_CHECKED = [4, 7, 9, 10, 11]  # trend, candles, gaps and patterns need daily history


def snapshot_report(symbol, reason=""):
    """An analyze.report()-shaped dict from TradingView's latest values (today and the day before), for stocks without
    usable daily history. Steps in NOT_CHECKED can't be read; S/R come from monthly pivots and the 52-week range."""
    import datetime as dt
    sym = symbol.strip().upper()
    used = [p if p in SMA_LENGTHS else min(SMA_LENGTHS, key=lambda n: (abs(n - p), n)) for p in analyze.MA]
    if len(set(used)) < 3:
        raise ConnectionError(f"TradingView has no moving averages close to {analyze.MA}; try 5 / 9 / 18.")
    cols = ["description", "open", "high", "low", "close", "close[1]", "volume", "average_volume_10d_calc", "RSI", "RSI[1]",
            "MACD.macd", "MACD.signal", "MACD.macd[1]", "MACD.signal[1]", "price_52_week_low", "price_52_week_high",
            "Pivot.M.Classic.S1", "Pivot.M.Classic.S2", "Pivot.M.Classic.R1", "Pivot.M.Classic.R2"] + \
           [f"SMA{u}" for u in used] + [f"SMA{u}[1]" for u in used]
    rows = _scan({"symbols": {"tickers": [f"EGX:{sym}"]}, "columns": cols})
    if not rows:
        raise ConnectionError(f"TradingView has no data for {sym} either. Check the code, or use a CSV of daily prices.")
    v = dict(zip(cols, rows[0]))
    if None in [v["close"], v["close[1]"], v["RSI"], v["RSI[1]"], v["MACD.macd"], v["MACD.signal"]] + [v[f"SMA{u}"] for u in used]:
        raise ConnectionError(f"TradingView doesn't have enough data for {sym} yet (a new listing?). Use a CSV of daily prices.")
    c, today = v["close"], dt.date.today().isoformat()
    r2 = lambda x: None if x is None else round(x, 2)
    piv = [v[k] for k in ("Pivot.M.Classic.S1", "Pivot.M.Classic.S2", "Pivot.M.Classic.R1", "Pivot.M.Classic.R2") if v[k]]
    piv = piv if len(set(piv)) > 1 else []  # some stocks get one repeated (meaningless) pivot value
    sup = sorted({r2(x) for x in piv if x < c}, reverse=True)
    res = sorted({r2(x) for x in piv if x > c})
    lo, hi = v["price_52_week_low"], v["price_52_week_high"]
    pct = lambda x: None if x is None else round(abs(c - x) / c * 100, 2)
    f, m, s = used
    now = [v[f"SMA{u}"] for u in used]; prev = [v[f"SMA{u}[1]"] for u in used]
    def cross(a, b):
        if None in (prev[a], prev[b]): return []
        if prev[a] <= prev[b] and now[a] > now[b]: return [(today, "UP")]
        if prev[a] >= prev[b] and now[a] < now[b]: return [(today, "DOWN")]
        return []
    order = f"{f}>{m}>{s} (uptrend order)" if now[0] > now[1] > now[2] else \
            f"{f}<{m}<{s} (downtrend order)" if now[0] < now[1] < now[2] else "mixed (intermingling)"
    rsi, rsi1 = v["RSI"], v["RSI[1]"]
    zone = "overbought >=70" if rsi >= 70 else "oversold <=30" if rsi <= 30 else "bullish 50-70" if rsi > 50 else "bearish 30-50" if rsi < 50 else "centerline 50"
    ml, ms, ml1, ms1 = v["MACD.macd"], v["MACD.signal"], v["MACD.macd[1]"], v["MACD.signal[1]"]
    mcross = [] if None in (ml1, ms1) else [(today, "UP")] if ml1 <= ms1 and ml > ms else [(today, "DOWN")] if ml1 >= ms1 and ml < ms else []
    avg = v["average_volume_10d_calc"] or 0
    no_candle = {"date": today, "prior_trend": "flat", "shape": "Not checked", "engulfing": None}
    subs = [f"MA{u}" for p, u in zip(analyze.MA, used) if p != u]
    return {
        "symbol": sym, "name": v["description"] or sym, "bars": 0, "snapshot": True,
        "not_checked": sorted(NOT_CHECKED + ([] if sup or res else [2, 3])),  # no pivots: no recent S/R, no price location
        "source": "TradingView snapshot (latest session)", "reason": reason,
        "ma_note": "TradingView has no " + ", ".join(f"MA{p}" for p, u in zip(analyze.MA, used) if p != u) + ", so "
                   + ", ".join(subs) + " is used instead." if subs else "",
        "last_bar": {"d": today, "o": v["open"], "h": v["high"], "l": v["low"], "c": c, "v": v["volume"] or 0},
        "levels": {"recent_90d": {"supports_nearest_first": sup[:3], "resistances_nearest_first": res[:3]},
                   "historical_1y": {"supports_nearest_first": [r2(lo)] if lo and lo < c else [],
                                     "resistances_nearest_first": [r2(hi)] if hi and hi > c else []},
                   "pct_to_nearest_recent_support": pct(sup[0] if sup else None),
                   "pct_to_nearest_recent_resistance": pct(res[0] if res else None),
                   "period_high": r2(hi), "period_low": r2(lo)},
        "trend_swings": {"last_swing_highs_oldest_first": [], "last_swing_lows_oldest_first": [], "higher_high_steps": 0,
                         "higher_low_steps": 0, "lower_high_steps": 0, "lower_low_steps": 0, "swing_points_last_90d": []},
        "moving_averages": {"periods": used, f"MA{f}": r2(now[0]), f"MA{m}": r2(now[1]), f"MA{s}": r2(now[2]),
                            f"price_vs_MA{s}": "above" if c > now[2] else "below", "alignment": order, f"MA{s}_slope_5d_pct": None,
                            f"alarm_crosses_{f}x{m}": cross(0, 1), f"first_crosses_{f}x{s}": cross(0, 2), f"confirm_crosses_{m}x{s}": cross(1, 2)},
        "volume": {"today": v["volume"] or 0, "avg20": round(avg), "ratio_vs_avg20": round((v["volume"] or 0) / avg, 2) if avg else None,
                   "last5": [(today, round(c - v["close[1]"], 2), v["volume"] or 0)], "note": "average of the last 10 days (TradingView)"},
        "candles_last3": [no_candle] * 3,
        "rsi14": {"now": round(rsi, 1), "prev": round(rsi1, 1), "zone": zone, "min_max_30d": (round(min(rsi, rsi1), 1), round(max(rsi, rsi1), 1)),
                  "level_crosses_30d": [], "divergence": ["none detected"]},
        "gaps_30d": "none", "closes_last10": [(today, round(v["close[1]"], 2)), (today, round(c, 2))],
        "macd": {"line": round(ml, 3), "signal": round(ms, 3), "hist": round(ml - ms, 3),
                 "hist_prev": round(ml1 - ms1, 3) if None not in (ml1, ms1) else round(ml - ms, 3), "crosses_30d": mcross},
    }


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


if __name__ == "__main__":  # python fundamentals.py COMI | --health | --snapshot COMI
    import sys
    if not 2 <= len(sys.argv) <= 3:
        sys.exit("Usage: python fundamentals.py SYMBOL  |  --health  |  --snapshot SYMBOL")
    try:
        out = market_health() if sys.argv[1] == "--health" else snapshot_report(sys.argv[2]) if sys.argv[1] == "--snapshot" \
            else for_symbol(sys.argv[1])
        print(json.dumps(out, indent=1, default=str))
    except Exception as e:
        sys.exit(f"ERROR: {e}")
