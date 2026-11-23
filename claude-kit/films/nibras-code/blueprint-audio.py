# Score + foley + voice mix for the blueprint water-test film. All sounds synthesised here (numpy); voice = Kokoro wavs.
import numpy as np, soundfile as sf, soxr
from scipy.signal import butter, sosfilt
SR, DUR = 44100, 17.0
N = int(SR * DUR); rng = np.random.default_rng(4)
def buf(): return np.zeros(N)
def put(dst, src, t, g=1.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    src = src[:N - i]; dst[i:i + len(src)] += src * g
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)
def env(n, a=.004, d=.2): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def f(m): return 440 * 2 ** ((m - 69) / 12)

def box(m, dur=1.4, bright=1.0):          # music-box / celesta tone
    n = int(dur * SR); t = np.arange(n) / SR; fr = f(m)
    x = np.sin(2 * np.pi * fr * t) + .45 * bright * np.sin(2 * np.pi * fr * 2.76 * t) * np.exp(-t * 9) + .25 * np.sin(2 * np.pi * fr * 5.4 * t) * np.exp(-t * 16) + .3 * np.sin(2 * np.pi * fr * 2 * t) * np.exp(-t * 4)
    return x * env(n, .002, dur * .28)
def pizz(m, dur=.5):                       # plucked bass
    n = int(dur * SR); t = np.arange(n) / SR; fr = f(m)
    x = sum(np.sin(2 * np.pi * fr * k * t) / k * np.exp(-t * (5 + 3 * k)) for k in range(1, 7))
    return lp(x, 1400) * env(n, .003, .22)
def scratch(dur, g=1.0):                   # technical pen on paper
    n = int(dur * SR); x = bp(rng.standard_normal(n), 2200, 6000); t = np.arange(n) / SR
    return x * (.55 + .45 * np.sin(2 * np.pi * 23 * t + rng.random() * 6) ** 2) * np.minimum(t / .02, 1) * np.minimum((dur - t) / .04, 1) * g
def click(fr=3800): n = int(.05 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * fr * t) * np.exp(-t * 160) + .4 * rng.standard_normal(n) * np.exp(-t * 400)
def pat(): n = int(.08 * SR); t = np.arange(n) / SR; fr = 280 + rng.random() * 320; return np.sin(2 * np.pi * (fr + 200 * np.exp(-t * 60)) * t) * np.exp(-t * 70)

music, foley, voice = buf(), buf(), buf()
B = .5                                      # 120 bpm
OST = [74, 81, 77, 81, 76, 81, 77, 81]      # D minor ostinato (eighths)
# S1: sparse ticking motive under the water
for i in range(0, 9): put(music, box(OST[i % 8] , .6, .6), i * B / 2, .16)
for t in (0, 1.0, 2.0): put(music, pizz(38), t, .5)
# S2: one questioning figure, left unresolved
for i, m in enumerate((81, 84, 88)): put(music, box(m, 1.8), 2.5 + i * .5, .34)
put(music, box(91, 2.0, .5), 4.0, .2)
# S3: the mechanism — ostinato, voices join with each part
t = 5.0
while t < 9.7:
    k = int(round((t - 5.0) / (B / 2)))
    put(music, box(OST[k % 8], .7), t, .26)
    if k % 2 == 0: put(music, pizz(38 if (k // 2) % 4 < 2 else 33), t, .55)
    if t >= 6.5: put(music, box(OST[(k + 6) % 8] + 3, .6, .7), t, .15)     # canon voice
    if t >= 8.0 and k % 2 == 1: put(music, box(OST[k % 8] + 12, .4, .5), t, .12)
    t += B / 2
# silence 9.75-10.25, then the count: one low pluck + bell
put(music, pizz(38, .9), 10.27, .7); put(music, box(86, 2.2), 10.3, .32); put(music, box(81, 2.0), 10.9, .2)
# stamp: full cadence, D major
for m in (50, 62, 66, 69, 74, 78, 86): put(music, box(m, 3.2), 12.07, .26)
put(music, pizz(38, 1.2), 12.07, .9)
# end card: theme in augmentation
for i, m in enumerate((74, 78, 81, 78, 74, 81)): put(music, box(m, 1.6, .6), 12.85 + i * .5, .2)
for m in (50, 62, 69, 74, 78): put(music, box(m, 2.8, .5), 15.6, .16)

# foley
n1 = int(4.6 * SR); tt = np.arange(n1) / SR                                  # water spray on glass
spray = bp(rng.standard_normal(n1), 900, 7000) * (.7 + .3 * np.sin(2 * np.pi * 9 * tt) ** 2)
lvl = np.interp(tt, [0, .08, .3, 2.2, 2.4, 4.4, 4.6], [0, .2, 1, .9, .32, .28, 0])
put(foley, spray * lvl, 0, .2)
for a, d, g in ((0, .3, .5), (4.42, .85, .55), (10.25, .65, .8), (12.5, .8, .5), (13.05, .45, .4), (13.65, .4, .4)): put(foley, scratch(d), a, .16 * g)
for t0 in np.arange(2.4, 4.4, .23): put(foley, pat(), t0 + rng.random() * .1, .12)                 # drips at the sill
for t0 in np.arange(5.0, 9.75, .16): put(foley, pat(), t0 + rng.random() * .08, .1)               # drops through the section
n2 = int(4.8 * SR); t2 = np.arange(n2) / SR; put(foley, bp(rng.standard_normal(n2), 500, 3000) * np.minimum(t2 / .3, 1) * np.minimum((4.8 - t2) / .3, 1), 4.95, .035)   # rain bed
for t0 in (5.15, 6.65, 8.15): put(foley, click(), t0, .3)
nq = int(.25 * SR); tq = np.arange(nq) / SR; put(foley, np.sin(2 * np.pi * (300 + 900 * tq / .25) * tq) * np.exp(-tq * 14), 2.42, .22)   # question pop
nw = int(.45 * SR); tw = np.arange(nw) / SR; wh = rng.standard_normal(nw); wh = lp(wh, 2500) * np.sin(np.pi * tw / .45) ** 2; put(foley, wh, 4.47, .3)   # whip pan
ns = int(.5 * SR); ts = np.arange(ns) / SR                                    # rubber stamp
put(foley, np.sin(2 * np.pi * (45 + 60 * np.exp(-ts * 30)) * ts) * np.exp(-ts * 9) + .5 * lp(rng.standard_normal(ns), 900) * np.exp(-ts * 40), 12.07, .9)
put(foley, click(2600), 14.1, .22); put(foley, box(93, .8), 14.1, .12)

# voice
for i, t0 in enumerate((.10, 2.45, 5.10, 6.55, 8.05, 10.35), 1):   # end card stays silent of voice
    x, sr = sf.read(f'audio/vo_{i}.wav'); x = x if x.ndim == 1 else x.mean(1); x = soxr.resample(x, sr, SR); put(voice, x / (np.abs(x).max() + 1e-9), t0, .85)

# duck music under voice (~0.36x), foley by half
e = np.abs(voice); w = int(.12 * SR); e = np.convolve(e, np.ones(w) / w, 'same'); duck = np.clip(e / .05, 0, 1); duck = np.convolve(duck, np.ones(w) / w, 'same')
mix = voice + music * (1 - .64 * duck) * .9 + foley * (1 - .5 * duck)
mix[int(9.78 * SR):int(10.22 * SR)] *= .15                                    # the breath before the count
fade = int(.25 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix * 1.1) / 1.1; mix /= max(1e-9, np.abs(mix).max()) / .9
sf.write('audio/mix_raw.wav', np.stack([mix, mix], 1), SR); print('mix ok', round(len(mix) / SR, 2))
