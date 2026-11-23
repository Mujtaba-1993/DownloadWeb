# Thermal film: cold sparse score + camera instrument sounds + Kokoro VO. End card has no voice.
import numpy as np, soundfile as sf, soxr
from scipy.signal import butter, sosfilt
SR, DUR = 44100, 16.4
N = int(SR * DUR); rng = np.random.default_rng(9)
def buf(): return np.zeros(N)
def put(dst, src, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: src = src[:N - i]; dst[i:i + len(src)] += src * g
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)
def env(n, a=.004, d=.2): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def f(m): return 440 * 2 ** ((m - 69) / 12)
def glass(m, dur=2.0, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; fr = f(m)
    x = np.sin(2*np.pi*fr*t) + .35*np.sin(2*np.pi*fr*2.32*t)*np.exp(-t*3) + .2*np.sin(2*np.pi*fr*4.25*t)*np.exp(-t*7)
    return x * env(n, .01, dur * .35) * g
def pad(ms, dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = sum(np.sin(2*np.pi*f(m)*t + .3*np.sin(2*np.pi*.2*t)) for m in ms)
    return lp(x, 1800) * np.minimum(t / .8, 1) * np.minimum((dur - t) / .8, 1) * g / len(ms)
def beep(fr, d=.09): n = int(d * SR); t = np.arange(n) / SR; return np.sin(2*np.pi*fr*t) * np.minimum(t/.003,1) * np.minimum((d-t)/.01,1)
def sweep(d, up=True):
    n = int(d * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); k = 2048
    for i in range(0, n, k):
        p = i / n; c = 400 + 5000 * (p if up else 1 - p); out[i:i+k] = bp(x[i:i+k], c * .7, c * 1.3)
    return (out + .25*np.sin(2*np.pi*100*t)) * np.sin(np.pi * t / d) ** 1.5
def clack(): n = int(.12 * SR); t = np.arange(n) / SR; return lp(rng.standard_normal(n), 2500) * np.exp(-t*60) + .6*np.sin(2*np.pi*180*t)*np.exp(-t*50)

music, fx, voice = buf(), buf(), buf()
t = np.arange(N) / SR
fan = lp(rng.standard_normal(N), 700) * .5 + .3 * np.sin(2*np.pi*60*t) + .15*np.sin(2*np.pi*120*t)
fx += fan * .05 * (t < 13.4)
put(fx, sweep(1.4), 0, .35); put(fx, sweep(1.5, False), 8.3, .35)
put(fx, clack(), 2.6, .4); put(fx, clack(), 4.9, .45); put(fx, clack(), 7.8, .4); put(fx, clack(), 10.9, .45)
for i, tt in enumerate((1.0, 1.05)): put(fx, beep(1800, .05), tt, .25)
put(fx, beep(2200), 2.8, .35)
for k in range(8): put(fx, beep(3200, .02), 2.85 + k * .035, .12)
for k in range(3): put(fx, beep(880, .12), 3.35 + k * .3, .3); put(fx, beep(660, .12), 3.5 + k * .3, .3)
hiss = lp(bp(rng.standard_normal(int(2.9*SR)), 300, 4000), 3000); hiss *= np.sin(np.pi*np.arange(len(hiss))/len(hiss)); put(fx, hiss, 4.9, .12)
put(fx, beep(2400, .06), 9.9, .3); put(fx, beep(3000, .06), 11.65, .3)
# score: cold, sparse
put(music, pad([38, 45, 50], 7.6), 0, .5)
for i, m in enumerate((74, 77, 81, 76)): put(music, glass(m, 2.4), .2 + i * 1.3, .22)
put(music, pad([37, 44, 49], 3.0), 4.9, .45)
for i, m in enumerate((73, 76, 80)): put(music, glass(m, 2.2), 5.0 + i * .95, .18)
put(music, pad([38, 45, 53], 3.1), 7.8, .5)
for i, m in enumerate((74, 79, 83, 86)): put(music, glass(m, 2.0), 8.3 + i * .38, .2)
put(music, pad([38, 50, 54, 57, 62], 5.6), 11.6, .75)          # the one warm chord: verdict
for i, m in enumerate((74, 78, 81, 86)): put(music, glass(m, 2.4), 13.5 + i * .45, .26)
put(music, pad([50, 57, 62, 66], 2.6), 13.8, .5)
# voice (no voice on the end card)
for i, t0 in enumerate((.10, 2.85, 5.05, 7.95, 11.05), 1):
    x, sr = sf.read(f'audio/vo_{i}.wav'); x = x if x.ndim == 1 else x.mean(1); x = soxr.resample(x, sr, SR); put(voice, x / (np.abs(x).max() + 1e-9), t0, .85)
e = np.abs(voice); w = int(.12 * SR); e = np.convolve(e, np.ones(w)/w, 'same'); duck = np.convolve(np.clip(e/.05, 0, 1), np.ones(w)/w, 'same')
mix = voice + music * (1 - .64*duck) * .9 + fx * (1 - .4*duck)
mix[int(10.75*SR):int(10.95*SR)] *= .2
fade = int(.3*SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix*1.1)/1.1; mix /= max(1e-9, np.abs(mix).max()) / .9
sf.write('audio/mix_raw.wav', np.stack([mix, mix], 1), SR); print('mix ok', round(len(mix)/SR, 2))
