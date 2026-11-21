#!/usr/bin/env python3
"""2.5D parallax shots from stills + depth, cinematic grade, zoom-blur transitions -> frames piped to ffmpeg."""
import cv2, numpy as np, subprocess, json, sys, os
W, H, FPS = 1080, 1920, 30
D = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(sys.argv[1])); out = sys.argv[2]

def grade(f):
    f = f.astype(np.float32) / 255
    f = np.clip((f - 0.5) * 1.12 + 0.5, 0, 1)                          # contrast
    f = f ** np.array([1.0, 0.99, 1.03], np.float32)                     # warm (BGR: lift red, cool blue a bit)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV); hsv[..., 1] *= 1.06; f = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    f *= np.clip(1.08 - 0.28 * r ** 2, 0.55, 1)[..., None]               # vignette
    return np.clip(f * 255, 0, 255).astype(np.uint8)

VIG = None
def shot(s):
    img = cv2.imread(os.path.join(D, "clean", s["img"] + ".jpg")); dep = np.load(os.path.join(D, "clean", s["img"] + "_d.npy"))
    sh, sw = img.shape[:2]; n = int(s["dur"] * FPS)
    uu, vv = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    for i in range(n):
        t = i / max(1, n - 1); e = t * t * (3 - 2 * t)                    # ease in-out
        cx = s["cx"][0] + (s["cx"][1] - s["cx"][0]) * e; cy = s["cy"][0] + (s["cy"][1] - s["cy"][0]) * e
        z = s["zoom"][0] + (s["zoom"][1] - s["zoom"][0]) * e
        base = sh / H / z                                                 # source px per output px
        sx = cx + (uu - W / 2) * base; sy = cy + (vv - H / 2) * base
        d = cv2.remap(dep, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        k = s.get("dolly", 0) * e * (d - 0.35)                            # near things grow faster
        px = s.get("par", 0) * (e - 0.5) * (d - 0.5) * sw * 0.02          # near things slide more
        mx = cx + (sx - cx) / (1 + k) - px; my = cy + (sy - cy) / (1 + k)
        yield cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def zoomblur(a, b, n=8):
    for i in range(n):
        t = i / (n - 1); src = a if t < 0.5 else b; amt = 1 - abs(t - 0.5) * 2
        acc = np.zeros_like(src, np.float32)
        for k in range(6):
            s = 1 + 0.035 * amt * k; M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
            acc += cv2.warpAffine(src, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        f = acc / 6; f = f * (1 - 0.25 * amt) + 255 * 0.25 * amt * (t > 0.4) * (t < 0.6)  # light flash at the cut
        yield np.clip(f, 0, 255).astype(np.uint8)

def end_card(s, last):
    bg = cv2.GaussianBlur(last, (0, 0), 25); bg = (bg * 0.45).astype(np.uint8)
    for _ in range(int(s["dur"] * FPS)): yield bg

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
prev_tail, last = None, None
for s in spec["shots"]:
    frames = list(end_card(s, last)) if s.get("end") else [grade(f) for f in shot(s)]
    if prev_tail is not None:
        for f in zoomblur(prev_tail, frames[0]): ff.stdin.write(f.tobytes())
        frames = frames[4:]
    for f in frames[:-4] if not s.get("end") else frames: ff.stdin.write(f.tobytes())
    prev_tail = frames[-1]; last = frames[-1]
ff.stdin.close(); ff.wait(); print(out)
