# video tools: ffmpeg, moviepy, auto-editor, scenedetect, yt-dlp, librosa, faster-whisper, manim, remotion
apt-get install -y -q libcairo2-dev libpango1.0-dev pkg-config >/dev/null 2>&1 || true
pip install -q moviepy auto-editor "scenedetect[opencv-headless]" yt-dlp librosa faster-whisper || true
SP=$(python3 -c "import sysconfig;print(sysconfig.get_paths()['purelib'])"); rm -rf /tmp/srt
pip download -q --no-deps --no-binary :all: srt==3.5.3 -d /tmp/srt && tar xzf /tmp/srt/srt-3.5.3.tar.gz -C /tmp/srt \
  && cp /tmp/srt/srt-3.5.3/srt.py $SP/ && mkdir -p $SP/srt-3.5.3.dist-info \
  && printf "Metadata-Version: 2.1\nName: srt\nVersion: 3.5.3\n" > $SP/srt-3.5.3.dist-info/METADATA \
  && echo "srt.py,," > $SP/srt-3.5.3.dist-info/RECORD || true
pip install -q manim pedalboard "pillow>=12.2.0" || true
mkdir -p ~/.fonts && curl -sSfL -o ~/.fonts/Lalezar-Regular.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/lalezar/Lalezar-Regular.ttf && fc-cache -f || true
mkdir -p ~/remotion && cd ~/remotion && { [ -f package.json ] || npm init -y >/dev/null; } \
  && npm i --silent remotion @remotion/cli @remotion/renderer || true
cd ~ || true
