#!/bin/bash
# Media/video toolkit for Al Nibras content (installed by the cloud environment setup script)
cd ~ || true; KD=$(cd "$(dirname "$0")" && pwd)
cp -r "$KD"/skills/* ~/.claude/skills/ 2>/dev/null; mkdir -p ~/tools/remotion; cp "$KD"/tools/*.py ~/tools/; cp -r "$KD"/tools/remotion/* ~/tools/remotion/
pip install -q --index-url https://download.pytorch.org/whl/cpu torch torchvision || true
pip install -q "rembg[cpu]" transformers opencv-python-headless spandrel librosa "scenedetect[opencv-headless]" auto-editor ffmpeg-normalize mediapipe ccvfi piper-tts "git+https://github.com/JuneYaooo/rea-video@86486c6e104b917fb4b6a2d6501134686c05b219" || true
git clone -q --depth 1 https://github.com/JuneYaooo/rea-video /tmp/rea && rm -rf ~/.claude/skills/rea-video && cp -r /tmp/rea/skills/rea-video ~/.claude/skills/ || true
mkdir -p ~/.cache/lama ~/.cache/esrgan ~/tools/piper ~/tools/sfx ~/tools/remotion/public && curl -sfL -o ~/.fonts/Lalezar.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/lalezar/Lalezar-Regular.ttf && fc-cache -f >/dev/null || true
[ -f ~/.cache/lama/lama.onnx ] || curl -sfL -o ~/.cache/lama/lama.onnx https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx || true
[ -f ~/.cache/esrgan/RealESRGAN_x2plus.pth ] || curl -sfL -o ~/.cache/esrgan/RealESRGAN_x2plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth || true
PV=https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium; for f in ar_JO-kareem-medium.onnx ar_JO-kareem-medium.onnx.json; do [ -f ~/tools/piper/$f ] || curl -sfL -o ~/tools/piper/$f $PV/$f; done || true
(cd ~/tools/remotion && cp ~/.fonts/Tajawal-Bold.ttf ~/.fonts/Lalezar.ttf public/ && npm i --silent remotion@4.0.242 @remotion/cli@4.0.242 react@18.3.1 react-dom@18.3.1) || true
for q in whoosh impact riser transition door glass click; do curl -sL -A Mozilla/5.0 "https://mixkit.co/free-sound-effects/$q/" | grep -aoE 'https://assets\.mixkit\.co/active_storage/sfx/[0-9]+/[0-9]+-preview\.mp3' | sort -u | head -3 | while read u; do curl -sfL -o ~/tools/sfx/${q}_$(basename $u) $u; done; done || true
# --- added: voice tools (isolated venvs), music, other session's video tools ---
mkdir -p ~/tools/music && for n in 440 441 466 13; do [ -f ~/tools/music/$n.mp3 ] || curl -sfL -o ~/tools/music/$n.mp3 https://assets.mixkit.co/music/$n/$n.mp3; done || true
pip install -q edge-tts || true
[ -x ~/tools/voice-venv/bin/python ] || { python3 -m venv ~/tools/voice-venv && ~/tools/voice-venv/bin/pip install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu && ~/tools/voice-venv/bin/pip install -q deepfilternet soundfile safetensors pandas librosa omegaconf rich tqdm tabulate matplotlib scipy resampy && ~/tools/voice-venv/bin/pip install -q --no-deps resemble-enhance && ~/tools/voice-venv/bin/pip install -q "numpy>=2,<2.3"; } || true
VP=$(~/tools/voice-venv/bin/python -c "import site;print(site.getsitepackages()[0])" 2>/dev/null)
if [ -n "$VP" ]; then sed -i 's/^from torchaudio.backend.common import AudioMetaData/AudioMetaData = object/' $VP/df/io.py 2>/dev/null
  mkdir -p $VP/deepspeed/runtime $VP/deepspeed/accelerator; printf 'class DeepSpeedConfig: pass\ndef init_distributed(*a,**k): pass\n' > $VP/deepspeed/__init__.py
  echo 'def clip_grad_norm_(*a,**k): pass' > $VP/deepspeed/runtime/utils.py; echo 'class DeepSpeedEngine: pass' > $VP/deepspeed/runtime/engine.py; touch $VP/deepspeed/runtime/__init__.py; echo 'def get_accelerator(): return None' > $VP/deepspeed/accelerator/__init__.py
  R=$VP/resemble_enhance/model_repo/enhancer_stage2; mkdir -p $R/ds/G/default; for f in hparams.yaml ds/G/latest ds/G/default/mp_rank_00_model_states.pt; do [ -f $R/$f ] || curl -sfL -o $R/$f https://huggingface.co/ResembleAI/resemble-enhance/resolve/main/enhancer_stage2/$f; done; fi
D=~/tools/models/DeepFilterNet3; mkdir -p $D/checkpoints; [ -f $D/checkpoints/model_120.ckpt.best ] || { curl -sfL -o $D/config.ini https://huggingface.co/fal/DeepFilterNet3/resolve/main/config.ini && curl -sfL -o $D/m.safetensors https://huggingface.co/fal/DeepFilterNet3/resolve/main/model.safetensors && ~/tools/voice-venv/bin/python -c "from safetensors.torch import load_file;import torch;torch.save(load_file('$D/m.safetensors'),'$D/checkpoints/model_120.ckpt.best')"; } || true
[ -x ~/tools/tts-venv/bin/python ] || { python3 -m venv ~/tools/tts-venv && ~/tools/tts-venv/bin/pip install -q torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu && ~/tools/tts-venv/bin/pip install -q --no-deps chatterbox-tts==0.1.7 && ~/tools/tts-venv/bin/pip install -q "numpy>=2" librosa==0.11.0 s3tokenizer transformers==5.2.0 diffusers==0.29.0 "resemble-perth>=1.0.0" conformer==0.3.2 safetensors==0.5.3 pyloudnorm omegaconf soundfile; } || true
bash "$KD"/video-tools/setup-video.sh || true
pip install -q "numpy>=2.1" || true
# --- pro-motion runtime deps + SILMA Arabic TTS ---
sed -i "s#puppeteer.launch({ headless: 'new', #puppeteer.launch({ headless: 'new', args: ['--no-sandbox'], #" ~/.claude/skills/pro-motion/scripts/render-fast.js 2>/dev/null || true
[ -d ~/films/nibras/tools/node_modules/puppeteer ] || CHROME=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1) bash ~/.claude/skills/pro-motion/scripts/setup.sh ~/films/nibras --yes || true
[ -x ~/tools/silma-venv/bin/python ] || { python3 -m venv ~/tools/silma-venv && ~/tools/silma-venv/bin/pip install -q torch torchaudio --index-url https://download.pytorch.org/whl/cpu && ~/tools/silma-venv/bin/pip install -q silma-tts && ~/tools/silma-venv/bin/pip install -q --force-reinstall --no-deps torchvision torchaudio torchcodec --index-url https://download.pytorch.org/whl/cpu; } || true
# --- Kokoro English TTS + open-source motion libs ---
[ -x ~/tools/kokoro-venv/bin/python ] || { python3 -m venv ~/tools/kokoro-venv && ~/tools/kokoro-venv/bin/pip install -q kokoro-onnx soundfile; } || true
mkdir -p ~/tools/models/kokoro && for f in kokoro-v1.0.onnx voices-v1.0.bin; do [ -s ~/tools/models/kokoro/$f ] || curl -sfL -o ~/tools/models/kokoro/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f; done || true
mkdir -p ~/tools/motion-libs/lib && (cd ~/tools/motion-libs && { [ -f package.json ] || npm init -y >/dev/null; } && npm i --silent p5 p5.brush matter-js roughjs pixi.js pixi-filters animejs thinking-orbs && cp node_modules/p5/lib/p5.min.js node_modules/matter-js/build/matter.min.js node_modules/roughjs/bundled/rough.js node_modules/animejs/dist/bundles/anime.umd.min.js node_modules/pixi.js/dist/pixi.min.js node_modules/p5.brush/dist/p5.brush.js lib/) || true
