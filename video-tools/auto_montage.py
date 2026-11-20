#!/usr/bin/env python3
"""Auto montage: picks shots and cuts them to the music beat, no manual decisions.

Usage: python3 auto_montage.py CLIPS_DIR MUSIC_FILE OUT.mp4 [--vertical] [--max 30]

Decisions it makes by itself:
  - Finds every scene in every clip (PySceneDetect) and scores it by motion.
  - Finds the music beats and loudness (librosa).
  - Quiet parts of the song -> longer shots (4 beats); loud parts -> fast cuts (1-2 beats).
  - Uses the most active shots first, rotates between source clips so it never repeats back-to-back.
  - Takes the middle of each scene (skips shaky starts/ends), fades in/out at start and end.
"""
import argparse, glob, os, random
import numpy as np, librosa
from scenedetect import detect, ContentDetector
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx, afx

EXT = (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")


def scenes(path):
    clip = VideoFileClip(path)
    found = [(s.get_seconds(), e.get_seconds()) for s, e in detect(path, ContentDetector())]
    if not found:
        found = [(0, clip.duration)]
    out = []
    for s, e in found:
        if e - s < 0.6:
            continue
        # motion score: mean frame difference sampled across the scene
        ts = np.linspace(s, e - 0.05, 6)
        fr = [clip.get_frame(t).astype(np.float32) for t in ts]
        motion = float(np.mean([np.abs(a - b).mean() for a, b in zip(fr, fr[1:])]))
        out.append({"src": path, "start": s, "end": e, "motion": motion})
    clip.close()
    return out


def beat_plan(music, max_len):
    y, sr = librosa.load(music, duration=max_len)
    _, beats = librosa.beat.beat_track(y=y, sr=sr)
    bt = librosa.frames_to_time(beats, sr=sr)
    if len(bt) < 4:
        bt = np.arange(0, len(y) / sr, 0.5)
    rms = librosa.feature.rms(y=y)[0]
    rt = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    lo, hi = np.percentile(rms, 35), np.percentile(rms, 75)
    cuts, i = [], 0
    while i < len(bt) - 1:
        e = np.interp(bt[i], rt, rms)
        step = 4 if e < lo else (1 if e > hi else 2)
        j = min(i + step, len(bt) - 1)
        cuts.append((bt[i], bt[j]))
        i = j
    return cuts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips"); ap.add_argument("music"); ap.add_argument("out")
    ap.add_argument("--vertical", action="store_true", help="1080x1920 for Reels/TikTok/Shorts")
    ap.add_argument("--max", type=float, default=30, help="max length in seconds")
    a = ap.parse_args()
    random.seed(1)

    files = sorted(f for f in glob.glob(os.path.join(a.clips, "*")) if f.lower().endswith(EXT))
    pool = sorted((s for f in files for s in scenes(f)), key=lambda s: -s["motion"])
    if not pool:
        raise SystemExit("no usable clips found")
    cuts = beat_plan(a.music, a.max)
    W, H = (1080, 1920) if a.vertical else (1920, 1080)

    srcs, parts, last, k = {}, [], None, 0
    for s0, s1 in cuts:
        need = s1 - s0
        cand = [s for s in pool if s["end"] - s["start"] >= need and s["src"] != last] or \
               [s for s in pool if s["end"] - s["start"] >= need] or pool
        sc = cand[k % len(cand)]; k += 1
        last = sc["src"]
        mid = (sc["start"] + sc["end"]) / 2
        st = max(sc["start"], mid - need / 2)
        src = srcs.setdefault(sc["src"], VideoFileClip(sc["src"]))
        c = src.subclipped(st, min(st + need, src.duration)).without_audio()
        sc_ = max(W / c.w, H / c.h)
        c = c.resized(sc_).cropped(x_center=c.w * sc_ / 2, y_center=c.h * sc_ / 2, width=W, height=H)
        parts.append(c)
        print(f"{s0:6.2f}-{s1:6.2f}s  {os.path.basename(sc['src'])} @ {st:.2f}s")

    v = concatenate_videoclips(parts).with_effects([vfx.FadeIn(0.4), vfx.FadeOut(0.8)])
    music = AudioFileClip(a.music).subclipped(0, v.duration).with_effects([afx.AudioFadeOut(1.0)])
    v.with_audio(music).write_videofile(a.out, fps=30, codec="libx264", audio_codec="aac", logger=None)
    print("saved", a.out, f"({v.duration:.1f}s, {len(parts)} cuts)")


if __name__ == "__main__":
    main()
