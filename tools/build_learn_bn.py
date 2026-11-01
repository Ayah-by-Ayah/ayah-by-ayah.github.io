#!/usr/bin/env python3
"""Builds learn-bn.json (Bangla meanings for the Learn tables and the word card) from tools/learn_src/bn_meanings.txt.
Each line: n|singular|plural 1|Bangla  or  v|māḍī|muḍāriʿ|Bangla  (the same key the learn/<s>.json rows carry).
Output: {"n":{"sg|p1":bn}, "v":{"madi|mud":bn}, "ns":{sg:bn}, "vs":{madi:bn}}  (ns/vs = by first form only, for the word card).
AI-drafted Bangla glosses, unreviewed."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
out = {"n": {}, "v": {}, "ns": {}, "vs": {}}
for l in open(f'{HERE}/learn_src/bn_meanings.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    if not l.strip(): continue
    t, a, b, bn = l.split('|', 3)
    out[t][f'{a}|{b}'] = bn
    out[t + 's'].setdefault(a, bn)
# per-word glosses of the word card (English quran.com gloss -> Bangla), tools/learn_src/bn_glosses.txt: english|bangla
out["g"] = {}
gp = f'{HERE}/learn_src/bn_glosses.txt'
if os.path.exists(gp):
    for l in open(gp, encoding='utf-8'):
        l = l.rstrip('\n')
        if '|' in l:
            e, b = l.rsplit('|', 1); out["g"][e.strip()] = b.strip()
json.dump(out, open(f'{ROOT}/learn-bn.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('learn-bn.json:', len(out['n']), 'nouns,', len(out['v']), 'verbs,', len(out['g']), 'word glosses')
