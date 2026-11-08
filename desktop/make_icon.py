"""Draw the app icon (green road sign with a download arrow) as PNG + ICO.

Needs Pillow. PyInstaller turns the PNG into .icns on macOS by itself.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "assets"
GREEN = (11, 107, 58, 255)
WHITE = (255, 255, 255, 255)


def draw(size: int = 1024) -> Image.Image:
    s = size / 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = round(4 * s)  # macOS icons keep a margin around the plate
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=round(13 * s), fill=GREEN)
    b = round(9 * s)
    d.rounded_rectangle(
        [b, b, size - b, size - b], radius=round(9 * s), outline=WHITE, width=round(3.5 * s)
    )
    w = round(5 * s)
    cx = size / 2
    d.line([(cx, 18 * s), (cx, 40 * s)], fill=WHITE, width=w)
    d.line([(cx - 10 * s, 31 * s), (cx, 41 * s), (cx + 10 * s, 31 * s)], fill=WHITE, width=w, joint="curve")
    d.line([(21 * s, 47 * s), (43 * s, 47 * s)], fill=WHITE, width=w)
    for x, y in [(cx, 18 * s), (21 * s, 47 * s), (43 * s, 47 * s), (cx - 10 * s, 31 * s), (cx + 10 * s, 31 * s)]:
        r = w / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=WHITE)
    return img


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    img = draw()
    img.save(OUT / "icon.png")
    img.save(OUT / "icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("icon written to", OUT)
