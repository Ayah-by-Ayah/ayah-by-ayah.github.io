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
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Ayah by Ayah">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231E4E79'/%3E%3Ctext x='32' y='44' font-size='34' text-anchor='middle' fill='white' font-family='serif'%3E%D8%A2%3C/text%3E%3C/svg%3E">
<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
'''
PWA_JS = r'''<script>
/* Install as an app + offline use (public site only). Service worker: sw.js */
(function(){
  var h = location.hostname, test = /[?&]pwa=1/.test(location.search);
  if (!test && (h === "127.0.0.1" || h === "localhost")) return;     // the Windows exe and local tests do not need it
  if (!("serviceWorker" in navigator)) return;
  var FILES = __FILES__;
  navigator.serviceWorker.register("sw.js").catch(function(){});
  var deferred = null, KEY = "aba.offline";
  function get(k){ try { return localStorage.getItem(k); } catch(e){ return null; } }
  function set(k,v){ try { localStorage.setItem(k,v); } catch(e){} }
  var bar = document.createElement("div");
  bar.setAttribute("style", "position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:9999;max-width:520px;margin:0 auto;background:#1E4E79;color:#fff;border-radius:14px;padding:10px 12px;font:14px/1.35 system-ui,sans-serif;box-shadow:0 6px 24px rgba(0,0,0,.28);display:none;align-items:center;gap:8px;flex-wrap:wrap");
  var msg = document.createElement("span"); msg.style.flex = "1 1 160px";
  function btn(label, fn, solid){ var b = document.createElement("button"); b.type = "button"; b.textContent = label; b.onclick = fn;
    b.setAttribute("style", "border:1px solid #fff;border-radius:10px;padding:7px 12px;font:600 13px system-ui,sans-serif;cursor:pointer;" + (solid ? "background:#fff;color:#1E4E79" : "background:transparent;color:#fff")); return b; }
  var bInstall = btn("Install app", function(){ if (deferred) { deferred.prompt(); deferred.userChoice.finally(function(){ deferred = null; render(); }); } }, true);
  var bSave = btn("Save for offline (≈35 MB)", saveAll, true);
  var bHide = btn("Not now", function(){ set("aba.pwahide", String(Date.now())); bar.style.display = "none"; }, false);
  bar.appendChild(msg); bar.appendChild(bInstall); bar.appendChild(bSave); bar.appendChild(bHide);
  document.addEventListener("DOMContentLoaded", function(){ document.body.appendChild(bar); render(); });
  window.addEventListener("beforeinstallprompt", function(e){ e.preventDefault(); deferred = e; render(); });
  window.addEventListener("appinstalled", function(){ deferred = null; render(); });
  var standalone = window.matchMedia && window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
  var busy = false;
  function render(){
    var hidden = +get("aba.pwahide") || 0, saved = get(KEY) === "1";
    var show = !busy && (hidden === 0 || Date.now() - hidden > 7*864e5) && (!saved || (deferred && !standalone));
    if (busy) { bar.style.display = "flex"; return; }
    bar.style.display = show ? "flex" : "none";
    bInstall.style.display = deferred && !standalone ? "" : "none";
    bSave.style.display = saved ? "none" : "";
    msg.textContent = saved ? "Saved for offline use. You can install it as an app." : "Use Ayah by Ayah offline, like an app.";
  }
  function saveAll(){
    if (busy) return; busy = true; bInstall.style.display = bSave.style.display = bHide.style.display = "none"; bar.style.display = "flex";
    var i = 0, done = 0, failed = 0, N = FILES.length;
    function upd(){ msg.textContent = "Saving for offline… " + Math.round(done / N * 100) + "%"; }
    function next(){
      if (i >= N) return;
      var f = FILES[i++];
      fetch(f).then(function(r){ if (!r.ok) failed++; return r.arrayBuffer(); }).catch(function(){ failed++; })
        .then(function(){ done++; upd(); if (done === N) finish(); else next(); });
    }
    function finish(){
      busy = false; bHide.style.display = "";
      if (failed === 0) { set(KEY, "1"); render(); msg.textContent = "Saved for offline use."; bar.style.display = "flex"; setTimeout(function(){ bar.style.display = "none"; }, 4000); }
      else { msg.textContent = "Some files could not be saved (" + failed + "). Check the connection and try again."; bSave.style.display = ""; bSave.textContent = "Try again"; }
    }
    upd(); for (var k = 0; k < 5; k++) next();
  }
})();
</script>'''
FILES = ['quran.json', 'indopak.json', 'indopak-font.woff2', 'conc.json', 'forms.json', 'tr-bn.json', 'tr-ur.json', 'learn-bn.json', 'data/content.json']
for d in ('grammar', 'syntax', 'learn', 'exercise'):
    FILES += ['%s/%d.json' % (d, n) for n in range(1, 115) if os.path.exists(os.path.join(ROOT, d, '%d.json' % n))]
import json, hashlib
html = meta + head + '\n</head>\n<body>' + body + PWA_JS.replace('__FILES__', json.dumps(FILES)) + '\n</body>\n</html>\n'
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html)
manifest = {"name": "Ayah by Ayah", "short_name": "Ayah by Ayah", "description": "Qur'an study, one ayah at a time",
            "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any",
            "background_color": "#1E4E79", "theme_color": "#1E4E79", "lang": "en",
            "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                      {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                      {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open(os.path.join(ROOT, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps(manifest, indent=1))
SW = r'''/* Ayah by Ayah service worker (generated by tools/build_site.py). Offline use for the public site.
   - index.html and data/content.json: network first (new publishes arrive), cached copy when offline
   - every other file: cached copy first, refreshed quietly in the background (304 when unchanged) */
const SHELL = "aba-shell-__V__", DATA = "aba-data";
const CORE = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "quran.json", "indopak.json", "indopak-font.woff2", "data/content.json", "forms.json", "conc.json", "tr-bn.json", "learn-bn.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(SHELL).then(c => Promise.allSettled(CORE.map(u => c.add(new Request(u, {cache: "reload"}))))).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("aba-shell-") && k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const isShell = u => { const p = new URL(u).pathname; return p.endsWith("/") || p.endsWith("/index.html") || p.endsWith("/data/content.json"); };
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  if (u.origin !== location.origin) return;
  if (r.mode === "navigate" || isShell(r.url)) {
    e.respondWith(fetch(r).then(res => { if (res.ok) { const c = res.clone(); caches.open(SHELL).then(ca => ca.put(r.mode === "navigate" ? "index.html" : r, c)); } return res; })
      .catch(() => caches.match(r.mode === "navigate" ? "index.html" : r, {ignoreSearch: true}).then(m => m || caches.match("index.html"))));
    return;
  }
  e.respondWith(caches.match(r, {ignoreSearch: true}).then(m => {
    const net = fetch(r, {cache: "no-cache"}).then(res => { if (res.ok) { const c = res.clone(); caches.open(DATA).then(ca => ca.put(r, c)); } return res; });
    if (m) { net.catch(() => {}); return m; }
    return net;
  }));
});
'''
ver = hashlib.sha1((html + json.dumps(manifest)).encode('utf-8')).hexdigest()[:10]
open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8').write(SW.replace('__V__', ver))
open(os.path.join(ROOT, '.nojekyll'), 'w').write('')
print('index.html written,', len(html), 'bytes')
