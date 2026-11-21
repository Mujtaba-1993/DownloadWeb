import sys, torch, torchaudio, soundfile as sf, os
from resemble_enhance.enhancer.inference import enhance, denoise
import resemble_enhance
from pathlib import Path
run_dir = Path(os.path.join(os.path.dirname(resemble_enhance.__file__), 'model_repo', 'enhancer_stage2'))
a, sr = sf.read(sys.argv[1], dtype='float32')
if a.ndim > 1: a = a.mean(1)
mode = sys.argv[3] if len(sys.argv) > 3 else 'enhance'
x = torch.from_numpy(a)
if mode == 'denoise': out, osr = denoise(x, sr, 'cpu', run_dir=run_dir)
else: out, osr = enhance(x, sr, 'cpu', nfe=64, solver='midpoint', lambd=0.9, tau=0.5, run_dir=run_dir)
sf.write(sys.argv[2], out.numpy(), osr); print('done', osr)
