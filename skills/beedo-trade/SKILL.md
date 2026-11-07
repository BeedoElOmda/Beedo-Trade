---
name: beedo-trade
description: Beedo-Trade analyses Egyptian Exchange (EGX) stocks with the user's own technical-analysis course method (support/resistance, 2H/2L trend, MA 5/9/18 crossovers, RSI zones and divergence, volume, reversal candles, gaps, chart patterns) and gives an Alarm / First / Confirm Buy or Sell signal, with separate actions for a cash holder and a shareholder. Use this skill whenever the user asks about an EGX or Egyptian stock (COMI, TMGH, SWDY, ETEL, EAST, FWRY, any 4-letter EGX code or a Cairo-listed company name), asks "should I buy/sell/hold X", wants a technical analysis, a buy or sell signal, entry/exit levels or a trade plan for Egyptian stocks, compares EGX stocks, or mentions Beedo, Beedo-Trade or "my course method", even if they don't name the skill.
---

# Beedo-Trade

Analyse an EGX stock the way the user's own course teaches, then turn the result into a clear signal and, if wanted, a trade plan. The user built this method in their MBA technical-analysis course; the value of this skill is applying *their* rules consistently, not general TA opinions.

The full rulebook is in `references/course-rules.md`. Read it before your first analysis in a conversation: the signal names, thresholds and role-based actions there are what the user expects to see.

## Tools this skill uses

| Need | Tool |
|---|---|
| Daily history + course indicators (MA 5/9/18 crosses, RSI 14, swings, S/R, volume, candles, gaps) | `python -I <skill-dir>/scripts/analyze.py SYMBOL` |
| Today's TradingView snapshot (close, RSI, pivots S1-S3/R1-R3, Bollinger, MACD) | `egx-mcp` tool `stock_data_egx` |
| Quick price only | `egx-mcp` tool `stock_price_egx` |
| Gold / silver price in EGP (for gold comparisons or a "move to gold" question) | `egx-mcp` tools `gold_price`, `silver_price` |
| Position size, when the user has set limits (max loss per trade, cash buffer, per-stock cap) | `trader-budget` skill, if installed (amounts in EGP) |
| Check a planned order against those limits | `trader-risk` skill, if installed |

The `trader-*` skills are optional: if they are not available, do the sizing and limit checks yourself with the same arithmetic. They were built for US markets. Use only their arithmetic. `trader-exit` assumes US intraday rules (opening-range stops, closing flat before 4 p.m. New York time), so do stop/target math yourself as described in step 6.

If `python` is not on PATH, run the script with `uv run --no-project python <skill-dir>/scripts/analyze.py SYMBOL` instead. The script needs only Python's standard library and pulls daily bars from Yahoo Finance (`COMI` → `COMI.CA`). If it fails (network, unknown symbol), say so, and fall back to `stock_data_egx` alone: you still have RSI, SMA5/10/20, pivots and today's candle, but no crossover history. Say which steps you could not check.

If the egx-mcp tools are not loaded in this session, the script alone is enough for the analysis.

## Workflow

### 1. Pin down the stock and the user's position
- Use the 4-letter EGX code. If the user gave a company name, map it (e.g. CIB → COMI, Talaat Moustafa → TMGH, Elsewedy → SWDY, Telecom Egypt → ETEL, Eastern Company → EAST, Fawry → FWRY). If unsure, ask.
- Does the user already own it (shareholder) or have cash (cash holder)? If they didn't say, give both actions; don't stop to ask.

### 2. Collect data (run both in parallel)
- Run `analyze.py SYMBOL`.
- Call `stock_data_egx` for the same symbol.
- Check that the two agree on the last close. If they differ, one source is stale: use the newer date and mention it.

### 3. Walk the course checklist
Go through the 11 steps in this order, and give each step one rung: **Alarm Buy, First Buy, Confirm Buy, Hold, Alarm Sell, First Sell, Confirm Sell**. Write one line of evidence per step, using numbers.

1. **Historical S/R**: `levels.historical_1y`, period high/low.
2. **Recent S/R**: `levels.recent_90d`. As a second opinion, add TradingView's *Classic* monthly pivots (`Pivot.M.Classic.*`); ignore the Camarilla set, which is often inconsistent for EGX.
3. **Price location**: which pricing zone of the course table (before/at/below support, before/at/failed resistance). "At" ≈ within about 1.5%.
4. **Trend**: use the step counts in `trend_swings` (`higher_high_steps`, `lower_low_steps`, …). A step is one swing beating the previous one. Two steps up in both highs and lows identifies an uptrend; three confirms it. Same for down.
5. **Moving averages**: latest crossover of 5×9 (Alarm), 5×18 (First), 9×18 (Confirm), and its date; the MA order; the MA18 slope. A newer cross overrides an older one.
6. **Volume**: today vs 20-day average, plus the price/volume combination over the last 5 days.
7. **Reversal candles**: the script's shape in its trend context. A reversal candle needs the next candle to confirm it, so a candle on the latest bar is only an Alarm.
8. **RSI**: zone, direction, recent crosses of 30/50/70, divergence.
9. **Gaps**: classify each real gap (breakaway / continuation / exhaustion / island) from where it sits in the trend, its volume and whether it was filled. Ask about dividends if a gap is large and sudden.
10. **Reversal patterns**: look at `swing_points_last_90d` for H&S, double/triple tops or bottoms. Only claim a pattern you can point to with dates and prices; otherwise write "none clear".
11. **Continuation patterns**: triangles from the same swing points (flat highs with rising lows, and so on). Same rule: only claim it with evidence.

The script automates the arithmetic. The judgment calls (pattern shapes, gap type, which zone) are yours, and the course rules are the standard to use.

### 4. Decide the overall signal
Combine the steps the way the course does: no single indicator decides alone.

**Trend and moving averages set the ceiling.** They are the backbone of the method; candles, RSI, volume and gaps are early evidence that can only move the signal *within* that ceiling:
- Confirmed downtrend (3 lower-low steps) *and* MA crosses still down → the strongest buy-side signal is **Alarm Buy**, however good the candles and RSI look. It upgrades to First Buy only once MA5 crosses above MA18 (or the trend count breaks).
- Mirror rule: confirmed uptrend with MA crosses up → at most **Alarm Sell** until MA5 crosses below MA18.

Within that ceiling:
- **Confirm Buy/Sell** needs the MA 9×18 cross (or 5>9>18 order) in that direction, RSI on the same side of 50, and supporting volume. Also, price must not be pressing against the level in the way (no Confirm Buy right under resistance).
- **First Buy/Sell**: the MA 5×18 cross, or RSI moving from the extreme toward 50, *plus* at least one supporting step (candle, S/R bounce/break, gap, divergence).
  - "From the extreme toward 50" means RSI touched ≤30 in the last 30 days and is now rising but below 50 (buy side), or the mirror for ≥70 (sell side). This is the course's "Up from 30% → 50%" row.
- **Alarm**: early signs only (5×9 cross, a single reversal candle, divergence, RSI at an extreme).
- **Hold**: the steps conflict, or the trend is sideways.

Then apply the course overrides: don't buy near resistance; in a sideways trend the shareholder reduces and the cash holder waits; in a "danger uptrend" (a sharp rise with no correction), warn against chasing.

State the deciding reason in the signal line, e.g. "Alarm Buy: bullish evidence, but trend and MAs still down".

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

## Checklist
| # | Step | Reading | Rung |
|---|---|---|---|
| 1 | Historical S/R | ... | ... |
...
| 11 | Continuation patterns | ... | ... |

**What would change the signal:** <the next trigger up, e.g. "MA9 crossing above MA18 = Confirm Buy"; and the next trigger down, e.g. "close below 125.8 support = First Sell">

_Course-method analysis for learning and decision support, not investment advice. Check the live price and today's disclosures before trading._
```

### 6. Trade plan (only when the user wants to act, or asks for entry/stop/target)
If the signal is only Alarm or Hold, you may still give the plan, but label it **"ready for when <trigger> happens, not to act on today"**. That is what the user needs to prepare.

- **Entry**: the trigger level from "What would change the signal" (e.g. a close above resistance, or the day MA5 crosses above MA18).
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

## Several stocks
To compare or scan several codes, run the script for each (in parallel), then give one summary table (symbol, close, trend, MA state, RSI, signal) before any per-stock detail the user asks for.

## Notes
- EGX trades Sunday to Thursday from 10:00 Cairo time. On a weekend, the "latest" bar is Thursday's close; say so.
- Yahoo and TradingView data can lag. Remind the user to confirm the live price before trading.
