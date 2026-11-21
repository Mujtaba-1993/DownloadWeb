#!/usr/bin/env python3
"""Cinematic AI horror short: SDXL-Turbo images -> Depth-Anything 2.5D camera moves -> neural Arabic
voices (edge-tts) with word-synced captions -> procedural horror sound design.
Usage: python3 horror_story.py WORK_DIR OUT.mp4   (stages are cached in WORK_DIR)"""
import os, sys, json, math, asyncio, ssl, subprocess
import numpy as np, cv2, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

WD_, OUT = sys.argv[1], sys.argv[2]
os.makedirs(WD_, exist_ok=True)
J = lambda *p: os.path.join(WD_, *p)
W, H, FPS = 1080, 1920, 30
FONT = "/root/.fonts/Lalezar-Regular.ttf"

STYLE = ("dark cinematic horror digital painting, Saudi Arabia, muted desaturated colors, teal and amber moonlight, "
         "volumetric fog, film grain, highly detailed, dramatic shadows, 35mm, masterpiece")
IMAGES = {
    "hook": "looking straight down into an ancient stone well at night, pitch black depths, a pale thin human hand reaching up from the darkness",
    "grandma": "old Saudi grandmother in black abaya and face veil sitting on the floor of a dark mud-brick room, a single oil lantern, telling a story, wrinkled hands",
    "walk": "two young Saudi men in white thobes and red shemagh seen from behind walking toward an abandoned mud-brick village in the desert at dusk",
    "covered": "courtyard of an abandoned mud-brick house at dusk, an old stone well covered with a wooden board and a heavy rock on top",
    "lift": "young Saudi man in white thobe seen from behind lifting a heavy rock off an old wooden well cover, dusk, courtyard, ominous",
    "down": "view down into a deep dark old stone well, rough stones, nothing but darkness at the bottom",
    "sleep": "young man sleeping on a thin floor mattress in an old mud-brick room at night, blue moonlight through a small wooden window",
    "window": "view through a small old wooden window at night onto a courtyard with a stone well under moonlight, thick fog",
    "empty": "empty thin floor mattress with a crumpled blanket in a dusty old mud-brick room, morning light beams, eerie silence",
    "sandals": "a pair of men's leather sandals left on the sand next to an old stone well, early morning, ominous",
    "eyes": "old stone well at night in a courtyard, two faint glowing white eyes deep inside the darkness of the well",
    "scare": "terrifying pale ghoul face with hollow black eyes and wide black mouth emerging from darkness, extreme close-up, horror",
}
NEG = "text, watermark, logo, cartoon, bright, cheerful, blurry, deformed"

V_NARR = ("ar-SA-HamedNeural", "+2%", "-6Hz")
V_GRAN = ("ar-SA-ZariyahNeural", "-10%", "-18Hz")
V_MOM = ("ar-SA-ZariyahNeural", "-28%", "-12Hz")
V_SAUD = ("ar-KW-FahedNeural", "-30%", "-22Hz")
# (image, voice, text, kind)  kind: narr | well (voice from the well) | grandma | scare
SCRIPT = [
    ("hook", V_GRAN, "إذا ناداك أحد باسمك... من داخل البير... لا تجاوب.", "grandma"),
    ("grandma", V_NARR, "هذا اللي كانت تقوله جدتي، وأنا ما صدقتها.", "narr"),
    ("walk", V_NARR, "قبل سنتين، رحت أنا وخويي سعود لبيت جدي المهجور، في قرية طين وسط الصحراء.", "narr"),
    ("covered", V_NARR, "في الحوش كان فيه بير قديم، مسكّر بلوح خشب، وفوقه حجر ثقيل.", "narr"),
    ("lift", V_NARR, "سعود ضحك وقال: خلنا نشوف وش فيه، وشال الحجر.", "narr"),
    ("down", V_NARR, "ما كان فيه شي، بس ظلام.", "narr"),
    ("sleep", V_NARR, "بالليل... صحيت على صوت.", "narr"),
    ("sleep", V_MOM, "خالد... يا خالد...", "well"),
    ("window", V_NARR, "صوت أمي! بس أمي كانت في الرياض، والصوت طالع من البير.", "narr"),
    ("window", V_NARR, "تذكرت كلام جدتي، وما جاوبت.", "narr"),
    ("empty", V_NARR, "الصبح، فراش سعود كان فاضي.", "narr"),
    ("sandals", V_NARR, "دورنا عليه في كل مكان، وآخر شي لقيناه نعاله، جنب البير.", "narr"),
    ("eyes", V_NARR, "ومن يومها، كل ليلة، أسمع سعود يناديني.", "narr"),
    ("eyes", V_SAUD, "خالد... تعال...", "well"),
    ("eyes", V_NARR, "وأمس...", "narr"),
    ("eyes", V_NARR, "جاوبته.", "narr"),
]
SCARE_HOLD, END_CARD = 1.6, 3.0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode()[-1200:])


# ------------------------------------------------------------------ 1. voices + word timings
async def tts_all():
    import edge_tts, aiohttp
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    for i, (_, (voice, rate, pitch), text, kind) in enumerate(SCRIPT):
        if os.path.exists(J(f"v{i}.json")):
            continue
        words, audio = [], bytearray()
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary",
                                 connector=aiohttp.TCPConnector(ssl=ctx), proxy=os.environ.get("HTTPS_PROXY"))
        async for ch in c.stream():
            if ch["type"] == "audio":
                audio += ch["data"]
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
        open(J(f"v{i}.mp3"), "wb").write(audio)
        af = "aresample=48000,highpass=f=60,acompressor=threshold=0.12:ratio=3:makeup=2"
        if kind == "well":   # far away, inside a stone well
            af += ",lowpass=f=2200,aecho=0.8:0.85:120|260|420:0.5|0.35|0.2,volume=1.6"
        elif kind == "grandma":
            af += ",aecho=0.7:0.6:60:0.25,volume=1.2"
        else:
            af += ",aecho=0.6:0.4:40:0.12"
        run(["ffmpeg", "-y", "-i", J(f"v{i}.mp3"), "-af", af, "-ac", "1", J(f"v{i}.wav")])
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                           "-of", "csv=p=0", J(f"v{i}.wav")]))
        json.dump({"dur": d, "words": words}, open(J(f"v{i}.json"), "w"), ensure_ascii=False)
        print("voice", i, round(d, 2), len(words), "words")


asyncio.run(tts_all())

# ------------------------------------------------------------------ 2. images (SDXL-Turbo, local CPU)
todo = [k for k in IMAGES if not os.path.exists(J(f"img_{k}.png"))]
if todo:
    import torch
    from diffusers import AutoPipelineForText2Image
    pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16")
    for k in todo:
        best = None
        im = pipe(f"{IMAGES[k]}, {STYLE}", negative_prompt=NEG, num_inference_steps=3, guidance_scale=0.0,
                  width=576, height=1024, generator=torch.manual_seed(abs(hash(k)) % 10000)).images[0]
        im.save(J(f"img_{k}.png")); print("image", k)
    del pipe

# ------------------------------------------------------------------ 3. depth maps (Depth-Anything V2)
todo = [k for k in IMAGES if not os.path.exists(J(f"depth_{k}.npy"))]
if todo:
    from transformers import pipeline
    dp = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
    for k in todo:
        d = np.asarray(dp(Image.open(J(f"img_{k}.png")))["depth"], np.float32)
        d = (d - d.min()) / (np.ptp(d) + 1e-6)
        np.save(J(f"depth_{k}.npy"), d); print("depth", k)

# ------------------------------------------------------------------ 4. timeline
info = [json.load(open(J(f"v{i}.json"))) for i in range(len(SCRIPT))]
t, TL = 0.6, []
for i, (img, _, text, kind) in enumerate(SCRIPT):
    pre = 0.0
    if i == len(SCRIPT) - 1:
        pre = 1.1  # dead silence before the last word
    t += pre
    TL.append({"i": i, "img": img, "t0": t, "dur": info[i]["dur"], "kind": kind, "words": info[i]["words"]})
    t += info[i]["dur"] + (0.45 if kind != "well" else 0.35)
SCARE_T = TL[-1]["t0"] + TL[-1]["dur"] + 0.15
TOTAL = SCARE_T + SCARE_HOLD + END_CARD
# shots = consecutive lines on the same image
SHOTS = []
for e in TL:
    if SHOTS and SHOTS[-1]["img"] == e["img"]:
        SHOTS[-1]["t1"] = e["t0"] + e["dur"] + 0.45
    else:
        SHOTS.append({"img": e["img"], "t0": 0 if not SHOTS else e["t0"] - 0.25, "t1": e["t0"] + e["dur"] + 0.45})
for a, b in zip(SHOTS, SHOTS[1:]):
    a["t1"] = b["t0"]
SHOTS[-1]["t1"] = SCARE_T
SHOTS.append({"img": "scare", "t0": SCARE_T, "t1": SCARE_T + SCARE_HOLD})
print("total %.1fs, %d shots" % (TOTAL, len(SHOTS)))

# camera move per shot: (zoom_from, zoom_to, dolly, pan_x, pan_y)
MOVES = {"hook": (1.0, 1.22, 0.10, 0, 0), "grandma": (1.08, 1.0, 0.06, 30, 0), "walk": (1.0, 1.12, 0.08, -20, 0),
         "covered": (1.12, 1.0, 0.07, 25, 10), "lift": (1.0, 1.1, 0.06, -15, 0), "down": (1.0, 1.35, 0.14, 0, 0),
         "sleep": (1.0, 1.15, 0.06, 20, 0), "window": (1.0, 1.25, 0.10, 0, -10), "empty": (1.1, 1.0, 0.06, -25, 0),
         "sandals": (1.0, 1.18, 0.08, 0, 10), "eyes": (1.0, 1.45, 0.12, 0, 0), "scare": (1.0, 1.35, 0.05, 0, 0)}

FOCUS = {"eyes": (0.49, 0.80), "covered": (0.5, 0.75), "lift": (0.5, 0.7)}
# ------------------------------------------------------------------ 5. render
OV = 1.12  # overscan so camera moves never show edges
SRC, DEP = {}, {}
for k in IMAGES:
    im = cv2.imread(J(f"img_{k}.png"))
    im = cv2.resize(im, (int(W * OV), int(H * OV)), interpolation=cv2.INTER_LANCZOS4)
    im = cv2.addWeighted(im, 1.5, cv2.GaussianBlur(im, (0, 0), 2), -0.5, 0)  # sharpen after upscale
    SRC[k] = im
    d = cv2.resize(np.load(J(f"depth_{k}.npy")), (int(W * OV), int(H * OV)))
    DEP[k] = cv2.GaussianBlur(d, (0, 0), 6)
gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(3)
FOG = [cv2.GaussianBlur(rng.random((H // 4, W // 2)).astype(np.float32), (0, 0), 18) for _ in range(2)]
FOG = [cv2.resize((f - f.min()) / np.ptp(f), (W * 2, H)) for f in FOG]
VIG = (1 - 0.75 * np.clip(((gx - W / 2) / (W * 0.62)) ** 2 + ((gy - H / 2) / (H * 0.6)) ** 2, 0, 1))[..., None]


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def shot_at(t):
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            return s
    return None


def warp(k, p, t, shake):
    z0, z1, dolly, px, py = MOVES[k]
    e = ease(p)
    z = z0 + (z1 - z0) * e
    if k == "scare":
        z = 1.0 + 0.35 * (1 - math.exp(-p * 6))
    src, dep = SRC[k], DEP[k]
    fx, fy = FOCUS.get(k, (0.5, 0.5))
    cx = src.shape[1] * (0.5 + (fx - 0.5) * min(1, (z - 1) / 0.3))
    cy = src.shape[0] * (0.5 + (fy - 0.5) * min(1, (z - 1) / 0.3))
    cx = min(max(cx, W / 2 / z), src.shape[1] - W / 2 / z)   # keep the view inside the picture
    cy = min(max(cy, H / 2 / z), src.shape[0] - H / 2 / z)
    dsm = cv2.resize(dep, (W, H)) - 0.5
    s = z * (1 + dolly * e * dsm)            # near things grow faster -> depth
    sx = (gx - W / 2) / s + cx - (px * e) * (dsm + 0.5) * 2 + shake[0]
    sy = (gy - H / 2) / s + cy - (py * e) * (dsm + 0.5) * 2 + shake[1]
    return cv2.remap(src, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def grade(img, t, flicker, red=0.0):
    f = img.astype(np.float32) / 255
    f = f * (0.82 + flicker)
    lum = f.mean(2, keepdims=True)
    f = lum + (f - lum) * 0.78                         # desaturate
    f = f + np.array([0.035, 0.015, -0.01]) * (1 - lum)  # teal shadows (BGR)
    f = f * VIG
    if red:
        f[..., 2] += red; f[..., :2] *= 1 - red * 0.6
    fog = (FOG[0][:, int(t * 25) % W: int(t * 25) % W + W] * 0.6 +
           FOG[1][:, int(t * 12 + 400) % W: int(t * 12 + 400) % W + W] * 0.4)
    f = f + fog[..., None] * 0.07
    f = f + rng.normal(0, 0.035, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)  # grain
    return np.clip(f * 255, 0, 255).astype(np.uint8)


def chroma(img, amt):
    if amt < 1:
        return img
    o = img.copy()
    o[..., 2] = np.roll(img[..., 2], int(amt), 1); o[..., 0] = np.roll(img[..., 0], -int(amt), 1)
    return o


_F = {}


def font(sz):
    if sz not in _F:
        _F[sz] = ImageFont.truetype(FONT, sz)
    return _F[sz]


def caption(img_bgr, t):
    """word-synced caption: chunk of up to 4 words, spoken word highlighted"""
    for e in TL:
        if e["t0"] - 0.05 <= t < e["t0"] + e["dur"] + 0.3:
            ws = e["words"]
            if not ws:
                return img_bgr
            lt = t - e["t0"]
            cur = max([i for i, w in enumerate(ws) if w[0] <= lt + 0.05] or [0])
            a = (cur // 4) * 4
            chunk = ws[a:a + 4]
            pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            d = ImageDraw.Draw(pil)
            sz = 96
            col_hi = (255, 60, 50) if e["kind"] == "well" else (255, 214, 0)
            text = " ".join(w[2] for w in chunk)
            tw = d.textlength(text, font=font(sz), direction="rtl")
            if tw > 980:
                sz = int(sz * 980 / tw); tw = 980
            x = W / 2 + tw / 2   # RTL: start from the right edge
            for j, w in enumerate(chunk):
                ww = d.textlength(w[2], font=font(sz), direction="rtl")
                on = a + j == cur
                k = 1.0
                if on:
                    k = 1 + 0.12 * max(0, 1 - (lt - w[0]) / 0.15)
                fs = int(sz * k)
                d.text((x - ww / 2, 1520), w[2], font=font(fs), anchor="mm", direction="rtl",
                       fill=col_hi if on else (255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
                x -= ww + d.textlength(" ", font=font(sz))
            return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
    return img_bgr


def end_card(t):
    p = t / END_CARD
    pil = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(pil)
    a = int(255 * ease(p / 0.3))
    d.text((W / 2, 820), "لا تجاوب...", font=font(170), anchor="mm", direction="rtl", fill=(a, 0, 0))
    d.text((W / 2, 1040), "إذا ناداك أحد الليلة", font=font(110), anchor="mm", direction="rtl", fill=(a, a, a))
    b = int(255 * ease((p - 0.4) / 0.3))
    d.text((W / 2, 1400), "تابع للجزء الثاني", font=font(80), anchor="mm", direction="rtl", fill=(b, b, b))
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "10M", "-bufsize", "20M",
                         "-pix_fmt", "yuv420p", J("video.mp4")], stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for fi in range(n):
    t = fi / FPS
    if t >= SCARE_T + SCARE_HOLD:
        frame = end_card(t - SCARE_T - SCARE_HOLD)
    else:
        s = shot_at(t)
        p = (t - s["t0"]) / (s["t1"] - s["t0"])
        k = s["img"]
        scare = k == "scare"
        well_voice = any(e["kind"] == "well" and e["t0"] <= t < e["t0"] + e["dur"] for e in TL)
        amp = 28 if scare else (5 if well_voice else 0)
        shake = (amp * math.sin(t * 73), amp * math.cos(t * 59))
        flick = 0.0
        if k in ("sleep", "window", "eyes", "hook") or scare:
            flick = -0.18 * (np.sin(t * 31) > 0.93) - 0.08 * abs(math.sin(t * 7.3))
        frame = warp(k, p, t, shake)
        frame = grade(frame, t, flick, red=0.25 * max(0, 1 - (t - SCARE_T) / 0.4) if scare else 0)
        if scare:
            frame = chroma(frame, 18 * max(0.2, 1 - (t - SCARE_T) / 0.8))
            if t - SCARE_T < 0.06:
                frame = np.full_like(frame, 255)
        tc = t - s["t0"]
        if tc < 0.25 and s["t0"] > 0 and not scare:  # dip from black between shots
            frame = (frame * ease(tc / 0.25)).astype(np.uint8)
        if not scare:
            frame = caption(frame, t)
        if t < 0.6:
            frame = (frame * ease(t / 0.6)).astype(np.uint8)
    proc.stdin.write(frame.tobytes())
    if fi % 300 == 0:
        print(f"frame {fi}/{n}", flush=True)
proc.stdin.close(); proc.wait()

# ------------------------------------------------------------------ 6. sound design
SR = 48000
N = int(TOTAL * SR) + SR
tt = np.arange(N) / SR
mix = np.zeros(N)


def put(sig, at, g=1.0):
    i = int(at * SR)
    if 0 <= i < N:
        mix[i:i + len(sig)] += sig[: N - i] * g


def lp(x, a):
    y, o = 0.0, np.empty_like(x)
    b = np.zeros_like(x)
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x)


nz = np.random.default_rng(9).standard_normal(N)
# drone: two detuned low tones + breathing wind
drone = (np.sin(2 * np.pi * 43 * tt) + np.sin(2 * np.pi * 45.3 * tt) * 0.8 + 0.4 * np.sin(2 * np.pi * 86.5 * tt))
drone *= 0.06 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * tt))
wind = lp(nz, 0.02) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * tt + 1)) * 0.25
amb = drone + wind
amb[int((SCARE_T - 1.25) * SR):int(SCARE_T * SR)] *= 0.05     # silence before the scare
amb[int((SCARE_T + SCARE_HOLD) * SR):] *= 0.4
mix += amb
# heartbeat from the night scenes, speeding up
hb_start = TL[6]["t0"]
b = hb_start
while b < SCARE_T - 1.3:
    prog = (b - hb_start) / (SCARE_T - hb_start)
    for off, g in ((0, 1.0), (0.18, 0.7)):
        x = np.arange(int(0.25 * SR)) / SR
        put(np.sin(2 * np.pi * (55 - 20 * x) * x) * np.exp(-x * 18) * 0.5 * g, b + off)
    b += 1.1 - 0.5 * prog
# low boom on each shot change
for s in SHOTS[1:-1]:
    x = np.arange(int(1.5 * SR)) / SR
    put(np.sin(2 * np.pi * (40 + 30 * np.exp(-x * 8)) * x) * np.exp(-x * 2.5) * 0.35, s["t0"])
# reverse-swell into the last word, then the stinger
x = np.arange(int(1.0 * SR)) / SR
put(lp(nz[:len(x)], 0.1) * (x / 1.0) ** 3 * 0.6, SCARE_T - 1.0)
x = np.arange(int(2.0 * SR)) / SR
sting = sum(np.sin(2 * np.pi * f * x + np.sin(2 * np.pi * 7 * x) * 3) for f in (466, 494, 523, 554, 988))
sting = sting * np.exp(-x * 1.8) * 0.18 + nz[:len(x)] * np.exp(-x * 6) * 0.5
sting += np.sin(2 * np.pi * (60 - 25 * x) * x) * np.exp(-x * 2) * 0.9
put(sting, SCARE_T)
# voices
for e in TL:
    a, _ = sf.read(J(f"v{e['i']}.wav"))
    put(a, e["t0"], 1.0)
sf.write(J("mix.wav"), np.stack([mix, mix], 1).astype(np.float32), SR)
run(["ffmpeg", "-y", "-i", J("video.mp4"), "-i", J("mix.wav"), "-map", "0:v", "-map", "1:a",
     "-af", "loudnorm=I=-14:TP=-1.5:LRA=14", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
     "-t", str(TOTAL), "-movflags", "+faststart", OUT])
print("saved", OUT, round(TOTAL, 1))
