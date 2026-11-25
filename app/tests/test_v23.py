"""2.3: back-test settings, dividends, my trading rules and the example plan (no network)."""
import datetime as dt, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
import dividends
from beedo_app import engine


def fake_bars(n=80):
    return [dict(d=f"2026-01-{i:03d}", o=100 + i, h=101 + i, l=99 + i, c=100 + i, v=1000) for i in range(n)]


def test_backtest_levels_and_fees(monkeypatch):
    # signal: buy at day 65 (rung 2), sell at day 75 (rung -2); an Alarm (rung 1) on day 62
    plan = {62: 1, 65: 2, 75: -2}
    monkeypatch.setattr(engine, "rungs", lambda bars, report, start=None: [(i, plan.get(i, 0)) for i in range(61, len(bars) + 1)])
    bars = fake_bars()
    course = engine.backtest(bars, None)
    assert [t["buy_date"] for t in course["trades"]] == [bars[64]["d"]] and course["settings"]["buy_at"] == 2
    early = engine.backtest(bars, None, buy_at=1)  # any buy: enters on the Alarm
    assert early["trades"][0]["buy_date"] == bars[61]["d"]
    strict = engine.backtest(bars, None, buy_at=3)  # Confirm only: never buys
    assert strict["trades"] == []
    with_fees = engine.backtest(bars, None, fee_pct=1)
    assert with_fees["trades"][0]["pct"] < course["trades"][0]["pct"] and with_fees["hold_pct"] < course["hold_pct"]


def test_dividend_summary_from_history():
    cash = [("2022-04-10", 1.0), ("2023-04-12", 1.2), ("2024-04-08", 1.5), ("2025-04-09", 1.5), ("2026-04-07", 1.5)]
    r = dividends.summarize(cash, [("2025-12-01", 11, 10), ("2018-09-01", 10, 1)], dt.date(2026, 11, 25), close=30)
    assert r["kind"] == "Both" and r["expected"]["month"] == "2027-04" and r["last_bonus"]["one_for"] == 10
    assert dividends.bonus_ratio(10, 1) is None  # a real split is not a dividend


def test_risk_profile_scores_and_safety_cap():
    assert engine.risk_profile([1, 2, 1, 2, 1, 2])["label"] == "Careful"
    assert engine.risk_profile([3, 3, 3, 3, 3, 3])["label"] == "Balanced"
    bold = engine.risk_profile([4, 4, 4, 4, 4, 4])
    assert bold["label"] == "Bold" and bold["rules"]["risk_pct"] == 3 and not bold["capped"]
    capped = engine.risk_profile([4, 1, 4, 4, 4, 4])  # money needed within a year
    assert capped["label"] == "Careful" and capped["capped"]
    assert engine.risk_profile([4, 4, 4, 4, 4, 1])["label"] == "Careful"  # most of the savings
    assert engine.risk_profile([1, 2, 3]).get("error")


def cand(sym, sector, rung=2, q=1, entry=100.0, stop=95.0, dy=None):
    return {"symbol": sym, "name": sym, "sector": sector, "rung": rung, "label": "First Buy", "quality": "Fair",
            "quality_level": q, "quality_score": 60, "entry": entry, "stop": stop, "dividend_yield": dy}


def test_example_plan_keeps_cash_and_caps():
    rules = dict(engine.RULES["Balanced"])  # 2% risk, 15% per stock, 8 stocks, 20% cash, 30% per sector
    cands = [cand(f"S{i}", "Finance" if i < 4 else f"Sector{i}") for i in range(12)] + [cand("WEAK", "X", q=0), cand("ALARM", "Y", rung=1)]
    p = engine.build_plan(100_000, rules, cands)
    syms = [r["symbol"] for r in p["rows"]]
    assert "WEAK" not in syms and "ALARM" not in syms  # quality and signal rules
    assert len(p["rows"]) <= 8 and p["cash"] >= 20_000 - 1  # number of stocks and cash kept aside
    assert all(r["cost"] <= 15_000 for r in p["rows"])  # max in one stock
    assert sum(r["cost"] for r in p["rows"] if r["sector"] == "Finance") <= 30_000  # max per sector
    assert all(r["loss_at_stop"] <= 2_000 for r in p["rows"])  # 2% risk per trade
    assert engine.build_plan(100_000, rules, [])["rows"] == []  # nothing qualifies: all cash
