# Word-forms data (forms.json)

`forms.json` (singular/plural of nouns; māḍī, muḍāriʿ, amr and maṣdar of verbs) is derived from:

- **Arramooz Al-Waseet / arramooz-pysqlite** Arabic dictionary by Taha Zerrouki — GPL-3.0 (https://github.com/linuxscout/arramooz-pysqlite). `forms.json` is a derivative work and is therefore also offered under **GPL-3.0**.
- **The Quranic Arabic Corpus** (lemmas, root and the forms attested in the Qur'an) — see its own terms at corpus.quran.com.
- Gaps (all verb paradigms, and nouns missing from the dictionary) were completed by AI and are **not yet reviewed** by a scholar; the app says so beside the card.

Rebuild: `tools/build_forms.py` → verb batches (`tools/forms_src/verbs_out.json`) → `tools/merge_forms.py`.
