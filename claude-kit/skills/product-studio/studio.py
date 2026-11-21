#!/usr/bin/env python3
"""Product photo studio: cut out the product, place it on a clean branded
background with a soft shadow, add an Arabic headline / logo, export for
Instagram (post 1080x1350, story/reel cover 1080x1920, square 1080x1080).

usage: studio.py IN.jpg OUTDIR [--bg "#f2efe9"] [--bg2 "#d9d2c5"] [--scene scene.jpg]
                 [--title "..."] [--sub "..."] [--logo logo.png] [--sizes post,story,square]
                 [--model isnet-general-use] [--fill 0.72]
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

SIZES = {"post": (1080, 1350), "story": (1080, 1920), "square": (1080, 1080)}
FONT_DIRS = [os.path.expanduser("~/.fonts"), "/usr/share/fonts"]


def font(name, size):
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for f in files:
                if f.lower().startswith(name.lower()):
                    return ImageFont.truetype(os.path.join(root, f), size, layout_engine=ImageFont.Layout.RAQM)
    return ImageFont.load_default()


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cutout(path, model):
    from rembg import remove, new_session
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
    out = remove(img, session=new_session(model), alpha_matting=True,
                 alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15)
    box = out.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    return out.crop(box) if box else out


def background(size, c1, c2, scene):
    w, h = size
    if scene:
        s = ImageOps.fit(Image.open(scene).convert("RGB"), size)
        return s.filter(ImageFilter.GaussianBlur(18)).convert("RGBA")
    a, b = hexrgb(c1), hexrgb(c2)
    bg = Image.new("RGB", size)
    d = ImageDraw.Draw(bg)
    for y in range(h):  # soft vertical gradient, light top -> darker floor
        t = (y / h) ** 1.6
        d.line([(0, y), (w, y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return bg.convert("RGBA")


def compose(prod, size, c1, c2, scene, title, sub, logo, fill):
    w, h = size
    canvas = background(size, c1, c2, scene)
    text_h = int(h * 0.2) if title else 0
    area_w, area_h = int(w * fill), int((h - text_h) * fill)
    p = prod.copy()
    p.thumbnail((area_w, area_h), Image.LANCZOS)
    x = (w - p.width) // 2
    y = text_h + (h - text_h - p.height) // 2 + int(h * 0.02)
    # contact shadow: squashed, blurred silhouette under the product
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ell = Image.new("L", (int(p.width * 0.9), max(12, int(p.height * 0.06))), 0)
    ImageDraw.Draw(ell).ellipse([0, 0, ell.width, ell.height], fill=110)
    sh.paste((0, 0, 0, 255), (x + (p.width - ell.width) // 2, y + p.height - ell.height // 2), ell)
    canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(int(w * 0.02))))
    # soft drop shadow from the product alpha
    ds = Image.new("RGBA", size, (0, 0, 0, 0))
    ds.paste((0, 0, 0, 70), (x + 14, y + 18), p.getchannel("A"))
    canvas = Image.alpha_composite(canvas, ds.filter(ImageFilter.GaussianBlur(28)))
    canvas.alpha_composite(p, (x, y))
    d = ImageDraw.Draw(canvas)
    dark = sum(hexrgb(c1)) < 380 and not scene
    ink = (255, 255, 255) if dark or scene else (30, 30, 30)
    if title:
        f = font("Tajawal", int(w * 0.075))
        d.text((w // 2, int(h * 0.09)), title, font=f, fill=ink, anchor="mm", direction="rtl",
               stroke_width=3 if scene else 0, stroke_fill=(0, 0, 0))
    if sub:
        f2 = font("Cairo", int(w * 0.04))
        d.text((w // 2, int(h * 0.09) + int(w * 0.085)), sub, font=f2, fill=ink, anchor="mm",
               direction="rtl", stroke_width=2 if scene else 0, stroke_fill=(0, 0, 0))
    if logo:
        lg = Image.open(logo).convert("RGBA")
        lg.thumbnail((int(w * 0.2), int(w * 0.12)))
        canvas.alpha_composite(lg, (w - lg.width - 40, h - lg.height - 40))
    return canvas.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("outdir")
    ap.add_argument("--bg", default="#f4f1ec"); ap.add_argument("--bg2", default="#d8d1c4")
    ap.add_argument("--scene"); ap.add_argument("--title"); ap.add_argument("--sub")
    ap.add_argument("--logo"); ap.add_argument("--sizes", default="post,story")
    ap.add_argument("--model", default="isnet-general-use"); ap.add_argument("--fill", type=float, default=0.72)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.src))[0]
    prod = cutout(a.src, a.model)
    prod.save(os.path.join(a.outdir, base + "_cutout.png"))
    for s in a.sizes.split(","):
        out = compose(prod, SIZES[s], a.bg, a.bg2, a.scene, a.title, a.sub, a.logo, a.fill)
        p = os.path.join(a.outdir, f"{base}_{s}.jpg")
        out.save(p, quality=93)
        print(p)


if __name__ == "__main__":
    sys.exit(main())
