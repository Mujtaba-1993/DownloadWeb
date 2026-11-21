import sys
from silma_tts.api import SilmaTTS
ref, reftext, out = sys.argv[1], sys.argv[2], sys.argv[3]
m = SilmaTTS(device='cpu')
for i, line in enumerate(sys.stdin.read().strip().split('\n')):
    m.infer(ref_file=ref, ref_text=reftext, gen_text=line, nfe_step=32, speed=0.95, file_wave=f'{out}_{i+1}.wav', remove_silence=True, show_info=lambda *a: None)
    print('ok', i + 1, flush=True)
