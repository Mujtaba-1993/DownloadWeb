#!/usr/bin/env python3
"""Gemini TTS (free key via session proxy, header x-goog-api-key). Saudi dialect by style prompt.
usage: gemini_tts.py "النص" out.mp3 [voice=Charon] [style] [model=gemini-2.5-flash-preview-tts]"""
import sys, json, base64, subprocess, urllib.request, os, ssl
text, out = sys.argv[1], sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else 'Charon'
style = sys.argv[4] if len(sys.argv) > 4 else 'اقرأ بلهجة سعودية نجدية طبيعية، بنبرة واثقة ودافية مثل معلّق إعلان، بدون مبالغة:'
model = sys.argv[5] if len(sys.argv) > 5 else 'gemini-2.5-flash-preview-tts'
body = {"contents": [{"parts": [{"text": f"{style} {text}"}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": "proxy-injected"})
ca = '/root/.ccr/ca-bundle.crt'; ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else None
d = json.load(urllib.request.urlopen(req, timeout=180, context=ctx))
pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
raw = out + ".pcm"; open(raw, "wb").write(pcm)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, "-b:a", "160k", out], check=True); os.remove(raw); print(out)
