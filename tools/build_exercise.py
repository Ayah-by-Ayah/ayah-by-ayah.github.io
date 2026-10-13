#!/usr/bin/env python3
"""Builds exercise/<s>.json for the Exercise tab. Each question blanks one word of an ayah; options are word
references "s:a:i" (i = word number in the ayah) so the app can show them in the reader's chosen script.
Specs are hand-written in exercise_src/spec<s>.py: {ayah: [(blank word no., highlight text in Saheeh translation, [3 distractor words])]}."""
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'exercise_src'))
from common import *
def build(s):
    spec = importlib.import_module(f'spec{s}').SPEC; out = {}; errs = []
    for a, qs in spec.items():
        en = Q[s-1]['v'][a-1][1]; assert verified(s, a), (s, a)
        sets = []
        for (i, hl, ds) in qs:
            if hl not in en or en.count(hl) != 1: errs.append(f'{s}:{a} highlight "{hl}" not unique in translation')
            opts = [f'{s}:{a}:{i}']; words = {norm(mad(s, a)[i-1])}
            for d in ds:
                r = find(d, prefer=s)
                if not r: errs.append(f'{s}:{a} distractor {d} not found'); continue
                if norm(mad(*r[:2])[r[2]-1]) in words: errs.append(f'{s}:{a} duplicate option {d}'); continue
                words.add(norm(mad(*r[:2])[r[2]-1])); opts.append('%d:%d:%d' % r)
            if len(opts) != 4: errs.append(f'{s}:{a} needs 4 options, has {len(opts)}')
            sets.append({'w': i, 'hl': hl, 'o': opts})
        out[str(a)] = sets
    return {'s': s, 'ayahs': out}, errs
if __name__ == '__main__':
    os.makedirs(f'{ROOT}/exercise', exist_ok=True)
    for s in map(int, sys.argv[1:] or [97]):
        d, errs = build(s)
        print('\n'.join(errs) or 'ok')
        if not errs: json.dump(d, open(f'{ROOT}/exercise/{s}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
