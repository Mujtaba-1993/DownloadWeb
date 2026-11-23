# Al Nibras Aluminum — Brand File (read before any video/motion)
## Colours
- Navy #1F2A6B (logo ring) · Orange #F2641C (logo crescent, accents, CTA buttons)
- Warm gold #FFB46B (highlight word on dark) · Brown #8E5B2B (website accent)
- Paper/cream #EFEDE8 / #F3EEE6 (light scenes) · Ink #141414 / #0b0b0d (dark scenes)
## Fonts (all in ~/tools/remotion/public and ~/films/*/assets/fonts)
- Headlines: IBM Plex Sans Arabic Bold (Plex.woff2)
- Key word / emotion: Amiri Italic (AmiriIt.woff2) in orange or warm gold, 1.15-1.2x size
- Numbers & phone: Tajawal Bold (Tajawal-Bold.ttf) — Plex has no Latin digits
- Latin wordmarks (HOME etc.): Helvetica Neue 600
## Motion rules
- Voice from frame 0 + motion from frame 0 (Higgsfield: weak hooks without them).
- Hook -> promise -> value -> OPEN LOOP (black, word-by-word) -> value -> CTA.
- Transitions: sash-style sweep (aluminium bar wipe), cyan light streak, zoom-through a window.
- Springs: damping 9-14; text enters up 40-60px + blur; one SFX per move; music ducks to 0.04 during open loops.
- Show the REAL product: full door/window photo cards (white border, rounded, shadow). Never rembg cutouts of windows (glass disappears).
- End card: logo -> "النبراس للألمنيوم" -> "المعاينة مجانية" -> orange pill "واتساب 0594774046".
- Voices: English Kokoro af_heart + Arabic subtitles (user favourite) / SILMA Arabic. Never Piper/edge.
## Open-source effects (installed ~/tools/motion-libs, browser builds in lib/)
p5 + p5.brush (textured brush strokes), Matter.js (physics drops/bounces), Rough.js (hand-drawn sketch look), PixiJS + pixi-filters (glow/displacement/CRT), Anime.js (timelines), thinking-orbs (dotted particle orbs, ESM/React — usable in Remotion).

## HARD RULE (user complained 3 times): NEVER crop/zoom photos to fill 9:16. Always show the WHOLE photo (fit inside ~1040x1560) on a blurred, darkened copy of itself. Any motion zoom <= 3-4%. Check a still for "too close" before any full render.
- NO more 'pick a number / vote' formats (user annoyed, 2026-11-22). Also avoid 'personality' numbered lists.
- HARD RULE (user, 2026-11-22): ALWAYS clean every clip/photo before use: remove reflections, dirt, mess/clutter (autoclean OWLv2+LaMa for photos; delogo/inpaint + crop-free cleanup for video). Never ship uncleaned media.
- No AI 'finished room' hero shots: viewers spot them as AI (user, 2026-11-22). End on plain black logo card.
- Cutting shows ALUMINIUM shavings (silver slivers), never iron filings or sparks (user, 2026-11-22).
