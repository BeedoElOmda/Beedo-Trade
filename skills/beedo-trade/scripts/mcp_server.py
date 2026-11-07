# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.6,<2"]  # mcp 2.x renamed FastMCP
# ///
"""Beedo-Trade as a standalone MCP server (for Claude Desktop and any MCP client).

Run:  uv run --script mcp_server.py
Tools: beedo_method (the course method), beedo_analyze (indicators for one EGX stock).
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
    body = body.replace("python -I <skill-dir>/scripts/analyze.py SYMBOL", "the beedo_analyze tool")
    return body + "\n\n---\n\n" + RULES.read_text(encoding="utf-8")

@mcp.tool()
def beedo_analyze(symbol: str) -> str:
    """Course indicators for one EGX stock from a year of daily prices: S/R levels, trend swing steps,
    MA 5/9/18 crossovers (Alarm/First/Confirm), volume vs 20-day average, reversal candles, RSI 14 zone and
    divergence, gaps. symbol: 4-letter EGX code such as COMI, TMGH, SWDY."""
    sym = symbol.strip().upper()
    try:
        bars, name = analyze.fetch(sym)
    except Exception as e:
        return f"Could not download prices for {sym}: {e}. Check the symbol is a valid EGX code."
    if len(bars) < 60:
        return f"Only {len(bars)} daily bars for {sym}; need 60+. Check the symbol."
    return json.dumps({"symbol": sym, "name": name, "bars": len(bars), **analyze.analyze(bars)}, default=str)

@mcp.prompt()
def beedo_trade_analysis(symbol: str, position: str = "unknown") -> str:
    """Analyse one EGX stock with the Beedo course method."""
    return (f"Analyse {symbol.upper()} with my Beedo-Trade course method. My position: {position} "
            "(cash holder, shareholder or unknown). Call beedo_method first, then beedo_analyze, "
            "and give the full report with the signal, both roles' actions and the 11-step checklist.")

if __name__ == "__main__":
    mcp.run()
