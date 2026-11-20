# Video tools

- `install.sh` — reinstalls all video editing tools (ffmpeg, MoviePy, auto-editor, PySceneDetect, yt-dlp, librosa, faster-whisper, Manim, Remotion).
- `auto_montage.py` — automatic montage cut to the music beat:
  `python3 auto_montage.py CLIPS_DIR MUSIC_FILE out.mp4 [--vertical] [--max 30]`
- `make_music.py` — original copyright-free 120 BPM track (intro, tape-stop, drop, outro):
  `python3 make_music.py out.wav [length] [drop_s] [outro_s]`
- `make_music_emotional.py` — original emotional piano track for memories videos:
  `python3 make_music_emotional.py out.wav length drop_s`
