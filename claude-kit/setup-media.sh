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
