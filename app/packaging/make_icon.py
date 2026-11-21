"""Makes the desktop icons (.ico for Windows, .icns for macOS) and the start-up splash from icon.png,
the Beedo-Trade icon (1024 x 1024, transparent corners). The Android icons come from mobile/icon.svg (same design)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

img = Image.open(Path(__file__).with_name("icon.png")).convert("RGBA")
out = Path(sys.argv[1] if len(sys.argv) > 1 else "beedo.ico")
img.save(out, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
img.resize((256, 256), Image.LANCZOS).save(out.with_suffix(".png"))
img.save(out.with_suffix(".icns"))  # macOS app icon

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
