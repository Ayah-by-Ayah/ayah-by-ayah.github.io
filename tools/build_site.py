"""Build the public site's index.html from tools/app.html.

The private platform (claude.ai artifact) is published straight from tools/app.html.
The public GitHub Pages edition is the same file wrapped in a full HTML document;
with no window.claude it runs in static mode and reads data/content.json.

Usage (from the repo root):  python3 tools/build_site.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'tools', 'app.html'), encoding='utf-8').read()
i = src.index('</style>') + len('</style>')
head, body = src[:i], src[i:]
meta='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Read the Qur'an ayah by ayah: Arabic in IndoPak and Madani script, a revised English translation, notes, lessons, word analysis and full grammar and iʿrāb, in English, Bangla, Arabic and Urdu.">
<meta property="og:title" content="Ayah by Ayah">
<meta property="og:description" content="Qur'an study, one ayah at a time: translation, notes, lessons, word analysis and grammar.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#1E4E79">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231E4E79'/%3E%3Ctext x='32' y='44' font-size='34' text-anchor='middle' fill='white' font-family='serif'%3E%D8%A2%3C/text%3E%3C/svg%3E">
<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
'''
html = meta + head + '\n</head>\n<body>' + body + '\n</body>\n</html>\n'
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html)
open(os.path.join(ROOT, '.nojekyll'), 'w').write('')
print('index.html written,', len(html), 'bytes')
