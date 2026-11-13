"""Fundamentals rating tests on made-up companies (no network)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "beedo-trade" / "scripts"))
import fundamentals as F

def co(symbol, **kw):
    base = dict(symbol=symbol, name=symbol, sector="Process Industries", industry="Chemicals", close=10, market_cap=1e9,
                pe=None, pb=None, roe=None, net_margin=None, debt_to_equity=None, eps_growth=None, revenue_growth=None, dividend_yield=None)
    return {**base, **kw}

PEERS = [co(f"P{i}", pe=12, pb=2.5, roe=14, net_margin=8, debt_to_equity=0.8, eps_growth=15) for i in range(6)]

def rate(row):
    return F.rate(row, PEERS + [row])

def test_strong_company():
    q = rate(co("GOOD", pe=7, pb=1.2, roe=25, net_margin=18, debt_to_equity=0.3, eps_growth=35, dividend_yield=5))["quality"]
    assert q["label"] == "Strong" and q["score"] >= 70

def test_weak_company():
    q = rate(co("BAD", pe=-3, pb=6, roe=2, net_margin=1, debt_to_equity=2.5, eps_growth=-20))["quality"]
    assert q["label"] == "Weak"

def test_not_enough_data():
    q = rate(co("THIN", pb=1.0, dividend_yield=3))["quality"]
    assert q["label"] == "Not enough data" and q["level"] is None

def test_banks_skip_margin_and_debt_rules():
    r = rate(co("BANK", industry="Regional Banks", sector="Finance", pe=6, pb=1.1, roe=30, eps_growth=25, net_margin=50, debt_to_equity=0.4))
    keys = {x["key"] for x in r["rules"]}
    assert r["bank"] and "net_margin" not in keys and "debt_to_equity" not in keys and r["quality"]["label"] == "Strong"

def test_peer_medians_use_industry_first():
    p = F.peer_medians(co("X", pe=9), PEERS)
    assert p["pe"] == {"median": 12, "group": "industry"}

def test_verdict_matrix():
    assert F.verdict(2, 3)["tone"] == "good"
    assert F.verdict(0, 3)["text"].startswith("Speculative")
    assert F.verdict(2, -2)["tone"] == "warn"
    assert F.verdict(None, 2)["tone"] == "neutral"
