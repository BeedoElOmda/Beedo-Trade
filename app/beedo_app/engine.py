"""Beedo-Trade signal engine: the course rules (skills/beedo-trade/SKILL.md + course-rules.md) as code.

Input is the dict from analyze.report(); output is the 11-step checklist, the overall signal,
the actions for a cash holder and a shareholder, and what would change the signal.
Rungs are integers: -3 Confirm Sell .. 0 Hold .. +3 Confirm Buy.
"""
RUNGS = {-3: "Confirm Sell", -2: "First Sell", -1: "Alarm Sell", 0: "Hold",
         1: "Alarm Buy", 2: "First Buy", 3: "Confirm Buy"}
NEAR = 1.5  # % distance that counts as "at" a level (course: price testing support/resistance)

ACTIONS = {  # course: trend tables, RSI table and pricing-zone table
    3: ("Buy the full position.", "Hold, or add on pullbacks."),
    2: ("Buy part of the position (e.g. half). Add the rest on Confirm Buy.", "Hold."),
    1: ("Get ready, but don't buy yet. Wait for First Buy.", "Hold."),
    0: ("Stay in cash and wait for a clear signal.", "Hold. In a sideways market the course says reduce or step out."),
    -1: ("Stay out.", "Get ready to sell: tighten your stop."),
    -2: ("Stay out.", "Sell part of the position (reduce)."),
    -3: ("Stay out.", "Sell."),
}


def _pct(a, b):
    return abs(a - b) / b * 100


def _step(n, name, reading, rung, note=""):
    return {"n": n, "name": name, "reading": reading, "rung": rung, "label": RUNGS[rung], "note": note}


def evaluate(r):
    close = r["last_bar"]["c"]
    lv, ts, ma, vol, rsi = r["levels"], r["trend_swings"], r["moving_averages"], r["volume"], r["rsi14"]
    steps = []

    # 1-2. Support / resistance: at a support = Alarm Buy, at a resistance = Alarm Sell
    def sr(n, name, block):
        s = (block["supports_nearest_first"] or [None])[0]
        res = (block["resistances_nearest_first"] or [None])[0]
        rung, txt = 0, f"support {s or '-'} | resistance {res or '-'}"
        if s and _pct(close, s) <= NEAR:
            rung = 1
        elif res and _pct(res, close) <= NEAR:
            rung = -1
        return _step(n, name, txt, rung)
    steps.append(sr(1, "Historical support & resistance", lv["historical_1y"]))
    steps.append(sr(2, "Recent support & resistance", lv["recent_90d"]))

    # 3. Price location (course pricing-zone table)
    ds, dr = lv["pct_to_nearest_recent_support"], lv["pct_to_nearest_recent_resistance"]
    if dr is not None and dr <= NEAR:
        zone, rung = "At resistance: don't buy; wait for breakout and retest", -1
    elif ds is not None and ds <= NEAR:
        zone, rung = "At support: best buy zone if a reversal confirms", 1
    elif ds is None:
        zone, rung = "Below all recent supports (breakdown)", -2
    elif dr is None:
        zone, rung = "Above all recent resistances (breakout)", 2
    else:
        zone, rung = f"Mid-range: {ds}% above support, {dr}% below resistance", 0
    steps.append(_step(3, "Price location", zone, rung))

    # 4. Trend: 2 steps identify, 3 confirm (higher highs AND higher lows, or the mirror)
    up = min(ts["higher_high_steps"], ts["higher_low_steps"])
    dn = min(ts["lower_high_steps"], ts["lower_low_steps"])
    if up >= 2:
        rung, txt = (3 if up >= 3 else 2), f"Uptrend: {up} higher highs and higher lows"
    elif dn >= 2:
        rung, txt = (-3 if dn >= 3 else -2), f"Downtrend: {dn} lower highs and lower lows"
    else:
        rung = 0
        txt = (f"No clear trend (HH {ts['higher_high_steps']}, HL {ts['higher_low_steps']}, "
               f"LH {ts['lower_high_steps']}, LL {ts['lower_low_steps']})")
    trend_rung = rung
    confirmed_down = ts["lower_low_steps"] >= 3
    confirmed_up = ts["higher_high_steps"] >= 3
    steps.append(_step(4, "Trend", txt, rung))

    # 5. Moving averages 5/9/18: state of the ladder (5x9 Alarm, 5x18 First, 9x18 Confirm)
    m5, m9, m18 = ma["MA5"], ma["MA9"], ma["MA18"]
    if m5 > m9 > m18: rung = 3
    elif m5 < m9 < m18: rung = -3
    elif m5 > m18 and m5 > m9: rung = 2
    elif m5 < m18 and m5 < m9: rung = -2
    elif m5 > m9: rung = 1
    elif m5 < m9: rung = -1
    else: rung = 0
    ma_rung = rung
    last_cross = max((e + [k] for k, evs in (("5x9", ma["alarm_crosses_5x9"]), ("5x18", ma["first_crosses_5x18"]),
                                             ("9x18", ma["confirm_crosses_9x18"])) for e in map(list, evs)),
                     default=None, key=lambda e: e[0])
    txt = f"MA5 {m5} | MA9 {m9} | MA18 {m18}: {ma['alignment']}"
    if last_cross:
        txt += f"; last cross {last_cross[2]} {last_cross[1]} on {last_cross[0]}"
    steps.append(_step(5, "Moving averages 5 / 9 / 18", txt, rung))

    # 6. Volume confirms the move (price up + volume up = buyers, price down + volume up = sellers)
    ratio = vol["ratio_vs_avg20"] or 0
    move = sum(d for _, d, _ in vol["last5"])
    if ratio >= 1.0 and move > 0: rung, txt = 1, "Rising price on above-average volume (buyers in control)"
    elif ratio >= 1.0 and move < 0: rung, txt = -1, "Falling price on above-average volume (sellers in control)"
    elif move < 0: rung, txt = 0, "Falling price on light volume (selling is fading)"
    else: rung, txt = 0, "Rising price on light volume (buying is fading)"
    steps.append(_step(6, "Volume", f"{txt}. Today {ratio}x the 20-day average.", rung))

    # 7. Reversal candles: one candle = Alarm; confirmed by the next candle = First
    c = r["candles_last3"]
    bull = lambda x: x["engulfing"] == "Bullish Engulfing" or x["shape"].startswith(("Hammer (", "Inverted Hammer ("))
    bear = lambda x: x["engulfing"] == "Bearish Engulfing" or x["shape"].startswith(("Hanging Man", "Shooting Star"))
    closes = [p for _, p in r["closes_last10"]]
    rung, txt = 0, f"Latest candle: {c[-1]['shape']}"
    if bull(c[-2]) and closes[-1] > closes[-2]:
        rung, txt = 2, f"{c[-2]['engulfing'] or c[-2]['shape']} on {c[-2]['date']}, confirmed by a higher close"
    elif bear(c[-2]) and closes[-1] < closes[-2]:
        rung, txt = -2, f"{c[-2]['engulfing'] or c[-2]['shape']} on {c[-2]['date']}, confirmed by a lower close"
    elif bull(c[-1]):
        rung, txt = 1, f"{c[-1]['engulfing'] or c[-1]['shape']} today: needs the next candle to confirm"
    elif bear(c[-1]):
        rung, txt = -1, f"{c[-1]['engulfing'] or c[-1]['shape']} today: needs the next candle to confirm"
    steps.append(_step(7, "Reversal candles", txt, rung))

    # 8. RSI (course RSI table) + divergence
    now, prev = rsi["now"], rsi["prev"]
    lo30, hi30 = rsi["min_max_30d"]
    rising = now > prev
    if now >= 70: rung = -1
    elif now <= 30: rung = 1
    elif now > 50: rung = 3 if rising else (-2 if hi30 >= 70 else 0)
    elif now < 50: rung = (2 if lo30 <= 30 else 0) if rising else -3
    else: rung = 0
    div = [d for d in rsi["divergence"] if d != "none detected"]
    if rung == 0 and div:
        rung = 1 if div[0].startswith("POSITIVE") else -1
    txt = f"RSI {now} ({'rising' if rising else 'falling'} from {prev}), zone {rsi['zone']}"
    if div:
        txt += f"; {div[0].split(':')[0].lower()} divergence"
    rsi_rung = rung
    steps.append(_step(8, "RSI (14)", txt, rung))

    # 9. Gaps: newest real gap still open
    gaps = r["gaps_30d"] if isinstance(r["gaps_30d"], list) else []
    open_gaps = [g for g in gaps if not g["filled_since"]]
    rung, txt, note = 0, "No open gaps in the last 30 days", ""
    if open_gaps:
        g = open_gaps[-1]
        strong = (g["vol_ratio"] or 0) >= 1.5
        rung = (2 if strong else 1) * (1 if g["dir"] == "UP" else -1)
        txt = f"Open gap {g['dir'].lower()} on {g['date']} ({g['from']} to {g['to']}), volume {g['vol_ratio']}x"
        note = "Check the chart: breakaway, continuation or exhaustion depends on where it sits in the trend."
    steps.append(_step(9, "Price gaps", txt, rung, note))

    # 10-11. Chart patterns are judged by eye on the swing points (marked on the chart)
    steps.append(_step(10, "Reversal patterns", "Look for head & shoulders, double/triple tops or bottoms on the marked swing points", 0,
                       "Judged on the chart; not scored automatically."))
    steps.append(_step(11, "Continuation patterns", "Look for ascending, descending or symmetrical triangles on the marked swing points", 0,
                       "Judged on the chart; not scored automatically."))

    return {"steps": steps, **_overall(steps, close, ds, dr, trend_rung, ma_rung, rsi_rung, now,
                                       confirmed_down, confirmed_up, lv, ma)}


def _overall(steps, close, ds, dr, trend_rung, ma_rung, rsi_rung, rsi_now, confirmed_down, confirmed_up, lv, ma):
    by = {s["n"]: s["rung"] for s in steps}
    support_buy = [n for n in (1, 2, 3, 6, 7, 9) if by[n] > 0] + ([8] if rsi_rung > 0 else [])
    support_sell = [n for n in (1, 2, 3, 6, 7, 9) if by[n] < 0] + ([8] if rsi_rung < 0 else [])

    def side(sign):
        sup = support_buy if sign > 0 else support_sell
        vol_ok = by[6] * sign > 0          # Confirm needs volume behind the move, not just "not against"
        trend_ok = trend_rung * sign >= 0  # and no identified trend in the opposite direction
        rsi_side = (rsi_now > 50) if sign > 0 else (rsi_now < 50)
        if ma_rung * sign == 3 and rsi_side and vol_ok and trend_ok:
            return 3
        rsi_turn = rsi_rung * sign >= 2  # RSI turning from the extreme, or crossing 50, in this direction
        if (ma_rung * sign >= 2 or rsi_turn) and len(sup) >= 1:
            return 2
        if ma_rung * sign >= 1 or len(sup) >= 1 or trend_rung * sign >= 2:
            return 1
        return 0

    buy, sell = side(1), side(-1)
    reason = []
    # Trend + MAs set the ceiling: candles/RSI alone can't turn a confirmed downtrend into a buy
    capped = {1: [], -1: []}  # why each side was held back; only the winning side's notes are shown
    if confirmed_down and ma_rung < 0 and buy > 1:
        buy = 1; capped[1].append("trend and moving averages are still down")
    if confirmed_up and ma_rung > 0 and sell > 1:
        sell = 1; capped[-1].append("trend and moving averages are still up")
    if buy == 3 and dr is not None and dr <= NEAR:
        buy = 2; capped[1].append("price is pressing against resistance")
    # Course: sideways market = cash holder waits for a breakout (step 3 shows a break out of the range)
    if trend_rung == 0 and abs(by[3]) < 2 and abs(ma_rung) < 3 and max(buy, sell) > 1:
        for sd in (1, -1): capped[sd].append("the market is moving sideways: wait for a breakout")
        buy, sell = min(buy, 1), min(sell, 1)
    # Course: price above the MA = no sell recommendation; below it = no buy recommendation
    above = close > ma["MA18"]
    if above and sell > 1:
        sell = 1; capped[-1].append("price is still above MA18")
    if not above and buy > 1:
        buy = 1; capped[1].append("price is still below MA18")

    if buy > sell: rung = buy
    elif sell > buy: rung = -sell
    elif buy == 1: rung = 1 if above else -1  # equally weak evidence: price's side of MA18 decides
    else:
        rung = 0
        if buy: reason.append("buy and sell evidence balance out")

    if rung: reason += capped[1 if rung > 0 else -1]
    cash, share = ACTIONS[rung]
    sideways = trend_rung == 0 and abs(ma_rung) <= 1
    if rung == 0 and not sideways:
        share = "Hold."
    nxt = _next_triggers(ma, lv, close)
    why = {3: "trend, moving averages, RSI and volume all agree upward",
           2: "an uptrend is starting but isn't confirmed yet",
           1: "early signs of a turn upward only",
           0: "no clear signal",
           -1: "early signs of a turn downward only",
           -2: "a downtrend is starting",
           -3: "trend, moving averages, RSI and volume all agree downward"}[rung]
    if reason:
        why += "; capped because " + " and ".join(reason)
    return {"signal": {"rung": rung, "label": RUNGS[rung], "why": why},
            "actions": {"cash": cash, "shareholder": share}, "next": nxt}


def _next_triggers(ma, lv, close):
    m5, m9, m18 = ma["MA5"], ma["MA9"], ma["MA18"]
    up, down = [], []
    if not m5 > m9: up.append("MA5 crossing above MA9 = Alarm Buy")
    if not m5 > m18: up.append("MA5 crossing above MA18 = First Buy")
    if not m9 > m18: up.append("MA9 crossing above MA18 = Confirm Buy")
    if not m5 < m9: down.append("MA5 crossing below MA9 = Alarm Sell")
    if not m5 < m18: down.append("MA5 crossing below MA18 = First Sell")
    if not m9 < m18: down.append("MA9 crossing below MA18 = Confirm Sell")
    s = (lv["recent_90d"]["supports_nearest_first"] or [None])[0]
    res = (lv["recent_90d"]["resistances_nearest_first"] or [None])[0]
    if res: up.append(f"a close above {res} on above-average volume = breakout")
    if s: down.append(f"a close below {s} = support broken")
    return {"up": up[:3], "down": down[:3]}


def trade_plan(r, cash=None, risk_pct=2.0):
    """Entry at the last close, stop just under the nearest recent support, target 2R (course: don't buy into resistance)."""
    close = r["last_bar"]["c"]
    sup = [s for s in r["levels"]["recent_90d"]["supports_nearest_first"] if s < close]
    res = r["levels"]["recent_90d"]["resistances_nearest_first"]
    if not sup:
        return {"error": "No recent support below the price to place a stop."}
    stop = round(sup[0] * 0.99, 2)
    risk = round(close - stop, 2)
    target = round(close + 2 * risk, 2)
    plan = {"entry": close, "stop": stop, "risk_per_share": risk, "risk_pct": round(risk / close * 100, 2),
            "target": target, "first_resistance": res[0] if res else None, "warnings": []}
    if res and res[0] < target:
        plan["warnings"].append(f"Resistance at {res[0]} comes before the target: take partial profit there if bearish candles appear.")
        if (res[0] - close) < risk:
            plan["warnings"].append("The first resistance is less than 1R away: poor risk-reward. The course says don't buy near resistance.")
    if cash:
        max_loss = cash * risk_pct / 100
        shares = int(min(max_loss // risk if risk > 0 else 0, cash // close))
        plan.update(shares=shares, cost=round(shares * close, 2), loss_at_stop=round(shares * risk, 2),
                    loss_pct_of_cash=round(shares * risk / cash * 100, 2))
    return plan
