"""Engine tests on synthetic price paths (no network). Run: uv run pytest -q"""
import math, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
import analyze
from beedo_app import engine


def bars_from(closes, vol=1000, vol_last=None):
    out = []
    for k, c in enumerate(closes):
        o = closes[k - 1] if k else c
        v = vol_last if (vol_last and k == len(closes) - 1) else vol
        out.append(dict(d=f"2026-{1 + k // 28:02d}-{1 + k % 28:02d}", o=o, h=max(o, c) * 1.005, l=min(o, c) * 0.995, c=c, v=v))
    return out


def run(closes, **kw):
    return engine.evaluate(analyze.report(bars_from(closes, **kw), "TEST", "Test"))


def wave(base, slope, n=150, amp=3.0, period=12):
    return [round(base + slope * k + amp * math.sin(2 * math.pi * k / period), 2) for k in range(n)]


def test_steady_uptrend_is_a_buy():
    out = run(wave(100, 0.4), vol_last=3000)
    assert out["signal"]["rung"] >= 2, out["signal"]
    assert out["actions"]["cash"].startswith(("Buy", "Buy part"))
    assert len(out["steps"]) == 11


def test_steady_downtrend_is_a_sell():
    out = run(wave(160, -0.4), vol_last=3000)
    assert out["signal"]["rung"] <= -2, out["signal"]
    assert out["actions"]["shareholder"].startswith(("Sell", "Sell part"))


def test_flat_market_is_not_a_confirm():
    out = run(wave(100, 0.0, amp=1.0))
    assert abs(out["signal"]["rung"]) <= 1, out["signal"]


def test_trade_plan_math():
    r = analyze.report(bars_from(wave(100, 0.4)), "TEST", "Test")
    p = engine.trade_plan(r, cash=50_000, risk_pct=2)
    assert "error" not in p
    assert p["stop"] < p["entry"] < p["target"]
    assert abs((p["target"] - p["entry"]) - 2 * p["risk_per_share"]) < 0.02
    assert p["loss_at_stop"] <= 50_000 * 0.02 + 1e-6 and p["cost"] <= 50_000


def test_every_step_has_a_valid_rung():
    for closes in (wave(100, 0.4), wave(160, -0.4), wave(100, 0)):
        for s in run(closes)["steps"]:
            assert s["rung"] in engine.RUNGS and s["label"] == engine.RUNGS[s["rung"]]


def test_weekly_groups_by_calendar_week():
    days = [("2026-01-05", 10), ("2026-01-06", 12), ("2026-01-09", 11), ("2026-01-12", 13)]
    w = engine.weekly([{"d": d, "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 5} for d, c in days])
    assert [(x["d"], x["o"], x["h"], x["l"], x["c"], x["v"]) for x in w] == [("2026-01-05", 10, 13, 9, 11, 15), ("2026-01-12", 13, 14, 12, 13, 5)]


def test_backtest_buys_on_first_buy_and_sells_on_first_sell():
    bars = [{"d": f"d{i}", "o": c, "h": c, "l": c, "c": c, "v": 1} for i, c in enumerate([10] * 60 + [10, 12, 15, 9])]
    rungs = iter([0, 2, 3, -2, 0])  # one per day from bar 60: hold, buy at 10, hold, sell at 15, nothing
    real = engine.evaluate
    engine.evaluate = lambda rep: {"signal": {"rung": next(rungs)}}
    try:
        r = engine.backtest(bars, lambda b: b)
    finally:
        engine.evaluate = real
    assert [(t["buy"], t["sell"], t["pct"], t["open"]) for t in r["trades"]] == [(10, 15, 50.0, False)]
    assert r["method_pct"] == 50.0 and r["wins"] == 1 and r["hold_pct"] == -10.0


def test_alerts_price_levels_and_signal_changes():
    rows = {"COMI": {"symbol": "COMI", "close": 100, "rung": 2}, "TMGH": {"symbol": "TMGH", "close": 50, "rung": 0}}
    hits = engine.alerts(rows, [{"symbol": "COMI", "above": 95, "below": 80}, {"symbol": "TMGH", "below": 50}, {"symbol": "GONE", "above": 1}],
                         {"COMI": 1, "TMGH": 0})
    assert [(h["symbol"], h["kind"]) for h in hits] == [("COMI", "above"), ("TMGH", "below"), ("COMI", "signal")]
    assert "Alarm Buy to First Buy" in hits[2]["text"]


def test_portfolio_profit_and_totals():
    rows = {"COMI": {"symbol": "COMI", "name": "CIB", "close": 120, "date": "d", "rung": 2, "label": "First Buy", "action": "Hold."},
            "BAD": {"symbol": "BAD", "error": "no prices"}}
    p = engine.portfolio([{"symbol": "COMI", "qty": 10, "price": 100}, {"symbol": "BAD", "qty": 1, "price": 5}], rows)
    assert (p["cost"], p["value"], p["pl"], p["pl_pct"]) == (1000, 1200, 200, 20.0)
    assert p["rows"][0]["pl_pct"] == 20.0 and p["rows"][1]["error"] == "no prices"
