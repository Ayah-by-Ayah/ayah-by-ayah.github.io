import json, re, collections
R = '/home/claude/ayah-by-ayah.github.io/'
F = json.load(open(R + 'forms.json'))['n']
inv = json.load(open(R + 'tools/learn_src/inventory.json'))['n']
LEAD = re.compile(r"^(?:(?:and|so|then|but|or|that|indeed|surely|verily|for|in|of|to|with|by|like|as|from|on|upon|those|which|who|whoever|not|no|a|an|the|his|her|their|your|our|my|its|[Ww]hat|this|these|[Ss]ome|every|all|any|is|are|was|were|be|been|being|will|shall|would|may|might|can|could|does|do|did|has|have|had)\s+)+", re.I)
def clean(g):
    g = re.sub(r"\[[^\]]*\]", lambda m: m.group(0)[1:-1] if m.group(0)[1:-1] in ('the','of') else '', g)
    g = re.sub(r"\([^)]*\)", " ", g)
    g = g.replace('[', '').replace(']', '')
    g = re.sub(r"\s+", " ", g).strip(" ,.;:!?\"'")
    g = LEAD.sub("", g).strip()
    return g
def best_gloss(d):
    c = collections.Counter()
    for g, n in d['gl'].items():
        cg = clean(g)
        if cg and not re.search(r"[^A-Za-z \-']", cg): c[cg.lower()] += n
    if not c: return ''
    top = sorted(c.items(), key=lambda x: (-x[1], len(x[0])))
    return top[0][0]
AR = re.compile(r'^[ء-ْٰٱ]+$')
MK = re.compile('[\u064B-\u0652\u0670]')
def voweled(x):
    letters = len(MK.sub('', x))
    return len(MK.findall(x)) >= max(1, letters // 3)
def plurals(sg, pl, sm, sf, tags=()):
    out = []
    ok = lambda x: x and AR.match(x) and voweled(x)
    plain = lambda x: MK.sub('', x)
    for want in (1, 0):
        for p, q in pl:
            if q == want and ok(p) and p not in out and plain(p) != plain(sg):
                out.append(p)
    out = out[:2]
    base = re.sub('[\u064B\u064C\u064D\u064E\u064F\u0650]+$', '', sg)
    fem = base.endswith('\u0629')
    if len(out) < 2 and sm and not fem and not out and any(t in tags for t in ('ACT_PCPL', 'PASS_PCPL', 'ADJ')) and 'VN' not in tags:
        out.append(base + '\u064F\u0648\u0646\u064E')
    if len(out) < 2 and sf and fem and not out:
        out.append(re.sub('[\u064B-\u0652]+$', '', base[:-1]) + '\u064E\u0627\u062A\u064C')
    return out[:2]
def noun_row(lem):
    e = F[lem]; sg = e[0]
    pl = e[1]
    if e[2]:   # lemma is itself a plural of e[2]
        sg = e[2] if AR.match(e[2]) else sg
    return sg, plurals(sg, pl, e[3][0], e[3][1], inv[lem]['tags'] if lem in inv else ())
if __name__ == '__main__':
    import random
    random.seed(11)
    ks = list(inv)
    for k in random.sample(ks, 40):
        sg, pl = noun_row(k)
        print(k, '|', sg, pl, '|', best_gloss(inv[k]), '|', dict(list(inv[k]['gl'].items())[:2]))
