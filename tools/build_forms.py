#!/usr/bin/env python3
"""Step 1 of the word-forms table.  Usage:
   python3 tools/build_forms.py <arabicdictionary.sqlite> <workdir>
Reads grammar/1..114.json (Quranic Arabic Corpus) and the Arramooz dictionary (GPL, github.com/linuxscout/arramooz-pysqlite),
writes <workdir>/nouns.json (finished entries) and <workdir>/verbs_in.json (verb lemmas with everything a checker or translator needs).
Step 2 (verbs) is done in batches and merged by tools/merge_forms.py into forms.json."""
import json, re, sys, sqlite3, collections, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
HAR = 'ؐ-ًؚ-ٰٟۖ-ۭـ'
def N(t):
    t = re.sub('[' + HAR + ']', '', t); t = re.sub('[ٱأإآء]', 'ا', t)
    return t.replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و')
def NR(r): return N(r).replace('ا', 'و') if False else N(r)
def caseless(t):  # drop the final case vowel / tanwin of a surface form
    return re.sub('[ً-ِْ]+$', '', t).replace('ٰ', 'ا') if t else t
c = sqlite3.connect(DB)
nouns = collections.defaultdict(list); verbs = collections.defaultdict(list)
cols = [r[1] for r in c.execute('pragma table_info(nouns)')]
for r in c.execute('select * from nouns'):
    d = dict(zip(cols, r)); nouns[N(d['vocalized'])].append(d)
vcols = [r[1] for r in c.execute('pragma table_info(verbs)')]
for r in c.execute('select * from verbs'):
    d = dict(zip(vcols, r)); verbs[N(d['vocalized'])].append(d)
masdar_of = collections.defaultdict(list)
for k, L in nouns.items():
    for d in L:
        if (d.get('wordtype') or '').startswith('مصدر') and d.get('original'): masdar_of[d['original']].append(d['vocalized'])

lem = {}   # (lemma, kind) -> info
for s in range(1, 115):
    for ai, a in enumerate(json.load(open(f'{ROOT}/grammar/{s}.json'))):
        for w in a:
            for text, coarse, f in w[2]:
                fl = f.split('|')
                if 'PREF' in fl or 'SUFF' in fl: continue
                L = [x[4:] for x in fl if x.startswith('LEM:')]
                if not L or coarse not in ('N', 'V'): continue
                if coarse == 'N' and any(x in fl for x in ('PN', 'DEM', 'REL', 'PRON', 'LOC', 'T')): continue
                root = next((x[5:] for x in fl if x.startswith('ROOT:')), '')
                vf = next((x[3:] for x in fl if x.startswith('VF:')), '')
                pgn = next((x for x in fl if re.fullmatch(r'[123]?[MF]?[SDP]', x)), '')
                tense = next((x for x in fl if x in ('PERF', 'IMPF', 'IMPV')), '')
                mood = next((x[5:] for x in fl if x.startswith('MOOD:')), '')
                k = (L[0], coarse)
                e = lem.setdefault(k, dict(lemma=L[0], kind=coarse, root=root, vf=vf, n=0, gl=collections.Counter(), forms=collections.Counter(), adj='ADJ' in fl))
                e['n'] += 1; e['gl'][w[1]] += 1
                e['forms'][(text, tense, pgn, mood, 'PASS' in fl)] += 1
if not os.path.exists(OUT + '/_ok'): pass
def vkey(t):  # comparison key: same letters and same vowels, ignoring spelling variants and the final case vowel
    t = re.sub('[ٱأإآ]', 'ا', t or ''); t = t.replace('ى', 'ي').replace('ٰ', 'ا')
    t = re.sub('[ـْ]', '', t)
    t = re.sub('َ(?=ا)', '', t)
    t = re.sub('([ً-ِ])ّ', 'ّ\\1', t)
    t = re.sub('[ً-ِْ]+$', '', t)
    t = re.sub('^[^ء-ي]+', '', t)
    return t
def vowel_ok(a, b): return vkey(a) == vkey(b)
out_n = {}; v_in = []
plural_of = collections.defaultdict(list)  # vkey(plural) -> [(singular vocalized, root)]
def _clean(x):
    x = re.sub(r'\s*جج\s*:?.*$', '', x).strip(); x = re.sub(r'\s*مُثَنَّاهَا.*$', '', x).strip()
    return x if x and 'مؤنَّث' not in x and ' ' not in x else ''
for _k, _L in nouns.items():
    for _d in _L:
        for _p in [_clean(x) for x in re.split(r'[;؛]', _d.get('broken_plural') or '')]:
            if _p: plural_of[vkey(_p)].append((_d['vocalized'], _d.get('root') or ''))
SPL = lambda s: [x.strip() for x in re.split(r'[;؛]', s or '') if x.strip()]
def clean_pl(x):
    x = re.sub(r'\s*جج\s*:?.*$', '', x).strip()
    x = re.sub(r'\s*مُثَنَّاهَا.*$', '', x).strip()
    return x if x and 'مؤنَّث' not in x and ' ' not in x else ''
for (l, kind), e in lem.items():
    top_gl = [g for g, _ in e['gl'].most_common(3)]
    if kind == 'N':
        cands = nouns.get(N(l), [])
        if not cands: continue
        best = None; bs = -1
        for d in cands:
            sc = (2 if N(d.get('root') or '') == N(e['root']) else 0) + (4 if vowel_ok(d['vocalized'], l) else 0) + (1 if d.get('broken_plural') else 0) + (1 if d.get('number') == 'مفرد' else 0)
            if sc > bs: best, bs = d, sc
        d = best
        rev = [x for x in plural_of.get(vkey(l), []) if N(x[1]) == N(e['root'])]
        if bs < 7 and rev:  # the lemma is itself a plural of a singular listed in the dictionary
            sg = rev[0][0]
            att = collections.Counter()
            for (text, tense, pgn, mood, ps), n in e['forms'].items(): att[(caseless(text), 'pl')] += n
            out_n[l] = dict(sg=sg, root=e['root'], pl=[l], sound_m=False, sound_f=False, pl_of=sg, att=[[f, k, n] for (f, k), n in att.most_common(8)], match=9)
            continue
        pl = [p for p in (clean_pl(x) for x in SPL(d.get('broken_plural'))) if p]
        att = collections.Counter()
        for (text, tense, pgn, mood, ps), n in e['forms'].items():
            if pgn.endswith('P') or pgn.endswith('D'): att[(caseless(text), 'pl' if pgn.endswith('P') else 'du')] += n
        out_n[l] = dict(sg=d['vocalized'], root=e['root'], pl=pl, sound_m=bool(d.get('masculin_plural')), sound_f=bool(d.get('feminin_plural')),
                        pl_of=(d.get('single') or '') if 'جمع' in (d.get('number') or '') else '',
                        att=[[f, k, n] for (f, k), n in att.most_common(8)], match=bs)
    else:
        past = N(l); cands = verbs.get(past, [])
        att = collections.Counter()
        for (text, tense, pgn, mood, ps), n in e['forms'].items():
            att[(text, tense, pgn, mood, ps)] += n
        att_l = [[t, ten, pg, mo, int(ps), n] for (t, ten, pg, mo, ps), n in att.most_common(40)]
        v_in.append(dict(lemma=l, root=e['root'], form=e['vf'], gloss=top_gl, count=e['n'],
                         dict=[dict(past=d['vocalized'], future_type=d['future_type']) for d in cands if N(d.get('root') or '') == N(e['root']) or len(cands) == 1],
                         masdar_dict=sorted(set(masdar_of.get(l, []) + [m for d in cands for m in masdar_of.get(d['vocalized'], [])]))[:12],
                         attested=att_l))
# Qur'anic nouns of the same root (candidates for the maṣdar)
byroot = collections.defaultdict(list)
for (l, kind), e in lem.items():
    if kind == 'N': byroot[e['root']].append([l, e['gl'].most_common(1)[0][0], e['n']])
for v in v_in: v['nouns_same_root'] = sorted(byroot.get(v['root'], []), key=lambda x: -x[2])[:12]
json.dump(out_n, open(OUT + '/nouns.json', 'w'), ensure_ascii=False)
json.dump(v_in, open(OUT + '/verbs_in.json', 'w'), ensure_ascii=False)
print(len(out_n), 'noun lemmas matched;', len(v_in), 'verb lemmas')
