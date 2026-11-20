#!/usr/bin/env python3
"""Generate an original, copyright-free upbeat track (120 BPM) with intro, tape-stop, drop and outro.
Usage: python3 make_music.py out.wav [length_s] [drop_s] [stop_s]
  drop_s: where the full beat starts; stop_s: where the outro starts."""
import sys, numpy as np, soundfile as sf
from pedalboard import Pedalboard, Reverb, Compressor, Limiter, LowpassFilter, HighpassFilter

SR = 44100
L = float(sys.argv[2]) if len(sys.argv) > 2 else 26
DROP = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
OUTRO = float(sys.argv[4]) if len(sys.argv) > 4 else 22.0
BEAT = 0.5
rng = np.random.default_rng(7)
N = int(L * SR)
t_all = np.arange(N) / SR


def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig


def env(d, dec):
    t = np.arange(int(d * SR)) / SR
    return t, np.exp(-t / dec)


def kick():
    t, e = env(0.35, 0.09)
    f = 45 + 110 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * e


def clap():
    t, e = env(0.2, 0.05)
    return rng.standard_normal(len(t)) * e * 0.5


def hat():
    t, e = env(0.05, 0.012)
    n = rng.standard_normal(len(t))
    return np.diff(n, prepend=0) * e * 0.25


def saw(f, d):
    t = np.arange(int(d * SR)) / SR
    return 2 * ((t * f) % 1) - 1


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


# I - V - vi - IV in C, one chord per bar (2 s)
CHORDS = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
drums, bass, stabs, pad, fx = (np.zeros(N) for _ in range(5))

beat_t = DROP
while beat_t < OUTRO:
    b = int(round((beat_t - DROP) / BEAT))
    add(drums, kick(), beat_t)
    if b % 2 == 1:
        add(drums, clap(), beat_t)
    add(drums, hat(), beat_t + BEAT / 2)
    ch = CHORDS[(b // 4) % 4]
    for k in (0, 1):  # 8th-note bass
        _, e = env(0.22, 0.08)
        add(bass, saw(note(ch[0] - 24), 0.22) * e * 0.5, beat_t + k * BEAT / 2)
    _, e = env(0.25, 0.07)  # offbeat chord stab
    add(stabs, sum(saw(note(m + 12), 0.25) for m in ch) * e * 0.12, beat_t + BEAT / 2)
    beat_t += BEAT

# soft pad for intro and outro
for start, end in ((0, DROP - 1.0), (OUTRO, L)):
    d = max(end - start, 0.1)
    t = np.arange(int(d * SR)) / SR
    ch = CHORDS[0]
    a = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.8).clip(0)
    add(pad, sum(np.sin(2 * np.pi * note(m) * t) for m in ch) * a * 0.12, start)

# tape-stop (rewind) sound in the second before the drop
d = 1.0
t = np.arange(int(d * SR)) / SR
f = note(72) * (1 - t / d) ** 1.5 + 20
add(fx, np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.08 * (1 - t / d), DROP - d)
# riser into the drop
t = np.arange(int(1.0 * SR)) / SR
add(fx, rng.standard_normal(len(t)) * (t / 1.0) ** 2 * 0.15, DROP - 1.0)

drums = Pedalboard([Compressor(threshold_db=-12, ratio=4)])(drums.astype(np.float32), SR)
bass = Pedalboard([LowpassFilter(400)])(bass.astype(np.float32), SR)
stabs = Pedalboard([LowpassFilter(3500), Reverb(room_size=0.4, wet_level=0.25)])(stabs.astype(np.float32), SR)
pad = Pedalboard([Reverb(room_size=0.8, wet_level=0.4)])(pad.astype(np.float32), SR)
fx = Pedalboard([HighpassFilter(200)])(fx.astype(np.float32), SR)
mix = drums * 0.9 + bass * 0.8 + stabs + pad + fx
mix = Pedalboard([Compressor(threshold_db=-10, ratio=3), Limiter(threshold_db=-1)])(mix.astype(np.float32), SR)
sf.write(sys.argv[1], np.stack([mix, mix], 1), SR)
print("music saved", sys.argv[1], f"{L}s")
