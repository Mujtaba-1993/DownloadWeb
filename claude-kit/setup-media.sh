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

# --- GitHub skills added 2026-11-23: idea engine, reel review, stickman, film styles (all MIT, pinned) ---
gskill() { # gskill <repo> <commit> <dir> <path-in-repo>...
  r=$1; c=$2; d=$3; shift 3; rm -rf "$d"; git init -q "$d" && git -C "$d" sparse-checkout set --no-cone $(printf '/%s/ ' "$@") \
    && git -C "$d" fetch -q --depth 1 --filter=blob:none "https://github.com/$r.git" "$c" \
    && git -C "$d" checkout -q FETCH_HEAD && for p in "$@"; do n=$(basename "$p"); rm -rf ~/.claude/skills/$n; cp -r "$d/$p" ~/.claude/skills/$n; done
}
gskill opus-pro/reel-runbook 68b9003c2b0d62ef8a52179ad4f05e6170c68601 /tmp/g-rr skills/hooks skills/topics || true
gskill vyralcontent/content-skills 349e495d97029a3e6303a7510e3f39c73f36d8fe /tmp/g-vy skills/viral-short-form-ideas skills/viral-hooks skills/viral-instagram-reels || true
gskill coreyhaines31/marketingskills 8fd2fcade2fd6629026e9dfe6d133b55b36968b9 /tmp/g-mk skills/ad-creative || true
gskill OpenClaudia/openclaudia-skills 03557e315375f709d71eaf59c00094a21292f660 /tmp/g-oc skills/video-ad-analysis || true
gskill rampstackco/claude-skills 9d281db6e7a5c4a0084ba89c91633a07f5f7e42b /tmp/g-rs skills/ads-creative-development || true
gskill superamped/ai-marketing-skills 5d01d5428862c4d2c2ffb86338088886c6b0f97f /tmp/g-sa skills/research/competitor-content-analysis || true
gskill slaw469/claude-content-system 0080a802f5f68db558f5cd09e4ab4dc734799d9a /tmp/g-sl skills/content-ideation || true
gskill Melvynx/video-agent-skills f4542923f7f796a1fa0e544cbfc1109d5eec87d8 /tmp/g-mx skills/outliers || true
gskill alirezarezvani/claude-code-skill-factory ba18b31703542d9d7eda5f9ba94f0df65a59dddf /tmp/g-ar generated-skills/content-trend-researcher || true
gskill Samin12/content-skill-pack d8359683a062023e28c5864a74aefe07970d5cdb /tmp/g-csp skills/ideation || true
gskill NousResearch/hermes-agent 45665879083359efe1fc5134ddd2f5dffd804139 /tmp/g-her optional-skills/creative/creative-ideation || true
gskill kaomei/stickman-video-director 7e6dd4241a73abc1e97341136c36cbff73c22458 /tmp/g-stk skills/directing-stickman-videos || true
gskill lemomo-ai/lemo-opuscar 8ca0dd805e214bcc1d30714cd5b9d21cc02a454b /tmp/g-lemo plugin/skills/lemo-opuscar || true
gskill obra/superpowers 22f0b463e7a5e579904dd6211a520321035526f7 /tmp/g-sp skills/brainstorming || true
gskill product-on-purpose/thinking-framework-skills 6ab95db2d6469e4b65f3eb3ed265e46a6a1e69a8 /tmp/g-tf skills/think-scamper skills/think-far-analogy-ideation skills/think-assumption-reversal skills/think-morphological-analysis skills/think-brainwriting skills/think-role-storming skills/think-question-burst skills/think-frame-creation skills/think-random-frameworks skills/think-problem-restatement skills/think-abstraction-laddering skills/think-framework-advisor skills/think-contradiction-resolution skills/think-premortem skills/think-red-team-light || true
rm -rf /tmp/g-rr /tmp/g-vy /tmp/g-csp /tmp/g-her /tmp/g-stk /tmp/g-lemo
mkdir -p ~/films/nibras/code && cp "$KD"/films/nibras-code/* ~/films/nibras/code/ 2>/dev/null || true

# --- voice/music separation (Demucs htdemucs, MIT, run from source) + Gemini TTS batch tool, added 2026-11-23 ---
mkdir -p ~/tools/sep && cp -r "$KD"/tools/sep/* ~/tools/sep/ && cp "$KD"/tools/gemini_tts_batch.py ~/tools/ 2>/dev/null || true
[ -d ~/tools/sep/demucs ] || git clone -q --depth 1 https://github.com/facebookresearch/demucs.git ~/tools/sep/demucs || true
[ -d ~/tools/sep/julius ] || git clone -q --depth 1 https://github.com/adefossez/julius.git ~/tools/sep/julius || true
[ -s ~/tools/sep/htdemucs.th ] || curl -sfL -o ~/tools/sep/htdemucs.th https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/955717e8-8726e21a.th || true
