"""Time machine: the odds that a trade plan reaches its target or its stop first.

    python -I timemachine.py COMI --entry 80.5 --stop 76.2 --target 89.1 [--days 20] [--seed 19] [--json]

Method adapted from trader-timemachine in github.com/jakeschincariol/day-trader-skill (MIT license), rebuilt for EGX:
free EGX prices are daily only (no 5-minute bars), so it replays whole trading days, not intraday bars.
1. 10,000 replays: start at the entry and build the next N trading days from the stock's own past daily moves,
   drawn at random (seeded, so a run can be repeated). A day that touches the stop counts as the stop, even if it
   also touched the target, and a gap below the stop still counts as -1R (a real fill can be worse).
2. History: the same plan (same % distances to stop and target) on real past days, without any simulation.
A simulation from the past, not a prediction. Standard library only.
"""
import json, os, random, statistics, sys

DAYS, REPLAYS, SEED, MIN_CASES = 20, 10_000, 19, 10


def _moves(bars):
    """Each day's open, high, low and close as ratios to the previous close."""
    return [(b["o"] / p["c"], b["h"] / p["c"], b["l"] / p["c"], b["c"] / p["c"]) for p, b in zip(bars, bars[1:]) if p["c"] > 0]


def _walk(days, stop, target):
    """days: (open, high, low, close) prices in order. -> ('target' | 'stop' | 'neither', last close)."""
    c = None
    for o, h, l, c in days:
        if l <= stop:
            return "stop", c
        if h >= target:
            return "target", c
    return "neither", c


def verdict(t, s, rr):
    """t, s: target-first and stop-first counts; rr: target distance / stop distance.
    A plan aiming for rr times its risk breaks even when the target comes first 1 in (1 + rr) times."""
    if not t + s:
        return "Neither the target nor the stop was reached in any replay."
    need, got = 100 / (1 + rr), 100 * t / (t + s)
    gap, side = abs(got - need), "target" if got > need else "stop"
    head = (("Close to a coin flip" if abs(rr - 1) < 0.05 else "Close to break-even") if gap < 5
            else f"Leans toward the {side}" if gap < 15 else f"Strongly toward the {side}")
    return f"{head}: the target came first in {got:.0f}% of the replays that reached one side; a {rr:.1f}R plan needs {need:.0f}% to break even."


def history(bars, entry, stop, target, days=DAYS, starts=None):
    """The same plan on real past days: entry at that day's close, stop and target at the same % distances.
    starts: indexes of the days to test (default every day after the first 60); open-ended recent cases are skipped."""
    ks, kt, risk_pct = stop / entry, target / entry, (entry - stop) / entry
    n = {"target": 0, "stop": 0, "neither": 0}
    rs = []
    for i in (range(60, len(bars) - 1) if starts is None else starts):
        c0 = bars[i]["c"]
        path = [(b["o"], b["h"], b["l"], b["c"]) for b in bars[i + 1:i + 1 + days]]
        if not path:
            continue
        side, last = _walk(path, c0 * ks, c0 * kt)
        if side == "neither" and len(path) < days:
            continue  # too recent: the trade would still be running
        n[side] += 1
        rs.append(-1 if side == "stop" else (kt - 1) / risk_pct if side == "target" else (last / c0 - 1) / risk_pct)
    cases = sum(n.values())
    return {**n, "cases": cases, "enough": cases >= MIN_CASES, "avg_r": round(statistics.mean(rs), 2) if rs else None}


def run(bars, entry, stop, target, days=DAYS, replays=REPLAYS, seed=SEED, starts=None):
    """bars: daily bars (d, o, h, l, c), oldest first, ideally two years. A buy plan: stop < entry < target."""
    if not 0 < stop < entry < target:
        return {"error": "The plan needs a stop below the entry and a target above it."}
    moves = _moves(bars)
    if len(moves) < 60:
        return {"error": "Not enough price history for the time machine (it needs at least 60 trading days)."}
    rng, risk, rr = random.Random(seed), entry - stop, (target - entry) / (entry - stop)
    n, rs, closes = {"target": 0, "stop": 0, "neither": 0}, [], []
    for _ in range(replays):
        price, path = entry, []
        for _ in range(days):
            o, h, l, c = (x * price for x in rng.choice(moves))
            path.append((o, h, l, c)); price = c
        side, last = _walk(path, stop, target)
        n[side] += 1
        closes.append(price)  # the price on the last day, whether or not the plan had already ended
        rs.append(rr if side == "target" else -1 if side == "stop" else (last - entry) / risk)
    pct = {k: round(v * 100 / replays, 1) for k, v in n.items()}
    q = statistics.quantiles(closes, n=20)
    out = {"entry": entry, "stop": stop, "target": target, "rr": round(rr, 2), "days": days, "replays": replays, "seed": seed,
           "from": bars[0]["d"], "to": bars[-1]["d"],
           "target_pct": pct["target"], "stop_pct": pct["stop"], "neither_pct": pct["neither"],
           "avg_r": round(statistics.mean(rs), 2),
           "close": {"median": round(statistics.median(closes), 2), "p5": round(q[0], 2), "p95": round(q[-1], 2)},
           "verdict": verdict(n["target"], n["stop"], rr), "notes": [],
           "history": history(bars, entry, stop, target, days, starts)}
    if pct["neither"] > 40:
        out["notes"].append(f"{pct['neither']}% of the replays reached neither within {days} trading days; the price then decides those.")
    return out


def text(r, symbol=""):
    if r.get("error"):
        return r["error"]
    h = r["history"]
    lines = [f"{symbol} time machine: {r['replays']:,} replays of the next {r['days']} trading days, seed {r['seed']}.",
             f"Plan: entry {r['entry']}, stop {r['stop']}, target {r['target']} ({r['rr']}R). Moves from {r['from']} to {r['to']}.",
             f"  target first  {r['target_pct']}%", f"  stop first    {r['stop_pct']}%", f"  neither       {r['neither_pct']}%",
             f"  Price after {r['days']} days: median {r['close']['median']}, 90% of replays between {r['close']['p5']} and {r['close']['p95']}.",
             f"  Average R: {r['avg_r']:+}",
             (f"History: the same plan on {h['cases']} real past days: {h['target']} target, {h['stop']} stop, {h['neither']} neither. Average R {h['avg_r']:+}."
              if h["enough"] else f"History: only {h['cases']} past cases, too few to judge."),
             r["verdict"], *r["notes"], "A simulation built from past prices, not a prediction."]
    return "\n".join(lines)


def selftest():
    up = [{"d": f"d{i}", "o": 100 + i, "h": 101 + i, "l": 99.5 + i, "c": 100 + i} for i in range(120)]
    r = run(up, 219, 210, 237, replays=500)
    assert r["target_pct"] > 90 and r["stop_pct"] == 0, r  # a steady climb reaches the target, never the stop
    assert run(up, 219, 210, 237, replays=500) == r  # same seed, same numbers
    assert run(up, 219, 230, 237).get("error")
    assert verdict(50, 50, 1).startswith("Close to a coin flip") and verdict(40, 60, 2).startswith("Leans toward the target")
    assert verdict(10, 90, 1).startswith("Strongly toward the stop")
    print("selftest ok")


if __name__ == "__main__":
    import argparse
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # sibling import under python -I
    import analyze
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("symbol", nargs="?")
    for a in ("entry", "stop", "target"):
        ap.add_argument(f"--{a}", type=float)
    ap.add_argument("--days", type=int, default=DAYS)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--csv")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); sys.exit()
    if not (a.symbol and a.entry and a.stop and a.target):
        ap.error("give SYMBOL --entry --stop --target")
    sym = a.symbol.upper()
    if a.csv:
        bars = analyze.load_csv(a.csv)
    elif sym in ("GOLD", "SILVER"):
        import metals
        bars = metals.bars(sym)[0]
    else:
        bars = analyze.fetch(sym, "2y")[0]
    res = run(bars, a.entry, a.stop, a.target, a.days, seed=a.seed)
    print(json.dumps(res) if a.json else text(res, sym))
