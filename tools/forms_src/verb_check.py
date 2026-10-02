#!/usr/bin/env python3
"""check.py in_NN.json out_NN.json  -> prints problems. Output: list of {lemma,past,pres,imp,mas:[...],note}"""
import json, re, sys
def vkey(t):
    t = re.sub('[ٱأإآ]', 'ا', t or ''); t = t.replace('ى', 'ي').replace('ٰ', 'ا')
    t = re.sub('[ـْ]', '', t); t = re.sub('َ(?=ا)', '', t); t = re.sub('([ً-ِ])ّ', 'ّ\\1', t)
    t = re.sub('[ً-ِْ]+$', '', t); t = re.sub('^[^ء-ي]+', '', t)
    return t
def cons(t): return re.sub('[^ء-ي]', '', re.sub('[ٱأإآؤئ]', 'ا', t)).replace('ى', 'ي')
def voweled(t):  # every consonant (not alif/waw/ya used as long vowel) must carry a mark -> weak test: >= 1 mark per 2 letters
    L = len(re.findall('[ء-ي]', t)); M = len(re.findall('[ً-ْ]', t))
    return M * 2 >= L
inp = {x['lemma']: x for x in json.load(open(sys.argv[1]))}
out = json.load(open(sys.argv[2]))
seen = set(); bad = 0
for o in out:
    l = o.get('lemma'); x = inp.get(l); p = []
    if not x: print('UNKNOWN', l); bad += 1; continue
    seen.add(l)
    for k in ('past', 'pres', 'imp'):
        if o.get(k) and not voweled(o[k]): p.append(k + ' not voweled')
    if o.get('past') and vkey(o['past']) != vkey(l): p.append('past != lemma')
    if o.get('pres') and not re.match('^[يُ]', o['pres']) : p.append('pres not 3ms')
    for a in x['attested'].get('IMPF', []):
        m = re.match(r'(.+)\(3MS/IND', a)
        if m and o.get('pres') and vkey(m.group(1)) != vkey(o['pres']) and not o.get('note'): p.append('pres != attested ' + m.group(1))
    for a in x['attested'].get('IMPV', []):
        m = re.match(r'(.+)\(2MS', a)
        if m and o.get('imp') and vkey(m.group(1)) != vkey(o['imp']) and not o.get('note'): p.append('imp != attested ' + m.group(1))
    for m in o.get('mas', []):
        if not voweled(m): p.append('masdar not voweled ' + m)
    if cons(o.get('past', '')) != cons(l) and o.get('past'): p.append('consonants differ')
    if p: bad += 1; print(l, '|', '; '.join(p))
miss = set(inp) - seen
if miss: print('MISSING', len(miss), list(miss)[:5])
print('problems:', bad, 'of', len(out))
