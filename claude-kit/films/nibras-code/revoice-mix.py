# Original music+SFX stem (Demucs) + Arabic Gemini VO at the same placements as mix.py.
import numpy as np, soundfile as sf, soxr
SR = 44100
def load(p):
    x, sr = sf.read(p); x = x if x.ndim == 1 else x.mean(1); return soxr.resample(x, sr, SR) if sr != SR else x
def build(stem, vo, out):
    m, sr = sf.read(stem); m = soxr.resample(m, sr, SR) if sr != SR else m; N = len(m); voice = np.zeros(N)
    for f, t in vo:
        v = load(f); v = v / (np.abs(v).max() + 1e-9); i = int(t * SR); v = v[:max(0, N - i)]; voice[i:i + len(v)] += v * .9
    e = np.convolve(np.abs(voice), np.ones(int(.12 * SR)) / (.12 * SR), 'same'); duck = np.clip(e / .05, 0, 1)[:, None]
    mix = voice[:, None] + m * (.85 - .45 * duck)
    mix = np.tanh(mix * 1.05) / 1.05; mix /= np.abs(mix).max() / .9; sf.write(out, mix, SR)
build('sep_tools/music.wav', [(f'tools_c{i}.wav', t) for i, t in enumerate([.05, 2.55, 5.33, 7.60, 9.58, 12.24, 16.70], 1)], 'tools_mix2_raw.wav')
build('sep_change/music.wav', [(f'change_c{i}.wav', t) for i, t in enumerate([.05, 3.0, 6.05, 7.0, 8.15], 1)], 'change_mix2_raw.wav')
print('ok')
