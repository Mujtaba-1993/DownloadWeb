#!/usr/bin/env python3
"""Rebuild the private Al Nibras media library inside THIS session (never uploaded anywhere).
usage: nibras_media_restore.py ALLMEDIA_JSON [--clean]
ALLMEDIA_JSON = list of {id,type,url,ts} produced in the Composio workbench from
INSTAGRAM_GET_IG_USER_MEDIA (fields id,permalink,timestamp,media_type,media_url,children{media_url,media_type}).
Output: ~/nibras-media/m (originals), ~/nibras-media/lib_src (one best frame per item, named <stage>__<id>.jpg using tags.json),
        ~/nibras-media/lib_clean (LaMa-cleaned, with --clean)."""
import json, os, sys, subprocess, shutil
from concurrent.futures import ThreadPoolExecutor
K = os.path.dirname(os.path.abspath(__file__)); R = os.path.expanduser('~/nibras-media')
TAGS = os.path.expanduser('~/.claude/skills/nibras-content-expert/media/tags.json')
os.makedirs(f'{R}/m', exist_ok=True); os.makedirs(f'{R}/lib_src', exist_ok=True)
items = [x for x in json.load(open(sys.argv[1])) if x.get('url')]
def get(x):
    p = f"{R}/m/{x['id']}.{'mp4' if x['type'] == 'VIDEO' else 'jpg'}"
    if not os.path.exists(p): subprocess.run(['curl', '-sL', '-m', '120', '-o', p, x['url']])
with ThreadPoolExecutor(16) as ex: list(ex.map(get, items))
tags = json.load(open(TAGS)) if os.path.exists(TAGS) else []
best = {}
for o in tags:
    b = os.path.basename(o['f'])[:-4]; src = b.split('@')[0]
    if o['tag'] == 'text': continue
    sc = o['p'] * min(o['sharp'], 800)
    if src not in best or sc > best[src][0]: best[src] = (sc, b, o['tag'])
for src, (sc, b, tag) in best.items():
    out = f'{R}/lib_src/{tag}__{src}.jpg'
    if os.path.exists(out): continue
    if '@' in b and os.path.exists(f'{R}/m/{src}.mp4'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', b.split('@')[1], '-i', f'{R}/m/{src}.mp4', '-frames:v', '1', '-q:v', '2', out])
    elif os.path.exists(f'{R}/m/{src}.jpg'): shutil.copy(f'{R}/m/{src}.jpg', out)
print('library', len(os.listdir(f'{R}/lib_src')), 'items in', R)
if '--clean' in sys.argv:
    subprocess.run(['python3', os.path.expanduser('~/tools/autoclean.py'), f'{R}/lib_src', f'{R}/lib_clean'])
