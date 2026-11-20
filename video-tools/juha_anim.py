#!/usr/bin/env python3
"""2D vector animation: 'Juha, his son and the donkey' (folk tale / Aesop's Miller, Son and Ass).
Draws everything in code with pycairo (characters, parallax desert village, camera), Arabic text with
Pillow+raqm, narration from Piper TTS (lines.json made by juha_voice.py), music + sound effects.
Usage: python3 juha_anim.py WORK_DIR OUT.mp4 [--preview]"""
import sys, json, math, subprocess, os
import numpy as np, cairo, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W_DIR, OUT = sys.argv[1], sys.argv[2]
PREVIEW = "--preview" in sys.argv
WD, HT, FPS = 1080, 1920, 30
FONT = "/root/.fonts/Lalezar-Regular.ttf"
GROUND = 1380
SPEED = 140  # world scroll px/s
PI = math.pi


def hx(c, a=1.0):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def back_out(x):  # overshoot pop
    x = min(1, max(0, x))
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def ell(c, x, y, rx, ry, col, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(rx, ry)
    c.arc(0, 0, 1, 0, 2 * PI); c.restore()
    c.set_source_rgba(*col); c.fill()


def poly(c, pts, col, stroke=None, lw=0):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgba(*col)
    if stroke:
        c.fill_preserve(); c.set_source_rgba(*stroke); c.set_line_width(lw); c.stroke()
    else:
        c.fill()


def line(c, x1, y1, x2, y2, col, w):
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x1, y1); c.line_to(x2, y2)
    c.set_source_rgba(*col); c.set_line_width(w); c.stroke()


def limb(c, pts, col, w):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.set_source_rgba(*col); c.set_line_width(w); c.stroke()


# ---------------------------------------------------------------- characters
SKIN = hx("#d9a173"); SKIN_D = hx("#b97f55"); INK = hx("#2b1d14")

STYLE = {
    "juha": dict(robe="#c4622d", robe_d="#9c4a1f", belt="#f2c14e", head="turban", beard="#3a2a20", s=1.0),
    "son": dict(robe="#3f8f5a", robe_d="#2d6a42", belt="#f2e3c4", head="cap", beard=None, s=0.72),
    "v1": dict(robe="#f4f1ea", robe_d="#d8d2c4", belt=None, head="ghutra_red", beard="#3b2b22", s=0.98),
    "v2": dict(robe="#4a6fa5", robe_d="#355282", belt="#e8d9b0", head="ghutra_white", beard="#2a2a2a", s=0.95),
    "v3": dict(robe="#7b4f9e", robe_d="#5b377a", belt="#f0c75e", head="hijab", beard=None, s=0.9),
    "v4": dict(robe="#6b7f3a", robe_d="#4f5f28", belt="#e8d9b0", head="turban_small", beard="#cfcfcf", s=0.96),
}


def head(c, st, t, talk, mood, blink_seed):
    hy = -362
    # neck + head
    ell(c, 0, hy + 40, 22, 22, SKIN_D)
    ell(c, 0, hy, 50, 54, SKIN)
    ell(c, -30, hy + 4, 10, 14, SKIN_D)  # ear
    if st["head"] == "hijab":
        poly(c, [(-62, hy - 20), (-58, hy + 80), (30, hy + 70), (10, hy + 20), (-20, hy - 30)], hx(st["robe_d"]))
        ell(c, -4, hy - 30, 60, 46, hx(st["robe_d"]))
    # nose
    ell(c, 46, hy + 4, 16, 13, SKIN_D)
    # eye with blink
    bl = (math.sin(t * 1.3 + blink_seed) > 0.985) or ((t + blink_seed) % 3.7 < 0.12)
    ell(c, 22, hy - 12, 11, 2 if bl else 12, hx("#ffffff"))
    if not bl:
        ell(c, 26, hy - 11, 6, 7, INK)
        ell(c, 28, hy - 14, 2, 2, hx("#ffffff"))
    # eyebrow (mood)
    tilt = {"angry": 0.45, "worried": -0.4, "happy": -0.1}.get(mood, 0.0)
    c.save(); c.translate(22, hy - 30); c.rotate(tilt)
    line(c, -14, 0, 14, 0, INK, 6); c.restore()
    # beard
    if st["beard"]:
        poly(c, [(-28, hy + 8), (-10, hy + 70), (30, hy + 80), (52, hy + 40), (50, hy + 20), (10, hy + 28)], hx(st["beard"]))
    # mouth
    mo = (0.35 + 0.65 * abs(math.sin(t * 13))) if talk else 0.0
    if mood == "laugh":
        mo = 0.8 + 0.2 * abs(math.sin(t * 20))
    if mo > 0.05:
        ell(c, 30, hy + 30, 13, 4 + 12 * mo, hx("#5a1e14"))
        ell(c, 30, hy + 30 + 6 * mo, 8, 4 * mo, hx("#d4555a"))
    else:
        c.save(); c.translate(30, hy + 28)
        c.arc(0, -6 if mood in ("happy", None) else 4, 12, 0.35 * PI if mood != "angry" else 1.2 * PI,
              0.75 * PI if mood != "angry" else 1.8 * PI)
        c.set_source_rgba(*INK); c.set_line_width(4); c.stroke(); c.restore()
    # headwear
    h = st["head"]
    if h == "turban":
        ell(c, 0, hy - 48, 66, 40, hx("#f7f3ea"))
        for k in range(3):
            c.save(); c.translate(0, hy - 60 + k * 14)
            c.scale(64, 10); c.arc(0, 0, 1, 0.1 * PI, 0.9 * PI); c.restore()
            c.set_source_rgba(*hx("#d9d2c0")); c.set_line_width(3); c.stroke()
        ell(c, 4, hy - 86, 16, 12, hx("#c4622d"))
    elif h == "turban_small":
        ell(c, 0, hy - 44, 56, 30, hx("#efe6d2"))
    elif h == "cap":
        c.save(); c.translate(0, hy - 30); c.arc(0, 0, 50, PI, 2 * PI); c.restore()
        c.set_source_rgba(*hx("#f7f3ea")); c.fill()
    elif h.startswith("ghutra"):
        cl = hx("#f7f3ea")
        poly(c, [(-56, hy - 40), (56, hy - 44), (40, hy + 40), (-70, hy + 110), (-80, hy + 10)], cl)
        if h == "ghutra_red":
            for k in range(6):
                line(c, -60 + k * 18, hy - 30, -70 + k * 12, hy + 80, hx("#c0392b", 0.7), 4)
        ell(c, 0, hy - 44, 58, 16, hx("#1d1d1d"))  # agal


def human(c, who, x, y, t, mode="walk", talk=False, mood=None, face=1, point=False, phase=0.0, sc=1.0):
    """mode: walk | stand | ride | carry. (x,y) = feet (or hip when riding)."""
    st = STYLE[who]
    s = st["s"] * sc
    c.save(); c.translate(x, y); c.scale(s * face, s)
    rd, rdd = hx(st["robe"]), hx(st["robe_d"])
    ph = t * 2 * PI * 1.6 + phase
    walk = mode in ("walk", "carry")
    bob = -abs(math.sin(ph)) * 10 if walk else (-abs(math.sin(t * 8)) * 6 if mood == "laugh" else 0)
    if mode == "ride":
        c.translate(0, 150)  # hip at origin -> feet frame
    c.translate(0, bob)
    # legs
    pants = hx("#3b2f2a")
    if mode == "ride":
        limb(c, [(-10, -150), (50, -140), (60, -60)], pants, 24)
        ell(c, 70, -52, 20, 9, INK)
    else:
        a = math.sin(ph) * 0.45 if walk else 0
        for sgn, col in ((-1, hx("#2a211d")), (1, pants)):
            fx, fy = math.sin(a * sgn) * 120, -150 + math.cos(a * sgn) * 150
            limb(c, [(0, -150), (fx, fy)], col, 24)
            ell(c, fx + 10, min(fy, 0) - 2, 22, 9, INK)
    # robe (sways)
    sway = math.sin(ph) * 8 if walk else 0
    hem = -110 if mode != "ride" else -120
    poly(c, [(-50, -318), (50, -318), (78 + sway, hem), (-78 + sway, hem)], rd)
    poly(c, [(8, -318), (50, -318), (78 + sway, hem), (24 + sway, hem)], rdd)
    if st["belt"]:
        poly(c, [(-60, -236), (60, -236), (62, -214), (-62, -214)], hx(st["belt"]))
    # far arm / near arm
    if mode == "carry":
        arms = [(-30, -305, 10, -400), (30, -305, 40, -402)]
    elif point:
        arms = [(-30, -305, -40, -200), (30, -305, 120 + 10 * math.sin(t * 9), -330 - 20 * abs(math.sin(t * 9)))]
    elif mood == "laugh":
        arms = [(-30, -305, -20, -215), (30, -305, 50, -225 + 10 * math.sin(t * 16))]
    elif mode == "ride":
        arms = [(-30, -305, 50, -220), (30, -305, 70, -215)]
    else:
        sw = math.sin(ph) * 70 if walk else 0
        arms = [(-30, -305, -10 - sw, -190), (30, -305, 20 + sw, -190)]
    for i, (ax, ay, hx_, hy_) in enumerate(arms):
        limb(c, [(ax, ay), (hx_, hy_)], rdd if i == 0 else rd, 30)
        ell(c, hx_, hy_, 13, 13, SKIN)
    head(c, st, t, talk, mood, phase * 3 + hash(who) % 7)
    c.restore()


def donkey(c, x, y, t, walk=True, strain=False, scared=False, upside=False):
    c.save(); c.translate(x, y)
    if upside:
        c.scale(1, -1)
    ph = t * 2 * PI * (2.6 if strain else 1.6)
    grey, grey_d, belly = hx("#8e8a96"), hx("#6f6b78"), hx("#c9c4cf")
    sq = 0.86 if strain else 1.0
    bob = -abs(math.sin(ph)) * (4 if strain else 8) if walk else 0
    wob = math.sin(t * 30) * 4 if strain else 0
    if upside:  # dangling legs swing
        walk, bob = False, 0
    c.translate(wob, bob)
    # legs
    for i, (lx, off) in enumerate(((-105, 0), (-80, PI), (95, PI), (120, 0))):
        a = math.sin(ph + off) * (0.35 if walk else 0)
        if upside:
            a = math.sin(t * 5 + off) * 0.15
        top = -150 * sq
        fx, fy = lx + math.sin(a) * 110, top + math.cos(a) * (150 * sq - 4)
        col = grey_d if i in (0, 2) else grey
        knee = -4 if strain else 0
        limb(c, [(lx, top), (lx + (fx - lx) * 0.5 + knee * 6, top + (fy - top) * 0.5), (fx, fy)], col, 26)
        ell(c, fx, fy + 2, 16, 9, INK)
    # tail
    tw = math.sin(t * 6) * 0.3
    c.save(); c.translate(-150, -230 * sq); c.rotate(0.6 + tw)
    limb(c, [(0, 0), (-10, 60), (-6, 100)], grey_d, 10); ell(c, -6, 108, 10, 18, INK); c.restore()
    # body
    ell(c, 0, -215 * sq, 160, 78 * sq, grey)
    ell(c, 10, -185 * sq, 120, 38 * sq, belly)
    # neck + head
    nod = math.sin(ph) * 0.06 if walk else 0
    c.save(); c.translate(130, -250 * sq); c.rotate(-0.15 + nod + (0.25 if strain else 0))
    poly(c, [(-30, 30), (30, 30), (70, -90), (20, -110)], grey)
    c.translate(70, -110)
    for k, e in enumerate((-0.25, 0.15)):  # ears
        c.save(); c.translate(-20 + k * 14, -30); c.rotate(-0.5 + e + math.sin(t * 4 + k) * 0.12 - (0.6 if scared else 0))
        ell(c, 0, -50, 15, 52, grey_d if k == 0 else grey); ell(c, 0, -48, 7, 38, hx("#e3b5c0")); c.restore()
    ell(c, 0, 0, 50, 40, grey)
    ell(c, 50, 22, 36, 28, belly)
    ell(c, 66, 18, 5, 7, INK)  # nostril
    bl = (t % 4.1) < 0.12
    ell(c, 8, -12, 11, 2 if bl else (14 if scared else 11), hx("#ffffff"))
    if not bl:
        ell(c, 12, -10, 6, 7, INK)
    if strain or scared:
        line(c, -6, -32, 22, -24 if scared else -38, INK, 5)
    c.restore()
    # saddle blanket
    poly(c, [(-70, -285 * sq), (60, -285 * sq), (55, -205 * sq), (-65, -205 * sq)], hx("#b03a48"))
    for k in range(6):
        ell(c, -55 + k * 22, -205 * sq, 6, 6, hx("#f2c14e"))
    if strain:  # sweat drops
        for k in range(3):
            yy = ((t * 1.5 + k * 0.33) % 1)
            ell(c, 190 + k * 20, -330 + yy * 90, 7, 11, hx("#7fc7ff", 1 - yy))
    c.restore()


# ---------------------------------------------------------------- world
rng = np.random.default_rng(11)
PALMS = [i * 520 + rng.uniform(-120, 120) for i in range(-2, 40)]
HOUSES = [(i * 330 + rng.uniform(-40, 40), rng.uniform(0.8, 1.25), rng.random() < 0.3) for i in range(-3, 60)]
STONES = [(rng.uniform(-500, 20000), rng.uniform(GROUND + 30, 1900), rng.uniform(4, 12)) for _ in range(500)]
CLOUDS = [(rng.uniform(-200, 4000), rng.uniform(250, 650), rng.uniform(0.7, 1.4)) for _ in range(14)]


def sky(c):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, *hx("#ff9f6b")[:3]); g.add_color_stop_rgb(0.45, *hx("#ffcf8f")[:3])
    g.add_color_stop_rgb(1, *hx("#fff0d2")[:3])
    c.rectangle(-WD, -HT, WD * 3, GROUND + HT); c.set_source(g); c.fill()
    rg = cairo.RadialGradient(800, 760, 40, 800, 760, 520)
    rg.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.9); rg.add_color_stop_rgba(1, 1, 0.9, 0.7, 0)
    c.arc(800, 760, 520, 0, 2 * PI); c.set_source(rg); c.fill()
    ell(c, 800, 760, 95, 95, hx("#fff4d6"))


def cloud(c, x, y, s):
    for dx, dy, r in ((0, 0, 60), (55, -20, 70), (115, 0, 55), (60, 15, 60)):
        ell(c, x + dx * s, y + dy * s, r * s * 1.3, r * s * 0.8, hx("#ffffff", 0.75))


def palm(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-12, 0); c.curve_to(-10, -150, 20, -260, 30, -380); c.line_to(48, -378)
    c.curve_to(38, -260, 14, -150, 14, 0); c.close_path(); c.set_source_rgba(*hx("#8a5a34")); c.fill()
    for a in (-2.6, -2.1, -1.6, -1.1, -0.6, -0.15):
        c.save(); c.translate(40, -380); c.rotate(a)
        c.move_to(0, 0); c.curve_to(60, -40, 120, -20, 170, 30); c.curve_to(110, 0, 60, -5, 0, 12)
        c.close_path(); c.set_source_rgba(*hx("#3f7a3a")); c.fill(); c.restore()
    ell(c, 40, -372, 16, 14, hx("#6b3e1e"))
    c.restore()


def house(c, x, y, s, dome, col):
    c.save(); c.translate(x, y); c.scale(s, s)
    poly(c, [(-90, 0), (90, 0), (90, -150), (-90, -150)], col)
    poly(c, [(-95, -150), (95, -150), (95, -164), (-95, -164)], col)
    for k in range(-2, 3):
        poly(c, [(k * 36 - 8, -164), (k * 36 + 8, -164), (k * 36 + 8, -178), (k * 36 - 8, -178)], col)
    dk = tuple(v * 0.7 for v in col[:3]) + (1,)
    c.save(); c.translate(-30, -70); c.arc(0, 0, 18, PI, 2 * PI); c.line_to(18, 30); c.line_to(-18, 30); c.close_path()
    c.set_source_rgba(*dk); c.fill(); c.restore()
    poly(c, [(30, -110), (56, -110), (56, -80), (30, -80)], dk)
    if dome:
        c.arc(0, -164, 58, PI, 2 * PI); c.set_source_rgba(*col); c.fill()
        line(c, 0, -222, 0, -250, dk, 5); ell(c, 0, -252, 6, 6, dk)
    c.restore()


def world(c, cam):
    sky(c)
    for x, y, s in CLOUDS:
        cloud(c, (x - cam * 0.05) % 2600 - 400, y, s)
    # far dunes
    c.move_to(-50, GROUND - 120)
    for x in range(-50, WD + 60, 30):
        c.line_to(x, GROUND - 150 - 60 * math.sin((x + cam * 0.15) / 260) - 25 * math.sin((x + cam * 0.15) / 97))
    c.line_to(WD + 60, GROUND); c.line_to(-50, GROUND); c.close_path()
    c.set_source_rgba(*hx("#efc08a")); c.fill()
    # village (parallax 0.35)
    for hx_, s, dome in HOUSES:
        sx = hx_ - cam * 0.35
        if -200 < sx < WD + 200:
            house(c, sx, GROUND - 40, s * 0.8, dome, hx("#d79a66"))
    # mid ground band
    c.rectangle(-50, GROUND - 50, WD + 100, 60); c.set_source_rgba(*hx("#e2ad74")); c.fill()
    for px in PALMS:  # palms (parallax 0.6)
        sx = px - cam * 0.6
        if -300 < sx < WD + 300:
            palm(c, sx, GROUND + 10, 0.95)
    # ground
    g = cairo.LinearGradient(0, GROUND, 0, HT)
    g.add_color_stop_rgb(0, *hx("#e7b47a")[:3]); g.add_color_stop_rgb(1, *hx("#c98d56")[:3])
    c.rectangle(-50, GROUND, WD + 100, HT); c.set_source(g); c.fill()
    poly(c, [(-50, GROUND + 60), (WD + 50, GROUND + 60), (WD + 50, GROUND + 200), (-50, GROUND + 200)], hx("#f0c993"))
    for x, y, r in STONES:
        sx = (x - cam) % 2400 - 200
        if -20 < sx < WD + 20:
            ell(c, sx, y, r * 1.6, r, hx("#b98352", 0.8))


def bush(c, x, y, s):
    for dx, r in ((0, 70), (60, 90), (130, 65)):
        ell(c, x + dx * s, y, r * s, r * s * 0.75, hx("#5f8a3e"))
        ell(c, x + dx * s - 10, y - 15, r * s * 0.6, r * s * 0.4, hx("#7aa851"))


# ---------------------------------------------------------------- text (Pillow raqm, cached)
_TXT = {}


def text_img(txt, size, fill=(255, 255, 255, 255), stroke=(0, 0, 0, 255), sw=None, maxw=960):
    key = (txt, size, fill, stroke)
    if key not in _TXT:
        f = ImageFont.truetype(FONT, size)
        d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        w = d.textlength(txt, font=f, direction="rtl")
        if w > maxw:
            f = ImageFont.truetype(FONT, int(size * maxw / w)); w = maxw
        sw = sw if sw is not None else max(2, size // 12)
        im = Image.new("RGBA", (int(w) + 4 * sw + 20, int(size * 1.6) + 4 * sw), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((im.width / 2, im.height / 2), txt, font=f, fill=fill, anchor="mm",
                                direction="rtl", stroke_width=sw, stroke_fill=stroke)
        _TXT[key] = im
    return _TXT[key]


def paste(base, im, cx, cy, scale=1.0, alpha=1.0):
    if scale <= 0.02 or alpha <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def bubble(c, cx, cy, w, h, tx, ty, k):
    """speech bubble in cairo, scale k (pop)"""
    c.save(); c.translate(cx, cy); c.scale(k, k)
    r = 40
    x0, y0 = -w / 2, -h / 2
    c.new_sub_path()
    c.arc(x0 + w - r, y0 + r, r, -PI / 2, 0); c.arc(x0 + w - r, y0 + h - r, r, 0, PI / 2)
    c.arc(x0 + r, y0 + h - r, r, PI / 2, PI); c.arc(x0 + r, y0 + r, r, PI, 1.5 * PI); c.close_path()
    c.set_source_rgba(1, 1, 1, 1); c.fill_preserve(); c.set_source_rgba(*INK); c.set_line_width(7); c.stroke()
    tdx, tdy = (tx - cx) / k, (ty - cy) / k
    c.move_to(-30, h / 2 - 4); c.line_to(tdx, tdy); c.line_to(30, h / 2 - 4); c.close_path()
    c.set_source_rgba(1, 1, 1, 1); c.fill_preserve(); c.set_source_rgba(*INK); c.stroke()
    c.rectangle(-36, h / 2 - 12, 72, 10); c.set_source_rgba(1, 1, 1, 1); c.fill()
    c.restore()


# ---------------------------------------------------------------- timeline
lines = json.load(open(os.path.join(W_DIR, "lines.json")))
GAP = 0.35
t = 0.0
for ln in lines:
    if ln["scene"] == 1 and ln["spk"] == "N":
        t += 0.5  # breath after hook
    ln["t0"] = t
    t += ln["dur"] + GAP
END_CARD = 3.2
TOTAL = t + END_CARD
SCENES = {}
for ln in lines:
    s = SCENES.setdefault(ln["scene"], [ln["t0"], ln["t0"] + ln["dur"] + GAP])
    s[1] = ln["t0"] + ln["dur"] + GAP
SCENES[1][0] = SCENES[0][1]
SCENES[6][1] = TOTAL
VILLAGER = {1: "v1", 2: "v2", 3: "v3", 4: "v4", 5: "v1"}
print("total %.1fs" % TOTAL, {k: [round(a, 2), round(b, 2)] for k, (a, b) in SCENES.items()})


VLINES = [(ln["t0"], ln["t0"] + ln["dur"]) for ln in lines if ln["spk"] == "V"]


def speed_at(t):
    k = 1.0
    for a, b in VLINES:
        if a - 0.4 <= t <= b + 0.4:
            k = min(k, 1 - min(ease((t - a + 0.4) / 0.4), ease((b + 0.4 - t) / 0.4)))
    return SPEED * k


_TT = np.arange(0, TOTAL + 1, 1 / FPS)
_CAM = np.concatenate([[0], np.cumsum([speed_at(x) / FPS for x in _TT[:-1]])])


def cam_at(t):
    return float(np.interp(t, _TT, _CAM))


def scene_at(t):
    for k, (a, b) in SCENES.items():
        if a <= t < b:
            return k, t - a, b - a
    return 6, t - SCENES[6][0], SCENES[6][1] - SCENES[6][0]


def line_at(t):
    for ln in lines:
        if ln["t0"] <= t < ln["t0"] + ln["dur"]:
            return ln
    return None


def draw_cast(c, sc, t, lt, cam, ln, moving=True):
    X = 410  # group anchor on screen
    talkJ = bool(ln and ln["spk"] == "J")
    walking = sc != 6
    if sc in (0, 5):  # carrying the donkey on a pole
        pole_y = GROUND - 400
        donkey(c, X + 20, pole_y + 18, t, upside=True, scared=True)
        human(c, "son", X - 190, GROUND, t, "carry", mood="worried", phase=PI)
        line(c, X - 210, GROUND - 0.72 * 402, X + 250, GROUND - 402, hx("#7a4b26"), 18)
        human(c, "juha", X + 220, GROUND, t, "carry", mood="worried")
        return
    W_ = "walk" if moving else "stand"
    mw = None if moving else "worried"
    if sc == 1:
        donkey(c, X, GROUND, t, walk=moving)
        human(c, "juha", X - 15, GROUND - 255, t, "ride", mood="happy" if moving else "worried")
        human(c, "son", X - 230, GROUND, t, W_, phase=PI, mood="worried")
    elif sc == 2:
        donkey(c, X, GROUND, t, walk=moving)
        human(c, "son", X - 10, GROUND - 255, t, "ride", mood="happy" if moving else "worried")
        human(c, "juha", X - 245, GROUND, t, W_, phase=PI, mood=mw)
    elif sc == 3:
        donkey(c, X, GROUND + 6, t, strain=True, walk=True)
        human(c, "son", X + 50, GROUND - 230, t, "ride", mood="happy")
        human(c, "juha", X - 60, GROUND - 230, t, "ride", mood="happy")
    elif sc == 4:
        human(c, "son", X - 220, GROUND, t, W_, phase=PI, mood=mw)
        donkey(c, X - 40, GROUND, t, walk=moving)
        human(c, "juha", X + 170, GROUND + 40, t, W_, mood=mw)
    elif sc == 6:  # stop, Juha turns to his son, then to us
        donkey(c, X - 40, GROUND, t, walk=False)
        human(c, "son", X - 260, GROUND, t, "stand", mood="worried" if lt < 4 else "happy")
        human(c, "juha", X + 230, GROUND + 40, t, "stand", talk=talkJ, mood="happy", face=-1 if lt < 2.2 else 1)


def villager_pos(sc, t):
    """world-anchored so the villager slides past while he talks"""
    vl = [ln for ln in lines if ln["scene"] == sc and ln["spk"] == "V"]
    if not vl:
        return None
    return cam_at(vl[0]["t0"]) + (860 if sc in (3, 4) else 820) - cam_at(t)


def render():
    os.makedirs(W_DIR, exist_ok=True)
    sfx_marks = []
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WD, HT)
    times = np.arange(0, TOTAL, 1 / FPS)
    if PREVIEW:
        times = [1.0, SCENES[1][0] + 6, SCENES[1][0] + 10, SCENES[2][0] + 4, SCENES[3][0] + 3,
                 SCENES[4][0] + 3, SCENES[5][0] + 3.5, SCENES[6][0] + 2, SCENES[6][0] + 5, TOTAL - 1.0]
    proc = None
    if not PREVIEW:
        proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                                 "-s", f"{WD}x{HT}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                 "-crf", "18", "-pix_fmt", "yuv420p", os.path.join(W_DIR, "video.mp4")],
                                stdin=subprocess.PIPE)
    prev_sc = None
    for fi, t in enumerate(times):
        sc, lt, sd = scene_at(t)
        if sc != prev_sc:
            sfx_marks.append(("whoosh" if sc not in (5, 6) else ("boing" if sc == 5 else "chime"), t))
            prev_sc = sc
        ln = line_at(t)
        cam = cam_at(t) if sc != 6 else cam_at(SCENES[6][0])
        moving = speed_at(t) > SPEED * 0.3
        c = cairo.Context(surf)
        # camera: slow push-in each scene, punch on scene start, shake on punchlines
        z = 1.32 + 0.06 * ease(lt / max(sd, 0.1)) + 0.08 * max(0, 1 - lt / 0.35)
        if sc == 0:
            z = 1.6 - 0.2 * ease(lt / sd)
        if sc == 6:
            z = 1.32 + 0.3 * ease((lt - 1.0) / 3.0)
        shx = shy = 0
        if ln and ln["spk"] == "V" and t - ln["t0"] < 0.35:
            shx, shy = 12 * math.sin(t * 90), 10 * math.cos(t * 70)
        fx_, fy_ = (500, 1180) if sc != 6 else (640, 1080)
        c.translate(fx_ + shx, fy_ + shy); c.scale(z, z); c.translate(-fx_, -fy_)
        world(c, cam)
        # villager(s)
        vx = villager_pos(sc, t) if sc in VILLAGER else None
        vtalk = bool(ln and ln["spk"] == "V")
        if vx is not None and -300 < vx < WD + 300:
            mood = "laugh" if sc == 5 else "angry"
            human(c, VILLAGER[sc], vx, GROUND - 20, t, "stand", talk=vtalk and sc != 5, mood=mood, face=-1,
                  point=vtalk and sc != 5)
            if sc == 5:
                human(c, "v2", vx + 170, GROUND - 30, t + 0.3, "stand", mood="laugh", face=-1, sc=0.95)
                human(c, "v3", vx - 150, GROUND - 25, t + 0.7, "stand", mood="laugh", face=-1, sc=0.92)
        draw_cast(c, sc, t, lt, cam, ln, moving)
        for bx in (300, 1700, 3100, 4500, 5900, 7300):  # foreground bushes, fastest parallax
            sx = bx - cam * 1.3
            if -300 < sx < WD + 100:
                bush(c, sx, HT - 120, 1.2)
        # bubble shapes (cairo) -- villagers and Juha
        bub = None
        if ln and ln["spk"] in ("V", "J"):
            k = back_out((t - ln["t0"]) / 0.3)
            if ln["spk"] == "V" and vx is not None:
                bub = (0, 0, vx - 30, GROUND - 400, k, ln["text"])
            elif ln["spk"] == "J":
                bub = (0, 0, 690, GROUND - 440, k, ln["text"])
            if bub:
                sx_, sy_ = c.user_to_device(bub[2], bub[3])
                bub = (540, 330, sx_, sy_, bub[4], bub[5])
        # vignette
        rg = cairo.RadialGradient(540, 960, 500, 540, 960, 1250)
        rg.add_color_stop_rgba(0, 0, 0, 0, 0); rg.add_color_stop_rgba(1, 0.15, 0.05, 0, 0.45)
        c.identity_matrix(); c.rectangle(0, 0, WD, HT); c.set_source(rg); c.fill()
        if bub:
            bubble(c, bub[0], bub[1], 900, 230, bub[2], min(bub[3], 900), bub[4])
        # ---- text layer (Pillow)
        buf = np.ndarray((HT, WD, 4), np.uint8, surf.get_data()).copy()
        img = Image.fromarray(buf[..., [2, 1, 0, 3]], "RGBA")
        if bub:
            paste(img, text_img(bub[5], 88, (40, 25, 15, 255), (255, 255, 255, 0), sw=0, maxw=820),
                  bub[0], bub[1], bub[4])
        if ln and ln["spk"] == "N" and sc != 0:
            k = back_out((t - ln["t0"]) / 0.25)
            paste(img, text_img(ln["text"], 110), 540, 1640, k)
        if sc == 0:
            k = back_out(lt / 0.3)
            paste(img, text_img("ليش جحا", 150, (255, 255, 255, 255)), 540, 300, k)
            paste(img, text_img("شايل حماره؟!", 190, (255, 210, 0, 255)), 540, 480, k)
        if sc == 1 and lt < 1.4:
            paste(img, text_img("القصة من البداية...", 110), 540, 400, back_out(lt / 0.3), alpha=min(1, (1.4 - lt) / 0.3))
        endc = t - (TOTAL - END_CARD)
        if endc > 0:
            ov = Image.new("RGBA", (WD, HT), (25, 12, 5, int(170 * ease(endc / 0.5))))
            img.alpha_composite(ov)
            paste(img, text_img("رضا الناس", 210, (255, 210, 0, 255)), 540, 760, back_out(endc / 0.35))
            paste(img, text_img("غاية لا تُدرك", 190), 540, 980, back_out((endc - 0.2) / 0.35))
            paste(img, text_img("أرسلها لشخص يهتم بكلام الناس", 80, (255, 255, 255, 255)), 540, 1300,
                  back_out((endc - 0.8) / 0.35))
        # scene-change flash
        for a, _ in SCENES.values():
            if 0 <= t - a < 0.1 and a > 0.5:
                img.alpha_composite(Image.new("RGBA", (WD, HT), (255, 255, 255, int(200 * (1 - (t - a) / 0.1)))))
        frame = np.asarray(img)[..., [2, 1, 0, 3]].tobytes()
        if PREVIEW:
            img.convert("RGB").resize((360, 640)).save(os.path.join(W_DIR, f"pv{fi:02d}.jpg"))
        else:
            proc.stdin.write(frame)
        if fi % 300 == 0:
            print(f"frame {fi}/{len(times)}", flush=True)
    if proc:
        proc.stdin.close(); proc.wait()
    return sfx_marks


marks = render()
if PREVIEW:
    sys.exit(0)

# ---------------------------------------------------------------- audio
SR = 48000
N = int(TOTAL * SR) + SR
voice = np.zeros(N)
for ln in lines:
    a, sr = sf.read(ln["wav"])
    i = int(ln["t0"] * SR)
    voice[i:i + len(a)] += a[: N - i]
fx = np.zeros(N)
rg = np.random.default_rng(1)


def put(sig, at):
    i = int(at * SR)
    if 0 <= i < N:
        fx[i:i + len(sig)] += sig[: N - i]


def whoosh(d=0.4):
    tt = np.arange(int(d * SR)) / SR
    n = rg.standard_normal(len(tt)); y = 0.0; o = np.zeros_like(n)
    for j in range(len(n)):
        y += (0.02 + 0.45 * (tt[j] / d) ** 2) * (n[j] - y); o[j] = y
    return o * np.sin(PI * tt / d) ** 2 * 0.35


def boing():
    tt = np.arange(int(0.7 * SR)) / SR
    f = 180 + 120 * np.sin(2 * PI * 9 * tt) * np.exp(-tt * 3)
    return np.sin(2 * PI * np.cumsum(f) / SR) * np.exp(-tt * 3) * 0.35


def chime():
    tt = np.arange(int(1.5 * SR)) / SR
    return sum(np.sin(2 * PI * f * tt) for f in (880, 1320, 1760)) * np.exp(-tt * 3) * 0.08


def pop():
    tt = np.arange(int(0.08 * SR)) / SR
    return np.sin(2 * PI * (600 - 3000 * tt) * tt) * np.exp(-tt * 40) * 0.3


for kind, at in marks:
    put({"whoosh": whoosh, "boing": boing, "chime": chime}[kind](), max(0, at - (0.3 if kind == "whoosh" else 0)))
for ln in lines:
    if ln["spk"] in ("V", "J"):
        put(pop(), ln["t0"])
put(chime(), TOTAL - END_CARD)
sf.write(os.path.join(W_DIR, "voice.wav"), voice.astype(np.float32), SR)
sf.write(os.path.join(W_DIR, "fx.wav"), fx.astype(np.float32), SR)
subprocess.run(["python3", "/home/user/video-tools/make_music.py", os.path.join(W_DIR, "music.wav"), str(TOTAL),
                str(SCENES[1][0]), str(TOTAL - END_CARD)], check=True)
fc = ("[1:a]volume=1.0,asplit=2[v][sc];[2:a]volume=0.32,lowpass=f=6000[m];"
      "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=10:release=250[md];[3:a]volume=0.9[f];"
      "[md][v][f]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=0[a]")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(W_DIR, "video.mp4"),
                "-i", os.path.join(W_DIR, "voice.wav"), "-i", os.path.join(W_DIR, "music.wav"),
                "-i", os.path.join(W_DIR, "fx.wav"), "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
                "-t", str(TOTAL), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT],
               check=True)
print("saved", OUT, round(TOTAL, 1))
