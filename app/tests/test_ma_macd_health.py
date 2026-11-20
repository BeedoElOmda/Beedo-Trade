"""Moving averages you choose, MACD and market health (no network). Run: uv run pytest -q"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
import analyze, fundamentals
from beedo_app import engine
from beedo_app.main import _valid_ma
from test_engine import bars_from


def test_chosen_moving_averages_drive_the_signal():
    old = analyze.MA
    try:
        analyze.MA = (8, 13, 200)
        closes = [100 + k * 0.2 for k in range(260)]
        assert analyze.min_bars() == 206
        r = engine.evaluate(analyze.report(bars_from(closes), "T", "T"))
        step = r["steps"][4]
        assert step["name"] == "Moving averages 8 / 13 / 200" and step["reading"].startswith("MA8 ")
        assert step["rung"] == 3  # steady rise: 8 > 13 > 200
        try:
            analyze.report(bars_from(closes[:150]), "T", "T"); assert False
        except analyze.NoHistory as e:
            assert "206" in str(e)
    finally:
        analyze.MA = old


def test_macd_is_step_12():
    rise = engine.evaluate(analyze.report(bars_from([100 + k * 0.5 + (k % 3) * 0.2 for k in range(120)]), "T", "T"))["steps"]
    fall = engine.evaluate(analyze.report(bars_from([200 - k * 0.5 - (k % 3) * 0.2 for k in range(120)]), "T", "T"))["steps"]
    assert len(rise) == 12 and rise[11]["name"] == "MACD (12 / 26 / 9)"
    assert rise[11]["rung"] > 0 and fall[11]["rung"] < 0


def test_valid_ma():
    assert _valid_ma(["8", 13, 200]) == [8, 13, 200]
    assert _valid_ma([13, 8, 200]) is None and _valid_ma([1, 2, 3]) is None and _valid_ma([5, 9, 300]) is None and _valid_ma("x") is None


def test_macd():
    line, sig, hist = analyze.macd([100 + k for k in range(60)])
    assert line[24] is None and line[25] is not None and sig[32] is None and sig[33] is not None
    assert abs(line[-1] - 7.0) < 0.01 and abs(hist[-1]) < 0.01  # straight line: EMA12 - EMA26 = 7, signal catches up


def test_market_health():
    assert fundamentals.health((110, 1, 100, 90, 60), [(2, 1, 1, 1)] * 7 + [(1, -1, 2, 2)] * 3)["label"] == "Healthy"
    assert fundamentals.health((80, -1, 100, 90, 40), [(1, -1, 2, 2)] * 7)["label"] == "Weak"
    h = fundamentals.health((95, 0, 100, 90, 50), [(2, 1, 1, 1)] * 5 + [(1, -1, 2, 2)] * 5)
    assert h["label"] == "Mixed" and h["above_sma50_pct"] == 50 and (h["advancers"], h["decliners"]) == (5, 5)
