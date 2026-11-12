# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.6,<2"]  # mcp 2.x renamed FastMCP
# ///
"""Beedo-Trade as a standalone MCP server (for Claude Desktop and any MCP client).

Run:  uv run --script mcp_server.py
Tools: beedo_method (the course method), beedo_analyze (indicators for one EGX stock),
beedo_history (raw daily prices). It runs on the user's own computer, so it can reach Yahoo Finance
even when Claude's sandbox cannot.
"""
import json, sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze  # noqa: E402  (same folder)

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
def beedo_analyze(symbol: str) -> str:
    """Course indicators for one EGX stock from a year of daily prices: S/R levels, trend swing steps,
    MA 5/9/18 crossovers (Alarm/First/Confirm), volume vs 20-day average, reversal candles, RSI 14 zone and
    divergence, gaps. symbol: 4-letter EGX code such as COMI, TMGH, SWDY."""
    sym = symbol.strip().upper()
    try:
        bars, name = analyze.fetch(sym)
        return json.dumps(analyze.report(bars, sym, name), default=str)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def beedo_history(symbol: str, bars: int = 130) -> str:
    """Raw daily price history (date, open, high, low, close, volume in EGP), oldest first, for one EGX stock.
    Use it to inspect chart patterns, gaps or swings yourself. symbol: 4-letter EGX code. bars: 5 to 250."""
    sym = symbol.strip().upper()
    try:
        rows, _ = analyze.fetch(sym)
    except Exception as e:
        return f"Error: {e}"
    rows = rows[-max(5, min(bars, 250)):]
    return json.dumps({"symbol": sym, "currency": "EGP", "columns": ["date", "open", "high", "low", "close", "volume"],
                       "bars": [[b["d"], b["o"], b["h"], b["l"], b["c"], b["v"]] for b in rows]})

@mcp.prompt()
def beedo_trade_analysis(symbol: str, position: str = "unknown") -> str:
    """Analyse one EGX stock with the Beedo course method."""
    return (f"Analyse {symbol.upper()} with my Beedo-Trade course method. My position: {position} "
            "(cash holder, shareholder or unknown). Call beedo_method first, then beedo_analyze, "
            "and give the full report with the signal, both roles' actions and the 11-step checklist.")

if __name__ == "__main__":
    mcp.run()
