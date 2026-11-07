"""Beedo-Trade: compute the mechanical parts of the course checklist for one EGX stock.

Usage:  python analyze.py COMI            (EGX code; ".CA" is added for Yahoo)
        python analyze.py --selftest
Stdlib only. Daily bars come from Yahoo Finance (COMI -> COMI.CA).
"""
import json, sys, urllib.request, datetime as dt

# ---------- data ----------
def fetch(symbol, rng="1y"):
    ysym = symbol.upper() if "." in symbol else symbol.upper() + ".CA"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ysym}?range={rng}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.load(r)["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    bars = []
    for i, t in enumerate(res.get("timestamp") or []):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c):
            continue  # Yahoo leaves holes on non-trading days
        h, l = max(o, h, l, c), min(o, h, l, c)  # Yahoo sometimes reports a low above the open
        bars.append(dict(d=dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(),
                         o=round(o, 2), h=round(h, 2), l=round(l, 2), c=round(c, 2), v=v or 0))
    return bars, res["meta"].get("longName") or ysym

# ---------- indicators ----------
def sma(xs, n):
    return [None if i + 1 < n else sum(xs[i + 1 - n:i + 1]) / n for i in range(len(xs))]

def rsi_wilder(closes, n=14):
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    ch = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    ag = sum(max(x, 0) for x in ch[:n]) / n
    al = sum(max(-x, 0) for x in ch[:n]) / n
    def val(g, l): return 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    out[n] = val(ag, al)
    for i in range(n, len(ch)):
        ag = (ag * (n - 1) + max(ch[i], 0)) / n
        al = (al * (n - 1) + max(-ch[i], 0)) / n
        out[i + 1] = val(ag, al)
    return out

def crosses(fast, slow, bars, lookback=40):
    ev = []
    for i in range(max(1, len(bars) - lookback), len(bars)):
        if None in (fast[i], slow[i], fast[i - 1], slow[i - 1]):
            continue
        if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]:
            ev.append((bars[i]["d"], "UP"))
        elif fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]:
            ev.append((bars[i]["d"], "DOWN"))
    return ev

def swings(bars, k=3):
    """Fractal swing points: a high/low that is the extreme of k bars on each side."""
    pts = []
    for i in range(k, len(bars) - k):
        win = bars[i - k:i + k + 1]
        if bars[i]["h"] == max(b["h"] for b in win):
            pts.append((i, "H", bars[i]["h"]))
        if bars[i]["l"] == min(b["l"] for b in win):
            pts.append((i, "L", bars[i]["l"]))
    return pts

def candle(b, prev_trend):
    body = abs(b["c"] - b["o"]); rng = b["h"] - b["l"] or 1e-9
    up = b["h"] - max(b["o"], b["c"]); lo = min(b["o"], b["c"]) - b["l"]
    if body <= 0.1 * rng:
        return "Doji (indecision)"
    if lo >= 2 * body and up <= body:
        return "Hammer (bullish reversal)" if prev_trend == "down" else "Hanging Man (bearish reversal)" if prev_trend == "up" else "Hammer-shape (no trend context)"
    if up >= 2 * body and lo <= body:
        return "Inverted Hammer (bullish reversal)" if prev_trend == "down" else "Shooting Star (bearish reversal)" if prev_trend == "up" else "Inverted-hammer shape (no trend context)"
    return ("White/bullish" if b["c"] > b["o"] else "Black/bearish") + " body"

def engulf(p, b):
    if b["c"] > b["o"] and p["c"] < p["o"] and b["c"] >= p["o"] and b["o"] <= p["c"]:
        return "Bullish Engulfing"
    if b["c"] < b["o"] and p["c"] > p["o"] and b["o"] >= p["c"] and b["c"] <= p["o"]:
        return "Bearish Engulfing"
    return None

# ---------- report ----------
def analyze(bars):
    C = [b["c"] for b in bars]; V = [b["v"] for b in bars]
    ma5, ma9, ma18 = sma(C, 5), sma(C, 9), sma(C, 18)
    rsi = rsi_wilder(C)
    last = bars[-1]; i = len(bars) - 1
    r = {"last_bar": last}

    # Step 1-3: support / resistance from swing points
    sw = swings(bars)
    def cluster(xs):  # merge levels within 1.5% so each zone is reported once
        out = []
        for x in sorted(xs):
            if out and x <= out[-1][-1] * 1.015: out[-1].append(x)
            else: out.append([x])
        return [round(sum(g) / len(g), 2) for g in out]
    def levels(points):
        sup = [x for x in cluster(p for _, t, p in points if t == "L") if x < last["c"]]
        res = [x for x in cluster(p for _, t, p in points if t == "H") if x > last["c"]]
        return {"supports_nearest_first": sup[::-1][:3], "resistances_nearest_first": res[:3]}
    rec = levels([p for p in sw if p[0] >= len(bars) - 90])
    def pct(x): return None if x is None else round(abs(last["c"] - x) / last["c"] * 100, 2)
    s1 = rec["supports_nearest_first"][0] if rec["supports_nearest_first"] else None
    r1 = rec["resistances_nearest_first"][0] if rec["resistances_nearest_first"] else None
    r["levels"] = {
        "recent_90d": rec, "historical_1y": levels(sw),
        "pct_to_nearest_recent_support": pct(s1), "pct_to_nearest_recent_resistance": pct(r1),
        "period_high": round(max(b["h"] for b in bars), 2), "period_low": round(min(b["l"] for b in bars), 2),
    }

    # Step 4: trend from the last swing highs/lows
    recent = [p for p in sw if p[0] >= len(bars) - 90]
    hs = [p for _, t, p in recent if t == "H"][-4:]
    ls = [p for _, t, p in recent if t == "L"][-4:]
    def run(xs, rising):  # consecutive steps (not points) ending at the latest swing
        n = 0
        for a, b in zip(xs[::-1][1:], xs[::-1]):
            if (b > a) == rising: n += 1
            else: break
        return n
    r["trend_swings"] = {
        "last_swing_highs_oldest_first": hs, "last_swing_lows_oldest_first": ls,
        "higher_high_steps": run(hs, True), "higher_low_steps": run(ls, True),
        "lower_high_steps": run(hs, False), "lower_low_steps": run(ls, False),
        "swing_points_last_90d": [(bars[j]["d"], t, round(p, 2), bars[j]["v"]) for j, t, p in recent[-10:]],
    }

    # Step 5: moving averages 5 / 9 / 18
    slope = None if ma18[i - 5] is None else round((ma18[i] - ma18[i - 5]) / ma18[i - 5] * 100, 2)
    order = "5>9>18 (uptrend order)" if ma5[i] > ma9[i] > ma18[i] else \
            "5<9<18 (downtrend order)" if ma5[i] < ma9[i] < ma18[i] else "mixed (intermingling)"
    r["moving_averages"] = {
        "MA5": round(ma5[i], 2), "MA9": round(ma9[i], 2), "MA18": round(ma18[i], 2),
        "price_vs_MA18": "above" if last["c"] > ma18[i] else "below",
        "alignment": order, "MA18_slope_5d_pct": slope,
        "alarm_crosses_5x9": crosses(ma5, ma9, bars),
        "first_crosses_5x18": crosses(ma5, ma18, bars),
        "confirm_crosses_9x18": crosses(ma9, ma18, bars),
    }

    # Step 6: volume
    avg20 = sum(V[-21:-1]) / 20
    r["volume"] = {
        "today": V[-1], "avg20": round(avg20), "ratio_vs_avg20": round(V[-1] / avg20, 2) if avg20 else None,
        "last5": [(b["d"], round(b["c"] - p["c"], 2), b["v"]) for p, b in zip(bars[-6:-1], bars[-5:])],
    }

    # Step 7: reversal candles (trend context = 10-day close direction before the candle)
    cs = []
    for j in range(len(bars) - 3, len(bars)):
        ref = C[j - 10]
        tr = "up" if C[j - 1] > ref * 1.02 else "down" if C[j - 1] < ref * 0.98 else "flat"
        cs.append({"date": bars[j]["d"], "prior_trend": tr, "shape": candle(bars[j], tr),
                   "engulfing": engulf(bars[j - 1], bars[j])})
    r["candles_last3"] = cs

    # Step 8: RSI
    rv = [x for x in rsi[-30:] if x is not None]
    def zone(x):
        return "overbought >=70" if x >= 70 else "oversold <=30" if x <= 30 else "bullish 50-70" if x > 50 else "bearish 30-50" if x < 50 else "centerline 50"
    rx = []
    for j in range(len(bars) - 30, len(bars)):
        a, b = rsi[j - 1], rsi[j]
        for lvl in (30, 50, 70):
            if a is not None and b is not None and (a - lvl) * (b - lvl) < 0:
                rx.append((bars[j]["d"], f"{'up' if b > a else 'down'} through {lvl}"))
    div = []
    for kind in ("H", "L"):
        pts = [(j, p) for j, t, p in sw if t == kind and j >= len(bars) - 60][-2:]
        if len(pts) == 2 and None not in (rsi[pts[0][0]], rsi[pts[1][0]]):
            (j1, p1), (j2, p2) = pts
            if kind == "H" and p2 > p1 and rsi[j2] < rsi[j1]:
                div.append(f"NEGATIVE (bearish): price higher high {p1:.2f}->{p2:.2f}, RSI lower {rsi[j1]:.1f}->{rsi[j2]:.1f}")
            if kind == "L" and p2 < p1 and rsi[j2] > rsi[j1]:
                div.append(f"POSITIVE (bullish): price lower low {p1:.2f}->{p2:.2f}, RSI higher {rsi[j1]:.1f}->{rsi[j2]:.1f}")
    r["rsi14"] = {"now": round(rsi[i], 1), "prev": round(rsi[i - 1], 1), "zone": zone(rsi[i]),
                  "min_max_30d": (round(min(rv), 1), round(max(rv), 1)),
                  "level_crosses_30d": rx, "divergence": div or ["none detected"]}

    # Step 9: gaps in the last 30 bars
    gaps = []
    for j in range(len(bars) - 30, len(bars)):
        p, b = bars[j - 1], bars[j]
        if max(b["l"] - p["h"], p["l"] - b["h"]) < 0.003 * p["c"]:
            continue  # ignore gaps under 0.3% of price: tick noise, not a real gap
        if b["l"] > p["h"]:
            filled = any(x["l"] <= p["h"] for x in bars[j + 1:])
            gaps.append({"date": b["d"], "dir": "UP", "from": p["h"], "to": b["l"],
                         "vol_ratio": round(b["v"] / avg20, 2) if avg20 else None, "filled_since": filled})
        elif b["h"] < p["l"]:
            filled = any(x["h"] >= p["l"] for x in bars[j + 1:])
            gaps.append({"date": b["d"], "dir": "DOWN", "from": p["l"], "to": b["h"],
                         "vol_ratio": round(b["v"] / avg20, 2) if avg20 else None, "filled_since": filled})
    r["gaps_30d"] = gaps or "none"
    r["closes_last10"] = [(b["d"], round(b["c"], 2)) for b in bars[-10:]]
    return r

def selftest():
    up = [100 + k for k in range(60)]
    assert rsi_wilder(up)[-1] == 100.0
    assert abs(rsi_wilder([100 - k for k in range(60)])[-1]) < 1e-9
    assert sma([1, 2, 3, 4], 2)[-1] == 3.5
    zig = [10, 12, 11, 13, 12, 14, 13, 12, 11, 10] * 3  # just checks run() counts steps
    zb = [dict(d=str(k), o=c, h=c, l=c, c=c, v=1) for k, c in enumerate([10 + k * 0.1 for k in range(60)] + zig)]
    ts = analyze(zb)["trend_swings"]
    hs = ts["last_swing_highs_oldest_first"]
    assert ts["higher_high_steps"] + ts["lower_high_steps"] <= max(len(hs) - 1, 0)
    bars = [dict(d=str(k), o=c, h=c + 1, l=c - 1, c=c, v=1000) for k, c in enumerate(up)]
    r = analyze(bars)
    assert r["moving_averages"]["alignment"].startswith("5>9>18")
    v = [10] * 30 + [10 - k * 0.5 for k in range(10)] + [5 + k for k in range(20)]
    bars = [dict(d=str(k), o=c, h=c + .2, l=c - .2, c=c, v=1) for k, c in enumerate(v)]
    assert any(e[1] == "UP" for e in analyze(bars)["moving_averages"]["confirm_crosses_9x18"])
    assert candle(dict(o=10, c=10.2, h=10.25, l=9), "down").startswith("Hammer")
    assert candle(dict(o=10, c=9.8, h=11, l=9.78), "up").startswith("Shooting")
    print("selftest ok")

if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest(); sys.exit()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bars, name = fetch(sys.argv[1])
    if len(bars) < 60:
        sys.exit(f"Only {len(bars)} daily bars for {sys.argv[1]}; need 60+. Check the symbol.")
    out = {"symbol": sys.argv[1].upper(), "name": name, "bars": len(bars), **analyze(bars)}
    print(json.dumps(out, indent=1, default=str))
