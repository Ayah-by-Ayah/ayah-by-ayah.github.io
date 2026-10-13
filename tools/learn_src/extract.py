#!/usr/bin/env python3
"""Step 1 of the Learn tables. Reads grammar/1..114.json + forms.json, writes tools/learn_src/inventory.json:
{ "n": {lemma: {"surahs": {s: [ayahs]}, "gl": {gloss: count}, "root": r, "tags": [...]}},
  "v": {lemma: {"surahs": {...}, "gl": {...}, "root": r, "vf": [..]}} }"""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = json.load(open(f'{ROOT}/forms.json'))
EXCL = ('PN', 'DEM', 'REL', 'PRON', 'LOC', 'T')
inv = {'n': {}, 'v': {}}
for s in range(1, 115):
    for a, ws in enumerate(json.load(open(f'{ROOT}/grammar/{s}.json')), 1):
        for w in ws:
            segs = w[2]
            stems = [x for x in segs if not ({'PREF', 'SUFF'} & set(x[2].split('|')))]
            bare = len(segs) == 1
            for text, pos, f in stems:
                wi = ws.index(w) + 1
                fl = f.split('|')
                L = [x[4:] for x in fl if x.startswith('LEM:')]
                if not L or pos not in ('N', 'V'): continue
                L = L[0]
                if pos == 'N':
                    if any(x in fl for x in EXCL) or L not in F['n']: continue
                    d = inv['n'].setdefault(L, {'surahs': {}, 'gl': {}, 'root': '', 'tags': set()})
                else:
                    if L not in F['v']: continue
                    d = inv['v'].setdefault(L, {'surahs': {}, 'gl': {}, 'root': '', 'vf': set()})
                    d['vf'].update(x[3:] for x in fl if x.startswith('VF:'))
                    d.setdefault('forms', {})
                    d['forms'].setdefault(' '.join(x for x in fl if x in ('PERF','IMPF','IMPV') or x[:1] in '123' and len(x) <= 3), w[1])
                d.setdefault('first', {}).setdefault(str(s), a * 1000 + wi)
                d['surahs'].setdefault(str(s), [])
                if a not in d['surahs'][str(s)]: d['surahs'][str(s)].append(a)
                for x in fl:
                    if x.startswith('ROOT:'): d['root'] = x[5:]
                if pos == 'N':
                    d['tags'].update(x for x in fl if x in ('ADJ', 'ACT_PCPL', 'PASS_PCPL', 'VN', 'M', 'F'))
                    d['gl'][w[1]] = d['gl'].get(w[1], 0) + (3 if bare else 1)
for k in ('n', 'v'):
    for d in inv[k].values():
        for x in ('tags', 'vf'):
            if x in d: d[x] = sorted(d[x])
json.dump(inv, open(f'{ROOT}/tools/learn_src/inventory.json', 'w'), ensure_ascii=False)
print(len(inv['n']), 'noun lemmas;', len(inv['v']), 'verb lemmas;',
      sum(1 for d in inv['n'].values() if not d['gl']), 'nouns without any gloss')
