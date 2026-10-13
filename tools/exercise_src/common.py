import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Q = json.load(open(f'{ROOT}/quran.json')); IP = json.load(open(f'{ROOT}/indopak.json'))
L = re.compile('[ء-يٱ]')
def mad(s, a): return Q[s-1]['v'][a-1][0].split()
def ipt(s, a): return [t for t in IP[s-1][a-1].split() if L.search(t)]
_G = {}
def gram(s):
    if s not in _G: _G[s] = json.load(open(f'{ROOT}/grammar/{s}.json'))
    return _G[s]
def verified(s, a): return len(mad(s, a)) == len(ipt(s, a)) == len(gram(s)[a-1])
STOP = re.compile('[\u06D6-\u06DC\u0615\u06DE\u06E9\u200b-\u200f\ue000-\uf8ff]')
def norm(t): return ''.join(sorted(STOP.sub('', t)))
_IDX = None
def find(word, prefer=None):
    """first (s,a,i) in a verified ayah whose Madani token equals word (prefer ayahs of surah `prefer`, then short surahs)"""
    global _IDX
    if _IDX is None:
        _IDX = {}
        for s in range(1, 115):
            for a in range(1, len(Q[s-1]['v']) + 1):
                if not verified(s, a): continue
                for i, t in enumerate(mad(s, a), 1): _IDX.setdefault(norm(t), []).append((s, a, i))
    r = _IDX.get(norm(word), [])
    if not r: return None
    pr = [x for x in r if x[0] == prefer]
    return (pr or r)[0]
