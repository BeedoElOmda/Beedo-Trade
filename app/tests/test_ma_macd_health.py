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


def test_switched_off_steps_do_not_count():
    from test_engine import wave
    bars = bars_from(wave(100, 0.4), vol_last=3000)
    on = engine.evaluate(analyze.report(bars, "T", "T"))
    assert on["signal"]["rung"] >= 2
    engine.OFF.update({4, 5, 8, 12})  # trend, moving averages, RSI and MACD off: only weak evidence is left
    off = engine.evaluate(analyze.report(bars, "T", "T"))
    assert all(s.get("off") for s in off["steps"] if s["n"] in (4, 5, 8, 12))
    assert off["steps"][4]["rung"] == on["steps"][4]["rung"]  # still shown as read
    assert off["signal"]["rung"] < on["signal"]["rung"]


def test_industry_health():
    up, down = (2, 1, 1, 1, "Finance", "Banks"), (1, -1, 2, 2, "Finance", "Brokers")
    rows = fundamentals.industries([up] * 4 + [down] * 3 + [(1, 0, 2, 2, "Energy", "Oil")])
    by = {r["industry"]: r for r in rows}
    assert by["Banks"]["label"] == "Healthy" and by["Brokers"]["label"] == "Weak" and by["Oil"]["label"] == "Too few stocks"
    assert rows[0]["industry"] == "Banks" and rows[-1]["industry"] == "Oil"


def test_frozen_price_feed_is_refused():
    flat = [dict(d=f"2026-01-{k:02d}", o=71.05, h=71.05, l=71.05, c=71.05, v=0) for k in range(1, 29)] * 3
    try:
        analyze.report(flat, "ORAS", "Orascom"); assert False
    except analyze.NoHistory as e:
        assert "frozen" in str(e)


def test_impact_shows_which_ticks_change_the_signal():
    from test_engine import wave
    rep = analyze.report(bars_from(wave(100, 0.4), vol_last=3000), "T", "T")
    base = engine.evaluate(rep)["signal"]["label"]
    imp = engine.impact(rep)
    assert imp and all(label != base for label in imp.values())
    for n, label in imp.items():  # each listed step really gives that signal when unticked
        engine.OFF.clear(); engine.OFF.add(n)
        assert engine.evaluate(rep)["signal"]["label"] == label
    engine.OFF.clear()
    assert engine.evaluate(rep)["signal"]["label"] == base  # impact() leaves the switches as they were


def test_snapshot_fallback_caps_at_alarm(monkeypatch):
    # A strong snapshot (every readable step bullish) must still stop at Alarm Buy, with the history steps "Not checked"
    vals = {"description": "Test Co", "open": 10, "high": 10.6, "low": 9.9, "close": 10.5, "close[1]": 10, "volume": 3000,
            "average_volume_10d_calc": 1000, "RSI": 62, "RSI[1]": 55, "MACD.macd": 0.3, "MACD.signal": 0.1,
            "MACD.macd[1]": 0.05, "MACD.signal[1]": 0.08, "price_52_week_low": 7, "price_52_week_high": 12,
            "Pivot.M.Classic.S1": 9.5, "Pivot.M.Classic.S2": 9, "Pivot.M.Classic.R1": 11.5, "Pivot.M.Classic.R2": 12}
    sma = {5: (10.3, 10.1), 9: (10.1, 10.0), 20: (9.8, 9.7)}
    def fake_scan(body):
        cols = body["columns"]
        return [[vals.get(c, sma.get(int(c[3:].split("[")[0]), (None, None))[1 if "[1]" in c else 0] if c.startswith("SMA") else None)
                 for c in cols]]
    monkeypatch.setattr(fundamentals, "_scan", fake_scan)
    rep = fundamentals.snapshot_report("TEST")  # 5/9/18 -> 5/9/20 (TradingView has no SMA18)
    assert rep["snapshot"] and rep["moving_averages"]["periods"] == [5, 9, 20] and "MA18" in rep["ma_note"]
    ev = engine.evaluate(rep)
    assert ev["signal"]["label"] == "Alarm Buy" and "snapshot" in ev["signal"]["why"]
    assert all(s["reading"].startswith("Not checked") for s in ev["steps"] if s["n"] in (4, 7, 9, 10, 11))
    assert ev["steps"][11]["label"] == "First Buy" and "10-day" in ev["steps"][5]["reading"]


def test_signal_is_the_score_of_ticked_steps():
    from test_engine import wave
    rep = analyze.report(bars_from(wave(100, 0.4), vol_last=3000), "T", "T")
    ev = engine.evaluate(rep)
    rungs = {s["n"]: s["rung"] for s in ev["steps"]}
    assert ev["score"] == sum(rungs[n] for n in engine.SCORED)
    for n in engine.SCORED:  # every step that isn't at Hold moves the score when unticked
        engine.OFF.clear(); engine.OFF.add(n)
        assert engine.evaluate(rep)["score"] == ev["score"] - rungs[n]
    engine.OFF.clear()
    assert [engine._score([{"rung": r}])["signal"]["label"] for r in (3, 2, 1, 0, -1, -2, -3)] == \
        ["Alarm Buy", "Alarm Buy", "Hold", "Hold", "Hold", "Alarm Sell", "Alarm Sell"]
    assert engine._score([{"rung": 3}, {"rung": 3}, {"rung": 3}])["signal"]["label"] == "Confirm Buy"
    assert engine._score([{"rung": 3}, {"rung": 2}])["signal"]["label"] == "First Buy"


def test_score_alerts():
    rows = {"AAA": {"symbol": "AAA", "close": 10, "rung": 2, "score": 6}, "BBB": {"symbol": "BBB", "close": 10, "rung": -1, "score": -3}}
    hits = engine.alerts(rows, [{"symbol": "AAA", "score": 5}, {"symbol": "BBB", "score": -5}, {"symbol": "BBB", "score": -3}], {})
    assert [h["symbol"] for h in hits] == ["AAA", "BBB"] and "+6" in hits[0]["text"] and "-3" in hits[1]["text"]


def test_weekly_signal():
    from test_engine import wave
    from beedo_app.main import Api
    daily = bars_from(wave(100, 0.4) * 6, vol_last=3000)  # about 2 years of trading days
    import datetime as dt
    for k, b in enumerate(daily):  # real calendar days, so the bars group into weeks
        b["d"] = str(dt.date(2024, 1, 1) + dt.timedelta(days=k))
    w = Api._weekly_signal(daily, "T")
    assert w and set(w) == {"label", "rung", "score"} and w["label"] == engine.RUNGS[w["rung"]]
    assert Api._weekly_signal(daily[:100], "T") is None  # 20 weeks: too few for the checklist

def test_skill_weekly_view():
    from test_engine import wave
    import datetime as dt
    daily = bars_from(wave(100, 0.4) * 6, vol_last=3000)
    for k, b in enumerate(daily):
        b["d"] = str(dt.date(2024, 1, 1) + dt.timedelta(days=k))
    w = analyze.weekly_view(daily)
    assert w["weeks"] == len(analyze.weekly_bars(daily)) and "alignment" in w["moving_averages"] and "now" in w["rsi14"]
    assert "note" in analyze.weekly_view(daily[:100])

def test_each_alert_is_notified_once_a_day(tmp_path, monkeypatch):
    from beedo_app import main
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "SETTINGS", tmp_path / "settings.json")
    sent = []
    monkeypatch.setattr(main, "NOTIFY", lambda h: sent.append(h["text"]))
    api = main.Api()
    a, b = {"symbol": "AAA", "text": "AAA: score +6"}, {"symbol": "BBB", "text": "BBB closed at 9"}
    api._notify_new([a]); api._notify_new([a, b]); api._notify_new([a, b])
    assert sent == ["AAA: score +6", "BBB closed at 9"]  # the 15-minute re-checks don't repeat them

def test_latest_sessions_come_from_tradingview(monkeypatch):
    import datetime as dt
    b = lambda d, c, v=1000: dict(d=d, o=c, h=c, l=c, c=c, v=v)
    yahoo = [b("2026-11-18", 126.0), b("2026-11-19", 127.5), b("2026-11-22", 125.01)]  # Wed, Thu, Sun; Monday missing
    tv = [125.01, 127.5, 125.01, 126.5, 4142327, 127.5, 127.5, 124.55, 125.01, 2128757, 127.5]  # Monday, Sunday, Thursday's close
    monkeypatch.setattr(fundamentals, "_scan", lambda body: [tv])
    tue_morning = dt.datetime(2026, 11, 24, 7, 52)
    assert analyze.session_days(tue_morning) == (dt.date(2026, 11, 23), dt.date(2026, 11, 22))
    assert analyze.session_days(dt.datetime(2026, 11, 27, 12, 0))[0] == dt.date(2026, 11, 26)  # Friday: Thursday's session
    out = analyze.with_latest(yahoo, "COMI", tue_morning)
    assert [x["d"] for x in out] == ["2026-11-18", "2026-11-19", "2026-11-22", "2026-11-23"]
    assert out[-1]["c"] == 126.5 and out[-1]["v"] == 4142327 and "partial" not in out[-1] and out[-2]["l"] == 124.55
    during = analyze.with_latest(yahoo[:2], "COMI", dt.datetime(2026, 11, 23, 11, 30))  # Monday 11:30, Yahoo up to Thursday
    assert during[-1]["d"] == "2026-11-23" and during[-1]["partial"]
    tv[-1] = 71.05  # the sources don't line up (a holiday, a frozen Yahoo feed): Yahoo's history is kept
    assert analyze.with_latest(yahoo, "COMI", tue_morning) == yahoo

def test_existing_installs_start_on_system_theme_once(tmp_path, monkeypatch):
    import json
    from beedo_app import main
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "SETTINGS", tmp_path / "settings.json")
    (tmp_path / "settings.json").write_text(json.dumps({"theme": "dark", "watchlist": ["COMI"]}))  # an older version's save
    assert main.Api().get_settings()["theme"] == "system"
    main.Api().save_settings({"theme": "light"})  # the user then picks Light: kept from now on
    assert main.Api().get_settings()["theme"] == "light" and main.Api().get_settings()["watchlist"] == ["COMI"]