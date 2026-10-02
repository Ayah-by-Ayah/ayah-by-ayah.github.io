"""Assemble data/content.json (the public site's copy of the write-ups) from a database export.

Export every collection first with the ArtifactData tool, action "list", query {"limit": 1000},
and out_dir=<EXPORT_DIR>, for: notes, lessons, words, translations, irab, settings.
That writes <EXPORT_DIR>/<collection>/<doc_id>.json.

Usage (from the repo root):  python3 tools/make_content.py <EXPORT_DIR>
"""
import json, glob, os, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = sys.argv[1]

def load(c):
    out = []
    for f in sorted(glob.glob(os.path.join(E, c, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        d['id'] = os.path.basename(f)[:-5]
        out.append(d)
    return out

irab = {}
for d in load('irab'):            # docs irab/<s>-<group>: {s, ayahs:{a: entry}}
    s = str(d.get('s') or d['id'].split('-')[0])
    irab.setdefault(s, {}).update(d.get('ayahs', {}))
cats_f = os.path.join(E, 'settings', 'categories.json')
cats = json.load(open(cats_f, encoding='utf-8')).get('list', []) if os.path.exists(cats_f) else []
c = {
    'exportedAt': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'notes': load('notes'), 'lessons': load('lessons'), 'words': load('words'),
    'translations': load('translations'), 'categories': cats, 'irab': irab,
}
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
json.dump(c, open(os.path.join(ROOT, 'data', 'content.json'), 'w', encoding='utf-8'), ensure_ascii=False)
for k in ('notes', 'lessons', 'words', 'translations'):
    print(k, len(c[k]), [x['id'] for x in c[k]][:20])
print('categories', len(cats), '| irab surahs', len(irab))
