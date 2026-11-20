import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts")]
import timemachine  # noqa: E402


def bars(closes):
    return [{"d": f"d{i}", "o": c, "h": c * 1.01, "l": c * 0.99, "c": c} for i, c in enumerate(closes)]


def test_selftest():
    timemachine.selftest()


def test_falling_stock_hits_the_stop():
    r = timemachine.run(bars([200 - i for i in range(120)]), 81, 77, 89, replays=500)
    assert r["stop_pct"] > 90 and r["verdict"].startswith("Strongly toward the stop")
    assert r["history"]["stop"] > r["history"]["target"]


def test_history_uses_only_the_given_days_and_skips_open_cases():
    b = bars([100] * 80)  # flat: neither side is ever reached
    h = timemachine.history(b, 100, 95, 110, days=20, starts=[10, 70])
    assert h == {"target": 0, "stop": 0, "neither": 1, "cases": 1, "enough": False, "avg_r": 0.0}  # day 70 has <20 days after it


def test_gap_below_the_stop_counts_as_the_stop():
    assert timemachine._walk([(90, 91, 89, 90)], stop=95, target=110) == ("stop", 90)
    assert timemachine._walk([(100, 111, 94, 105)], stop=95, target=110)[0] == "stop"  # touched both: the stop
