# Word-gloss translation (English -> Bangla/Urdu) for the tap-a-word flash card
Inputs in_01..in_48.json: [id, english gloss, arabic word], 500 each. Outputs out_NN.json: [id, bn, ur] (same ids/order).
Done (23): 1-19, 21, 24, 26, 27.  Still to do (25): 20, 22, 23, 25, 28-48.
Resume: translate the missing batches with sonnet subagents (one batch each, ~12 at a time), validate (ids match, none empty),
then build gl.json {english gloss: [bn, ur]}, lazy-load it in drawWordCard when S.trLang is bn/ur (fallback to English, label "AI draft, unreviewed"),
test, publish to the artifact, update CLAUDE.md. Do NOT publish the public site unless Tanveer says so.
