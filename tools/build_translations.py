"""Rebuild tr-bn.json (Taisirul Quran) and tr-ur.json (Maududi) - arrays [surah][ayah] of text.

Sources (both downloadable from this environment):
  Bangla, Taisirul Quran (Quranic Universal Library, resource 184), packaged as SQLite:
    https://github.com/muntasimulhaque/quran/releases/download/pack-translation-taisirul-quran-bn-729c83aa/translation-taisirul-quran-bn.db
    (sha256 729c83aa09012e3a59a5afe1aa1f2e48fba4b1ca84e273b83e5d1352f21ff9c4; table translation(ayah_number 1..6236, text))
  Urdu, Abul A'la Maududi (tanzil.net) via fawazahmed0/quran-api:
    https://raw.githubusercontent.com/fawazahmed0/quran-api/1/editions/urd-abulaalamaududi.json

Usage (from the repo root):  python3 tools/build_translations.py taisir.db urd.json
"""
import json, os, sqlite3, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = json.load(open(os.path.join(ROOT, 'quran.json'), encoding='utf-8'))
rows = dict(sqlite3.connect(sys.argv[1]).execute('select ayah_number, text from translation'))
u = json.load(open(sys.argv[2], encoding='utf-8'))['quran']
bn, ur, g = [], [], 0
for s in Q:
    bn.append([]); ur.append([])
    for i in range(len(s['v'])):
        g += 1
        bn[-1].append(rows[g].strip())
        x = u[g-1]; assert (x['chapter'], x['verse']) == (s['n'], i + 1)
        ur[-1].append(x['text'].strip())
for name, data in (('tr-bn.json', bn), ('tr-ur.json', ur)):
    json.dump(data, open(os.path.join(ROOT, name), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok', g, 'ayahs')
