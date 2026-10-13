import json,re,collections,sys
sys.path.insert(0,'/home/claude/ayah-by-ayah.github.io/tools/learn_src')
import participles as P
R='/home/claude/ayah-by-ayah.github.io/'
F=json.load(open(R+'forms.json')); inv=json.load(open(R+'tools/learn_src/inventory.json'))
order=json.load(open(R+'tools/learn_src/verb_order.json')); mean=json.load(open(R+'tools/learn_src/verb_meanings.json'))
act=collections.defaultdict(set); pas=collections.defaultdict(set)
for lem,d in inv['n'].items():
    if d['root'] and 'ACT_PCPL' in d['tags']: act[d['root']].add(P.N(lem))
    if d['root'] and 'PASS_PCPL' in d['tags']: pas[d['root']].add(P.N(lem))
def forms(g):
    n=P.N(g); out={n}
    if g.endswith(P.KASRAN) or g.endswith(P.KASRAN+P.SHADDA) or P.KASRAN in g[-3:] or g.endswith('ى'): out.add(n+'ي')
    if g.endswith('ى'): out.add(n[:-1]+'ي')
    return out
def check(gen, attested):
    """None = nothing comparable; True/False = comparable & match"""
    g=forms(gen); comp=[a for a in attested if any(a[:2]==x[:2] and abs(len(a)-len(x))<=1 for x in g)]
    # same family: same first 2 letters and similar length
    if not comp: return None
    return any(a in g or any(a.startswith(x) or x.startswith(a) for x in g) and abs(len(a)-len(list(g)[0]))<=1 and a[-2:]==list(g)[0][-2:] for a in comp), comp
res={}; bad=[]; st=collections.Counter()
for i,k in enumerate(order):
    m=F['v'][k]; d=inv['v'][k]; tr=mean[str(i)][1]=='t'
    fa,mf=P.make(m[0],m[1],set(d['vf']),d['root'],tr); res[k]=(fa,mf)
    for kind,g,pool in (('fa',fa,act[d['root']]),('mf',mf,pas[d['root']])):
        if not g or not pool: continue
        r=check(g,pool)
        if r is None: st[kind,'none']+=1; continue
        ok,comp=r
        st[kind,'ok' if ok else 'bad']+=1
        if not ok: bad.append((kind,m[0],d['root'],g,comp))
if __name__=='__main__':
    print(dict(st))
    for b in bad: print(b)
