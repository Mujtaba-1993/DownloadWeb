import sys, torch, soundfile as sf
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
torch.set_num_threads(8)
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
ref, out = sys.argv[1], sys.argv[2]
ex = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
for i, line in enumerate(sys.stdin.read().strip().split('\n')):
    w = m.generate(line, language_id='ar', audio_prompt_path=ref or None, exaggeration=ex, cfg_weight=0.4, temperature=0.7)
    sf.write(f'{out}_{i+1}.wav', w.squeeze(0).numpy(), m.sr); print('ok', i+1, flush=True)
