# Rain film: cheeky marimba groove + rain/foley + Kokoro VO. End card has no voice.
import numpy as np, soundfile as sf, soxr
from scipy.signal import butter, sosfilt
SR, DUR = 44100, 22.4
N = int(SR * DUR); rng = np.random.default_rng(12)
def buf(): return np.zeros(N)
def put(dst, src, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: src = src[:N - i]; dst[i:i + len(src)] += src * g
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, btype='high', fs=SR, output='sos'), x)
def f(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=.003, d=.2): t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def marimba(m, dur=.5): n = int(dur*SR); t = np.arange(n)/SR; fr = f(m); return (np.sin(2*np.pi*fr*t) + .3*np.sin(2*np.pi*fr*4*t)*np.exp(-t*30)) * env(n, .002, .16)
def pluck(m, dur=.4): n = int(dur*SR); t = np.arange(n)/SR; fr = f(m); return lp(sum(np.sin(2*np.pi*fr*k*t)/k*np.exp(-t*(6+4*k)) for k in range(1,6)), 1200) * env(n, .003, .18)
def plink(fr): n = int(.12*SR); t = np.arange(n)/SR; return np.sin(2*np.pi*(fr + 600*np.exp(-t*80))*t) * np.exp(-t*45)
def noise(d): return rng.standard_normal(int(d*SR))
music, fx, voice = buf(), buf(), buf()
# groove: 104 bpm, C major-ish cheeky line, rests under the hook
bt = 60/104; mel = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 74, 71]
t0 = 0.0; k = 0
while t0 < 18.3:
    if not (13.55 < t0 < 14.15):
        put(music, marimba(mel[k % 16]), t0, .32 if k % 2 == 0 else .22)
        if k % 4 == 0: put(music, pluck([48, 53, 55, 48][(k // 4) % 4]), t0, .6)
    t0 += bt / 2; k += 1
for m in (60, 64, 67, 72): put(music, marimba(m, 1.6), 14.15, .25)                 # resolve after the rewind
for i, m in enumerate((72, 76, 79, 84)): put(music, marimba(m, 1.2), 18.45 + i * .22, .3)   # end card sting
for m in (48, 60, 64, 67): put(music, pluck(m, 1.6), 19.4, .45)
# rain bed + thunder at frame 0
rain = hp(lp(noise(DUR), 6000), 900); lvl = np.interp(np.arange(N)/SR, [0, .2, 13.5, 14.1, 18.3, 22.4], [.8, 1, 1, .2, .45, .45]); fx += rain * lvl * .06
th = lp(noise(2.2), 140) * np.exp(-np.arange(int(2.2*SR))/SR*1.6); put(fx, th, 0.0, 1.2)
crk = hp(noise(.25), 2000) * np.exp(-np.arange(int(.25*SR))/SR*18); put(fx, crk, .22, .5)
for k in range(9): put(fx, plink(700 + 200*rng.random()), .5 + k * .31, .35)          # drips on the rug
put(fx, lp(noise(1.6), 2500) * np.sin(np.pi*np.arange(int(1.6*SR))/(1.6*SR)), 3.1, .25)  # dust gust
gur = bp(noise(1.6), 200, 900) * (.5 + .5*np.sin(2*np.pi*7*np.arange(int(1.6*SR))/SR)); put(fx, gur, 5.0, .25)   # channel filling
spl = bp(noise(.6), 400, 3000) * np.exp(-np.arange(int(.6*SR))/SR*6); put(fx, spl, 6.4, .5)
for tc in (8.6, 9.1, 9.6): put(fx, hp(noise(.08), 1500) * np.exp(-np.arange(int(.08*SR))/SR*60), tc, .7)   # gasket cracks
for tc in (11.05, 11.5, 11.95): put(fx, bp(noise(.18), 1500, 6000) * np.exp(-np.arange(int(.18*SR))/SR*20), tc, .45)   # pages
put(fx, plink(260), 12.25, .7)                                                          # slipper plop
rw = noise(.55); n = len(rw); out = np.zeros(n)
for i in range(0, n, 2048): c = 600 + 5000 * i / n; out[i:i+2048] = bp(rw[i:i+2048], c*.7, c*1.3)
put(fx, out * np.sin(np.pi*np.arange(n)/n), 13.6, .5)                                  # rewind
for b in (3.0, 7.4, 10.9, 13.6, 18.4): put(fx, lp(noise(.3), 3000) * np.sin(np.pi*np.arange(int(.3*SR))/(.3*SR))**2, b - .15, .22)   # card flips
put(fx, plink(1500), 14.2, .4); put(fx, plink(820), 21.9, .35); put(fx, plink(1900), 10.95, .3); put(fx, plink(1200), 15.25, .35); put(fx, plink(1700), 16.5, .35)
for i, t1 in enumerate((.05, 3.40, 7.65, 11.10, 13.90, 16.45), 1):
    x, sr = sf.read(f'audio/gm_{i}.wav'); x = x if x.ndim == 1 else x.mean(1); x = soxr.resample(x, sr, SR); put(voice, x / (np.abs(x).max() + 1e-9), t1, .85)
e = np.abs(voice); w = int(.12*SR); e = np.convolve(e, np.ones(w)/w, 'same'); duck = np.convolve(np.clip(e/.05, 0, 1), np.ones(w)/w, 'same')
mix = voice + music * (1 - .62*duck) * .85 + fx * (1 - .45*duck)
fade = int(.04*SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix*1.1)/1.1; mix /= max(1e-9, np.abs(mix).max()) / .9
sf.write('audio/mix_raw.wav', np.stack([mix, mix], 1), SR); print('mix ok', round(len(mix)/SR, 2))
