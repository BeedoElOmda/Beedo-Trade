"""Google Play store pictures from the one Beedo-Trade icon (app/packaging/icon.png):
the 512 x 512 app icon (a full square: Play rounds the corners itself) and the 1024 x 500 feature graphic.
Run on Windows: python mobile/play/make_store_art.py   (needs Pillow)"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from make_icons import full_bleed  # noqa: E402  (the same square icon Android uses)

STOPS = [(0.0, (0x3F, 0x70, 0xE6)), (0.55, (0x1D, 0x45, 0xA7)), (1.0, (0x10, 0x9E, 0xA5))]  # the icon's gradient


def colour(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def font(size, bold=False):
    for name in (("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")):
        try:
            return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def feature_graphic(icon):
    w, h = 1024, 500
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        for y in range(h):
            px[x, y] = colour(min(1.0, (x + 0.35 * y) / (w + 0.35 * h)))
    logo = full_bleed(icon).resize((260, 260), Image.LANCZOS)
    mask = Image.new("L", (260 * 4, 260 * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 260 * 4 - 1, 260 * 4 - 1], radius=58 * 4, fill=255)
    img.paste(logo, (80, 120), mask.resize((260, 260), Image.LANCZOS))
    d = ImageDraw.Draw(img)
    d.text((390, 150), "Beedo-Trade", font=font(78, True), fill="white")
    d.text((394, 255), "EGX stock analysis with your", font=font(34), fill=(235, 242, 255))
    d.text((394, 300), "technical-analysis course method", font=font(34), fill=(235, 242, 255))
    d.text((394, 362), "Signals · Watchlist · Alerts · Gold & Silver", font=font(26), fill=(205, 225, 250))
    return img


if __name__ == "__main__":
    icon = Image.open(HERE.parent.parent / "app" / "packaging" / "icon.png").convert("RGBA")
    out = HERE / "store"
    out.mkdir(exist_ok=True)
    full_bleed(icon).resize((512, 512), Image.LANCZOS).save(out / "icon-512.png", optimize=True)
    feature_graphic(icon).save(out / "feature-graphic-1024x500.png", optimize=True)
    print("written to", out)
