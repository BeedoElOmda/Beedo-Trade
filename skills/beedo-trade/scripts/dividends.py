"""Beedo-Trade: dividend history of an EGX stock and the payout to expect next, from Yahoo Finance.

Usage:  python dividends.py COMI          (cash dividends, bonus shares, the usual month and the next expected payout)
        python dividends.py --selftest

Cash dividends come from Yahoo's dividend events. Bonus shares (stock dividends) show up in Yahoo as share changes:
5:4 means 1 free share for every 4 held. A ratio above 2:1 is treated as a stock split, not a dividend.
"Expected next" is a pattern from history, not an announcement: the company's general assembly decides.
"""
import collections, datetime as dt, json, sys, urllib.error, urllib.request

import analyze  # noqa: F401  (sets up the root certificates for HTTPS)

YEARS = 5  # the window used to judge the pattern
MONTHS = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def events(symbol, rng="10y"):
    """Cash dividends [(date, EGP per share)] and share changes [(date, new, old)], oldest first."""
    ysym = symbol.upper() if "." in symbol else symbol.upper() + ".CA"
    data, err = None, None
    for host in ("query1", "query2"):
        url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{ysym}?range={rng}&interval=1mo&events=div,split"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                data = json.load(r)
            break
        except (urllib.error.URLError, ValueError) as e:
            err = e
    if data is None:
        raise ConnectionError(f"Could not reach Yahoo Finance for {ysym}: {err}")
    res = ((data.get("chart") or {}).get("result") or [{}])[0]
    ev = res.get("events") or {}
    day = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()
    cash = sorted((day(d["date"]), round(d["amount"], 4)) for d in (ev.get("dividends") or {}).values() if d.get("amount"))
    splits = sorted((day(s["date"]), s.get("numerator"), s.get("denominator")) for s in (ev.get("splits") or {}).values()
                    if s.get("numerator") and s.get("denominator"))
    close = (res.get("meta") or {}).get("regularMarketPrice")
    return cash, splits, close


def bonus_ratio(new, old):
    """1 free share for every N held, or None for a real split (more than doubles the shares) or a reverse split."""
    r = new / old
    return round(1 / (r - 1), 1) if 1 < r <= 2.0 else None


def summarize(cash, splits, today=None, close=None):
    """Kind (Cash / Stock / Both / None) over the last YEARS years, the usual month, the yield and the next expected payout."""
    today = today or dt.date.today()
    since = f"{today.year - YEARS + 1}-01-01"  # the last YEARS calendar years, this one included
    recent_cash = [(d, a) for d, a in cash if d >= since]
    bonus = [(d, bonus_ratio(n, o)) for d, n, o in splits if bonus_ratio(n, o)]
    recent_bonus = [(d, r) for d, r in bonus if d >= since]
    kind = "Both" if recent_cash and recent_bonus else "Cash" if recent_cash else "Stock" if recent_bonus else "None"
    cash_years = sorted({d[:4] for d, _ in recent_cash})
    bonus_years = sorted({d[:4] for d, _ in recent_bonus})
    year_ago = today.replace(year=today.year - 1).isoformat()
    last12 = round(sum(a for d, a in cash if d > year_ago), 4)
    month = collections.Counter(int(d[5:7]) for d, _ in recent_cash).most_common(1)[0][0] if recent_cash else None
    out = {"kind": kind, "cash_years": len(cash_years), "bonus_years": len(bonus_years), "years": YEARS,
           "usual_month": month, "last_cash": ({"date": recent_cash[-1][0], "amount": recent_cash[-1][1]} if recent_cash else None),
           "cash_12m": last12, "yield_pct": round(last12 / close * 100, 2) if close and last12 else None,
           "last_bonus": ({"date": recent_bonus[-1][0], "one_for": recent_bonus[-1][1]} if recent_bonus else None),
           "history": {"cash": recent_cash, "bonus": recent_bonus}, "expected": None}
    # a habit: cash in at least 3 of the last 5 years, or bonus shares in at least 2
    expect = [k for k, ok in (("Cash", len(cash_years) >= 3), ("Stock", len(bonus_years) >= 2)) if ok]
    if expect:
        m = month or int(recent_bonus[-1][0][5:7])
        year = today.year if m > today.month or (m == today.month and not any(d[:7] == today.isoformat()[:7] for d, _ in recent_cash)) else today.year + 1
        out["expected"] = {"month": f"{year}-{m:02d}", "kind": "Both" if len(expect) == 2 else expect[0],
                           "regular": len(cash_years) >= 4 or len(bonus_years) >= 3}
    return out


def for_symbol(symbol, today=None):
    cash, splits, close = events(symbol)
    return {"symbol": symbol.upper(), "close": close, **summarize(cash, splits, today, close)}


def text(r):
    lines = [f"{r['symbol']}: {r['kind']} dividends over the last {r['years']} years "
             f"(cash in {r['cash_years']} of them, bonus shares in {r['bonus_years']})."]
    if r["last_cash"]:
        lines.append(f"  Last cash: {r['last_cash']['amount']} EGP per share on {r['last_cash']['date']}; "
                     f"usually in {MONTHS[r['usual_month']]}; last 12 months {r['cash_12m']} EGP"
                     + (f" ({r['yield_pct']}% of the price)." if r["yield_pct"] else "."))
    if r["last_bonus"]:
        lines.append(f"  Last bonus shares: 1 free share for every {r['last_bonus']['one_for']:g} on {r['last_bonus']['date']}.")
    e = r["expected"]
    lines.append(f"  Expected next: {e['kind'].lower()} around {e['month']} ({'a regular payer' if e['regular'] else 'pays often'}). "
                 "A pattern from history, not an announcement." if e else "  No regular pattern: no payout to expect.")
    return "\n".join(lines)


def selftest():
    cash = [("2022-04-10", 1.0), ("2023-04-12", 1.2), ("2024-04-08", 1.5), ("2025-04-09", 1.5), ("2026-04-07", 1.5)]
    splits = [("2025-12-01", 11, 10), ("2019-02-01", 5, 4), ("2018-09-01", 10, 1)]
    r = summarize(cash, splits, dt.date(2026, 11, 25), close=30.0)
    assert r["kind"] == "Both" and r["usual_month"] == 4 and r["cash_years"] == 5, r
    assert r["expected"] == {"month": "2027-04", "kind": "Cash", "regular": True}, r["expected"]
    assert r["last_bonus"] == {"date": "2025-12-01", "one_for": 10.0} and r["yield_pct"] == 5.0, r
    assert bonus_ratio(5, 4) == 4.0 and bonus_ratio(10, 1) is None and bonus_ratio(1, 10) is None
    r = summarize([("2024-06-01", 2.0)], [], dt.date(2026, 11, 25))
    assert r["kind"] == "Cash" and r["expected"] is None, r  # one payout is not a habit
    r = summarize(cash, [], dt.date(2026, 3, 1))
    assert r["expected"]["month"] == "2026-04", r  # still to come this year
    assert summarize([], [], dt.date(2026, 1, 1))["kind"] == "None"
    print("dividends selftest OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        print(text(for_symbol(sys.argv[1])))
    else:
        sys.exit(__doc__)
