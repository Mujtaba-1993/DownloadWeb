import json, subprocess, os
W = "/tmp/claude-0/-home-user/3d738a21-fb54-576d-b68a-8b9c9ea65a4f/scratchpad/juha/"
os.makedirs(W, exist_ok=True)
M = "/root/models/piper/ar_JO-kareem-medium.onnx"
# (scene, speaker, text for TTS with tashkeel, on-screen text)
LINES = [
    (0, "N", "لِمَاذَا يَحْمِلُ جُحَا حِمَارَهُ؟", "ليش جحا شايل حماره؟!"),
    (1, "N", "خَرَجَ جُحَا وَابْنُهُ إِلَى السُّوقِ، وَمَعَهُمَا حِمَارُهُمَا. فَرَكِبَ جُحَا، وَمَشَى ابْنُهُ.", "ركب جحا... ومشى ولده"),
    (1, "V", "يَا لَهُ مِنْ أَبٍ قَاسٍ! يَرْكَبُ، وَيَتْرُكُ الصَّغِيرَ يَمْشِي!", "أب قاسي! راكب وولده يمشي!"),
    (2, "N", "فَنَزَلَ جُحَا، وَأَرْكَبَ ابْنَهُ.", "نزل جحا... وركّب ولده"),
    (2, "V", "يَا لَهُ مِنْ وَلَدٍ عَاقٍّ! يَرْكَبُ، وَأَبُوهُ الْكَبِيرُ يَمْشِي!", "ولد عاق! وأبوه الكبير يمشي!"),
    (3, "N", "فَرَكِبَا مَعًا.", "فركبوا الاثنين"),
    (3, "V", "حَرَامٌ عَلَيْكُمَا! سَتَقْتُلَانِ الْحِمَارَ الْمِسْكِينَ!", "حرام عليكم! الحمار المسكين!"),
    (4, "N", "فَنَزَلَا، وَمَشَيَا بِجَانِبِهِ.", "نزلوا ومشوا جنبه"),
    (4, "V", "يَا لَلْغَبَاءِ! مَعَهُمَا حِمَارٌ، وَيَمْشِيَانِ!", "معهم حمار ويمشون؟!"),
    (5, "N", "فَحَمَلَا الْحِمَارَ عَلَى أَكْتَافِهِمَا!", "فشالوا الحمار!"),
    (5, "V", "هَا هَا هَا هَا! هَا هَا هَا!", "هههههههه"),
    (6, "J", "يَا بُنَيَّ... رِضَا النَّاسِ، غَايَةٌ لَا تُدْرَكُ.", "يا ولدي... رضا الناس غاية لا تُدرك"),
    (6, "N", "فَافْعَلْ مَا تَرَاهُ صَوَابًا.", "سوّ اللي تشوفه صح"),
]
# narrator normal; villagers higher & faster; Juha deeper & slower
PITCH = {"N": (1.0, 1.0), "V": (1.13, 1.05), "J": (0.88, 0.95)}
out = []
for i, (sc, sp, tts, disp) in enumerate(LINES):
    raw, o = f"{W}r{i}.wav", f"{W}l{i}.wav"
    subprocess.run(["python3", "-m", "piper", "-m", M, "-f", raw, "--length-scale", "1.05" if sp == "N" else "1.0"],
                   input=tts.encode(), check=True, capture_output=True)
    p, tempo = PITCH[sp]
    af = f"asetrate=22050*{p},aresample=48000,atempo={tempo / p:.4f},highpass=f=70,acompressor=threshold=0.1:ratio=3,volume=1.6"
    if sp == "V":
        af += ",aecho=0.6:0.3:25:0.2"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af, "-ac", "1", o], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", o]))
    out.append({"scene": sc, "spk": sp, "text": disp, "wav": o, "dur": round(d, 3)})
json.dump(out, open(W + "lines.json", "w"), ensure_ascii=False, indent=1)
for x in out:
    print(x["scene"], x["spk"], x["dur"], x["text"])
