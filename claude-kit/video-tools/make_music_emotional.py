#!/usr/bin/env python3
"""Original emotional piano track (120 BPM grid, half-time feel) for 'growing up' / memories videos.
Usage: python3 make_music_emotional.py out.wav length_s drop_s"""
import sys, numpy as np, soundfile as sf
from pedalboard import Pedalboard, Reverb, Compressor, Limiter, LowpassFilter

SR = 44100
L, DROP = float(sys.argv[2]), float(sys.argv[3])
N = int(L * SR)
rng = np.random.default_rng(5)
out = {k: np.zeros(N) for k in ("piano", "pad", "drums", "fx", "bass")}


def add(k, sig, at):
    i = int(at * SR)
    if 0 <= i < N:
        sig = sig[: N - i]
        out[k][i:i + len(sig)] += sig


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


def piano(m, d=1.6, v=0.25):
    t = np.arange(int(d * SR)) / SR
    f = note(m)
    s = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (1.5 + h)) for h, a in ((1, 1), (2, .45), (3, .2), (4, .1)))
    return s * np.minimum(1, t / 0.004) * v


# Am - F - C - G, one chord per 2 s
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
MEL = [76, 74, 72, 74, 72, 71, 72, 67]  # simple top line, one note per beat-pair
t = 0.0
k = 0
while t < L - 0.5:
    ch = CH[int(t // 2) % 4]
    arp = [ch[0], ch[1], ch[2], ch[1] + 12]
    add("piano", piano(arp[k % 4] + 12, v=0.16), t)       # 8th-note arpeggio
    if k % 4 == 0:
        add("piano", piano(ch[0] - 12, 2.0, 0.22), t)      # left hand bass note
    if t >= DROP and k % 2 == 0:
        add("piano", piano(MEL[(k // 2) % 8] + 12, 1.2, 0.2), t)  # melody after the drop
    k += 1
    t += 0.25

for i in range(int(L // 2) + 1):  # warm pad
    ch = CH[i % 4]
    tt = np.arange(int(2.0 * SR)) / SR
    env = np.minimum(1, tt / 0.5) * np.minimum(1, (2.0 - tt) / 0.5)
    add("pad", sum(np.sin(2 * np.pi * note(m) * tt) for m in ch) * env * 0.05, i * 2)

# soft half-time beat from the drop: kick on the beat, snap every second
b = DROP
while b < L - 1.0:
    tt = np.arange(int(0.3 * SR)) / SR
    add("drums", np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.1) * 0.7, b)
    if round((b - DROP) / 0.5) % 2 == 1:
        tt = np.arange(int(0.15 * SR)) / SR
        add("drums", rng.standard_normal(len(tt)) * np.exp(-tt / 0.03) * 0.25, b)
    add("bass", piano(CH[int(b // 2) % 4][0] - 24, 0.5, 0.35), b)
    b += 0.5

# riser + reverse-swell into the drop
tt = np.arange(int(1.0 * SR)) / SR
add("fx", rng.standard_normal(len(tt)) * (tt / 1.0) ** 3 * 0.12, DROP - 1.0)

P = lambda k, fx: fx(out[k].astype(np.float32), SR)
mix = (P("piano", Pedalboard([Reverb(room_size=0.75, wet_level=0.35)])) +
       P("pad", Pedalboard([LowpassFilter(1800), Reverb(room_size=0.9, wet_level=0.5)])) +
       P("drums", Pedalboard([Compressor(threshold_db=-14, ratio=4)])) +
       P("bass", Pedalboard([LowpassFilter(300)])) + out["fx"].astype(np.float32))
mix = Pedalboard([Compressor(threshold_db=-12, ratio=2.5), Limiter(threshold_db=-1.5)])(mix, SR)
sf.write(sys.argv[1], np.stack([mix, mix], 1), SR)
print("music saved")
