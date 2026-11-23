# One Gemini TTS request per video: all lines in one take, then split on the pauses into <out>_N.wav (24 kHz mono).
import sys, json, base64, urllib.request, numpy as np, soundfile as sf
lines_file, out, voice = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "Aoede")
model = sys.argv[4] if len(sys.argv) > 4 else "gemini-2.5-flash-preview-tts"
lines = [l.strip() for l in open(lines_file, encoding="utf-8") if l.strip()]
text = ("Say in a warm, friendly, confident female Saudi Gulf Arabic accent (Eastern Province), like a short social-media explainer. "
        "Read each line exactly as written and pause for about one second between lines:\n\n" + "\n\n".join(lines))
body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseModalities": ["AUDIO"],
        "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
try: r = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e: print("HTTP", e.code, e.read()[:300].decode()); sys.exit(1)
pcm = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
x = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768; sr = 24000
sf.write(out + "_full.wav", x, sr)
hop = int(.02 * sr); env = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
voiced = env > max(.02, env.max() * .04)
gaps, i = [], 0                                    # silent runs (start, end, length) in hops
while i < len(voiced):
    if not voiced[i]:
        j = i
        while j < len(voiced) and not voiced[j]: j += 1
        if i > 0 and j < len(voiced): gaps.append((i, j, j - i))
        i = j
    else: i += 1
# choose cuts nearest to where each line should end (by text length), keeping order; prefer long pauses
cand = [g for g in gaps if g[2] >= 12]                        # >= 0.24 s
lens = np.array([len(l.replace(' ', '')) for l in lines], float); frac = np.cumsum(lens)[:-1] / lens.sum()
v0, v1 = np.where(voiced)[0][[0, -1]]; cuts, last = [], -1
for f in frac:
    target = v0 + f * (v1 - v0 - sum(g[2] for g in cand) * 0) 
    best = min((g for g in cand if g[0] > last), key=lambda g: abs((g[0] + g[1]) / 2 - target) / (1 + g[2] / 40), default=None)
    if best is None: print("not enough pauses"); sys.exit(2)
    cuts.append(best); last = best[1]
v = np.where(voiced)[0]; a = v[0]; segs = []
for g in cuts: segs.append((a, g[0])); a = g[1]
segs.append((a, v[-1] + 1))
for k, (s, e) in enumerate(segs, 1):
    y = x[max(0, s * hop - int(.04 * sr)): min(len(x), e * hop + int(.08 * sr))]; sf.write(f"{out}_{k}.wav", y, sr)
    print("ok", k, round(len(y) / sr, 2), "| gap after", round(cuts[k - 1][2] * .02, 2) if k <= len(cuts) else "-")
