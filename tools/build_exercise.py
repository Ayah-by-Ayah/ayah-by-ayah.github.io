#!/usr/bin/env python3
"""Builds exercise/<s>.json for the Exercise tab. Each question blanks one word of an ayah; options are word
references "s:a:i" (i = word number in the ayah) so the app can show them in the reader's chosen script.
Specs are hand-written in exercise_src/spec<s>.py: {ayah: [(blank word no., highlight text in Saheeh translation, [3 distractor words])]}."""
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'exercise_src'))
from common import *
import auto
def build(s):
    spec = importlib.import_module(f'spec{s}').SPEC; out = {}; errs = []; filled = []
    for a, qs in spec.items():
        en = Q[s-1]['v'][a-1][1]; ver = verified(s, a)
        sets = []
        for (i, hl, ds) in qs:
            if hl not in en or en.count(hl) != 1: errs.append(f'{s}:{a} highlight "{hl}" not unique in translation')
            opts = [f'{s}:{a}:{i}']; words = {norm(mad(s, a)[i-1])}
            for d in ds:
                if len(opts) == 4: break
                r = find(d, prefer=s) or find_loose(d, prefer=s)
                if r and norm(mad(*r[:2])[r[2]-1]) in words: r = None
                if not r: continue
                words.add(norm(mad(*r[:2])[r[2]-1])); opts.append('%d:%d:%d' % r)
            if len(opts) < 4:
                fill = auto.auto_fill(s, a, i, words, 4 - len(opts))
                for x in fill: opts.append('%d:%d:%d' % x[:3]); words.add(x[7])
                filled.append(f'{s}:{a} #{i} {mad(s,a)[i-1]} +{len(fill)} auto: ' + ' '.join(mad(x[0], x[1])[x[2]-1] for x in fill))
            if len(opts) != 4: errs.append(f'{s}:{a} needs 4 options, has {len(opts)} (word {i})')
            sets.append({'w': i, 'hl': hl, 'o': opts, **({} if ver else {'m': 1})})
        out[str(a)] = sets
    if filled and os.environ.get('SHOWFILL'): print('\n'.join(filled))
    return {'s': s, 'ayahs': out}, errs
if __name__ == '__main__':
    os.makedirs(f'{ROOT}/exercise', exist_ok=True)
    surahs = [int(x) for x in sys.argv[1:]] or list(range(1, 115))
    stats = []
    for s in surahs:
        if os.path.exists(os.path.join(HERE, 'exercise_src', f'spec{s}.py')): d, errs = build(s)
        else: d, errs = auto.gen_surah(s), []
        n = len(Q[s-1]['v']); k = [len(v) for v in d['ayahs'].values()]
        stats.append((s, n, len(k), sum(k)))
        if errs: print(s, '\n'.join(errs))
        if not errs: json.dump(d, open(f'{ROOT}/exercise/{s}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('surahs', len(stats), 'ayahs', sum(x[1] for x in stats), 'with questions', sum(x[2] for x in stats), 'questions', sum(x[3] for x in stats))
    print('weakest:', sorted(stats, key=lambda x: x[2] / x[1])[:8])
