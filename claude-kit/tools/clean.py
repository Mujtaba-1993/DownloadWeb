#!/usr/bin/env python3
"""Remove clutter: auto-detect cardboard on floor + manual boxes, inpaint with LaMa ONNX tile-by-tile."""
import cv2, numpy as np, onnxruntime as ort, os, json, sys
S = ort.InferenceSession(os.path.expanduser("~/.cache/lama/lama.onnx"), providers=["CPUExecutionProvider"])

def lama_tile(img, m):
    i = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)[:, :, ::-1].astype(np.float32) / 255
    k = (cv2.resize(m, (512, 512), interpolation=cv2.INTER_NEAREST) > 127).astype(np.float32)
    o = S.run(None, {"image": i.transpose(2, 0, 1)[None], "mask": k[None, None]})[0][0].transpose(1, 2, 0)
    if o.max() <= 1.5: o = o * 255
    return np.clip(o, 0, 255).astype(np.uint8)[:, :, ::-1]

def inpaint(img, mask):
    out = img.copy(); H, W = mask.shape
    n, lab, st, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8))
    for c in range(1, n):
        x, y, w, h = st[c, :4]; side = int(max(256, 2.2 * max(w, h)))
        cx, cy = x + w // 2, y + h // 2
        x0, y0 = max(0, min(W - side, cx - side // 2)), max(0, min(H - side, cy - side // 2))
        x1, y1 = min(W, x0 + side), min(H, y0 + side)
        crop, cm = out[y0:y1, x0:x1], ((lab[y0:y1, x0:x1] == c) * 255).astype(np.uint8)
        res = cv2.resize(lama_tile(crop, cm), (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
        a = cv2.GaussianBlur(cv2.dilate(cm, np.ones((9, 9), np.uint8)), (15, 15), 0)[..., None] / 255.0
        out[y0:y1, x0:x1] = (res * a + crop * (1 - a)).astype(np.uint8)
    return out

def card_mask(img, top=0.62):
    h = img.shape[0]; hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (5, 50, 60), (25, 200, 215)); m[: int(h * top)] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, l, st, _ = cv2.connectedComponentsWithStats(m); out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, 4] > 150: out[l == i] = 255
    return cv2.dilate(out, np.ones((21, 21), np.uint8))

if __name__ == "__main__":
    src, dst, auto, boxes = sys.argv[1], sys.argv[2], sys.argv[3] == "1", json.loads(sys.argv[4])
    img = cv2.imread(src); m = card_mask(img) if auto else np.zeros(img.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes: m[y0:y1, x0:x1] = 255
    cv2.imwrite(dst.replace(".jpg", "_mask.png"), m)
    cv2.imwrite(dst, inpaint(img, m), [cv2.IMWRITE_JPEG_QUALITY, 95]); print(dst, img.shape)
