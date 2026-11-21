#!/usr/bin/env python3
"""Auto-clean a photo library: OWLv2 finds clutter (trash, rubble, boxes, buckets...), LaMa inpaints it.
usage: autoclean.py SRC_DIR DST_DIR  (writes DST/<name>.jpg + DST/report.json; originals untouched)"""
import sys, os, glob, json, cv2, numpy as np, torch
from PIL import Image
from transformers import Owlv2Processor, Owlv2ForObjectDetection
sys.path.insert(0, '/tmp/claude-0/-home-user/24b77e52-ec27-5a7d-83cc-73e00ba3eac4/scratchpad/pro')
sys.path.insert(0, os.path.expanduser('~/tools'))
from clean import inpaint  # LaMa ONNX tile inpaint
torch.set_num_threads(8)
src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
Q = ['trash', 'garbage bag', 'plastic bag', 'construction rubble', 'cardboard box', 'bucket', 'paint can',
     'plastic bottle', 'tangled cable', 'pile of debris', 'wooden plank on the floor', 'cement bag', 'broom', 'mop', 'ladder', 'paint roller', 'plastic chair']
P = Owlv2Processor.from_pretrained('google/owlv2-base-patch16-ensemble'); M = Owlv2ForObjectDetection.from_pretrained('google/owlv2-base-patch16-ensemble').eval()
rep = json.load(open(f'{dst}/report.json')) if os.path.exists(f'{dst}/report.json') else {}
files = sorted(glob.glob(f'{src}/*.jpg'))
for n, f in enumerate(files):
    name = os.path.basename(f)
    if name in rep: continue
    img = cv2.imread(f)
    if img is None: continue
    H, W = img.shape[:2]; pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    with torch.no_grad():
        inp = P(text=[Q], images=pil, return_tensors='pt'); out = M(**inp)
    side = max(H, W)  # owlv2 pads to square
    r = P.post_process_grounded_object_detection(out, threshold=0.16, target_sizes=[(side, side)])[0]
    mask = np.zeros((H, W), np.uint8); found = []
    for b, s, l in zip(r['boxes'].tolist(), r['scores'].tolist(), r['labels'].tolist()):
        x0, y0, x1, y1 = [int(v) for v in b]; x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
        area = (x1 - x0) * (y1 - y0) / (W * H)
        if area <= 0 or area > 0.10: continue                         # never erase big things (could be the product)
        cx, cy = (x0 + x1) / 2 / W, (y0 + y1) / 2 / H
        if 0.3 < cx < 0.7 and 0.2 < cy < 0.6 and area > 0.03: continue  # protect the centre subject
        pad = int(0.08 * max(x1 - x0, y1 - y0)) + 6
        mask[max(0, y0 - pad):min(H, y1 + pad), max(0, x0 - pad):min(W, x1 + pad)] = 255
        found.append([Q[l], round(s, 2), round(area, 3), [x0, y0, x1, y1]])
    if found:
        cv2.imwrite(f'{dst}/{name}', inpaint(img, mask), [cv2.IMWRITE_JPEG_QUALITY, 94])
    else:
        cv2.imwrite(f'{dst}/{name}', img, [cv2.IMWRITE_JPEG_QUALITY, 94])
    rep[name] = found
    if n % 10 == 0:
        json.dump(rep, open(f'{dst}/report.json', 'w')); print(n, len(files), name, found, flush=True)
json.dump(rep, open(f'{dst}/report.json', 'w')); print('done', sum(1 for v in rep.values() if v), 'cleaned of', len(rep))
