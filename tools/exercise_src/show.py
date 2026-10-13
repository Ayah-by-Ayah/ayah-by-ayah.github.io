import sys
from common import *
s=int(sys.argv[1]); lo,hi=int(sys.argv[2]),int(sys.argv[3])
for a in range(lo,hi+1):
    w=mad(s,a); g=gram(s)[a-1]; ok=len(g)==len(w)
    print(f'{s}:{a} '+' '.join(f'{i}.{x}'+(f'({g[i-1][1]})' if ok else '') for i,x in enumerate(w,1)))
    print('   EN:',Q[s-1]['v'][a-1][1])
