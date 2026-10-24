#!/usr/bin/env python3
"""Build the 15-line IndoPak page table used by the surah reader.

Source: tools/pages15_src.txt, one line per page "page | first ayah | last ayah"
(610 pages; copied 24 Oct 2026 from QUL, Quranic Universal Library, mushaf layout 6
"Indopak 15 lines - Qudratullah" https://qul.tarteel.ai/mushaf_layouts/6).
The script checks that the table is gap-free against quran.json (every ayah on exactly one
page, 1:1 first, 114:6 last) and then rewrites the block between /*PAGE15-START*/ and
/*PAGE15-END*/ in tools/app.html with  const PAGE15 = {surah: [[firstAyahOnAPage, page], ...]}.

Usage: python3 tools/build_pages.py
"""
import json, re, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
q = json.load(open(os.path.join(root, "quran.json"), encoding="utf-8"))
cnt = {s["n"]: len(s["v"]) for s in q}
rows = []
for line in open(os.path.join(root, "tools", "pages15_src.txt"), encoding="utf-8"):
    if not line.strip():
        continue
    p, a, b = [x.strip() for x in line.split("|")]
    rows.append((int(p), tuple(map(int, a.split(":"))), tuple(map(int, b.split(":")))))
errs = []
if [r[0] for r in rows] != list(range(1, 611)):
    errs.append("pages are not 1..610")
nxt = lambda s, a: (s, a + 1) if a < cnt[s] else (s + 1, 1)
if rows[0][1] != (1, 1):
    errs.append("does not start at 1:1")
for i, (p, f, l) in enumerate(rows):
    if f > l or f[1] > cnt[f[0]] or l[1] > cnt[l[0]]:
        errs.append(f"bad range on page {p}")
    if i + 1 < len(rows) and nxt(*l) != rows[i + 1][1]:
        errs.append(f"gap or overlap after page {p}")
if rows[-1][2] != (114, cnt[114]):
    errs.append("does not end at 114:6")
if errs:
    sys.exit("PAGE TABLE INVALID: " + "; ".join(errs))
by = {}
for p, (s, a), _ in rows:
    by.setdefault(s, []).append([a, p])
js = "const PAGE15 = " + json.dumps(by, separators=(",", ":")) + ";"
path = os.path.join(root, "tools", "app.html")
html = open(path, encoding="utf-8").read()
new, n = re.subn(r"/\*PAGE15-START\*/.*?/\*PAGE15-END\*/", lambda m: "/*PAGE15-START*/" + js + "/*PAGE15-END*/", html, flags=re.S)
if n != 1:
    sys.exit("markers /*PAGE15-START*/ ... /*PAGE15-END*/ not found exactly once in tools/app.html")
open(path, "w", encoding="utf-8").write(new)
print("OK: 610 pages, gap-free; PAGE15 written to tools/app.html")
