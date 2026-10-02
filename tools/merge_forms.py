#!/usr/bin/env python3
"""Merge noun table (build_forms.py output) and verb batches (out_NN.json) into forms.json.
Usage: python3 tools/merge_forms.py <workdir with nouns.json> <dir with out_*.json> [forms.json]
forms.json = {"n": {lemma: [singular, [[plural, q]...], plural_of, [sound masc, sound fem]]},
              "v": {lemma: [past, present, imperative, [masdars], note]},
              "meta": {...}}
q = 1 when that plural form itself occurs in the Qur'an (checked against the corpus), else 0."""
import json, re, sys, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
work, vdir = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else ROOT + '/forms.json'
def vk(t):
    t = re.sub('[ٱأإآ]', 'ا', t or ''); t = t.replace('ى', 'ي').replace('ٰ', 'ا')
    t = re.sub('[ـْٓ-ٕۖ-ۭ]', '', t); t = re.sub('ًا$', '', t); t = t.replace('اَ', 'ا'); t = re.sub('َ(?=ا)', '', t); t = re.sub('([ً-ِ])ّ', r'ّ\1', t)
    t = re.sub('[ً-ِْ]+$', '', t); t = re.sub('^[^ء-ي]+', '', t)
    return re.sub('[ةت]$', 'ت', re.sub('[ئؤ]$', 'ء', t))
def att_key(t):  # attested surface: drop the initial shadda left by assimilation of the article
    t = vk(t); return re.sub('^([ء-ي])ّ', r'\1', t)
nouns = json.load(open(work + '/nouns.json'))
def letters(t):  # [(consonant, marks)] with the final case vowel dropped
    t = re.sub('[ٱأإآءئؤ]', 'ا', t); t = t.replace('ى', 'ي'); t = re.sub('[ً-ِْ]+$', '', t)
    L = []
    for ch in t:
        if re.match('[ء-ي]', ch): L.append([ch, ''])
        elif L and re.match('[ً-ْ]', ch): L[-1][1] += ch
    return [(c, ''.join(sorted(m))) for c, m in L]
def compatible(sg, lem):  # every mark the dictionary gives must agree with the corpus lemma
    a, b = letters(sg), letters(lem)
    a = a[1:] if a and a[0][0] == 'ا' else a; b = b[1:] if b and b[0][0] == 'ا' else b
    a = [x for x in a if x[0] != 'ا' or x[1]]; b = [x for x in b if x[0] != 'ا' or x[1]]
    if len(a) < 2 or len(b) < 2: return False
    if [x[0] for x in a] != [x[0] for x in b]: return False
    return all(not x[1] or x[1].replace('ْ', '') == y[1].replace('ْ', '') or not y[1] for x, y in zip(a, b))
drop = [l for l, e in nouns.items() if ((e['match'] < 4 and not compatible(e['sg'], l)) or (e['match'] < 7 and len(letters(l)) < 3 and vk(e['sg']) != vk(l)))]
for l in drop: del nouns[l]
print('dropped', len(drop), 'doubtful dictionary matches')
N = {}
lemkeys = {vk(l) for l in nouns}
for l, e in nouns.items():
    attested = [(f, k, n) for f, k, n in e['att'] if k == 'pl']
    akeys = {att_key(f): n for f, k, n in attested}
    pls = []; seen = set()
    for p in e['pl']:
        k = vk(p)
        if k.startswith('ال'): continue
        if k in seen: continue
        seen.add(k); pls.append([p, 1 if (k in akeys or att_key(p) in akeys or k in lemkeys) else 0])
    sound = lambda t: bool(re.search('(ون|ين|ات|ان)$', re.sub('[ً-ٕ]', '', vk(t))))
    for f, k, n in attested[:3]:   # plural forms found in the Qur'an but missing from the dictionary
        ak = att_key(f)
        if ak in seen or vk(f) in seen or sound(f) or n < 1 or re.search('[ۖ-ۭ]', f): continue
        if ak == vk(e['sg']): continue
        seen.add(ak); pls.append([f, 1])
    N[l] = [e['sg'], pls, e['pl_of'], [int(bool(e['sound_m'])), int(bool(e['sound_f']))]]
V = {}
for f in sorted(glob.glob(vdir + '/out_*.json')):
    for o in json.load(open(f)):
        note = o.get('note', '')
        if re.search('wasl|corpus|spelling|lemma|checker|variant|truncated|inflected', note, re.I): note = ''   # production remarks, not for readers
        V[o['lemma']] = [o['past'], o['pres'], o['imp'], o.get('mas', []), note]
json.dump(dict(n=N, v=V, meta=dict(sources='Arramooz dictionary (GPL-3.0), Quranic Arabic Corpus, AI-completed gaps (unreviewed)')), open(out, 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(N), 'nouns', len(V), 'verbs', os.path.getsize(out) // 1024, 'KB')
