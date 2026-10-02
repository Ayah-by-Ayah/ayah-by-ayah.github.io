"""Convert an article .docx into the platform's article markdown, keeping the author's wording.

Conventions this handles (the author's usual Word layout):
  Title paragraph            -> becomes the note title (printed, not in the body)
  first italic line          -> subtitle; dropped from the body (use it as the summary)
  Heading 1 / Heading 2      -> "## " / "### " (bold markers inside headings removed)
  whole-paragraph Arabic     -> ">> " line (Qur'an / Arabic quotation block)
  "> *translation*" + "**— Sūrah x:y · trans. …**" -> one italic line "*…* (Sūrah x:y · trans. …)"
  inline <span dir="rtl">     -> plain Arabic
  \\[ \\]                     -> [ ]
Review the output: drop production notes (fonts, "check before publication", transcript notes),
and never keep lecture/speaker framing ("the lecturer says") - articles speak in their own voice.

Usage:  python3 tools/docx_to_note.py article.docx out.md
"""
import re, subprocess, sys
import docx  # python-docx

src, out_path = sys.argv[1], sys.argv[2]
d = docx.Document(src)
title = next((p.text for p in d.paragraphs if p.style.name == 'Title'), '')
md = subprocess.run(['pandoc', src, '-t', 'gfm', '--wrap=none'], capture_output=True, text=True, check=True).stdout
lines = md.split('\n')
if lines and re.match(r'^\*[^*].*\*\s*$', lines[0]):
    print('SUBTITLE:', lines[0].strip('* '))
    lines = lines[1:]
out, i = [], 0
while i < len(lines):
    l = lines[i]
    m = re.match(r'^(#+) (.*)$', l)
    if m:
        out.append('#' * (len(m.group(1)) + 1) + ' ' + re.sub(r'\*\*(.*?)\*\*', r'\1', m.group(2)).strip()); i += 1; continue
    m = re.match(r'^<span dir="rtl">(.*)</span>\s*$', l)
    if m:
        out.append('>> ' + m.group(1).strip()); i += 1; continue
    m = re.match(r'^> \*(.*)\*\s*$', l)
    if m:
        txt = m.group(1); j = i + 1
        while j < len(lines) and not lines[j].strip(): j += 1
        cm = re.match(r'^\*\*— (.*)\*\*\s*$', lines[j]) if j < len(lines) else None
        if cm:
            out.append('*' + txt + '* (' + cm.group(1) + ')'); i = j + 1; continue
        out.append('*' + txt + '*'); i += 1; continue
    out.append(re.sub(r'<span dir="rtl">(.*?)</span>', r'\1', l)); i += 1
body = '\n'.join(out).replace('\\[', '[').replace('\\]', ']')
body = re.sub(r'\n{3,}', '\n\n', body).strip()
body = re.sub(r'(## Abstract\n\n)\*(.*)\*\n', r'\1\2\n', body)   # abstract in roman, not italic
open(out_path, 'w', encoding='utf-8').write(body + '\n')
print('TITLE:', title)
print('wrote', out_path, len(body), 'chars')
