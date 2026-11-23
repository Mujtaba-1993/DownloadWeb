---
name: nibras-advisors
description: Advisor panel that reviews EVERY Al Nibras video before it is delivered (and can vote on video ideas before one is built). Four advisors, each built on a GitHub skill, review in parallel and a chair merges their verdicts into one score and a short fix list. Use automatically after rendering any Nibras video, or when the user says "المستشارين", "خل المستشارين يشوفونه", "راجع الفيديو".
---

# Nibras advisor panel (مجلس المستشارين)

Standing rule from the user (2026-11-23): "حط لي مستشارين على كل فديو، استخدم سكلز من قت هب".
Run this panel on every rendered Nibras video BEFORE sending it to the user. Fix what they agree on (one fix round), then deliver with the panel's scorecard.

## The four seats (spawn them in parallel, one Agent each, general-purpose)

| Seat | Built on (GitHub) | Judges |
|---|---|---|
| 1. مستشار الهوك والاحتفاظ | `~/.claude/skills/hooks` (opus-pro/reel-runbook, MIT) Review mode: `python3 ~/.claude/skills/hooks/scripts/analyze.py VIDEO --out DIR`, then its rubric | first frame, first 3 s, rehooks every 5-8 s, ending/loop. Score /10 with timestamps |
| 2. مستشار علم النفس الإعلاني | `~/.claude/skills/creative-psychology-hooks` (gomarble-ai/marketing-agent) + `marketing-psychology` | the mechanism (curiosity, proof, loss), offer and CTA strength, honesty of claims |
| 3. مستشار الجودة البصرية | `~/.claude/skills/media-judge` | broken/blank frames, text readability on a phone, clutter, what leads the eye, colour appeal |
| 4. صوت العميل | persona: home owner in Dammam/Khobar/Qatif, 30-55, building or renovating; reads `nibras-content-expert` SKILL.md (taste + feedback notes, rules 9, 29-31) | "would I stop scrolling, understand it, trust it, and message on WhatsApp?" Dialect, colours, clarity |

Each seat gets: the video path, a 1-line brief of what the video is for, and the instruction to extract frames itself (ffmpeg, 1 fps + the first 3 s at 6 fps) and LOOK at them. Each returns: score /10, top 3 problems with timestamps, top 3 keeps, one-line verdict (انشر / عدّل / أعد). Keep each report under 250 words.

## The chair (you)
Merge into one Arabic scorecard: each seat's score + verdict, the problems 2+ seats agree on first, then a single fix list (max 5). Apply the fixes in one round, re-render, and tell the user what the panel said in 6-10 lines.

## Idea vote mode
Before building, give the panel the candidate ideas (text only, no video): each seat ranks them and names the risk. Cheaper: run seats 1, 2 and 4 only.

## Cost note
The user wants to save credits: keep briefs short, cap reports, never re-run the whole panel after the fix round (only re-check the fixed items yourself).
