# Beedo-Trade

A Claude skill that analyses **Egyptian Exchange (EGX)** stocks with a structured technical-analysis method, the Beedo course checklist, and gives a clear signal: **Alarm / First / Confirm Buy or Sell**, or **Hold**. It gives separate advice for someone holding cash and someone who already owns the stock.

Ask Claude things like:

- "Analyse COMI with my course method."
- "I have 50,000 EGP. Should I buy TMGH? Give me entry, stop and target."
- "Compare SWDY, ETEL and EAST. Which has the best setup?"

## What it checks (11 steps)

1. Historical support and resistance
2. Recent support and resistance
3. Price location (which pricing zone)
4. Trend: 2 highs and 2 lows identify it, 3 confirm it
5. Moving averages 5 / 9 / 18: crossover of 5×9 = Alarm, 5×18 = First, 9×18 = Confirm
6. Volume against its 20-day average
7. Reversal candles: hammer, inverted hammer, hanging man, shooting star, doji, engulfing
8. RSI 14 (Wilder): zones 30 / 50 / 70 and divergence
9. Price gaps: breakaway, continuation, exhaustion, island
10. Reversal patterns: head and shoulders, double and triple tops or bottoms
11. Continuation patterns: triangles

The full rules are in [`skills/beedo-trade/references/course-rules.md`](skills/beedo-trade/references/course-rules.md).

## What's inside

| Part | What it does |
|---|---|
| `skills/beedo-trade/SKILL.md` | The method and the report format Claude follows |
| `skills/beedo-trade/scripts/analyze.py` | Downloads a year of daily prices (Yahoo Finance, e.g. `COMI.CA`) and calculates the MA crossovers, RSI, swing points, levels, volume, candles and gaps. Uses only Python's standard library. |
| EGX MCP server (installed by the script) | Today's TradingView snapshot for EGX stocks, plus gold and silver prices in EGP. Third-party project: [M-Abdelmegeed/EGX-Data-MCP-Server](https://github.com/M-Abdelmegeed/EGX-Data-MCP-Server). It is downloaded at install time, not included in this package. |

## Install

**You need:** [Claude Code](https://claude.com/claude-code) and/or Claude Desktop, [Git](https://git-scm.com), and [uv](https://docs.astral.sh/uv/).

### Windows

Run this in PowerShell, from this folder:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -GoldApiKey goldapi-YOUR-KEY
```

### macOS / Linux

```bash
chmod +x install.sh
./install.sh goldapi-YOUR-KEY
```

The key is optional. Without it, everything works except gold and silver prices. Get a free key at [goldapi.io](https://www.goldapi.io).

The installer:
1. Copies the skill to `~/.claude/skills/beedo-trade`.
2. Downloads the EGX server to `~/mcp-servers/EGX-Data-MCP-Server` (the tested version) and installs its packages.
3. Registers the EGX server with Claude Code, if installed.
4. Adds the EGX server to Claude Desktop's config. It saves a backup first.

Then start a new Claude Code session, or fully quit and reopen Claude Desktop.

### Claude.ai (web)

Upload `beedo-trade.skill` under **Settings → Capabilities → Skills**. On the web, the skill can't reach the EGX server or download price history. You'll need to give it the numbers yourself, or use Claude Code / Desktop instead.

## Optional extras

If you also have Anthropic's `trader-budget` and `trader-risk` skills, Beedo-Trade uses them for position sizing and limit checks. Without them, it does the same arithmetic itself.

## Uninstall

```bash
claude mcp remove egx-mcp -s user
```

Then delete `~/.claude/skills/beedo-trade` and `~/mcp-servers/EGX-Data-MCP-Server`, and remove the `egx-mcp` entry from Claude Desktop's config.

## Disclaimer

This is a learning and decision-support tool that applies a technical-analysis method. It is **not investment advice**. Price data from Yahoo Finance and TradingView can be delayed. Always check the live price and the day's EGX disclosures before trading. Claude does not place orders.

## License

[MIT](LICENSE). The EGX MCP server downloaded by the installer is a separate project with its own terms.
