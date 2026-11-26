"""Takes the user guide's screenshots from the running app (developer mode), with Playwright and Microsoft Edge.

  1. Start the app with a test profile:  APPDATA=<test folder> python -m beedo_app.main --serve
  2. uv run --no-project --with playwright python packaging/guide/take_shots.py <shots-dir>

Element shots are cropped to their cards; page shots are the whole window. Live data, so numbers change daily."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
URL = "http://127.0.0.1:8765/index.html"


def union(page, selectors, pad=6):
    boxes = [page.locator(s).first.bounding_box() for s in selectors]
    boxes = [b for b in boxes if b]
    x0, y0 = min(b["x"] for b in boxes), min(b["y"] for b in boxes)
    x1, y1 = max(b["x"] + b["width"] for b in boxes), max(b["y"] + b["height"] for b in boxes)
    return {"x": max(0, x0 - pad), "y": max(0, y0 - pad), "width": x1 - x0 + 2 * pad, "height": y1 - y0 + 2 * pad}


def snap(page, name, selectors=None):
    page.wait_for_timeout(600)
    if selectors:
        clip = union(page, selectors)
        page.set_viewport_size({"width": 1280, "height": max(860, int(clip["y"] + clip["height"]) + 20)})
        page.wait_for_timeout(400)
        clip = union(page, selectors)
        page.screenshot(path=str(OUT / name), clip=clip, full_page=True)
        page.set_viewport_size({"width": 1280, "height": 860})
    else:
        page.screenshot(path=str(OUT / name))
    print("saved", name)


def open_(page, hash_, wait="#result:not(.hidden)", extra=1500):
    page.goto("about:blank")
    page.goto(f"{URL}{hash_}")
    if wait:
        page.wait_for_selector(wait, timeout=60000)
    page.wait_for_timeout(extra)


def card(sel):
    return f"xpath=(//*[@id='{sel}']/ancestor::div[contains(concat(' ', @class, ' '), ' card ')])[1]"


with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    ctx = b.new_context(viewport={"width": 1280, "height": 860}, device_scale_factor=2, color_scheme="dark")
    page = ctx.new_page()
    D = "&theme=dark&noalerts"

    open_(page, f"#theme=dark&noalerts", wait="#empty", extra=4000)
    snap(page, "home.png")
    snap(page, "g_health.png", ["#health"])

    open_(page, f"#a=COMI{D}")
    snap(page, "g_signal.png", [".card.hero", ".card.actions"])
    snap(page, "g_keyfig.png", [card("keyFigures")])
    snap(page, "g_chart.png", [".chart-card"])
    snap(page, "g_checklist.png", [card("checklist"), ".stack"])
    snap(page, "g_fund.png", [card("fundGrid")])
    page.click("#btBtn"); page.wait_for_selector("#btOut .stats", timeout=120000)
    snap(page, "g_backtest.png", ["#btCard"])
    page.click("#tmBtn"); page.wait_for_selector("#tmOut .stats", timeout=120000)
    snap(page, "g_timemachine.png", ["#tmCard"])
    page.click("#tf button[data-tf='w']"); page.wait_for_function("() => (current && current.weeklyChart) || false", timeout=60000); page.wait_for_timeout(3000)
    snap(page, "g_weekly.png", [".chart-card"])

    open_(page, f"#a=ABUK{D}")
    snap(page, "sell.png", [".card.hero", ".card.actions"])
    open_(page, f"#a=GOLD{D}")
    snap(page, "g_gold.png", [".card.hero", ".card.actions"])

    open_(page, f"#p=watchlist&scan{D}", wait="#wTable tbody tr td .badge", extra=2500)
    snap(page, "watchlist.png")
    page.click("#alertCheck"); page.wait_for_timeout(5000)
    snap(page, "g_alerts.png", [card("alertList")])

    open_(page, f"#p=portfolio{D}", wait="#pTotals .stat", extra=2500)
    snap(page, "g_portfolio.png")
    snap(page, "g_rules.png", ["#rulesCard"])
    page.fill("#buildAmount", "200000"); page.click("#buildBtn")
    page.wait_for_selector("#buildOut .stats", timeout=180000)
    snap(page, "g_plan.png", ["#buildCard"])

    open_(page, f"#p=metals{D}", wait="#metalsGrid .metal-big", extra=2500)
    snap(page, "g_metals.png")

    open_(page, f"#p=screener{D}", wait="#iTable tbody tr td", extra=1500)
    page.click("#runScreener"); page.wait_for_selector("#sSummary:not(:empty)", timeout=180000)
    snap(page, "g_screener.png")
    page.click("#dWatch"); page.wait_for_selector("#dSummary:not(:empty)", timeout=120000)
    snap(page, "g_dividends.png", [card("dTable")])

    light = b.new_context(viewport={"width": 1280, "height": 860}, device_scale_factor=2, color_scheme="light")
    lp = light.new_page()
    open_(lp, "#a=EAST&theme=light&noalerts")
    snap(lp, "light.png")
    open_(lp, "#a=COMI&theme=dark&lang=ar&noalerts", extra=4000)
    snap(lp, "g_arabic.png")
    b.close()
