#!/usr/bin/env python3
"""Free Saudi Arabic voices (Microsoft neural: Hamed = male, Zariyah = female) via edge-tts.
usage: saudi_tts.py "النص" out.mp3 [hamed|zariyah] [rate e.g. +0% / -10%]
Works through the session proxy by loading its CA bundle."""
import sys, ssl, os, asyncio, edge_tts
from edge_tts import communicate
ca = '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca): communicate._SSL_CTX = ssl.create_default_context(cafile=ca)
text, out = sys.argv[1], sys.argv[2]
voice = {'hamed': 'ar-SA-HamedNeural', 'zariyah': 'ar-SA-ZariyahNeural'}.get((sys.argv[3] if len(sys.argv) > 3 else 'hamed').lower(), sys.argv[3] if len(sys.argv) > 3 else 'ar-SA-HamedNeural')
rate = sys.argv[4] if len(sys.argv) > 4 else '+0%'
asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(out)); print(out)
