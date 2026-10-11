/* Ayah by Ayah — offline edition shim.
   Loaded before the app. Gives the app a local stand-in for window.claude:
   - db        : the artifact's database, backed by the baseline embedded in this file + your edits on this device
   - user      : always the editor
   - sample    : none (the in-app AI needs a connection)
   - downloads : saves a file through the browser
   and answers the app's fetch() calls (quran.json, translations, grammar …) from data embedded in this file.
   Edits are kept in IndexedDB (fallback: localStorage) and exported as a sync file that the online platform imports. */
(function(){
"use strict";
const $json = (id) => JSON.parse(document.getElementById(id).textContent);
const BASE = $json("offline-base");          // {baseId, exportedAt, docs:{ "notes/x": {...} }}
const RES  = $json("offline-res");           // {"quran.json": "<base64 gzip>", ...}
const FORMAT = "ayah-by-ayah-offline-sync";

/* ---- stable hash of a document (same function lives in the online app, for conflict checks) ---- */
function stable(v){
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(stable).join(",") + "]";
  return "{" + Object.keys(v).filter(k => v[k] !== undefined).sort().map(k => JSON.stringify(k) + ":" + stable(v[k])).join(",") + "}";
}
function hashDoc(d){
  if (d == null) return null;
  const s = stable(d); let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
  for (let i = 0; i < s.length; i++) { const c = s.charCodeAt(i); h1 = Math.imul(h1 ^ c, 2654435761); h2 = Math.imul(h2 ^ c, 1597334677); }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
}
const clone = (v) => v === undefined ? undefined : JSON.parse(JSON.stringify(v));

/* ---- persistence: {baseId, overlay:{path: doc|null}, pending:{path:{baseHash, ts}}} ---- */
let state = {baseId: BASE.baseId, overlay: {}, pending: {}};
let persistMode = "memory";
const IDB = {name: "ayah-by-ayah-offline", store: "kv", key: "state"};
function idbOpen(){
  return new Promise((res, rej) => {
    let rq; try { rq = indexedDB.open(IDB.name, 1); } catch (e) { return rej(e); }
    rq.onupgradeneeded = () => rq.result.createObjectStore(IDB.store);
    rq.onsuccess = () => res(rq.result); rq.onerror = () => rej(rq.error);
  });
}
async function loadState(){
  let saved = null;
  try { const db = await idbOpen(); saved = await new Promise((res, rej) => { const r = db.transaction(IDB.store).objectStore(IDB.store).get(IDB.key); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); persistMode = "idb"; db.close(); }
  catch (e) {
    try { const t = localStorage.getItem("aba.offline.state"); if (t !== null) saved = JSON.parse(t); localStorage.setItem("aba.offline.probe", "1"); persistMode = "ls"; } catch {}
  }
  if (saved && typeof saved === "object") {
    state.overlay = saved.overlay || {}; state.pending = saved.pending || {};
    if (saved.baseId !== BASE.baseId) {
      // a newer offline file was opened: the fresh baseline wins everywhere except for edits not yet synced
      for (const p of Object.keys(state.overlay)) if (!state.pending[p]) delete state.overlay[p];
    }
  }
  state.baseId = BASE.baseId;
}
let saveTimer = 0, savePromise = Promise.resolve();
function persist(){
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { savePromise = savePromise.then(writeState).catch(() => {}); }, 30);
}
async function writeState(){
  if (persistMode === "idb") {
    const db = await idbOpen();
    await new Promise((res, rej) => { const tx = db.transaction(IDB.store, "readwrite"); tx.objectStore(IDB.store).put(clone(state), IDB.key); tx.oncomplete = () => res(); tx.onerror = () => rej(tx.error); });
    db.close();
  } else if (persistMode === "ls") { localStorage.setItem("aba.offline.state", JSON.stringify(state)); }
}

/* ---- document access ---- */
const baseDocs = BASE.docs;
function getDoc(path){ if (path in state.overlay) return state.overlay[path]; return Object.prototype.hasOwnProperty.call(baseDocs, path) ? baseDocs[path] : null; }
function allPaths(col){
  const out = new Set();
  for (const p of Object.keys(baseDocs)) if (p.startsWith(col + "/")) out.add(p);
  for (const p of Object.keys(state.overlay)) if (p.startsWith(col + "/")) out.add(p);
  return [...out].filter(p => getDoc(p) != null).sort();
}
const listeners = [];
function snapOf(col, filter){
  const docs = allPaths(col).map(p => ({id: p.slice(col.length + 1), data: () => clone(getDoc(p))})).filter(d => !filter || filter(d.data()));
  return {docs, size: docs.length, empty: !docs.length, forEach(f){ docs.forEach(f); }};
}
function notify(path){
  const col = path.split("/")[0];
  for (const l of listeners) {
    if (l.kind === "col" && l.col === col) queueMicrotask(() => { try { l.cb(snapOf(col, l.filter)); } catch (e) { console.error(e); } });
    if (l.kind === "doc" && l.path === path) queueMicrotask(() => { try { l.cb(docSnap(path)); } catch (e) { console.error(e); } });
  }
}
function docSnap(path){ const d = getDoc(path); return {exists: d != null, id: path.split("/").pop(), data: () => clone(d)}; }
function markPending(path){
  if (!state.pending[path]) {
    const cur = getDoc(path);
    state.pending[path] = {baseHash: hashDoc(cur), baseUpdatedAt: cur && cur.updatedAt != null ? cur.updatedAt : null, ts: Date.now()};
  } else state.pending[path].ts = Date.now();
}
function afterWrite(path){
  // an edit that puts a doc back exactly where it was last synced is no longer a change
  const p = state.pending[path];
  if (p && hashDoc(getDoc(path)) === p.baseHash) delete state.pending[path];
  persist(); notify(path); window.dispatchEvent(new Event("offline-pending"));
}
function write(path, doc){ markPending(path); state.overlay[path] = doc == null ? null : clone(doc); afterWrite(path); }
function docRef(path){
  const parts = path.split("/");
  return {
    id: parts[parts.length - 1], path,
    async get(){ return docSnap(path); },
    async set(d){ write(path, d); },
    async update(patch){ const cur = getDoc(path); if (cur == null) { const e = new Error("not found"); e.code = "not_found"; throw e; } write(path, Object.assign(clone(cur), clone(patch))); },
    async delete(){ write(path, null); },
    onSnapshot(cb){ const l = {kind: "doc", path, cb}; listeners.push(l); queueMicrotask(() => cb(docSnap(path))); return () => { const i = listeners.indexOf(l); if (i >= 0) listeners.splice(i, 1); }; }
  };
}
const db = {
  collection(col){
    return {
      doc: (id) => docRef(col + "/" + id),
      onSnapshot(cb){ const l = {kind: "col", col, cb, filter: null}; listeners.push(l); queueMicrotask(() => cb(snapOf(col))); return () => { const i = listeners.indexOf(l); if (i >= 0) listeners.splice(i, 1); }; },
      where(field, op, val){
        const filter = (d) => op === "==" ? d && d[field] === val : true;
        return { onSnapshot(cb){ const l = {kind: "col", col, cb, filter}; listeners.push(l); queueMicrotask(() => cb(snapOf(col, filter))); return () => { const i = listeners.indexOf(l); if (i >= 0) listeners.splice(i, 1); }; } };
      },
      async get(){ return snapOf(col); }
    };
  },
  doc: (path) => docRef(path)
};

/* ---- files the app fetches ---- */
const b64 = (s) => { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return u; };
const resCache = {};
function resource(key){
  if (!(key in RES)) return null;
  return resCache[key] ||= (async () => {
    const ds = new DecompressionStream("gzip");
    return new Response(new Blob([b64(RES[key])]).stream().pipeThrough(ds)).arrayBuffer();
  })();
}
const origFetch = window.fetch ? window.fetch.bind(window) : null;
window.fetch = async function(input, init){
  const url = String(typeof input === "string" ? input : (input && input.url) || "");
  const clean = url.split("#")[0].split("?")[0];
  const m = clean.match(/((?:grammar|syntax)\/\d+\.json|[\w.-]+\.(?:json|woff2))$/);
  if (m) {
    const p = resource(m[1]);
    if (p) { const buf = await p; return new Response(buf.slice(0), {status: 200, headers: {"Content-Type": m[1].endsWith(".woff2") ? "font/woff2" : "application/json; charset=utf-8"}}); }
    return new Response("", {status: 404});
  }
  if (/^https?:/i.test(clean) && origFetch && location.protocol !== "file:" && clean.indexOf(location.origin) !== 0) return origFetch(input, init);
  return new Response("", {status: 404});
};

/* ---- sync file ---- */
const pad = (n) => String(n).padStart(2, "0");
function pendingList(){ return Object.keys(state.pending).sort(); }
function buildSyncFile(){
  const changes = pendingList().map(path => {
    const d = getDoc(path), p = state.pending[path];
    const head = {path, baseHash: p.baseHash, baseUpdatedAt: p.baseUpdatedAt == null ? null : p.baseUpdatedAt, ts: p.ts};
    return d == null ? Object.assign({op: "delete"}, head) : Object.assign({op: "set", doc: clone(d)}, head);
  });
  return {format: FORMAT, version: 1, createdAt: new Date().toISOString(), baseId: BASE.baseId, baseExportedAt: BASE.exportedAt, changes};
}
function saveFile(filename, data, type){
  const blob = new Blob([data], {type: type || "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = filename; document.body.appendChild(a); a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
}
function exportChanges(){
  const f = buildSyncFile(), d = new Date();
  saveFile(`ayah-by-ayah-sync-${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}.json`, JSON.stringify(f, null, 1));
  return f.changes.length;
}
function markSynced(){ state.pending = {}; persist(); window.dispatchEvent(new Event("offline-pending")); }

window.__OFFLINE__ = {
  baseId: BASE.baseId, exportedAt: BASE.exportedAt, hashDoc, FORMAT,
  pendingCount: () => pendingList().length,
  pendingPaths: pendingList, buildSyncFile, exportChanges, markSynced,
  persistMode: () => persistMode,
  ready: null
};
window.__OFFLINE__.ready = loadState();

window.claude = {
  async use(name){
    await window.__OFFLINE__.ready;
    if (name === "db") return db;
    if (name === "user") return {canEdit: async () => true, isOwner: async () => true};
    if (name === "downloads") return {save: async ({filename, data}) => { saveFile(filename, data); }};
    return null;   // "sample" (AI) and anything else: not available offline
  }
};
})();
