# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.6,<2"]  # mcp 2.x renamed FastMCP
# ///
"""Beedo-Trade as a standalone MCP server (for Claude Desktop and any MCP client).

Run:  uv run --script mcp_server.py
Tools: beedo_method (the course method), beedo_analyze (indicators for one EGX stock, GOLD or SILVER),
beedo_history (raw daily prices), beedo_fundamentals (company rating), beedo_metals (gold and silver in EGP), beedo_timemachine (odds that a plan hits its target or stop first),
beedo_market_health (EGX30, market breadth and health per industry). It runs on the user's own computer, so it can reach Yahoo Finance
even when Claude's sandbox cannot.
"""
import json, sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze, dividends, fundamentals, metals, timemachine  # noqa: E402  (same folder)
import threading  # noqa: E402
_ma_lock = threading.Lock()


def _bars(sym):
    """Daily bars and a name: EGP per gram for GOLD / SILVER, Yahoo Finance for EGX codes."""
    return metals.bars(sym) if sym in metals.METALS else analyze.fetch(sym)

SKILL = HERE.parent / "SKILL.md"
RULES = HERE.parent / "references" / "course-rules.md"

mcp = FastMCP("beedo-trade", instructions=(
    "Beedo-Trade analyses Egyptian Exchange (EGX) stocks with the user's own technical-analysis course. "
    "For any question about an EGX stock (buy/sell/hold, signal, entry/stop/target), first call beedo_method "
    "once per conversation and follow it, then call beedo_analyze for each symbol. "
    "Pair it with the egx-mcp server's stock_data_egx for TradingView pivots if available."))

@mcp.tool()
def beedo_method() -> str:
    """The Beedo-Trade workflow, report format and full course rulebook. Call once before analysing EGX stocks."""
    # The skill's frontmatter is for Claude Code's skill loader; the body is the method.
    body = SKILL.read_text(encoding="utf-8").split("---", 2)[-1]
    return body + "\n\n---\n\n" + RULES.read_text(encoding="utf-8")

@mcp.tool()
def beedo_analyze(symbol: str, ma: str = "5,9,18") -> str:
    """Course indicators for one EGX stock from two years of daily prices: S/R levels, trend swing steps,
    fast/mid/slow moving-average crossovers (Alarm/First/Confirm), volume vs 20-day average, reversal candles,
    RSI 14 zone and divergence, gaps, MACD 12/26/9 (step 12). symbol: 4-letter EGX code such as COMI, TMGH, SWDY,
    or GOLD / SILVER (EGP per gram, international price at the official dollar rate).
    ma: fast,mid,slow moving averages, default "5,9,18" (the course's own); e.g. "8,13,200" for longer ones."""
    sym = symbol.strip().upper()
    try:
        periods = tuple(int(x) for x in ma.split(","))
        if len(periods) != 3 or not 2 <= periods[0] < periods[1] < periods[2] <= 250:
            return "Error: ma needs three whole numbers, fast < mid < slow, 2 to 250, e.g. 5,9,18"
        with _ma_lock:  # analyze.MA is module state; one analysis at a time keeps each call's periods
            analyze.MA = periods
            try:
                bars, name = _bars(sym)
                return json.dumps({**analyze.report(bars, sym, name), "weekly": analyze.weekly_view(bars)}, default=str)
            except analyze.NoHistory as e:  # no or frozen Yahoo history: TradingView snapshot ("snapshot": true)
                if sym in metals.METALS:
                    raise
                return json.dumps(fundamentals.snapshot_report(sym, str(e)), default=str)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def beedo_market_health() -> str:
    """Market health from TradingView's end-of-day data: EGX30 against its 50- and 200-day averages, the share of all
    EGX stocks above their 50- and 200-day averages, advancers and decliners, a Healthy / Mixed / Weak label, and the
    same breadth for every industry (healthiest first; under 3 stocks = no label). Context for a signal, not a rung."""
    try:
        return json.dumps(fundamentals.market_health(), default=str)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def beedo_history(symbol: str, bars: int = 130) -> str:
    """Raw daily price history (date, open, high, low, close, volume in EGP), oldest first, for one EGX stock.
    Use it to inspect chart patterns, gaps or swings yourself. symbol: 4-letter EGX code. bars: 5 to 250."""
    sym = symbol.strip().upper()
    try:
        rows, _ = _bars(sym)
    except Exception as e:
        return f"Error: {e}"
    rows = rows[-max(5, min(bars, 250)):]
    return json.dumps({"symbol": sym, "currency": "EGP", "columns": ["date", "open", "high", "low", "close", "volume"],
                       "bars": [[b["d"], b["o"], b["h"], b["l"], b["c"], b["v"]] for b in rows]})

@mcp.tool()
def beedo_fundamentals(symbol: str) -> str:
    """Company rating for one EGX stock: Strong / Fair / Weak with a score, each rule (P/E, P/B, return on equity,
    margin, debt, growth, dividend) with its value and reason, the peer medians it was compared with, and 27 key
    figures. Data: TradingView, last 12 months of reported results. A second opinion, not part of the technical course."""
    try:
        return json.dumps(fundamentals.for_symbol(symbol.strip().upper()), default=str)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def beedo_metals() -> str:
    """Gold (24k, 21k, 18k) and silver in EGP per gram, per ounce in USD and EGP, the official USD/EGP rate and the
    gold/silver ratio. International prices: Egyptian shop prices add a local premium."""
    try:
        return json.dumps(metals.summary())
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def beedo_dividends(symbol: str) -> str:
    """Dividend history of one EGX stock over the last 5 years (Yahoo Finance): cash dividends and bonus shares (stock
    dividends), Cash / Stock / Both, the usual month, the cash yield of the last 12 months, and the payout to expect next.
    The expected payout is a pattern from history, not an announcement: the company's general assembly decides."""
    try:
        return dividends.text(dividends.for_symbol(symbol.strip().upper()))
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def beedo_timemachine(symbol: str, entry: float, stop: float, target: float, days: int = 20) -> str:
    """Time machine for a buy plan: 10,000 replays of the next `days` trading days built from the stock's own daily
    moves of the last two years, giving the odds of target first, stop first or neither, the average R, the price
    range after `days` days and a verdict that weighs the target's R; plus the same plan on every real past day.
    Make the plan first (workflow step 6), then pass its entry, stop and target. Seed 19, so runs repeat exactly.
    symbol: EGX code, or GOLD / SILVER."""
    sym = symbol.strip().upper()
    try:
        bars = metals.bars(sym)[0] if sym in metals.METALS else analyze.fetch(sym, "2y")[0]
        return timemachine.text(timemachine.run(bars, entry, stop, target, max(5, min(days, 60))), sym)
    except Exception as e:
        return f"Error: {e}"

@mcp.prompt()
def beedo_trade_analysis(symbol: str, position: str = "unknown") -> str:
    """Analyse one EGX stock with the Beedo course method."""
    return (f"Analyse {symbol.upper()} with my Beedo-Trade course method. My position: {position} "
            "(cash holder, shareholder or unknown). Call beedo_method first, then beedo_analyze, "
            "and give the full report with the signal, both roles' actions and the 12-step checklist.")

if __name__ == "__main__":
    mcp.run()
