# AC explainer: soft pluck groove + UI/foley + SILMA Arabic VO (sped 1.3x). End card has no voice.
import numpy as np, soundfile as sf, soxr, json, re
from scipy.signal import butter, sosfilt
T = json.loads(re.search(r'= (\{.*\});', open('timings.js', encoding='utf-8').read()).group(1))
SR, DUR = 44100, T['total']; L, D = T['start'], T['dur']
N = int(SR * DUR); rng = np.random.default_rng(21)
def buf(): return np.zeros(N)
def put(dst, src, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: src = src[:N - i]; dst[i:i + len(src)] += src * g
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)
def f(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=.003, d=.2): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def bell(m, dur=.8): n = int(dur*SR); t = np.arange(n)/SR; fr = f(m); return (np.sin(2*np.pi*fr*t) + .25*np.sin(2*np.pi*fr*3*t)*np.exp(-t*12)) * env(n, .003, .3)
def pluck(m, dur=.5): n = int(dur*SR); t = np.arange(n)/SR; fr = f(m); return lp(sum(np.sin(2*np.pi*fr*k*t)/k*np.exp(-t*(5+3*k)) for k in range(1,6)), 1500) * env(n, .003, .22)
def pop(fr=900): n = int(.09*SR); t = np.arange(n)/SR; return np.sin(2*np.pi*(fr + 500*np.exp(-t*60))*t) * np.exp(-t*50)
def noise(d): return rng.standard_normal(int(d*SR))
music, fx, voice = buf(), buf(), buf()
bt = 60/92; prog = [(50, 57, 62, 66), (47, 54, 59, 62), (43, 50, 55, 59), (45, 52, 57, 61)]
t0, k = 0.0, 0
while t0 < L[8] + D[8]:
    ch = prog[(k // 8) % 4]
    put(music, pluck(ch[(k % 4)] + 12, .45), t0, .28)
    if k % 4 == 0: put(music, pluck(ch[0] - 12, .9), t0, .55)
    t0 += bt / 2; k += 1
for i, m in enumerate((74, 78, 81, 86)): put(music, bell(m, 1.4), L[8] + D[8] - 1.2 + i * .2, .22)
for b in (L[2], L[6], L[8]): put(fx, lp(noise(.3), 3000) * np.sin(np.pi*np.arange(int(.3*SR))/(.3*SR))**2, b - .15, .25)
put(fx, pop(700), .35, .5); put(fx, lp(noise(.12), 900)*np.exp(-np.arange(int(.12*SR))/SR*30), .9, .6)   # chip + X
for i in range(10): put(fx, pop(600 + 60*i), L[1] + .3 + i*.08, .12)
for a in (L[2]+.3, L[2]+1.2, L[3]+.2, L[3]+1.2, L[4]+.3, L[5]+.3, L[5]+1.5, L[5]+D[5]-.4): put(fx, pop(1000), a, .3)
hum = (np.sin(2*np.pi*58*np.arange(int((D[5])*SR))/SR) + .4*lp(noise(D[5]), 400)); put(fx, hum * np.minimum(1, np.arange(len(hum))/SR/.3), L[5], .12)
fan = lp(noise(L[6]-L[2]), 1200) * (.6 + .4*np.sin(2*np.pi*12*np.arange(int((L[6]-L[2])*SR))/SR)); put(fx, fan, L[2], .035)
for i in range(14): put(fx, pop(1500 + 300*rng.random()), L[6] + 1.2 + i*.33, .18)                         # drips
put(fx, lp(noise(.3), 500)*np.exp(-np.arange(int(.3*SR))/SR*12), L[7] + 1.9, .5)                       # clog thud
put(fx, pop(1300), L[8] + .9, .45); put(fx, pop(1600), L[8] + 1.4, .45)                                  # save / follow
for i in range(1, 10):
    x, sr = sf.read(f'audio/f_{i}.wav'); x = x if x.ndim == 1 else x.mean(1); x = soxr.resample(x, sr, SR); put(voice, x / (np.abs(x).max() + 1e-9), L[i-1], .9)
e = np.abs(voice); w = int(.12*SR); e = np.convolve(e, np.ones(w)/w, 'same'); duck = np.convolve(np.clip(e/.05, 0, 1), np.ones(w)/w, 'same')
mix = voice + music * (1 - .65*duck) * .8 + fx * (1 - .4*duck)
mix = np.tanh(mix*1.1)/1.1; mix /= max(1e-9, np.abs(mix).max()) / .9
sf.write('audio/mix_raw.wav', np.stack([mix, mix], 1), SR); print('mix ok', round(len(mix)/SR, 2))
