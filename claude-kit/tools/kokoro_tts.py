import sys, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('/root/tools/models/kokoro/kokoro-v1.0.onnx', '/root/tools/models/kokoro/voices-v1.0.bin')
voice, speed, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
for i, line in enumerate(sys.stdin.read().strip().split('\n')):
    s, sr = k.create(line, voice=voice, speed=speed, lang='en-us'); sf.write(f'{out}_{i+1}.wav', s, sr); print('ok', i + 1, round(len(s) / sr, 2), flush=True)
