"""Beedo-Trade desktop app: a native window (Edge WebView2) around the course engine."""
import json, os, sys, threading, webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import webview

if getattr(sys, "frozen", False):  # PyInstaller bundle
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE.parents[1] / "skills" / "beedo-trade" / "scripts"))
    sys.path.insert(0, str(BASE.parent))

import analyze  # noqa: E402  (shared with the Claude skill, so numbers always match)
from beedo_app import engine, fundamentals, metals  # noqa: E402

from beedo_app import __version__ as VERSION  # noqa: E402  (single source: beedo_app/__init__.py)
DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "BeedoTrade"
SETTINGS = DATA_DIR / "settings.json"
# Ratios shown as columns in the Watchlist and Screener tables
TABLE_FIGURES = ("market_cap", "pe", "pb", "roe", "net_margin", "debt_to_equity", "eps_growth", "dividend_yield", "perf_ytd")
DEFAULTS = {"watchlist": ["COMI", "TMGH", "SWDY", "ETEL", "EAST", "EGAL"], "cash": 50000, "risk_pct": 2,
            "theme": "dark"}


def _series(bars):
    closes = [b["c"] for b in bars]
    rsi = analyze.rsi_wilder(closes)
    line = lambda xs: [{"time": b["d"], "value": round(x, 2)} for b, x in zip(bars, xs) if x is not None]
    return {
        "candles": [{"time": b["d"], "open": b["o"], "high": b["h"], "low": b["l"], "close": b["c"]} for b in bars],
        "volume": [{"time": b["d"], "value": b["v"], "up": b["c"] >= b["o"]} for b in bars],
        "ma5": line(analyze.sma(closes, 5)), "ma9": line(analyze.sma(closes, 9)), "ma18": line(analyze.sma(closes, 18)),
        "rsi": line(rsi),
        "swings": [{"time": bars[i]["d"], "type": t, "price": p} for i, t, p in analyze.swings(bars) if i >= len(bars) - 120],
    }


class Api:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._window = None  # private: pywebview exposes public attributes to the page and would crawl the whole window object

    # ---------- settings ----------
    def get_settings(self):
        try:
            return {**DEFAULTS, **json.loads(SETTINGS.read_text(encoding="utf-8"))}
        except (OSError, ValueError):
            return dict(DEFAULTS)

    def save_settings(self, patch):
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
        b, name = analyze.fetch(sym)
        return b, name, "Yahoo Finance (daily)", "stock"

    def _build(self, bars, symbol, name, source, kind="stock"):
        rep = analyze.report(bars, symbol, name)
        out = {"symbol": symbol.upper(), "name": name, "source": source, "kind": kind, "last_bar": rep["last_bar"],
               "levels": rep["levels"], "rsi": rep["rsi14"], "ma": {k: rep["moving_averages"][k] for k in ("MA5", "MA9", "MA18")},
               "volume_ratio": rep["volume"]["ratio_vs_avg20"], **engine.evaluate(rep), "chart": _series(bars)}
        if kind == "metal":  # no company behind a metal: no ratios, rating or combined view
            out["fundamentals"], out["verdict"] = None, None
        else:
            out["fundamentals"] = self._fundamentals(symbol)
            out["verdict"] = fundamentals.verdict(out["fundamentals"].get("quality", {}).get("level"), out["signal"]["rung"])
        with self._lock:
            self._cache[symbol.upper()] = rep
        return out

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
            bars, name, source, kind = self._bars(sym)
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
            bars, name, _, kind = self._bars(sym)
            rep = analyze.report(bars, sym, name)
            ev = engine.evaluate(rep)
            with self._lock:
                self._cache[sym] = rep
            if kind == "metal":
                return {"symbol": sym, "name": name, "close": rep["last_bar"]["c"], "date": rep["last_bar"]["d"],
                        "rsi": rep["rsi14"]["now"], "ma": rep["moving_averages"]["alignment"], **ev["signal"],
                        "quality": "Metal", "quality_level": None, "quality_score": None, "verdict": None}
            fund = fund or self._fundamentals(sym)
            q = fund.get("quality", {})
            return {"symbol": sym, "name": name, "close": rep["last_bar"]["c"], "date": rep["last_bar"]["d"],
                    "rsi": rep["rsi14"]["now"], "ma": rep["moving_averages"]["alignment"], **ev["signal"],
                    "quality": q.get("label"), "quality_level": q.get("level"), "quality_score": q.get("score"),
                    "verdict": fundamentals.verdict(q.get("level"), ev["signal"]["rung"]),
                    **{k: (fund.get("figures") or {}).get(k) for k in TABLE_FIGURES}}
        except Exception as e:
            return {"symbol": sym, "error": str(e)}

    def scan(self, symbols):
        syms = [s.strip().upper() for s in symbols or [] if s.strip()][:40]
        with ThreadPoolExecutor(max_workers=6) as ex:
            return list(ex.map(self._technical_row, syms))

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

    def open_url(self, url):
        if str(url).startswith("https://"):
            webbrowser.open(url)

    def open_guide(self):
        # Installed: <app>\docs\...pdf (put there by the installer). Developer checkout: app\packaging\guide\...pdf
        here = Path(sys.executable).parent if getattr(sys, "frozen", False) else BASE.parent / "packaging" / "guide"
        for p in (here / "docs" / "Beedo-Trade User Guide.pdf", here / "Beedo-Trade User Guide.pdf"):
            if p.exists():
                os.startfile(p)
                return {"ok": True}
        webbrowser.open("https://github.com/BeedoElOmda/Beedo-Trade#standalone-windows-app-no-claude-needed")
        return {"ok": True, "online": True}

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
    api._window = webview.create_window("Beedo-Trade", str(BASE / "web" / "index.html"), js_api=api,
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
