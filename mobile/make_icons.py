"""Makes every Android icon Briefcase needs from app/packaging/icon.png (the one Mo'ashir Trade icon, 1024 px,
transparent rounded corners). Run: python mobile/make_icons.py   (needs Pillow)
Output: mobile/icons/beedotrade-{square,round,adaptive}-<size>.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
SIZES = {"square": [48, 72, 96, 144, 192, 320, 480, 640, 960, 1280], "round": [48, 72, 96, 144, 192],
         "adaptive": [108, 162, 216, 324, 432]}


def full_bleed(icon):
    """The icon with its rounded corners filled by the same row's gradient colour (a full square, no corners)."""
    n = icon.size[0]
    out = icon.copy()
    px, src = out.load(), icon.load()
    for y in range(n):
        left, right = src[n * 3 // 10, y], src[n * 7 // 10, y]
        for x in range(n):
            if px[x, y][3] < 255:  # corner (or its soft edge): blend in the row colour behind it
                bg = left if x < n // 2 else right
                a = px[x, y][3] / 255
                px[x, y] = tuple(round(px[x, y][i] * a + bg[i] * (1 - a)) for i in range(3)) + (255,)
    return out


def adaptive(fb):
    """Android masks the launcher icon to the phone's shape and shows only the middle 72 of 108 units:
    put the whole icon in that middle and extend its gradient outwards, so the phone shows the same design."""
    n = fb.size[0]
    big = n * 3 // 2
    # the background is one softened column of the gradient (inside the edge outline, left of the artwork) spread
    # across, so no text, line or outline shows twice
    col = fb.crop((n // 10, 0, n // 10 + 1, n))
    pad = (big - n) // 2  # row for row with the icon in the middle; above and below, its top and bottom colours
    tall = Image.new("RGBA", (1, big))
    tall.paste(col.crop((0, 0, 1, 1)).resize((1, pad)), (0, 0))
    tall.paste(col, (0, pad))
    tall.paste(col.crop((0, n - 1, 1, n)).resize((1, big - pad - n)), (0, pad + n))
    canvas = tall.filter(ImageFilter.GaussianBlur(n // 60)).resize((big, big), Image.NEAREST)
    canvas.paste(fb, ((big - n) // 2, (big - n) // 2))
    return canvas


if __name__ == "__main__":
    icon = Image.open(HERE.parent / "app" / "packaging" / "icon.png").convert("RGBA")
    fb = full_bleed(icon)
    variants = {"square": icon, "round": fb, "adaptive": adaptive(fb)}
    out = HERE / "icons"
    out.mkdir(exist_ok=True)
    for kind, sizes in SIZES.items():
        for s in sizes:
            img = variants[kind].resize((s, s), Image.LANCZOS)
            if kind == "round":
                mask = Image.new("L", (s * 4, s * 4), 0)
                ImageDraw.Draw(mask).ellipse([0, 0, s * 4 - 1, s * 4 - 1], fill=255)
                img.putalpha(mask.resize((s, s), Image.LANCZOS))
            img.save(out / f"beedotrade-{kind}-{s}.png", optimize=True)
    print("icons written to", out)
