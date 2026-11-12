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
