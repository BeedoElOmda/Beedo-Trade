"""Gold and silver in Egyptian pounds per gram, from Yahoo Finance's international prices.

Gold (GC=F) and silver (SI=F) are quoted in US dollars per troy ounce. Each day's price is converted with
that day's official USD/EGP rate (EGP=X), so the course method runs on the price an Egyptian buyer sees.
This is the international price: local shop prices add a premium and workmanship fees.
"""
import threading, time
import analyze

OUNCE_GRAMS = 31.1034768
METALS = {
    "GOLD": {"ticker": "GC=F", "name": "Gold (24k, EGP per gram)", "label": "Gold"},
    "SILVER": {"ticker": "SI=F", "name": "Silver (999, EGP per gram)", "label": "Silver"},
}
KARATS = {"24k": 24 / 24, "21k": 21 / 24, "18k": 18 / 24}
SOURCE = "Yahoo Finance (international price, converted at the official USD/EGP rate)"
CACHE_SECONDS = 600
_cache, _lock = {}, threading.Lock()


def _fetch(ticker):
    with _lock:
        hit = _cache.get(ticker)
        if hit and time.time() - hit[0] < CACHE_SECONDS:
            return hit[1]
    bars, _ = analyze.fetch(ticker)
    with _lock:
        _cache[ticker] = (time.time(), bars)
    return bars


def to_egp_per_gram(usd_bars, fx_bars):
    """Daily USD/oz bars -> EGP/gram bars, using the most recent USD/EGP rate on or before each day."""
    rates = sorted((b["d"], b["c"]) for b in fx_bars)
    out, j, rate = [], 0, None
    for b in sorted(usd_bars, key=lambda x: x["d"]):
        while j < len(rates) and rates[j][0] <= b["d"]:
            rate = rates[j][1]; j += 1
        if rate is None:
            continue  # no exchange rate yet for the earliest days
        k = rate / OUNCE_GRAMS
        out.append({"d": b["d"], "o": round(b["o"] * k, 2), "h": round(b["h"] * k, 2),
                    "l": round(b["l"] * k, 2), "c": round(b["c"] * k, 2), "v": b["v"]})
    return out


def bars(code):
    """EGP-per-gram daily bars for GOLD or SILVER, plus a display name."""
    m = METALS[code]
    return to_egp_per_gram(_fetch(m["ticker"]), _fetch("EGP=X")), m["name"]


def rate():
    """Official US dollar rate in EGP, with the change from the previous day."""
    fx = _fetch("EGP=X")
    return {"usd_egp": fx[-1]["c"], "usd_egp_change": round((fx[-1]["c"] / fx[-2]["c"] - 1) * 100, 2), "fx_date": fx[-1]["d"]}


def summary():
    """Price cards for the Gold & Silver page."""
    out = {**rate(), "source": SOURCE}
    rate_now = out["usd_egp"]
    for code, m in METALS.items():
        usd = _fetch(m["ticker"])
        last, prev = usd[-1], usd[-2]
        g = last["c"] * rate_now / OUNCE_GRAMS
        year = [b["c"] for b in usd[-252:]]
        out[code.lower()] = {
            "usd_oz": last["c"], "egp_oz": round(last["c"] * rate_now, 0), "egp_gram": round(g, 2),
            "change_usd": round((last["c"] / prev["c"] - 1) * 100, 2), "date": last["d"],
            "high_52w_usd": max(year), "low_52w_usd": min(year),
            "perf_1y_usd": round((last["c"] / year[0] - 1) * 100, 1),
        }
    out["gold"]["karats"] = {k: round(out["gold"]["egp_gram"] * f, 2) for k, f in KARATS.items()}
    # Gold/silver ratio: ounces of silver one ounce of gold buys. High = silver relatively cheap.
    out["gold_silver_ratio"] = round(out["gold"]["usd_oz"] / out["silver"]["usd_oz"], 1)
    return out
