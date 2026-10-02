# Ayah by Ayah — handbook for working on this project

Read this first in any new session. It is the memory of how the project works.
The owner and only editor is **Tanveer** (works in English, Bangla, Arabic, Urdu).

## 1. What exists and where

| Piece | Where | Notes |
|---|---|---|
| **Private platform** (the editor) | claude.ai artifact **https://claude.ai/artifact/Dvrgy2h2wVJpAWz9397aoo** | All writing and editing happens here. Private to Tanveer. |
| Its database (all content) | the artifact's database, read/written with the **ArtifactData** tool on that URL | Notes, lessons, word analyses, translation revisions, iʿrāb, categories. |
| **Public site** (read-only) | **https://ayah-by-ayah.github.io** — repo **Ayah-by-Ayah/ayah-by-ayah.github.io** (this repo) | GitHub Pages, free. Same app in "static mode", reading `data/content.json`. |
| App source | `tools/app.html` | One self-contained HTML/JS file. Published to the artifact as-is; wrapped into `index.html` for the public site by `tools/build_site.py`. |
| Data files (shared by both) | repo root | `quran.json` (Uthmani + Saheeh Intl), `indopak.json` + `indopak-font.woff2` (IndoPak script, default), `grammar/1..114.json` (Quranic Arabic Corpus morphology + quran.com glosses), `syntax/1..114.json` (NoorBayan treebank), `tr-bn.json` (Taisirul Quran), `tr-ur.json` (Maududi), `conc.json` (word-occurrence index). |
| Scripts | `tools/` | see section 6. |

To work on it in a new session: attach the repo (add_repo **Ayah-by-Ayah/ayah-by-ayah.github.io**, access "push"), clone it, and use the artifact URL above. Pushing works (the Claude GitHub App is installed on the Ayah-by-Ayah org).

## 2. Tanveer's standing rules

- **The public site is updated only when he says "publish" / "publish the latest".** Never publish on your own.
- **Before publishing, compare** the database export with the current `data/content.json`. If anything that was public is missing from the database, ask before publishing (he has deleted things on purpose before; ask, don't assume).
- **Keep his wording.** When turning his document into a note, change only the layout. Never add, soften or rephrase content without saying so.
- **Articles speak in their own voice.** Never "the lecturer says / the speaker argues / the transcript…". If a source document is framed around a lecture, rewrite it as a direct article (and say you did).
- **Verify every Qur'an quotation** against `quran.json` (`tools/verify_quotes.py`) and the quran.ai tools; **every hadith** with the Hadith tools (and sunnah.com for the public reference number); tafsir quotes with `fetch_tafsir`. Report the check result. Don't state unverifiable claims as fact.
- **All Arabic writing (articles, titles, summaries, drafts) is fully voweled** (harakat on every word), not only Qur'an quotations. Tanveer asked for this on 2 Oct 2026; the in-app AI prompts require it.
- Qur'an Arabic: fully voweled; when several ayahs are shown together, each ends with its ayah-number sign (۝٥ or ﴿٥﴾). He finds Amiri hard to read; IndoPak is the default script.
- **Bangla translation = Taisirul Quran.** Urdu = Maududi (chosen by Claude; he may change it). English = Saheeh International (his base, which he revises ayah by ayah).
- Category names are **English only**; the category filter is always a dropdown.
- Every note needs a category. When he names one, map it to the id below.
- If he asks for "a suitable title", propose one that names the question the article answers; keep his document's own title in it where possible.
- Commit messages end with the attribution lines given in the session's system reminder.

## 3. Database layout (ArtifactData collections)

**notes/<id>** — one ayah each. Readable ids, e.g. `manna-and-salwa`, `between-the-backbone-and-the-ribs`.
```json
{"kind":"explanation","s":2,"a":61,"cat":"caltcom","src":"en",
 "title":{"en":"…","bn":"","ar":"","ur":""}, "summary":{…same 4 keys…}, "body":{…same 4 keys…},
 "tags":["…"], "ai":{"bn":true}, "createdAt":ms, "updatedAt":ms}
```
`src` = language he wrote in. `ai.<lang>: true` = AI-drafted, shown to readers as unreviewed until he presses "Mark as reviewed". Leave other languages empty; he drafts them with the in-editor AI button.

**lessons/<id>** — same text fields plus `ranges: [{s, from, to}]` (a group of ayahs). No category.

**words/<id>** — word analysis: `s, a, w` (word index in the ayah, 1-based), `word, root, lemma, pos`, plus the text fields. Title may be empty (then the word itself is the heading in every language).

**translations/<id>** — his revised ayah translations. English: id `s-a`, `{s,a,text,note,updatedAt}`. Bangla/Urdu: id `s-a-bn` / `s-a-ur` with `lang`.

**irab/<s>-<group>** — `{s, ayahs:{<a>:{text:{en,bn,ar,ur}, ai, src, updatedAt}}}`, group = floor((a-1)/5).

**chunks/<kind>~<id>~<lang>~<r>~<i>** — extra pieces of a long write-up: `{kind(n|l|w), ref, lang, r, i, text}`. The note keeps piece 0 in `body.<lang>` and `more.<lang>={r,n}` (r = revision tag, n = number of pieces); the app stitches them on load (pieces ≤ 48,000 bytes). Always write chunk docs first, then the note, and delete stale chunks.

**settings/categories** — `{"list":[{"id","name":{"en"},"order"}]}`. Current ids:

| id | name |
|---|---|
| `csciobj` | Scientific Objections |
| `cscimir` | Scientific Miracles |
| `caltcom` | Alternative Commentary |
| `cconcept` | Concept |

Always read a document's `version` and pass `if_version` when changing an existing one.

## 4. Article format (body markdown)

`## Section`, `### Sub-section` (build the contents list) · `>> ` Qur'an/Arabic quotation line (Qur'an script, RTL) · `> ` quote · `- ` / `1. ` lists · `---` · `**bold**` `*italic*` `[text](url)` · footnotes `[^1]` + `[^1]: …` · references like 2:255 become links.
House style for a quoted ayah: the `>> ` Arabic line, blank line, then one italic translation line ending with the citation:
`*“…”* (Sūrat al-Baqarah 2:57 · trans. Sahih International)`.
Write-ups over ~900 characters (or with sections/footnotes) open as full article pages: `#n-<id>`, `#l-<id>`, `#w-<id>`.

## 5. Workflows

### A. "Add this document as a note at x:y, category …"
1. Copy the .docx to the scratchpad. `python3 tools/docx_to_note.py in.docx out.md` (prints TITLE and SUBTITLE).
2. Read the whole output. Remove production notes (fonts, "check before publication", transcript remarks) and any lecture framing; tell him what you removed.
3. `python3 tools/verify_quotes.py out.md`. Every Qur'an line must be OK (a stray tatweel or alif spelling is not a real difference; the script already ignores those). Check hadith/tafsir lines with the tools.
4. Build the note JSON (shape above; `src:"en"`, other languages empty, `ai:{}`), save with ArtifactData `set` on `notes/<readable-id>`.
5. Report: title, summary, category, tags, the verification result, anything you changed. If the article is mostly about a different ayah than the one he named, mention it (he usually wants the ayah the article is about).

### B. "Publish" / "publish the latest"
1. Export all seven collections (add `chunks`) (ArtifactData `list`, `query {"limit":1000}`, `out_dir` = scratchpad/export) — notes, lessons, words, translations, irab, settings, chunks.
2. Compare with the current `data/content.json` (see rule in section 2).
3. `python3 tools/make_content.py <export dir>` and, if `tools/app.html` changed, `python3 tools/build_site.py`.
4. Commit and push. Pages deploys in about 1–3 minutes.
5. Check it is live: WebFetch caches by URL, so fetch an odd path such as `https://ayah-by-ayah.github.io/data//content.json` and compare `exportedAt`. (curl from the shell to github.io is blocked by the proxy.)

### C. Changing the app
1. Edit `tools/app.html`.
2. Test locally: `python3 tools/build_site.py`, put a `data/content.json` next to it, serve the folder with a server that sends `charset=utf-8` (python's plain http.server does not, and the page then looks garbled), and drive it with Playwright (Chromium is preinstalled; `NODE_PATH=$(npm root -g)`). To test editor features, inject a fake `window.claude` with `addInitScript` (`use(n)` returning a stub db, `user.canEdit()`→true, and a `sample()` stub).
3. Publish to the artifact: Artifact tool, `file_path` = `tools/app.html`, `url` = the artifact URL. Other published files (data files) are kept; pass new or changed ones in `files`. Capabilities are carried forward (db with rule read:view / write:admin, user, sample, downloads) — don't pass `capabilities`.
4. Commit `tools/app.html` (and the rebuilt `index.html` only when he asks to publish).

## 6. Tools

| Script | Does |
|---|---|
| `tools/build_site.py` | `tools/app.html` → `index.html` (public wrapper with meta tags). |
| `tools/make_content.py <export>` | DB export → `data/content.json`. |
| `tools/docx_to_note.py in.docx out.md` | Word article → article markdown. |
| `tools/verify_quotes.py file.md` | Checks every `>> ` Qur'an line against `quran.json`. |
| `tools/build_conc.py` | Rebuilds `conc.json` from `grammar/`. |
| `tools/build_translations.py taisir.db urd.json` | Rebuilds `tr-bn.json`, `tr-ur.json` (sources listed in the script). |

## 7. Features (so you know what already exists)

Surah reader (IndoPak/Madani, font size, full screen) · revised translation per ayah with "compare with original" · translation language switch (English / বাংলা Taisirul / اردو Maududi) separate from the write-up language switch · Notes (category required, dropdown filter, tags, search) · Lessons (ayah ranges) · Word analysis (pick a word; whole-Qur'an occurrence list by lemma or root with forms and Makki/Madani counts; "Analyse usage with AI"; "Ask something specific" box) · grammar panel (morphology, sentence structure from the treebank, automatic traditional iʿrāb, his own iʿrāb in four languages) · article pages with contents list and footnotes · Share (link + ready text) · one-click "Back to …" after following an ayah link · AI drafting of the other three languages (uses the chosen translation of every ayah the piece mentions; never invents a title when his is empty) · backup download.

Ideas discussed but **not built yet**: image upload in notes (planned: upload button, compressed images in the artifact's file storage, copied to the repo on publish, captions translated, images extracted from .docx).

## 8. Content snapshot (2 Oct 2026)

Notes: `did-god-take-a-promise-from-our-souls` (7:172, Alternative Commentary), `between-the-backbone-and-the-ribs` (86:7, Scientific Objections), `manna-and-salwa` (2:61, Alternative Commentary; includes Bukhārī 4478 / Muslim 2049d on truffles), `the-basmala-a-comprehensive-study-for-the-seeker` (1:1, Concept; the former 5-part Basmala series merged into one article, 4 languages, bn/ur/ar AI drafts unreviewed; the per-part "Part N of 5" navigation lines were removed), `itmam-al-hujjah-and-divine-punishment` (2:7, Concept; from his Urdu paper "اتمامِ حجت اور عذابِ الٰہی", English + Bangla + Urdu, bn/ur AI-drafted unreviewed; Urdu transcribed from his pages, to be compared with his original). **A single database document is limited to about 256 KB**, so long write-ups are stored in pieces (`chunks` collection, see §3) and appear as one article; never split an article into parts. Word analyses: 2:2 لِّلْمُتَّقِينَ, 86:6 مَّآءٍ, 86:6 دَافِقٍ (English only). No lessons, translation revisions or iʿrāb yet.
