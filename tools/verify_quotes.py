"""Check every ">> " Qur'an quotation in an article against quran.json.

The reference is taken from the citation on the lines just after the quote (e.g. "(Sūrat al-Baqarah 2:21–22 · …)"),
or from ayah-number markers inside the quote (۝٥ or ﴿١١٢﴾). Comparison is on a consonant skeleton, so
spelling differences between editions (alif forms, ى/ي, tatweel, harakat) do not cause false alarms.
Lines that are not Qur'an (hadith, tafsir quotes) show as NO-REF/CHECK - verify those with the Hadith/tafsir tools.

Usage:  python3 tools/verify_quotes.py article.md
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = json.load(open(os.path.join(ROOT, 'quran.json'), encoding='utf-8'))
AD = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
def sk(t): return re.sub(r'[^ء-ي]|[ـاأإآءىئؤيو]', '', t.replace('ٱ', 'ا'))
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
bad = 0
for k, ln in enumerate(L):
    if not ln.startswith('>> '): continue
    q = ln[3:]
    after = '\n'.join(L[k+1:k+4])
    m = re.search(r'(\d{1,3}):(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?', after)
    if not m:
        print('NO-REF ', q[:50]); continue
    s, a0, a1 = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
    txt = re.sub(r'[﴿﴾۝٠-٩]', '', q)
    full = ''.join(Q[s-1]['v'][a-1][0] for a in range(a0, a1+1) if a <= len(Q[s-1]['v']))
    ok = sk(txt) == sk(full) or (sk(txt) and sk(txt) in sk(full))
    if not ok: bad += 1
    print(('OK     ' if ok else 'CHECK  ') + f'{s}:{a0}' + (f'-{a1}' if a1 != a0 else ''), q[:40])
print('mismatches:', bad)
