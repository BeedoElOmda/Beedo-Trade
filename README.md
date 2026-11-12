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
| `skills/beedo-trade/scripts/analyze.py` | Downloads a year of daily prices (Yahoo Finance, e.g. `COMI.CA`) and calculates the MA crossovers, RSI, swing points, levels, volume, candles and gaps. It can also read a CSV of daily prices you supply (`--csv`). Uses only Python's standard library. |
| `skills/beedo-trade/scripts/mcp_server.py` | Beedo-Trade as its own MCP server for Claude Desktop. Tools: `beedo_method` (the method and course rules), `beedo_analyze` (the indicators for one stock) and `beedo_history` (raw daily prices). Prompt: `beedo_trade_analysis`. It runs on your own computer, so it can download price history even when Claude's sandbox can't. Claude Code uses the skill instead. |
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
4. Adds two local MCP servers to Claude Desktop's config, `egx-mcp` and `beedo-trade`. It saves a backup first.

Then start a new Claude Code session, or fully quit and reopen Claude Desktop.

### Claude.ai (web)

Upload `beedo-trade.skill` under **Settings → Capabilities → Skills**. On the web, the skill can't reach the EGX server or download price history. You'll need to give it the numbers yourself, or use Claude Code / Desktop instead.

## If price history can't be downloaded

You'll see this as Claude saying it couldn't download price history or reach Yahoo Finance, or the report marking steps 1, 4, 6, 10 and 11 as "not checked".

- **Make sure the `beedo-trade` server is installed and running.** In Claude Desktop, check that it is listed under **Settings → Developer**. If it's missing, you have an older install: download the latest version and run the installer again. This server runs on your own computer, where Yahoo Finance isn't blocked. It replaces the older manual fix of editing the EGX server's `main.py`.
- **Check that your computer can reach Yahoo.** Open https://query1.finance.yahoo.com/v8/finance/chart/COMI.CA?range=5d&interval=1d in a browser. You should see text that includes prices. If not, a firewall, VPN or network setting is blocking it.
- **Some stocks aren't on Yahoo.** Yahoo covers the larger, widely traded EGX stocks (for example COMI and EGAL) but not every listed company. For a missing stock, upload a CSV of daily prices into the chat (date, open, high, low, close, volume; at least 60 trading days). Without one, Claude uses the TradingView snapshot only, and the signal is capped at **Alarm**.

## Optional extras

If you also have Anthropic's `trader-budget` and `trader-risk` skills, Beedo-Trade uses them for position sizing and limit checks. Without them, it does the same arithmetic itself.

## Uninstall

```bash
claude mcp remove egx-mcp -s user
```

Then delete `~/.claude/skills/beedo-trade` and `~/mcp-servers/EGX-Data-MCP-Server`, and remove the `egx-mcp` and `beedo-trade` entries from Claude Desktop's config.

## Disclaimer

This is a learning and decision-support tool that applies a technical-analysis method. It is **not investment advice**. Price data from Yahoo Finance and TradingView can be delayed. Always check the live price and the day's EGX disclosures before trading. Claude does not place orders.

## License

[MIT](LICENSE). The EGX MCP server downloaded by the installer is a separate project with its own terms.

## Standalone Windows app (no Claude needed)

`app/` holds Beedo-Trade as its own desktop program: type an EGX code and get the signal, the cash holder and shareholder actions, an interactive chart (candles, MA 5/9/18, support and resistance, swing points, volume, RSI), the 11-step checklist, a trade-plan calculator and a watchlist scanner. Light and dark themes.

**Company fundamentals (1.2):** each stock also gets a Strong / Fair / Weak company rating from standard rules (P/E, P/B, return on equity, margin, debt, growth, dividend), compared with similar companies, plus a **combined view** that joins it with the course signal. The **Screener** rates every EGX company and lists the strong ones that are in a buy zone. Fundamentals come from TradingView's market data and are not part of the Beedo technical course.

- **Install:** download `Beedo-Trade-Setup-x.y.z.exe` from the repository's Releases page and run it. Choose **Install for me only** (recommended, no administrator rights) or **Install for all users** (installs into Program Files after administrator approval). If Windows shows "Windows protected your PC", click **More info → Run anyway**; the app isn't code-signed.
- **User guide:** an illustrated guide (`app/packaging/guide/Beedo-Trade User Guide.pdf`) is installed with the app. Open it from the Start menu or the app's **User guide** button.
- **Uninstall:** **Settings → Apps → Installed apps → Beedo-Trade → Uninstall**, or **Uninstall Beedo-Trade** in the Start menu. You're asked whether to keep your watchlist and settings.
- **Build it yourself:** install [uv](https://docs.astral.sh/uv/) and Inno Setup (`winget install JRSoftware.InnoSetup`), then from `app/` run `powershell -ExecutionPolicy Bypass -File packaging\build.ps1`.
- **How it decides:** `app/beedo_app/engine.py` turns the course rules into code and uses the same `analyze.py` as the Claude skill, so the numbers match. Chart patterns (steps 10 and 11) are left for you to judge on the chart, where the swing points are marked.
