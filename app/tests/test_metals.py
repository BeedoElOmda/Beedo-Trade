"""Gold/silver conversion tests (no network)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
import metals


def bar(d, c):
    return {"d": d, "o": c, "h": c, "l": c, "c": c, "v": 1}


def test_converts_ounce_usd_to_gram_egp_with_that_days_rate():
    usd = [bar("2026-01-01", 100), bar("2026-01-02", 200), bar("2026-01-05", 300)]
    fx = [bar("2026-01-01", 50), bar("2026-01-02", 60)]  # no rate on 01-05: the last known one (60) applies
    out = metals.to_egp_per_gram(usd, fx)
    k = metals.OUNCE_GRAMS
    assert [b["c"] for b in out] == [round(100 * 50 / k, 2), round(200 * 60 / k, 2), round(300 * 60 / k, 2)]


def test_days_before_the_first_rate_are_skipped():
    out = metals.to_egp_per_gram([bar("2026-01-01", 100), bar("2026-01-02", 100)], [bar("2026-01-02", 50)])
    assert [b["d"] for b in out] == ["2026-01-02"]


def test_summary_karats(monkeypatch):
    data = {"EGP=X": [bar("2026-01-01", 50), bar("2026-01-02", 50)],
            "GC=F": [bar("2026-01-01", 3000), bar("2026-01-02", 3110.34768)],
            "SI=F": [bar("2026-01-01", 40), bar("2026-01-02", 41)]}
    monkeypatch.setattr(metals, "_fetch", lambda t: data[t])
    s = metals.summary()
    assert s["gold"]["egp_gram"] == 5000.0                      # 3110.35 USD/oz * 50 / 31.10 g
    assert s["gold"]["karats"] == {"24k": 5000.0, "21k": 4375.0, "18k": 3750.0}
    assert s["gold_silver_ratio"] == round(3110.34768 / 41, 1)
