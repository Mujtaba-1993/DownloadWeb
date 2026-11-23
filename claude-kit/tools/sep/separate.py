# Split a file into vocals + accompaniment with htdemucs (no pip install: repo + julius on sys.path).
import sys, os
sys.path[:0] = [os.path.expanduser('~/tools/sep/demucs'), os.path.expanduser('~/tools/sep/julius'), os.path.expanduser('~/tools/sep/stubs')]
import torch, numpy as np, soundfile as sf, subprocess
from demucs.states import load_model
from demucs.apply import apply_model
src, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
pkg = torch.load(os.path.expanduser('~/tools/sep/htdemucs.th'), map_location='cpu', weights_only=False)
model = load_model(pkg); model.eval(); sr = model.samplerate
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
wav = torch.from_numpy(np.frombuffer(raw, np.float32).copy().reshape(-1, 2).T)
ref = wav.mean(0); wav = (wav - ref.mean()) / (ref.std() + 1e-8)
torch.set_num_threads(4)
with torch.no_grad(): out = apply_model(model, wav[None], shifts=1, split=True, overlap=.25, progress=False)[0]
out = out * (ref.std() + 1e-8) + ref.mean()
names = model.sources; v = out[names.index('vocals')]; acc = out.sum(0) - v
sf.write(os.path.join(outdir, 'vocals.wav'), v.T.numpy(), sr); sf.write(os.path.join(outdir, 'music.wav'), acc.T.numpy(), sr)
print('ok', names, round(wav.shape[1] / sr, 2))
