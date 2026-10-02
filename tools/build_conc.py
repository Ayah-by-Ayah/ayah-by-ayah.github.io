"""Rebuild conc.json (whole-Qur'an occurrence index used by Word analysis) from grammar/*.json.

Format: {"L": {lemma: [code, ...]}, "R": {root: [lemma, ...]}}, code = surah*1e6 + ayah*1e3 + word.
The stem segment is the first non-prefix/suffix segment that is not a particle (else the first segment),
matching how the editor picks a word's lemma.

Usage (from the repo root):  python3 tools/build_conc.py
"""
import collections, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = collections.defaultdict(list); R = collections.defaultdict(set)
for s in range(1, 115):
    g = json.load(open(os.path.join(ROOT, 'grammar', f'{s}.json'), encoding='utf-8'))
    for a, ay in enumerate(g, 1):
        for w, word in enumerate(ay, 1):
            fl = lambda x: x[2].split('|')
            stems = [x for x in word[2] if 'PREF' not in fl(x) and 'SUFF' not in fl(x)]
            cand = [x for x in stems if x[1] != 'P'] or stems or word[2]
            f = fl(cand[0]); lem = next((x[4:] for x in f if x.startswith('LEM:')), None)
            if not lem: continue
            root = next((x[5:] for x in f if x.startswith('ROOT:')), '')
            L[lem].append(s * 1000000 + a * 1000 + w)
            if root: R[root].add(lem)
json.dump({'L': L, 'R': {k: sorted(v) for k, v in R.items()}},
          open(os.path.join(ROOT, 'conc.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(L), 'lemmas,', len(R), 'roots')
