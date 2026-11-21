#!/bin/bash
# Video production tools + skills (installed by the cloud environment setup script)
cd ~ || true
apt-get install -y -q libcairo2-dev libpango1.0-dev pkg-config >/dev/null 2>&1 || true
pip install -q moviepy auto-editor "scenedetect[opencv-headless]" yt-dlp librosa faster-whisper pedalboard \
  "rembg[cpu]" edge-tts pycairo diffusers transformers accelerate || true
pip install -q torch --index-url https://download.pytorch.org/whl/cpu || true
pip install -q "pillow>=12.2.0" || true
mkdir -p ~/.fonts ~/models && curl -sSfL -o ~/.fonts/Lalezar-Regular.ttf \
  https://raw.githubusercontent.com/google/fonts/main/ofl/lalezar/Lalezar-Regular.ttf && fc-cache -f || true
curl -sSfL -o ~/models/yunet.onnx https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx || true
mkdir -p ~/skills-src ~/.claude/skills && cd ~/skills-src && for x in \
  OpenMontageInc/OpenMontage@2e003e65fa99a0f329478a2c1cdcf26bc481933a \
  mromidev/claude-animated-shorts@e3b817b6afc6cd413466d43f11ba31209e034bbf \
  Vincentwei1021/video-shotcraft@075b548c2405a07b77129eb448b0b504fc60dea3 \
  pycodebr/heditor@4f19f560a5a26f3b32a3ea4114fa8b42b84c51f8; do r=${x%@*}; c=${x#*@}; d=$(basename $r); \
  [ -d $d/.git ] || { git init -q $d && git -C $d fetch -q --depth 1 https://github.com/$r.git $c && git -C $d checkout -q FETCH_HEAD; }; \
done || true
cp -r ~/skills-src/OpenMontage/.claude/skills/. ~/.claude/skills/ 2>/dev/null || true
for n in claude-animated-shorts video-shotcraft; do mkdir -p ~/.claude/skills/$n && cp -r ~/skills-src/$n/. ~/.claude/skills/$n/; done || true
mkdir -p ~/.claude/skills/heditor && cp -r ~/skills-src/heditor/skills/heditor/. ~/.claude/skills/heditor/ || true
pip install -q -r ~/skills-src/OpenMontage/requirements.txt || true
(cd ~/skills-src/OpenMontage/remotion-composer && npm install --silent --no-audit --no-fund) || true
pip install -q mediapipe youtube-transcript-api || true
PUPPETEER_SKIP_DOWNLOAD=1 npm install -g --silent @mermaid-js/mermaid-cli || true
cd ~/skills-src && [ -d BMTS-Lite/.git ] || { git init -q BMTS-Lite && git -C BMTS-Lite fetch -q --depth 1 https://github.com/sharbvane/BMTS-Lite.git d0b7c1fd5b96fb72d1378950fde8a5673a0813d1 && git -C BMTS-Lite checkout -q FETCH_HEAD; } || true
(cd ~/skills-src/BMTS-Lite && uv venv -q -p 3.11 .venv && uv pip install -q -p .venv/bin/python -r requirements-runtime.txt) || true
AAS=4a52ab5ef117bdce2c6ba8d87dd64df0c840dfea; SK="sfxmint remotion-captions creative-psychology-hooks emotional-arc-designer comment-to-dm-cta"
cd ~/skills-src && [ -d agentic-awesome-skills/.git ] || { git init -q agentic-awesome-skills && cd agentic-awesome-skills && \
  git sparse-checkout set --no-cone /skills_index.json $(for s in $SK; do echo /skills/$s/; done) && \
  git fetch -q --depth 1 --filter=blob:none https://github.com/sickn33/agentic-awesome-skills.git $AAS && git checkout -q FETCH_HEAD; } || true
for s in $SK; do mkdir -p ~/.claude/skills/$s && cp -r ~/skills-src/agentic-awesome-skills/skills/$s/. ~/.claude/skills/$s/; done || true
mkdir -p ~/bin && printf '%s\n' '#!/usr/bin/env python3' 'import json,sys,os' \
 'q=[w.lower() for w in sys.argv[1:]];d=json.load(open(os.path.expanduser("~/skills-src/agentic-awesome-skills/skills_index.json")))' \
 'r=sorted(((sum((i["id"]+" "+i["description"]).lower().count(w) for w in q),i["id"],i["description"][:110]) for i in d),reverse=True)' \
 '[print(f"{x[1]} | {x[2]}") for x in r[:25] if x[0]]' > ~/bin/skillfind && chmod +x ~/bin/skillfind || true
cd ~ || true
