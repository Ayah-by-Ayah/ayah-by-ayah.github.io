import json,re,collections,sys
sys.path.insert(0,'.')
import nouns
R='/home/claude/ayah-by-ayah.github.io/'
F=json.load(open(R+'forms.json'))['n']
EX=('PN','DEM','REL','PRON','LOC','T')
M={}
for s in range(1,115):
    for a,ws in enumerate(json.load(open(f'{R}grammar/{s}.json')),1):
        for wi,w in enumerate(ws,1):
            bare=len(w[2])==1
            for t,p,f in w[2]:
                fl=f.split('|')
                if 'PREF' in fl or 'SUFF' in fl or p!='N' or any(x in fl for x in EX): continue
                L=[x[4:] for x in fl if x.startswith('LEM:')]
                if not L or L[0] in F: continue
                d=M.setdefault(L[0],{'surahs':{},'gl':{},'root':'','tags':set(),'first':{},'n':0})
                d['n']+=1
                d['surahs'].setdefault(str(s),[])
                if a not in d['surahs'][str(s)]: d['surahs'][str(s)].append(a)
                d['first'].setdefault(str(s),a*1000+wi)
                for x in fl:
                    if x.startswith('ROOT:'): d['root']=x[5:]
                d['tags'].update(x for x in fl if x in ('ADJ','ACT_PCPL','PASS_PCPL','VN','M','F','MS','FS','MP','FP','MD','FD','INDEF'))
                d['gl'][w[1]]=d['gl'].get(w[1],0)+(3 if bare else 1)
for d in M.values(): d['tags']=sorted(d['tags'])
order=sorted(M,key=lambda k:-M[k]['n'])
json.dump({'inv':M,'order':order},open('missing.json','w'),ensure_ascii=False)
with open('missing_list.txt','w') as o:
    for i,k in enumerate(order):
        d=M[k]
        o.write(f"{i}|{k}|{d['n']}|{','.join(t for t in d['tags'] if t in ('ADJ','ACT_PCPL','PASS_PCPL','VN','F'))}|{nouns.best_gloss(d)}\n")
print(len(order))
