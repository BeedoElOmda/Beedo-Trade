"""Draws the app icon (blue-to-teal rounded square with a rising chart line) as a multi-size .ico."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

S = 512
img = Image.new("RGBA", (S, S))
grad = Image.new("RGBA", (S, S))
g = ImageDraw.Draw(grad)
for y in range(S):  # diagonal-ish gradient #2563EB -> #14B8A6
    t = y / S
    g.line([(0, y), (S, y)], fill=(int(37 + (20 - 37) * t), int(99 + (184 - 99) * t), int(235 + (166 - 235) * t), 255))
mask = Image.new("L", (S, S))
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=112, fill=255)
img.paste(grad, mask=mask)
d = ImageDraw.Draw(img)
pts = [(84, 372), (196, 252), (284, 316), (430, 150)]
d.line(pts, fill="white", width=46, joint="curve")
for x, y in pts[:-1]:
    d.ellipse([x - 23, y - 23, x + 23, y + 23], fill="white")
d.ellipse([430 - 40, 150 - 40, 430 + 40, 150 + 40], fill="white")
out = Path(sys.argv[1] if len(sys.argv) > 1 else "beedo.ico")
img.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
img.resize((256, 256), Image.LANCZOS).save(out.with_suffix(".png"))
img.resize((1024, 1024), Image.LANCZOS).save(out.with_suffix(".icns"))  # macOS app icon

# Splash screen shown by the launcher while the app starts (PyInstaller --splash)
from PIL import ImageFont
sp = Image.new("RGB", (520, 300), (11, 18, 32))
sd = ImageDraw.Draw(sp)
sd.rounded_rectangle([0, 0, 519, 299], radius=18, outline=(34, 48, 77), width=2)
sp.paste(img.resize((96, 96), Image.LANCZOS), (40, 70), img.resize((96, 96), Image.LANCZOS))
font = lambda size, bold=False: ImageFont.truetype("segoeuib.ttf" if bold else "segoeui.ttf", size)
sd.text((156, 78), "Beedo-Trade", font=font(40, True), fill=(230, 236, 247))
sd.text((158, 132), "EGX technical analysis, the Beedo way", font=font(17), fill=(138, 155, 186))
sd.rounded_rectangle([40, 214, 480, 220], radius=3, fill=(22, 33, 58))
sd.rounded_rectangle([40, 214, 220, 220], radius=3, fill=(59, 130, 246))
sp.save(out.with_name("splash.png"))
print(out)
