"""Beedo-Trade desktop app: a native window (Edge WebView2 on Windows, WebKit on macOS) around the course engine."""
import csv, json, os, re, subprocess, sys, threading, time, urllib.request, webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import certifi
try:
    import webview
except ImportError:  # Android / iOS: no desktop window; the phone app shows serve() in its own web view
    webview = None

# Packaged Python on macOS has no root certificates of its own, so every HTTPS request failed with
# CERTIFICATE_VERIFY_FAILED. Use the certifi bundle shipped inside the app; read on each new connection.
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

if getattr(sys, "frozen", False):  # PyInstaller bundle
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent
    for p in (BASE.parents[1] / "skills" / "beedo-trade" / "scripts", BASE.parent):
        if p.is_dir():  # source checkout only; on Android a missing folder on sys.path crashes Python's importer
            sys.path.insert(0, str(p))

import analyze  # noqa: E402  (shared with the Claude skill, so numbers always match)
import dividends, fundamentals, metals, timemachine  # noqa: E402  (also shared with the skill)
from beedo_app import engine  # noqa: E402

from beedo_app import __version__ as VERSION  # noqa: E402  (single source: beedo_app/__init__.py)
MAC = sys.platform == "darwin"
# Portable build: a portable.txt file beside the program keeps settings in its own "data" folder (USB stick, no install)
PORTABLE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) and (Path(sys.executable).parent / "portable.txt").exists() else None
DATA_DIR = PORTABLE_DIR / "data" if PORTABLE_DIR else \
    (Path.home() / "Library" / "Application Support" if MAC else Path(os.environ.get("APPDATA", Path.home()))) / "BeedoTrade"
SETTINGS = DATA_DIR / "settings.json"
# Ratios shown as columns in the Watchlist and Screener tables
TABLE_FIGURES = ("market_cap", "pe", "pb", "roe", "net_margin", "debt_to_equity", "eps_growth", "dividend_yield", "perf_ytd")
DEFAULTS = {"watchlist": ["COMI", "TMGH", "SWDY", "ETEL", "EAST", "EGAL"], "cash": 50000, "risk_pct": 2,
            "theme": "system", "lang": "en", "alerts": [], "portfolio": [], "signals": {}, "ma": [5, 9, 18], "steps_off": []}
REPO = "BeedoElOmda/Beedo-Trade"
NOTIFY = None  # the phone app sets this to show each alert as a phone notification
OPEN_URL = None  # the phone app sets this: Python's webbrowser can't open links on Android
ANDROID = hasattr(sys, "getandroidapilevel") or "ANDROID_ROOT" in os.environ
PLAY_URL = "https://play.google.com/store/apps/details?id=io.github.beedoelomda.beedotrade"
RULE_RANGES = {"risk_pct": (0.25, 5), "max_stock_pct": (5, 50), "max_stocks": (1, 15), "cash_pct": (0, 90),
               "max_sector_pct": (10, 100), "min_quality": (0, 2), "min_rung": (1, 3)}  # my trading rules: allowed values


def _valid_ma(ma):
    """Three whole numbers, fast < mid < slow, 2..250 (Yahoo gives about 500 trading days)."""
    try:
        f, m, s = (int(x) for x in ma)
    except (TypeError, ValueError):
        return None
    return [f, m, s] if 2 <= f < m < s <= 250 else None


def _series(bars):
    closes = [b["c"] for b in bars]
    rsi = analyze.rsi_wilder(closes)
    line = lambda xs: [{"time": b["d"], "value": round(x, 2)} for b, x in zip(bars, xs) if x is not None]
    f, m, s = analyze.MA
    md, sg, hist = analyze.macd(closes)
    return {
        "candles": [{"time": b["d"], "open": b["o"], "high": b["h"], "low": b["l"], "close": b["c"]} for b in bars],
        "volume": [{"time": b["d"], "value": b["v"], "up": b["c"] >= b["o"]} for b in bars],
        # keys ma5/ma9/ma18 are the fast/mid/slow slots of the chart; "periods" says which MAs they are
        "ma5": line(analyze.sma(closes, f)), "ma9": line(analyze.sma(closes, m)), "ma18": line(analyze.sma(closes, s)), "periods": [f, m, s],
        "macd": line(md), "macd_signal": line(sg), "macd_hist": [{"time": b["d"], "value": round(x, 3)} for b, x in zip(bars, hist) if x is not None],
        "rsi": line(rsi),
        "swings": [{"time": bars[i]["d"], "type": t, "price": p} for i, t, p in analyze.swings(bars) if i >= len(bars) - 120],
    }


class Api:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._save_lock = threading.Lock()  # settings are read-changed-written from several threads
        self._daily = {}  # symbol -> daily bars of the last analysis (weekly view, back-test)
        self._divs = {}  # symbol -> (time, dividend summary); dividends change a few times a year, so keep them 12 hours
        self._window = None  # private: pywebview exposes public attributes to the page and would crawl the whole window object
        s = self.get_settings()
        if not s.get("theme_is_system_default"):  # once: older versions saved "dark" as their default, so start everyone on System
            s = self.save_settings({"theme": "system", "theme_is_system_default": True})
        analyze.MA = tuple(_valid_ma(s["ma"]) or DEFAULTS["ma"])
        engine.OFF.update(n for n in s["steps_off"] if n in engine.SCORED)

    # ---------- settings ----------
    def get_settings(self):
        try:
            return {**DEFAULTS, **json.loads(SETTINGS.read_text(encoding="utf-8"))}
        except (OSError, ValueError):
            return dict(DEFAULTS)

    def save_settings(self, patch):
        if patch and "ma" in patch:
            ma = _valid_ma(patch["ma"])
            if not ma:
                return {"error": "Moving averages must be three whole numbers, fast < mid < slow, between 2 and 250."}
            patch = {**patch, "ma": ma}
            with self._lock:
                analyze.MA = tuple(ma)
                self._cache.clear()  # old analyses used the old averages
        if patch and "steps_off" in patch:
            off = sorted({int(n) for n in patch["steps_off"] if int(n) in engine.SCORED})
            patch = {**patch, "steps_off": off}
            engine.OFF.clear(); engine.OFF.update(off)
        with self._save_lock:
            s = {**self.get_settings(), **(patch or {})}
            try:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                SETTINGS.write_text(json.dumps(s, indent=1), encoding="utf-8")
            except OSError as e:
                return {"error": f"Could not save settings: {e}"}
            return s

    # ---------- analysis ----------
    @staticmethod
    def _bars(sym):
        """Daily bars, name and source for an EGX code, or for GOLD / SILVER (EGP per gram)."""
        if sym in metals.METALS:
            b, name = metals.bars(sym)
            return b, name, metals.SOURCE, "metal"
        b, name = analyze.fetch(sym, "2y")  # 2 years: room for a 200-day MA and the 2Y chart
        return b, name, "Yahoo Finance + TradingView (15 min delayed)", "stock"

    def _build(self, bars, symbol, name, source, kind="stock", rep=None):
        """rep given = TradingView snapshot (no daily bars): no chart, back-test or time machine."""
        rep = rep or analyze.report(bars, symbol, name)
        out = {"symbol": symbol.upper(), "name": name, "source": source, "kind": kind, "last_bar": rep["last_bar"],
               "levels": rep["levels"], "rsi": rep["rsi14"], "ma": {f"MA{p}": rep["moving_averages"][f"MA{p}"] for p in rep["moving_averages"]["periods"]},
               "volume_ratio": rep["volume"]["ratio_vs_avg20"], **engine.evaluate(rep), "chart": _series(bars) if bars else None,
               "snapshot": bool(rep.get("snapshot")), "reason": rep.get("reason", "")}
        if kind == "metal":  # no company behind a metal: no ratios, rating or combined view
            out["fundamentals"], out["verdict"] = None, None
        else:
            out["fundamentals"] = self._fundamentals(symbol)
            out["verdict"] = fundamentals.verdict(out["fundamentals"].get("quality", {}).get("level"), out["signal"]["rung"])
        out["impact"] = engine.impact(rep)
        out["weekly"] = self._weekly_signal(bars, symbol) if bars else None
        with self._lock:
            self._cache[symbol.upper()] = rep
            if bars:
                self._daily[symbol.upper()] = bars
            else:
                self._daily.pop(symbol.upper(), None)
        return out

    @staticmethod
    def _weekly_signal(bars, symbol):
        """The same checklist on weekly candles (2 years of days = about 104 weeks); None when there are too few weeks."""
        try:
            ev = engine.evaluate(analyze.report(engine.weekly(bars), symbol, ""))
        except analyze.NoHistory:
            return None
        return {"label": ev["signal"]["label"], "rung": ev["signal"]["rung"], "score": ev["score"]}

    @staticmethod
    def _snapshot(sym, why):
        """Yahoo has no usable history for an EGX stock: fall back to TradingView's latest values (signal capped at Alarm)."""
        try:
            return fundamentals.snapshot_report(sym, why)
        except Exception as e:
            raise analyze.NoHistory(f"{why} TradingView: {e}") from e

    @staticmethod
    def _fundamentals(symbol):
        try:  # fundamentals are a second opinion: if TradingView is unreachable, the technical analysis still shows
            return fundamentals.for_symbol(symbol)
        except Exception as e:
            return {"error": str(e), "quality": {"label": "Not enough data", "level": None, "score": None, "why": str(e)}, "rules": []}

    def analyze(self, symbol):
        sym = (symbol or "").strip().upper()
        if not sym.isalnum() or not 2 <= len(sym) <= 6:
            return {"error": "Enter an EGX code such as COMI, TMGH or SWDY."}
        try:
            try:
                bars, name, source, kind = self._bars(sym)
                analyze.report(bars, sym, name)  # raises NoHistory for short or frozen data
            except analyze.NoHistory as e:
                if sym in metals.METALS:
                    raise
                rep = self._snapshot(sym, str(e))
                return self._build(None, sym, rep["name"], rep["source"], "stock", rep)
            return self._build(bars, sym, name, source, kind)
        except Exception as e:  # shown in the UI, never a crash
            return {"error": str(e), "symbol": sym}

    def analyze_csv(self, symbol=""):
        paths = self._window.create_file_dialog(webview.OPEN_DIALOG, file_types=("CSV files (*.csv)", "All files (*.*)"))
        if not paths:
            return {"cancelled": True}
        path = paths[0]
        sym = (symbol or Path(path).stem.split("_")[0]).strip().upper()[:12] or "CSV"
        try:
            return self._build(analyze.load_csv(path), sym, f"{sym} (from {Path(path).name})", f"CSV: {Path(path).name}")
        except Exception as e:
            return {"error": f"Could not read the CSV: {e}"}

    def rescore(self, symbol):
        """The checklist and signal again for the last analysis, after steps were switched on or off (no download)."""
        sym = (symbol or "").upper()
        rep = self._cache.get(sym)
        if not rep:
            return {"error": "Analyse the stock first."}
        ev = engine.evaluate(rep)
        fund = self._fundamentals(sym) if sym not in metals.METALS else None
        verdict = fundamentals.verdict(fund.get("quality", {}).get("level"), ev["signal"]["rung"]) if fund else None
        return {**ev, "verdict": verdict, "impact": engine.impact(rep)}

    def plan(self, symbol, cash, risk_pct):
        rep = self._cache.get((symbol or "").upper())
        if not rep:
            return {"error": "Analyse the stock first."}
        try:
            cash = float(cash) if cash not in (None, "") else None
            risk_pct = float(risk_pct or 2)
        except ValueError:
            return {"error": "Cash and risk must be numbers."}
        if cash is not None and cash <= 0 or not 0 < risk_pct <= 20:
            return {"error": "Cash must be positive and risk between 0 and 20%."}
        return engine.trade_plan(rep, cash, risk_pct)

    def _technical_row(self, sym, fund=None):
        try:
            try:
                bars, name, _, kind = self._bars(sym)
                rep = analyze.report(bars, sym, name)
            except analyze.NoHistory as e:
                if sym in metals.METALS:
                    raise
                bars, kind = None, "stock"
                rep = self._snapshot(sym, str(e))
                name = rep["name"]
            ev = engine.evaluate(rep)
            with self._lock:
                self._cache[sym] = rep
                if bars:
                    self._daily[sym] = bars
            if kind == "metal":
                return {"symbol": sym, "name": name, "close": rep["last_bar"]["c"], "date": rep["last_bar"]["d"],
                        "rsi": rep["rsi14"]["now"], "ma": rep["moving_averages"]["alignment"], **ev["signal"], "score": ev.get("score"), "action": ev["actions"]["shareholder"],
                        "quality": "Metal", "quality_level": None, "quality_score": None, "verdict": None}
            fund = fund or self._fundamentals(sym)
            q = fund.get("quality", {})
            return {"symbol": sym, "name": name, "close": rep["last_bar"]["c"], "date": rep["last_bar"]["d"],
                    "rsi": rep["rsi14"]["now"], "ma": rep["moving_averages"]["alignment"], **ev["signal"], "score": ev.get("score"), "action": ev["actions"]["shareholder"],
                    "quality": q.get("label"), "quality_level": q.get("level"), "quality_score": q.get("score"),
                    "verdict": fundamentals.verdict(q.get("level"), ev["signal"]["rung"]),
                    **{k: (fund.get("figures") or {}).get(k) for k in TABLE_FIGURES}}
        except Exception as e:
            return {"symbol": sym, "error": str(e)}

    def scan(self, symbols):
        syms = [s.strip().upper() for s in symbols or [] if s.strip()][:40]
        with ThreadPoolExecutor(max_workers=6) as ex:
            return list(ex.map(self._technical_row, syms))

    def market_health(self):
        try:
            return fundamentals.market_health()
        except Exception as e:
            return {"error": str(e)}

    def metals(self):
        try:
            return metals.summary()
        except Exception as e:
            return {"error": f"Could not load gold and silver prices: {e}"}

    def sectors(self):
        try:
            return sorted({r["sector"] for r in fundamentals.market() if r.get("sector")})
        except Exception as e:
            return {"error": str(e)}

    def screener(self, min_quality=2, min_rung=2, sector=""):
        """Rates every EGX company, keeps those meeting the quality bar, then runs the course checklist on the best 40."""
        try:
            rows = fundamentals.market()
        except Exception as e:
            return {"error": str(e)}
        rated = [fundamentals.rate(r, rows) for r in rows if not sector or r.get("sector") == sector]
        keep = [f for f in rated if f["quality"]["level"] is not None and f["quality"]["level"] >= int(min_quality)]
        keep.sort(key=lambda f: -f["quality"]["score"])
        checked = keep[:40]  # each technical check downloads a year of prices, so cap the work
        with ThreadPoolExecutor(max_workers=6) as ex:
            results = list(ex.map(lambda f: self._technical_row(f["symbol"], f), checked))
        hits = [r for r in results if not r.get("error") and r["rung"] >= int(min_rung)]
        hits.sort(key=lambda r: (-r["rung"], -(r["quality_score"] or 0)))
        return {"rated": len(rated), "passed_quality": len(keep), "checked": len(checked),
                "skipped_no_prices": sum(1 for r in results if r.get("error")), "results": hits}

    # ---------- 2.3: my trading rules, example plan ----------
    def save_profile(self, answers):
        """The six answers -> a profile and its rules; the trade plan's risk per trade follows the rules."""
        try:
            p = engine.risk_profile(answers)
        except (TypeError, ValueError):
            return {"error": "Answer all six questions."}
        if p.get("error"):
            return p
        self.save_settings({"profile": {"answers": [int(x) for x in answers], **{k: p[k] for k in ("score", "label", "capped", "income")}},
                            "rules": p["rules"], "risk_pct": p["rules"]["risk_pct"]})
        return p

    def save_rules(self, rules):
        """Your own changes to the rules: each value inside its range."""
        try:
            clean = {k: float(rules[k]) for k in RULE_RANGES}
        except (KeyError, TypeError, ValueError):
            return {"error": "Fill in every rule with a number."}
        bad = [k for k, (lo, hi) in RULE_RANGES.items() if not lo <= clean[k] <= hi]
        if bad:
            return {"error": "Some rules are outside their allowed range."}
        for k in ("max_stocks", "min_quality", "min_rung"):
            clean[k] = int(clean[k])
        self.save_settings({"rules": clean, "risk_pct": clean["risk_pct"]})
        return {"rules": clean}

    def plan_builder(self, amount):
        """An example split of the amount from the user's rules and today's course signals. Not a recommendation."""
        s = self.get_settings()
        rules, prof = s.get("rules"), s.get("profile") or {}
        if not rules:
            return {"error": "Answer the questions in My trading rules first."}
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0
        if amount < 1000:
            return {"error": "Enter an amount of at least 1,000 EGP."}
        sc = self.screener(rules["min_quality"], rules["min_rung"])
        if sc.get("error"):
            return sc
        try:
            sectors = {r["symbol"]: r.get("sector") for r in fundamentals.market()}
        except Exception:
            sectors = {}
        cands = []
        for r in sc["results"]:
            tp = engine.trade_plan(self._cache[r["symbol"]]) if r["symbol"] in self._cache else {"error": "no data"}
            if not tp.get("error"):
                cands.append({**r, "sector": sectors.get(r["symbol"]), "entry": tp["entry"], "stop": tp["stop"]})
        return {**engine.build_plan(amount, rules, cands, prof.get("income")), "profile": prof.get("label"), "rules": rules}

    # ---------- 2.3: dividends ----------
    def _dividend(self, sym):
        hit = self._divs.get(sym)
        if hit and time.time() - hit[0] < 12 * 3600:
            return hit[1]
        try:
            r = dividends.for_symbol(sym)
        except Exception as e:
            r = {"symbol": sym, "error": str(e)}
        if not r.get("error"):
            self._divs[sym] = (time.time(), r)
        return r

    def dividends(self, scope="watchlist"):
        """Dividend history and the next expected payout. scope: "watchlist" (watchlist + portfolio) or "all" (every EGX company)."""
        try:
            rows = {r["symbol"]: r for r in fundamentals.market()}
        except Exception:
            rows = {}
        s = self.get_settings()
        syms = list(rows) if scope == "all" else list(dict.fromkeys(s["watchlist"] + [h["symbol"] for h in s["portfolio"]]))
        syms = [x for x in syms if x not in metals.METALS]
        with ThreadPoolExecutor(max_workers=8) as ex:
            found = list(ex.map(self._dividend, syms))
        out = [{**r, "name": (rows.get(r["symbol"]) or {}).get("name") or r["symbol"], "sector": (rows.get(r["symbol"]) or {}).get("sector")}
               for r in found if not r.get("error") and r["kind"] != "None"]
        out.sort(key=lambda r: ((r["expected"] or {}).get("month") or "9999", -(r["yield_pct"] or 0)))
        return {"checked": len(syms), "failed": sum(1 for r in found if r.get("error")), "results": out}

    # ---------- weekly view, back-test ----------
    def _history(self, sym, rng):
        """Longer daily history for a stock; metals and CSV imports use the bars of the last analysis."""
        sym = (sym or "").upper()
        cached = self._daily.get(sym)
        if cached is None:
            raise ValueError("Analyse the stock first.")
        if sym in metals.METALS:
            return cached
        try:
            return analyze.fetch(sym, rng)[0]
        except Exception:
            return cached

    def weekly(self, symbol):
        try:
            return _series(engine.weekly(self._history(symbol, "5y")))
        except Exception as e:
            return {"error": str(e)}

    def backtest(self, symbol, years=2, buy_at=2, sell_at=-2, fee_pct=0):
        """years 1, 2 or 5; buy_at 3 (Confirm), 2 (First or Confirm) or 1 (any buy); sell_at the same below zero; fee per buy and sell, %."""
        try:
            years, buy_at, sell_at, fee_pct = int(years or 2), int(buy_at or 2), int(sell_at or -2), float(fee_pct or 0)
        except (TypeError, ValueError):
            return {"error": "The back-test settings must be numbers."}
        if years not in (1, 2, 5) or buy_at not in (1, 2, 3) or sell_at not in (-1, -2, -3) or not 0 <= fee_pct <= 5:
            return {"error": "Back-test settings: 1, 2 or 5 years, a buy and a sell level, and a fee between 0 and 5%."}
        try:
            r = engine.backtest(self._history(symbol, f"{years}y"), lambda b: analyze.report(b, symbol, ""), buy_at, sell_at, fee_pct)
            return {**r, "settings": {**r.get("settings", {}), "years": years}} if not r.get("error") else r
        except Exception as e:
            return {"error": str(e)}

    def timemachine(self, symbol, days=20, rr=2, entry=None, stop=None):
        """Odds that a buy plan reaches its target or its stop first: 10,000 replays, plus the same plan on past days with the same signal.
        By default the trade plan: entry at the last close, stop under support, target 2R. entry / stop: your own prices."""
        sym = (symbol or "").upper()
        try:
            days, rr = int(days or 20), float(rr or 2)
            entry = float(entry) if entry not in (None, "") else None
            stop = float(stop) if stop not in (None, "") else None
        except (TypeError, ValueError):
            return {"error": "The time machine settings must be numbers."}
        if days not in (10, 20, 40, 60) or not 0.5 <= rr <= 5:
            return {"error": "Time machine settings: 10, 20, 40 or 60 days, and a target of 0.5 to 5 times the risk."}
        try:
            p = self.plan(sym, None, 2)
            if p.get("error") and (entry is None or stop is None):
                return p
            entry = entry or p["entry"]
            stop = stop or p["stop"]
            if not 0 < stop < entry:
                return {"error": "The stop must be below the entry price."}
            bars = self._history(sym, "2y")
            rows = engine.rungs(bars, lambda b: analyze.report(b, sym, ""))
            today = rows[-1][1]
            starts = [i - 1 for i, r in rows[:-1] if r == today]  # bars[i - 1] is the day that signal appeared
            target = round(entry + rr * (entry - stop), 2)
            return {**timemachine.run(bars, entry, stop, target, days=days, starts=starts), "signal": engine.RUNGS[today]}
        except Exception as e:
            return {"error": str(e)}

    # ---------- alerts, portfolio ----------
    def _rows(self, symbols):
        return {r["symbol"]: r for r in self.scan(list(dict.fromkeys(symbols)))}

    def check_alerts(self):
        """Price alerts reached, and signals that changed since the last check, for the watchlist, alerts and portfolio."""
        s = self.get_settings()
        rows = {k: r for k, r in self._rows(s["watchlist"] + [a["symbol"] for a in s["alerts"]] +
                                            [h["symbol"] for h in s["portfolio"]]).items() if not r.get("error")}
        hits = engine.alerts(rows, s["alerts"], s["signals"])
        self.save_settings({"signals": {k: r["rung"] for k, r in rows.items()}})
        if NOTIFY:
            self._notify_new(hits)
        return {"hits": hits, "checked": len(rows)}

    def _notify_new(self, hits):
        """Each alert becomes a notification once a day: the check repeats every 15 minutes, and a price alert stays reached."""
        today = time.strftime("%Y-%m-%d")
        seen = self.get_settings().get("notified") or {}
        sent = seen.get("texts", []) if seen.get("day") == today else []
        new = [h for h in hits if h["text"] not in sent]
        for h in new:
            NOTIFY(h)
        if new:
            self.save_settings({"notified": {"day": today, "texts": sent + [h["text"] for h in new]}})

    def portfolio(self):
        hold = self.get_settings()["portfolio"]
        return engine.portfolio(hold, self._rows([h["symbol"] for h in hold]))

    # ---------- export, updates ----------
    def export_csv(self, name, rows):
        """Saves a table as a CSV file that Excel opens directly (UTF-8 with a byte-order mark)."""
        if not self._window:
            return {"error": "Not available in developer mode."}
        path = self._window.create_file_dialog(webview.SAVE_DIALOG, save_filename=re.sub(r"[^\w-]", "", str(name)) + ".csv",
                                               file_types=("CSV files (*.csv)",))
        if not path:
            return {"cancelled": True}
        path = path if isinstance(path, str) else path[0]
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)
        except OSError as e:
            return {"error": f"Could not save the file: {e}"}
        return {"ok": True, "path": path}

    def check_update(self):
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest", headers={"User-Agent": "Beedo-Trade"})
            with urllib.request.urlopen(req, timeout=8) as r:
                latest = json.load(r)["tag_name"].lstrip("v")
            num = lambda v: tuple(int(x) for x in re.findall(r"\d+", v))
            # phones update from Google Play; Windows and Mac have no store, so they download from GitHub
            return {"latest": latest, "newer": num(latest) > num(VERSION), "url": PLAY_URL if ANDROID else f"https://github.com/{REPO}/releases/latest"}
        except Exception as e:  # offline or rate-limited: say nothing
            return {"error": str(e)}

    def open_url(self, url):
        if str(url).startswith("https://"):
            OPEN_URL(url) if OPEN_URL else webbrowser.open(url)

    def open_guide(self):
        # Windows install: <app>\docs (installer). macOS: inside the app bundle. Developer checkout: app/packaging/guide
        here = Path(sys.executable).parent if getattr(sys, "frozen", False) else BASE.parent / "packaging" / "guide"
        for d in (here / "docs", here, BASE / "docs"):
            for p in sorted(d.glob("Beedo-Trade User Guide*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)[:1]:  # newest guide
                subprocess.run(["open", str(p)]) if MAC else os.startfile(p)
                return {"ok": True}
        webbrowser.open("https://github.com/BeedoElOmda/Beedo-Trade#standalone-app-for-windows-and-mac-no-claude-needed")
        return {"ok": True, "online": True}

    def fx(self):
        try:
            return metals.rate()
        except Exception as e:
            return {"error": str(e)}

    def info(self):
        return {"version": VERSION, "data_dir": str(DATA_DIR)}


def serve(port=8765):
    """Developer mode: the same UI in a normal browser at http://127.0.0.1:<port> (no file dialog)."""
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    api = Api()
    api._window = None

    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(BASE / "web"), **kw)

        def do_POST(self):
            name = self.path.removeprefix("/api/")
            fn = getattr(api, name, None) if not name.startswith("_") else None
            args = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "[]")
            try:
                body = fn(*args) if fn and name != "analyze_csv" else {"error": "Not available in developer mode."}
            except Exception as e:
                body = {"error": str(e)}
            data = json.dumps(body, default=str).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    print(f"Beedo-Trade developer mode: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


def main():
    if "--serve" in sys.argv:
        return serve()
    api = Api()
    api._window = webview.create_window(f"Beedo-Trade {VERSION}", str(BASE / "web" / "index.html"), js_api=api,
                                       width=1360, height=880, min_size=(1024, 680), background_color="#0B1220")
    try:  # the launcher's splash screen (packaged build only) stays up until the window is ready
        import pyi_splash
        close = lambda *_: pyi_splash.is_alive() and pyi_splash.close()
        api._window.events.shown += close
        threading.Timer(30, close).start()  # never leave the splash up if the window event is missed
    except ImportError:
        pass
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
