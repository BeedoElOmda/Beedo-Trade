# Beedo-Trade

Technical analysis of **Egyptian Exchange (EGX)** stocks, gold and silver with the Beedo course checklist: one clear signal (**Alarm / First / Confirm Buy or Sell**, or **Hold**) and separate advice for someone holding cash and someone who already owns the stock.

[Download](https://github.com/BeedoElOmda/Beedo-Trade/releases/latest) · [Code signing policy](#code-signing-policy) · [Privacy](#privacy) · [Uninstall](#uninstall)

It comes in two forms: a **desktop app** for Windows and Mac (no Claude needed), and a **Claude skill** with its own MCP server. Both use the same calculation code, so the numbers match. It is a learning and decision-support tool, **not investment advice**.

## Standalone app for Windows and Mac (no Claude needed)

Beedo-Trade is a desktop program for Windows and Mac (source in `app/`): type an EGX code and get the signal, the cash holder and shareholder actions, an interactive chart (candles, moving averages you choose, support and resistance, swing points, volume, RSI, MACD, 5D to 2Y range), the checklist (the 11 course steps plus MACD as step 12), a trade-plan calculator and a watchlist scanner. Light and dark themes.

**Company fundamentals (1.2):** each stock also gets a Strong / Fair / Weak company rating from standard rules (P/E, P/B, return on equity, margin, debt, growth, dividend), compared with similar companies, plus a **combined view** that joins it with the course signal. The **Screener** rates every EGX company and lists the strong ones that are in a buy zone. Fundamentals come from TradingView's market data and are not part of the Beedo technical course.

**Gold & Silver (1.3):** a page with international gold prices per gram for 24k, 21k and 18k, silver per gram, the official dollar rate and the gold/silver ratio, all in EGP. Type `GOLD` or `SILVER` anywhere a stock code works to run the course checklist, chart and trade plan (in grams) on the metal, or add them to the watchlist. These are international prices; Egyptian shop prices add a local premium.

**New in 1.7: your own moving averages, MACD and market health.** Set the fast, mid and slow moving averages under the chart (default 5 / 9 / 18, the course's own). They draw the chart and give the signals: fast × mid = Alarm, fast × slow = First, mid × slow = Confirm. The chart adds a MACD 12 / 26 / 9 pane, also step 12 of the app's checklist (MACD above its signal and above zero = First Buy, below both = First Sell; only a First reading counts as evidence), and 5D, 1M, 3M, 6M, 1Y and 2Y buttons. A market-health line on the Analyze page says Healthy, Mixed or Weak, from the EGX30 against its 50- and 200-day averages and how many EGX stocks are above theirs (TradingView, end of day); the Screener adds the same health for every industry. Each scored checklist step has a tick box: untick it and it no longer counts in the signal; each step shows what unticking it would do today. The Claude skill follows the same method: 12 steps, 5 / 9 / 18 by default (other periods on request), steps you leave out, and a `beedo_market_health` tool.

**New in 1.6: Time machine.** Under the trade plan, one click shows how often the plan would reach its target before its stop: the next 20 trading days replayed 10,000 times from the stock's own daily moves of the past two years, plus the same plan on every past day that had the same signal, and a one-line verdict that weighs the target's R (a 2R plan breaks even at 1 win in 3). A simulation from past prices, not a prediction. Also in the Claude skill (`beedo_timemachine`). The method is adapted from the `trader-timemachine` skill in [jakeschincariol/day-trader-skill](https://github.com/jakeschincariol/day-trader-skill) (MIT), rebuilt for daily EGX prices because EGX has no free intraday data.

**New in 1.5:**

- **Portfolio:** enter what you own and what you paid; see cost, value, profit or loss, the signal and the shareholder action for each holding.
- **Alerts:** set a price to be told about, and get told when the signal of a watchlist or portfolio stock changes. Checked at start-up and every 15 minutes while the app is open, against the latest daily close.
- **Weekly chart:** switch the chart between daily and weekly candles (five years of history).
- **Back-test:** replay the checklist day by day over the past two years and compare it with buy and hold.
- **Export:** save an analysis as PDF, and the watchlist, screener or portfolio as a file Excel opens.
- **Arabic interface:** switch language from the left menu. Detailed readings built from live numbers stay in English.
- **Update notice:** the app tells you when a newer version is on GitHub.

**Investing.com data:** Investing.com blocks automated access, so download a stock's *Historical Data* as CSV there and use **Import CSV**; the app reads that file format directly.

- **Install:** download `Beedo-Trade-Setup-x.y.z.exe` from the repository's Releases page and run it. Choose **Install for me only** (recommended, no administrator rights) or **Install for all users** (installs into Program Files after administrator approval). If Windows shows "Windows protected your PC", click **More info → Run anyway**; the app isn't code-signed yet (free signing through SignPath Foundation is being set up, see [Code signing policy](#code-signing-policy)).
- **Portable version (Windows):** download `Beedo-Trade-Portable-x.y.z.zip`, unzip it anywhere (a USB stick works) and run `BeedoTrade.exe` inside. No installer and no administrator rights. Settings are kept in a `data` folder beside the program. To remove it, delete the folder.
- **User guide:** an illustrated guide (`app/packaging/guide/Beedo-Trade User Guide.pdf`) is installed with the app. Open it from the Start menu or the app's **User guide** button.
- **Uninstall:** **Settings → Apps → Installed apps → Beedo-Trade → Uninstall**, or **Uninstall Beedo-Trade** in the Start menu. You're asked whether to keep your watchlist and settings.
- **Mac:** download the `.dmg` from Releases (`arm64` for Apple Silicon, `x86_64` for Intel), drag Beedo-Trade to Applications, and on first launch allow it under **System Settings → Privacy & Security → Open Anyway** (the app isn't notarised by Apple). Not tested on a real Mac yet: please report problems.
- **Automatic builds:** publishing a GitHub release builds the Windows installer and both Mac `.dmg` files and attaches them (`.github/workflows/`).
- **Build it yourself:** install [uv](https://docs.astral.sh/uv/) and Inno Setup (`winget install JRSoftware.InnoSetup`), then from `app/` run `powershell -ExecutionPolicy Bypass -File packaging\build.ps1`.
- **How it decides:** `app/beedo_app/engine.py` turns the course rules into code and uses the same `analyze.py`, `fundamentals.py`, `metals.py` and `timemachine.py` as the Claude skill, so the numbers match. Chart patterns (steps 10 and 11) are left for you to judge on the chart, where the swing points are marked.

## Claude skill

The skill analyses **Egyptian Exchange (EGX)** stocks with a structured technical-analysis method, the Beedo course checklist, and gives a clear signal: **Alarm / First / Confirm Buy or Sell**, or **Hold**. It gives separate advice for someone holding cash and someone who already owns the stock.

Ask Claude things like:

- "Analyse COMI with my course method."
- "I have 50,000 EGP. Should I buy TMGH? Give me entry, stop and target."
- "Compare SWDY, ETEL and EAST. Which has the best setup?"
- "Run the time machine on that COMI plan: what are the odds?"

## What it checks (11 steps; the desktop app adds MACD as step 12)

1. Historical support and resistance
2. Recent support and resistance
3. Price location (which pricing zone)
4. Trend: 2 highs and 2 lows identify it, 3 confirm it
5. Moving averages 5 / 9 / 18: crossover of 5×9 = Alarm, 5×18 = First, 9×18 = Confirm (in the desktop app you can choose other periods)
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
| `skills/beedo-trade/scripts/mcp_server.py` | Beedo-Trade as its own MCP server for Claude Desktop. Tools: `beedo_method` (the method and course rules), `beedo_analyze` (the indicators for one stock, or for GOLD / SILVER), `beedo_history` (raw daily prices), `beedo_fundamentals`, `beedo_metals`, `beedo_timemachine` and `beedo_market_health` (market and industry health). Prompt: `beedo_trade_analysis`. It runs on your own computer, so it can download price history even when Claude's sandbox can't. Claude Code uses the skill instead. |
| `skills/beedo-trade/scripts/fundamentals.py` | Company rating (Strong / Fair / Weak) from standard rules on TradingView's market data, with the ratios behind it, plus market and industry health (`--health`). MCP tools: `beedo_fundamentals`, `beedo_market_health`. A second opinion; it never changes the course signal. |
| `skills/beedo-trade/scripts/metals.py` | Gold (24k, 21k, 18k) and silver in EGP per gram, the dollar rate and the gold/silver ratio. MCP tool: `beedo_metals`. `GOLD` and `SILVER` also work as symbols for the course checklist. |
| `skills/beedo-trade/scripts/timemachine.py` | Time machine: odds that a buy plan reaches its target or its stop first, from 10,000 seeded replays of the stock's own daily moves plus the same plan on real past days. MCP tool: `beedo_timemachine`. Shared with the app. |
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

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by [SignPath Foundation](https://signpath.org).

- **Committers and reviewers:** [Beedo El-Omda](https://github.com/BeedoElOmda)
- **Approvers:** [Beedo El-Omda](https://github.com/BeedoElOmda)

Only files built from this repository by its GitHub Actions workflow ([`build-windows.yml`](.github/workflows/build-windows.yml)) are signed, and every signing request is approved by hand: the Windows installer `Beedo-Trade-Setup-<version>.exe` and `BeedoTrade.exe` in the portable zip. Third-party files bundled by PyInstaller (the Python runtime and libraries) are included as published by their authors.

## Privacy

This program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it.

What the desktop app connects to, and why:

- **Yahoo Finance** (`query1/query2.finance.yahoo.com`): daily price history for the stock code, gold or silver you ask about.
- **TradingView** (`scanner.tradingview.com`): company fundamentals and the screener, when you open them.
- **GitHub** (`api.github.com`): the update notice checks whether a newer release exists.

These requests contain only the stock code or the request itself. No personal data, portfolio, watchlist or settings leave your computer; they are stored locally (or in the portable `data` folder). The services' own privacy policies apply to their sites. The Claude skill and its installers also download the EGX MCP server from GitHub and Python packages through uv.

## License

[MIT](LICENSE), for the app and the skill. The time machine's method is adapted from [jakeschincariol/day-trader-skill](https://github.com/jakeschincariol/day-trader-skill) (MIT). The EGX MCP server downloaded by the installer is a separate project with its own terms.
