"""Build the offline edition: ONE html file that runs without internet.

It contains the editor (tools/app.html), the Qur'an text, IndoPak script + font, the Bangla and Urdu
translations, grammar, treebank, word index and forms, plus a snapshot of the platform's database.
Edits are kept on the device and exported as a sync file; the online platform imports that file.

Usage (repo root):
  python3 tools/build_offline.py <db export dir> [out.html]
<db export dir> = the ArtifactData export (one folder per collection, one <doc id>.json per document;
"@" in a file name stands for "~" in the id, as ArtifactData writes it).
"""
import base64, glob, gzip, hashlib, json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
export = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "ayah-by-ayah-offline.html")

# ---- database snapshot ----
docs = {}
for col in sorted(os.listdir(export)):
    d = os.path.join(export, col)
    if not os.path.isdir(d):
        continue
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        doc_id = os.path.basename(f)[:-5].replace("@", "~")
        docs[f"{col}/{doc_id}"] = json.load(open(f, encoding="utf-8"))
exported_at = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
base_id = hashlib.sha1(json.dumps(docs, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
base = {"baseId": base_id, "exportedAt": exported_at, "docs": docs}

# ---- embedded files ----
res = {}
def add(key, path):
    raw = open(path, "rb").read()
    res[key] = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
for name in ["quran.json", "indopak.json", "indopak-font.woff2", "tr-bn.json", "tr-ur.json", "conc.json", "forms.json"]:
    add(name, os.path.join(ROOT, name))
for kind in ["grammar", "syntax"]:
    for n in range(1, 115):
        add(f"{kind}/{n}.json", os.path.join(ROOT, kind, f"{n}.json"))

def safe(js):  # keep the JSON inside <script> tags
    return js.replace("</", "<\\/").replace("<!--", "<\\!--")

src = open(os.path.join(ROOT, "tools", "app.html"), encoding="utf-8").read()
shim = open(os.path.join(ROOT, "tools", "offline_shim.js"), encoding="utf-8").read()
i = src.index("</style>") + len("</style>")
head, body = src[:i], src[i:]
meta = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Ayah by Ayah — offline</title>
<meta name="theme-color" content="#1E4E79">
<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
'''
html = (meta + head + "\n"
        + '<script id="offline-base" type="application/json">' + safe(json.dumps(base, ensure_ascii=False)) + "</script>\n"
        + '<script id="offline-res" type="application/json">' + safe(json.dumps(res)) + "</script>\n"
        + "<script>\n" + shim + "\n</script>\n</head>\n<body>" + body + "\n</body>\n</html>\n")
open(out, "w", encoding="utf-8").write(html)
print("offline edition:", out, round(len(html) / 1e6, 1), "MB; baseId", base_id, "; documents", len(docs))
