"""Renders mobile/icon.svg (the Beedo-Trade app icon) into every PNG size Briefcase needs for Android.
Run: uv run --no-project --with playwright python mobile/make_icons.py   (uses Microsoft Edge to draw the SVG)
Output: mobile/icons/beedotrade-{square,round,adaptive}-<size>.png"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
SVG = (HERE / "icon.svg").read_text(encoding="utf-8")
SIZES = {"square": [48, 72, 96, 144, 192, 320, 480, 640, 960, 1280], "round": [48, 72, 96, 144, 192],
         "adaptive": [108, 162, 216, 324, 432]}


def variant(kind):
    svg = SVG
    if kind == "round":  # full-bleed square; the page clips it to a circle
        svg = svg.replace('clip-path="url(#r)"', "")
    if kind == "adaptive":  # Android draws the background (splash colour) and the mask: keep only the B and arrow, scaled
        svg = svg.replace('clip-path="url(#r)"', 'transform="translate(512 512) scale(0.9) translate(-512 -512)"')
        svg = re.sub(r'<rect width="1024" height="1024" fill="url\(#(bg|glow)\)"/>', "", svg)  # to fit the round safe area (arrow tip at 0.95 of its radius)
        svg = re.sub(r"<!-- subtle grid -->\s*<g[^>]*>\s*<path[^>]*/>\s*</g>", "", svg)
    return svg


if __name__ == "__main__":
    out = HERE / "icons"
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge")
        page = b.new_page()
        for kind, sizes in SIZES.items():
            radius = "50%" if kind == "round" else "0"
            for s in sizes:
                page.set_viewport_size({"width": s, "height": s})
                page.set_content(f'<html><body style="margin:0;background:transparent">'
                                 f'<div id="i" style="width:{s}px;height:{s}px;border-radius:{radius};overflow:hidden">'
                                 f'{variant(kind).replace(chr(10), " ").replace("<svg ", f"<svg style=\"width:{s}px;height:{s}px;display:block\" ", 1)}'
                                 f'</div></body></html>')
                page.locator("#i").screenshot(path=str(out / f"beedotrade-{kind}-{s}.png"), omit_background=True)
        b.close()
    print("icons written to", out)
