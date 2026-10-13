#!/usr/bin/env python3
"""Builds learn/1..114.json (generated Ism / Fi'l study tables, one file per surah) for the Learn tab.
Sources: grammar/ (via tools/learn_src/inventory.json, made by learn_src/extract.py), forms.json,
learn_src/verb_meanings.json + noun_fixes.txt (meanings written by Claude), learn_src/participles.py (rule-built
ism fāʿil / ism mafʿūl). Everything here is an unreviewed draft (ai:true). A reviewed vocab/<s> document in the
database always wins over the generated file."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'learn_src'))
ROOT = os.path.dirname(HERE)
import nouns, participles
F = json.load(open(f'{ROOT}/forms.json'))
inv = json.load(open(f'{HERE}/learn_src/inventory.json'))
vorder = json.load(open(f'{HERE}/learn_src/verb_order.json'))
norder = json.load(open(f'{HERE}/learn_src/noun_order.json'))
vmean = json.load(open(f'{HERE}/learn_src/verb_meanings.json'))
fix = {}
for l in open(f'{HERE}/learn_src/noun_fixes.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    if '|' in l:
        i, m = l.split('|', 1); fix[int(i)] = m.strip()
# --- verbs
V = {}
for i, lem in enumerate(vorder):
    f = F['v'][lem]; d = inv['v'][lem]
    mean, t = vmean[str(i)]
    madi, mud, amr, masd = f[0], f[1], f[2], f[3]
    fa, mf = participles.make(madi, mud, set(d['vf']), d['root'], t == 't')
    V[lem] = dict(madi=madi, mud=mud, amr=amr if amr and amr != '-' else '', masdar='، '.join(masd[:2]) if masd else '', fa=fa, mf=mf, mean=mean)
# --- nouns
N = {}
for i, lem in enumerate(norder):
    d = inv['n'][lem]
    sg, pl = nouns.noun_row(lem)
    mean = fix.get(i) or nouns.best_gloss(d)
    N[lem] = dict(sg=sg, p1=pl[0] if pl else '', p2=pl[1] if len(pl) > 1 else '', mean=mean)
# nouns missing from forms.json (hand-written rows: i|singular|plural 1|plural 2|meaning; '-' = not a noun to list)
miss = json.load(open(f'{HERE}/learn_src/missing.json'))
for l in open(f'{HERE}/learn_src/missing_rows.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    if not l: continue
    f = l.split('|')
    lem = miss['order'][int(f[0])]
    if f[1] == '-': continue
    inv['n'][lem] = miss['inv'][lem]
    N[lem] = dict(sg=f[1], p1=f[2], p2=f[3], mean=f[4])
NOTE = ('Generated study table (draft, not yet reviewed): word list from the Qurʼanic Arabic Corpus; plurals, '
        'verb forms and masdars from the word-forms table; meanings and the rule-built ism fāʿil / ism mafʿūl '
        'written automatically. Forms and meanings may need correction.')
os.makedirs(f'{ROOT}/learn', exist_ok=True)
tot = 0
for s in range(1, 115):
    ism = {}; fil = {}
    for lem, d in inv['n'].items():
        if str(s) not in d['surahs']: continue
        r = N[lem]; k = (r['sg'], r['p1'])
        e = ism.setdefault(k, dict(r, ayahs=set(), first=10**9))
        e['ayahs'].update(d['surahs'][str(s)]); e['first'] = min(e['first'], d['first'][str(s)])
        if not e['mean'] and r['mean']: e['mean'] = r['mean']
    for lem, d in inv['v'].items():
        if str(s) not in d['surahs']: continue
        r = V[lem]; k = (r['madi'], r['mud'])
        e = fil.setdefault(k, dict(r, ayahs=set(), first=10**9))
        e['ayahs'].update(d['surahs'][str(s)]); e['first'] = min(e['first'], d['first'][str(s)])
    def out(m):
        rows = sorted(m.values(), key=lambda e: e['first'])
        for e in rows:
            e['ayahs'] = sorted(e['ayahs']); del e['first']
        return rows
    doc = dict(s=s, ai=True, note=NOTE, ism=out(ism), fil=out(fil))
    tot += len(doc['ism']) + len(doc['fil'])
    json.dump(doc, open(f'{ROOT}/learn/{s}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('wrote 114 files,', tot, 'rows')
