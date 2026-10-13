"""Automatic question generator for the Exercise tab (all surahs without a hand-written spec)."""
import re, random, collections
from common import *
STOPW = set("the of a an and to in is are be been being it its they them their he him his she her we us our you your i me my that this those these who whom which what by for with from on at as so then not no or but if than into upon over about there here do does did will would shall should can could may might have has had was were am also all any some just only very indeed o oh lo behold when while where how why whoever whosoever those who one ones other".split())
FEATSET_N = {'M','F','MS','FS','MP','FP','MD','FD','MS+','FS+'}
def segs(w): return w[2]
def parts(w):
    pre = ''.join(x[0] for x in w[2] if 'PREF' in x[2].split('|'))
    suf = ''.join(x[0] for x in w[2] if 'SUFF' in x[2].split('|'))
    stem = [x for x in w[2] if not ({'PREF','SUFF'} & set(x[2].split('|')))]
    return pre, suf, stem
def stripmarks(t): return re.sub('[ً-ْٰـٖ-ٟ]', '', t).replace('ٱ','ا').replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي').replace('ٰ','')
def info(w):
    """returns dict(sig, root, lem, pos) for a word eligible as a content word, else None"""
    pre, suf, stem = parts(w)
    if len(stem) != 1: return None
    t, pos, f = stem[0]; fl = f.split('|')
    if pos not in ('N', 'V'): return None
    if any(x in fl for x in ('PN','DEM','REL','PRON','LOC','T')) : return None
    root = next((x[5:] for x in fl if x.startswith('ROOT:')), ''); lem = next((x[4:] for x in fl if x.startswith('LEM:')), '')
    if not root: return None
    pre_s = stripmarks(pre); suf_s = stripmarks(suf)
    if pos == 'N':
        case = next((x for x in fl if x in ('NOM','ACC','GEN')), '')
        gn = tuple(sorted(x for x in fl if x in FEATSET_N))
        kind = tuple(sorted(x for x in fl if x in ('ADJ','ACT_PCPL','PASS_PCPL','VN')))
        sig = ('N', pre_s, suf_s, case, 'INDEF' in fl, gn, kind)
    else:
        asp = next((x for x in fl if x in ('PERF','IMPF','IMPV')), '')
        pers = next((x for x in fl if re.fullmatch(r'[123][MF]?[SDP]', x)), '')
        mood = next((x for x in fl if x.startswith('MOOD:')), '')
        vf = next((x for x in fl if x.startswith('VF:')), '')
        sig = ('V', pre_s, suf_s, asp, pers, mood, 'PASS' in fl, vf)
    return {'sig': sig, 'root': root, 'lem': lem, 'pos': pos, 'len': len(stripmarks(t)) + len(pre_s) + len(suf_s)}
def ctokens(gloss):
    g = re.sub(r'\([^)]*\)', ' ', gloss); g = re.sub(r'[\[\]\(\)]', ' ', g)
    return [t.lower() for t in re.findall(r"[A-Za-z']+", g) if t.lower() not in STOPW and len(t) > 2]
def stem(t):
    for suf in ('ing','ed','es','s','d'):
        if len(t) > len(suf) + 3 and t.endswith(suf): return t[:-len(suf)]
    return t
def highlight(gloss, en):
    best = None
    for t in sorted(ctokens(gloss), key=lambda x: -len(x)):
        st = stem(t)
        ms = [m for m in re.finditer(r"\b(%s[a-z']*)\b" % re.escape(st), en, re.I)]
        if len(ms) == 1:
            w = ms[0].group(1)
            if len(re.findall(r"\b%s\b" % re.escape(w), en, re.I)) == 1: return w
    return None

ART = set("the a an of to in on at for with from by and or then so but".split())
COP = set("is are was were am".split())
def _gtok(gloss): return [x.lower() for x in re.findall(r"[A-Za-z']+", re.sub(r'[\[\]]', ' ', re.sub(r'\([^)]*\)', ' ', gloss)))]
def _tmatch(e, gs):
    e = e.lower()
    for g in gs:
        if e == g: return True
        m = min(len(e), len(g))
        if m >= 4 and (e.startswith(g[:max(4, len(g) - 2)]) or g.startswith(e[:max(4, len(e) - 2)])): return True
    return False
def expand(gloss, en, hl):
    """Grow a one-word highlight to the whole phrase the Arabic word means ('You have bestowed favor', not 'bestowed')."""
    if not hl or en.count(hl) != 1: return hl
    gs = _gtok(gloss)
    toks = [(m.start(), m.end(), m.group()) for m in re.finditer(r"[A-Za-z']+", en)]
    k0 = next((k for k, (a, b, w) in enumerate(toks) if a == en.index(hl)), None)
    if k0 is None: return hl
    k1 = next((k for k, (a, b, w) in enumerate(toks) if b == en.index(hl) + len(hl)), None)
    if k1 is None: return hl
    def ok(k):
        a, b, w = toks[k]
        return w.lower() not in ART and w.lower() not in COP and _tmatch(w, gs)
    lo, hi = k0, k1
    while lo > 0 and en[toks[lo-1][1]:toks[lo][0]].strip() == '' and ok(lo-1): lo -= 1
    while hi + 1 < len(toks) and en[toks[hi][1]:toks[hi+1][0]].strip() == '' and ok(hi+1): hi += 1
    # a leading/trailing article is never part of the highlight
    new = en[toks[lo][0]:toks[hi][1]]
    return new if en.count(new) == 1 else hl
_POOL = None
def pool():
    global _POOL
    if _POOL: return _POOL
    P = collections.defaultdict(list)
    for s in range(1, 115):
        for a in range(1, len(Q[s-1]['v']) + 1):
            if not verified(s, a): continue
            m = mad(s, a)
            for i, w in enumerate(gram(s)[a-1], 1):
                inf = info(w)
                if inf: P[inf['sig']].append((s, a, i, inf['root'], inf['lem'], set(ctokens(w[1])), inf['len'], norm(m[i-1])))
    _POOL = P; return P
def gen_ayah(s, a):
    m = mad(s, a); g = gram(s)[a-1]
    if len(m) != len(g): return None
    en = Q[s-1]['v'][a-1][1]; rng = random.Random(s * 1000 + a); P = pool(); ver = verified(s, a)
    cands = []
    for i, w in enumerate(g, 1):
        inf = info(w)
        if not inf: continue
        hl = highlight(w[1], en)
        if not hl: continue
        hl = expand(w[1], en, hl)
        gl = set(ctokens(w[1])); ans = norm(m[i-1])
        pool_ = [c for c in P.get(inf['sig'], []) if c[3] != inf['root'] and c[4] != inf['lem'] and not (c[5] & gl) and c[7] != ans and abs(c[6] - inf['len']) <= 3 and not (c[0] == s and c[1] == a)]
        seen = set(); uniq = []
        for c in pool_:
            if c[7] in seen: continue
            seen.add(c[7]); uniq.append(c)
        if len(uniq) < 3: continue
        # spread over different roots
        rng.shuffle(uniq); pick = []; roots = set()
        for c in uniq:
            if c[3] in roots: continue
            roots.add(c[3]); pick.append(c)
            if len(pick) == 3: break
        if len(pick) < 3: continue
        cands.append((i, hl, ['%d:%d:%d' % (s, a, i)] + ['%d:%d:%d' % c[:3] for c in pick]))
    if not cands: return None
    if len(cands) > 4:
        step = len(cands) / 4.0
        cands = [cands[int(k * step + step / 2)] for k in range(4)]
    out = []
    for i, hl, o in cands:
        q = {'w': i, 'hl': hl, 'o': o}
        if not ver: q['m'] = 1
        out.append(q)
    return out
def gen_surah(s):
    out = {}
    for a in range(1, len(Q[s-1]['v']) + 1):
        r = gen_ayah(s, a)
        if r: out[str(a)] = r
    return {'s': s, 'ayahs': out}

def _relax(sig):
    return ('N', sig[1], '', sig[3], sig[4]) if sig[0] == 'N' else ('V', '', '', sig[3], sig[4])
_LF = None
def LEMF():
    global _LF
    if _LF is None:
        _LF = collections.Counter()
        for lst in pool().values():
            for x in lst: _LF[x[4]] += 1
    return _LF
_RP = None
def auto_fill(s, a, i, taken, n):
    """n attested words (refs) with the same grammatical signature as word i of s:a, different root/meaning, not in `taken` (normalised words); relaxed signature if needed."""
    global _RP
    g = gram(s)[a-1]; m = mad(s, a)
    if len(g) != len(m): return []
    inf = info(g[i-1])
    if not inf: return []
    if _RP is None:
        _RP = collections.defaultdict(list)
        for sg, lst in pool().items(): _RP[_relax(sg)].extend(lst)
    rng = random.Random(s * 100000 + a * 100 + i); gl = set(ctokens(g[i-1][1]))
    seen = set(taken) | {norm(x) for x in m} | {bare(x) for x in m}; out = []; roots = {inf['root']}
    for P, tol in ((pool().get(inf['sig'], []), 3), (_RP.get(_relax(inf['sig']), []), 4), (_RP.get(_relax(inf['sig']), []), 12)):
        c = [x for x in P if x[3] != inf['root'] and x[4] != inf['lem'] and not (x[5] & gl) and abs(x[6] - inf['len']) <= tol and not (x[0] == s and x[1] == a)]
        fr = LEMF()
        rng.shuffle(c); u = {}
        for x in c: u.setdefault((x[4], x[7]), x)
        c = sorted(u.values(), key=lambda x: -fr[x[4]])[:80]; rng.shuffle(c)
        for x in c:
            b = bare(x[7])
            if (x[3] in roots and tol < 12) or x[7] in seen or b in seen: continue
            roots.add(x[3]); seen.add(x[7]); seen.add(b); out.append(x)
            if len(out) == n: return out
    return out
