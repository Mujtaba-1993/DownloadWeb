# Video workflow (lessons learned)

## Before any job
1. `skillfind <words>` — search 3,000+ skills (agentic-awesome-skills index); use a ready skill before writing tools.
2. Installed skills worth using first: claude-animated-shorts (cartoon story shorts), heditor (vertical edits, thriller/trailer styles),
   OpenMontage skills (remotion, ffmpeg, video-edit, video-understand, ...), sfxmint (free CC0 SFX: `horror-game` set etc.),
   creative-psychology-hooks, emotional-arc-designer, remotion-captions, comment-to-dm-cta.
3. OpenMontage readiness: `cd ~/skills-src/OpenMontage && python3 -c "from tools.tool_registry import registry; registry.discover(); ..."`

## Rules (to save time and credits)
- Low-res preview of a few frames first; full render only after checking it.
- Target < 60 s for Reels/Snap. Check length before rendering.
- Final loudness -14 LUFS; encode crf ~21, maxrate 10M (grain explodes file size otherwise).
- Private family footage: never publish, never push videos; deliver only via the session.

## Known limits (no GPU here)
- Real AI motion (image-to-video) needs a paid key: Higgsfield / Kling / Runway / Veo (skills installed).
- Most natural voice: user's own recording (sync captions with faster-whisper) or ElevenLabs key. edge-tts sounds robotic to the user.
- SDXL-Turbo images ~15 s each on CPU; Depth-Anything for 2.5D camera moves.

## Scripts here
- horror_story.py: SDXL-Turbo images + depth camera + edge-tts word captions + sound design.
- juha_anim.py / juha_voice.py: 2D vector story animation (user found it weak; prefer claude-animated-shorts).
- auto_montage.py, make_music.py, make_music_emotional.py, install.sh, skillfind.
