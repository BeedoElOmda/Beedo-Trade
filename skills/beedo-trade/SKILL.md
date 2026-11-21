---
name: beedo-trade
description: Beedo-Trade analyses Egyptian Exchange (EGX) stocks with the user's own technical-analysis course method (support/resistance, 2H/2L trend, moving-average crossovers (5/9/18 by default, other periods on request), RSI zones and divergence, volume, reversal candles, gaps, chart patterns, MACD) and gives an Alarm / First / Confirm Buy or Sell signal, with separate actions for a cash holder and a shareholder. Use this skill whenever the user asks about an EGX or Egyptian stock (COMI, TMGH, SWDY, ETEL, EAST, FWRY, any 4-letter EGX code or a Cairo-listed company name), asks "should I buy/sell/hold X", wants a technical analysis, a buy or sell signal, entry/exit levels or a trade plan for Egyptian stocks, compares EGX stocks, or mentions Beedo, Beedo-Trade or "my course method", even if they don't name the skill.
---

# Beedo-Trade

Analyse an EGX stock the way the user's own course teaches, then turn the result into a clear signal and, if wanted, a trade plan. The user built this method in their MBA technical-analysis course; the value of this skill is applying *their* rules consistently, not general TA opinions.

The full rulebook is in `references/course-rules.md`. Read it before your first analysis in a conversation: the signal names, thresholds and role-based actions there are what the user expects to see.

## Tools this skill uses

| Need | Tool |
|---|---|
| Daily history + course indicators (fast/mid/slow MA crosses, RSI 14, MACD 12/26/9, swings, S/R, volume, candles, gaps) | `beedo_analyze`, or `python -I <skill-dir>/scripts/analyze.py SYMBOL` (see "Getting the price history" below for the fallbacks). Moving averages default to the course's 5 / 9 / 18; pass e.g. `ma="8,13,200"` (script: `--ma 8,13,200`) when the user wants other periods |
| Market health: EGX30 against its 50- and 200-day averages, breadth of all EGX stocks, and health per industry | `beedo_market_health`, or `python -I <skill-dir>/scripts/fundamentals.py --health` |
| Today's TradingView snapshot (close, RSI, pivots S1-S3/R1-R3, Bollinger, MACD) | `egx-mcp` tool `stock_data_egx` |
| Quick price only | `egx-mcp` tool `stock_price_egx` |
| Company fundamentals: Strong / Fair / Weak rating, the rules behind it, key ratios | `beedo_fundamentals`, or `python -I <skill-dir>/scripts/fundamentals.py SYMBOL` |
| Gold / silver in EGP per gram (24k, 21k, 18k), dollar rate, gold/silver ratio | `beedo_metals`, or `python -I <skill-dir>/scripts/metals.py`. If neither works: `egx-mcp` tools `gold_price`, `silver_price` |
| Odds that a buy plan reaches its target or its stop first (time machine) | `beedo_timemachine`, or `python -I <skill-dir>/scripts/timemachine.py SYMBOL --entry E --stop S --target T` |
| The course checklist on gold or silver | `beedo_analyze` or `analyze.py` with `GOLD` or `SILVER` as the symbol (EGP per gram) |
| Position size, when the user has set limits (max loss per trade, cash buffer, per-stock cap) | `trader-budget` skill, if installed (amounts in EGP) |
| Check a planned order against those limits | `trader-risk` skill, if installed |

The `trader-*` skills are optional: if they are not available, do the sizing and limit checks yourself with the same arithmetic. They were built for US markets. Use only their arithmetic. `trader-exit` assumes US intraday rules (opening-range stops, closing flat before 4 p.m. New York time), so do stop/target math yourself as described in step 6.

If the egx-mcp tools are not loaded in this session, the price history alone is enough for the analysis.

### Getting the price history (try in this order)
The indicators use two years of daily prices from Yahoo Finance (`COMI` → `COMI.CA`): the default 5 / 9 / 18 needs 60 trading days; a 200-day slow average needs at least 206.
1. **`beedo-trade` MCP server**, if its tools are loaded: `beedo_analyze` gives the same output as the script, and `beedo_history` gives the raw daily bars. Prefer it: it runs on the user's own computer, so it reaches Yahoo even when your sandbox can't.
2. **The script**: `python -I <skill-dir>/scripts/analyze.py SYMBOL`, or `uv run --no-project python <skill-dir>/scripts/analyze.py SYMBOL` if `python` is not on PATH. It uses only Python's standard library.
3. **A CSV of daily prices from the user**: `analyze.py --csv <file> SYMBOL`. It accepts the usual exports (Date, Open, High, Low, Close or Price, Volume; ISO or d/m/Y or m/d/Y dates; volumes like 1.2M). Ask for at least 60 trading days, ideally a year (206 or more if the user uses a 200-day slow average).
4. **Snapshot only** (TradingView's latest values). `beedo_analyze` and `analyze.py` switch to it by themselves when Yahoo has no history for the stock, or a frozen one (the same price with no trading for weeks, as with ORAS); you can also call `fundamentals.py --snapshot SYMBOL`. The result has `"snapshot": true`, the `reason`, and `not_checked`: the steps that need daily history (trend 4, candles 7, gaps 9, patterns 10 and 11, plus 2 and 3 when TradingView has no pivots). Step 1 comes from the 52-week low and high, step 2 from the monthly pivots, volume from the 10-day average, crosses from today against yesterday. If `ma_note` says a moving average was replaced (TradingView has no SMA18, so MA20 is used), say so. Mark the `not_checked` steps "Not checked", decide the signal from the rest, then **cap it at Alarm**, because the course never confirms without trend and MA history. Say clearly that it is a snapshot and that a CSV of daily prices (option 3) gives the full checklist. If no snapshot is available either, use `stock_data_egx` the same way.

What the errors mean:
- **"Could not reach Yahoo Finance"**: the network is blocked where the script ran, which is often your sandbox, not the user's PC. Tell the user that the local `beedo-trade` server fixes this. They can turn it on in their Claude Desktop settings, or re-run the Beedo-Trade installer to add it. Then go to option 3 or 4.
- **"CERTIFICATE_VERIFY_FAILED"** (mostly on a Mac): Python can't find root certificates. The scripts use the `certifi` bundle, or the Mac system bundle, automatically; if the error still appears, run the command with `SSL_CERT_FILE=/etc/ssl/cert.pem` in front of it, or install certifi (`uv pip install certifi`). It is not a network problem.
- **"Yahoo Finance has no price history"**: Yahoo doesn't carry that stock. This is common for smaller EGX companies, and nothing is wrong with the setup. The tools already fall back to option 4; offer option 3 (CSV) for the full checklist.
- **"The price data for X is frozen"**: Yahoo's feed for that stock stopped updating; same handling as above.

## Workflow

### 1. Pin down the stock and the user's position
- Use the 4-letter EGX code. If the user gave a company name, map it (e.g. CIB → COMI, Talaat Moustafa → TMGH, Elsewedy → SWDY, Telecom Egypt → ETEL, Eastern Company → EAST, Fawry → FWRY). If unsure, ask.
- Does the user already own it (shareholder) or have cash (cash holder)? If they didn't say, give both actions; don't stop to ask.

### 2. Collect data (run both in parallel)
- Get the price history and indicators (`beedo_analyze`, or `analyze.py SYMBOL`).
- Call `stock_data_egx` for the same symbol.
- Check that the two agree on the last close. If they differ, one source is stale: use the newer date and mention it.
- For a stock (not gold or silver), also get the company rating (`beedo_fundamentals`, or `fundamentals.py SYMBOL`). If it fails, carry on without it.
- Once per conversation, get the market health (`beedo_market_health`, or `fundamentals.py --health`): the market label and the row for the stock's industry go in the report. It is context only and never changes a rung.

### 3. Walk the course checklist
Go through the 12 steps in this order (the 11 course steps plus MACD), and give each step one rung: **Alarm Buy, First Buy, Confirm Buy, Hold, Alarm Sell, First Sell, Confirm Sell**. Write one line of evidence per step, using numbers.

1. **Historical S/R**: `levels.historical_1y`, period high/low.
2. **Recent S/R**: `levels.recent_90d`. As a second opinion, add TradingView's *Classic* monthly pivots (`Pivot.M.Classic.*`); ignore the Camarilla set, which is often inconsistent for EGX.
3. **Price location**: which pricing zone of the course table (before/at/below support, before/at/failed resistance). "At" ≈ within about 1.5%.
4. **Trend**: use the step counts in `trend_swings` (`higher_high_steps`, `lower_low_steps`, …). A step is one swing beating the previous one. Two steps up in both highs and lows identifies an uptrend; three confirms it. Same for down.
5. **Moving averages** (fast / mid / slow from `moving_averages.periods`, default 5 / 9 / 18): latest crossover of fast×mid (Alarm), fast×slow (First), mid×slow (Confirm), and its date; the MA order; the slow MA's slope. A newer cross overrides an older one.
6. **Volume**: today vs 20-day average, plus the price/volume combination over the last 5 days.
7. **Reversal candles**: the script's shape in its trend context. A reversal candle needs the next candle to confirm it, so a candle on the latest bar is only an Alarm.
8. **RSI**: zone, direction, recent crosses of 30/50/70, divergence.
9. **Gaps**: classify each real gap (breakaway / continuation / exhaustion / island) from where it sits in the trend, its volume and whether it was filled. Ask about dividends if a gap is large and sudden.
10. **Reversal patterns**: look at `swing_points_last_90d` for H&S, double/triple tops or bottoms. Only claim a pattern you can point to with dates and prices; otherwise write "none clear".
11. **Continuation patterns**: triangles from the same swing points (flat highs with rising lows, and so on). Same rule: only claim it with evidence.
12. **MACD 12 / 26 / 9** (`macd`): line above its signal = buy reading, below = sell reading. On the same side of zero it is **First** (above signal and above zero = First Buy; below signal and below zero = First Sell); on the other side of zero only **Alarm**. Mention whether the histogram is growing or shrinking and the last cross (`crosses_30d`). In step 4 below, MACD counts as supporting evidence only when it reads First.

**Steps the user leaves out.** The user can switch steps off (the desktop app has a tick box per step). If they ask to leave out steps, or say which ones they don't use, still show those steps with their reading, mark the rung "off", and leave them out of the score in step 4. Steps 10 and 11 are always judged by eye and never scored.

The script automates the arithmetic. The judgment calls (pattern shapes, gap type, which zone) are yours, and the course rules are the standard to use.

### 4. Decide the overall signal
The signal is a score, the same as the Beedo-Trade app (2.0 and later). Give each scored step (1-9 and 12, minus any the user left out) its rung: Confirm Buy +3, First Buy +2, Alarm Buy +1, Hold 0, Alarm Sell -1, First Sell -2, Confirm Sell -3. Add them up:
- **+9 or more** = Confirm Buy, **+5 to +8** = First Buy, **+2 to +4** = Alarm Buy, **-1 to +1** = Hold, and the mirror below zero for sells.
- With a TradingView snapshot (no price history) the steps it can't read score 0 and the signal stops at Alarm.

Then apply the course overrides: don't buy near resistance; in a sideways trend the shareholder reduces and the cash holder waits; in a "danger uptrend" (a sharp rise with no correction), warn against chasing.

Treat these overrides as warnings next to the signal, not changes to it. State the score in the signal line, e.g. "Alarm Buy: score +3 from 10 steps".

### 5. Report
Use this structure, in English (Arabic course terms in brackets are fine). Keep it tight: the user wants a decision, not an essay.

```
# Beedo-Trade: <SYMBOL> (<company>), close <price> EGP on <date>

**Signal: <rung>**: <one sentence why>

| | Action |
|---|---|
| Cash holder | ... |
| Shareholder | ... |

**Key levels:** support <s1>, <s2> · resistance <r1>, <r2>

**Company: <Strong / Fair / Weak> (<score>)**: <the main reasons, one line>. **Combined view:** <one sentence from the table below>

**Market: <Healthy / Mixed / Weak>** (EGX30 <above/below> its 50- and 200-day averages, <x>% of stocks above their 50-day) · **Industry <name>: <label>** (<y>% above 50-day, <n> stocks). Context only: a buy in a weak market or industry carries more risk.

## Checklist
| # | Step | Reading | Rung |
|---|---|---|---|
| 1 | Historical S/R | ... | ... |
...
| 11 | Continuation patterns | ... | ... |
| 12 | MACD 12/26/9 | ... | ... |

**What would change the signal:** <the next trigger up, e.g. "MA9 crossing above MA18 = Confirm Buy"; and the next trigger down, e.g. "close below 125.8 support = First Sell">

_Course-method analysis for learning and decision support, not investment advice. Check the live price and today's disclosures before trading._
```

### 6. Trade plan (only when the user wants to act, or asks for entry/stop/target)
If the signal is only Alarm or Hold, you may still give the plan, but label it **"ready for when <trigger> happens, not to act on today"**. That is what the user needs to prepare.

- **Entry**: the trigger level from "What would change the signal" (e.g. a close above resistance, or the day the fast MA crosses above the slow MA).
- **Stop**: just below the nearest support, or below the gap / neckline that triggered the signal. Risk per share = entry − stop.
- **Target**: 2 × risk above entry (2R). Then compare it with the resistances between entry and target:
  - If a resistance sits before 2R, name it as the first profit-taking zone (course: take partial profit at resistance on bearish candles).
  - If the first resistance is under about 1R away, say the risk-reward is poor. The course says don't buy near resistance.
- **Size**:
  - A First Buy starts a partial position (e.g. half). Add the rest on Confirm Buy.
  - From the user's cash, show shares, EGP cost, and EGP lost if the stop hits (also as % of their cash).
  - If the user has set limits (max loss per trade, cash buffer), use `trader-budget` and then `trader-risk`. If not, ask for their max loss per trade only if they want a firm size.
- **Gap risk**: a stop is a plan, not a guarantee; EGX can open below it.
- Claude does not place EGX orders; the user trades in their own broker app.
- **Time machine** (when the user asks "what are the odds", "replay this trade", "how often does this hit the target", or wants to test the plan): pass the plan's entry, stop and target to `beedo_timemachine` (or `timemachine.py`). It replays the next 20 trading days 10,000 times from the stock's own daily moves of the last two years, and checks the same plan on every real past day. Report, in this order: target first / stop first / neither, the price range after 20 days, the average R, the history line, then the verdict line exactly as printed, and the seed. A 2R plan only needs the target first about 1 time in 3 to break even, so never judge it by target-first vs stop-first alone: the verdict already weighs the R. If the history and the replays disagree, say so. Say once that it is a simulation from past prices, not a prediction: news, earnings and devaluations can do things those two years never did. EGX has no free intraday prices, so it works on whole days.

### 7. Company rating and combined view (stocks only)
The rating is a second opinion from standard fundamental rules. It is not part of the technical course, and it never changes the signal or the rung. Say that in one short clause when you show it. Leave the line out for gold and silver, and when no rating is available.

| Company | First or Confirm Buy | Hold or Alarm Buy | Any sell signal |
|---|---|---|---|
| Strong | Best setup | Watch: wait for a buy signal | Wait for the chart to turn |
| Fair | Acceptable: consider a smaller position | No edge right now | Stay out for now |
| Weak | Speculative: small size, or skip | Avoid | Avoid |

### 8. Gold and silver
`GOLD` and `SILVER` work as symbols: the checklist, signal and trade plan apply to the price in EGP per gram, and quantities are grams. These are international prices converted at the official dollar rate; Egyptian shop prices add a premium and workmanship fees, so say so. Steps that need a company (fundamentals) don't apply.

## Several stocks
To compare or scan several codes, run the script for each (in parallel), then give one summary table (symbol, close, trend, MA state, RSI, MACD, signal) before any per-stock detail the user asks for. For "which sectors are strong" or "how is the market", use `beedo_market_health` and show its industry table (healthiest first; industries with under 3 stocks have no label).

## Notes
- EGX trades Sunday to Thursday from 10:00 Cairo time. On a weekend, the "latest" bar is Thursday's close; say so.
- Yahoo and TradingView data can lag. Remind the user to confirm the live price before trading.
