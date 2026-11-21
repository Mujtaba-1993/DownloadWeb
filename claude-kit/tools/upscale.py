#!/usr/bin/env python3
"""Real-ESRGAN x2 video/image upscaler (CPU, tiled). usage: upscale.py in.(mp4|jpg) out.(mp4|jpg)"""
import sys, os, subprocess, torch, numpy as np, cv2, spandrel
torch.set_num_threads(os.cpu_count())
M = spandrel.ModelLoader().load_from_file(os.path.expanduser("~/.cache/esrgan/RealESRGAN_x2plus.pth")).eval()
def up(img, tile=256, pad=16):
    h, w = img.shape[:2]; out = np.zeros((h * 2, w * 2, 3), np.float32)
    t = torch.from_numpy(img[:, :, ::-1].copy()).permute(2, 0, 1).float()[None] / 255
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            y0, x0, y1, x1 = max(0, y - pad), max(0, x - pad), min(h, y + tile + pad), min(w, x + tile + pad)
            with torch.no_grad(): o = M(t[:, :, y0:y1, x0:x1])[0].permute(1, 2, 0).numpy()
            oy, ox = (y - y0) * 2, (x - x0) * 2; th, tw = min(tile, h - y) * 2, min(tile, w - x) * 2
            out[y * 2:y * 2 + th, x * 2:x * 2 + tw] = o[oy:oy + th, ox:ox + tw]
    return np.clip(out * 255, 0, 255).astype(np.uint8)[:, :, ::-1]
src, dst = sys.argv[1], sys.argv[2]
if src.lower().endswith((".jpg", ".png", ".jpeg")):
    cv2.imwrite(dst, up(cv2.imread(src))); sys.exit()
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 30
ok, f = cap.read(); H, W = f.shape[0] * 2, f.shape[1] * 2
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                      "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
n = 0
while ok:
    p.stdin.write(up(f).tobytes()); n += 1; ok, f = cap.read()
p.stdin.close(); p.wait(); print("frames", n)
