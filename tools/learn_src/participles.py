#!/usr/bin/env python3
"""Rule-based ism fa'il / ism maf'ul for the Learn tables. Input: a verb row from forms.json + root + meaning/transitivity.
Derived forms (II-X, quadriliteral) are built from the muḍāriʿ; form I from the root. Output is always flagged unreviewed."""
import re
FATHA, DAMMA, KASRA, SUKUN, SHADDA = 'َ', 'ُ', 'ِ', 'ْ', 'ّ'
FATHAN, DAMMAN, KASRAN = 'ً', 'ٌ', 'ٍ'
MARKS = 'ًٌٍَُِّْٰ'
HAMZA = 'أإءئؤآ'

def parse(s):
    out = []
    for ch in s:
        if ch in MARKS:
            if out: out[-1][1] += ch
        else:
            out.append([ch, ''])
    return out
def build(units): return ''.join(b + m for b, m in units)
def setvowel(m, v):
    """replace the short vowel/sukun in a mark string with v, keep shadda"""
    sh = SHADDA if SHADDA in m else ''
    return sh + v
def N(t):
    t = re.sub('[' + MARKS + 'ـ]', '', t)
    return t.replace('ٱ', 'ا').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ئ', 'ء').replace('ؤ', 'ء')

def seat_after(vowel_before, ):
    return 'ئ' if vowel_before == KASRA else 'أ'

def derived(mud, vf, kind):
    """kind 'fa' or 'mf'. Build from the muḍāriʿ (يُفْعِلُ / يَتَفَعَّلُ ...)."""
    u = parse(mud)
    if len(u) < 3 or u[0][0] != 'ي': return ''
    rest = [x[:] for x in u[1:]]
    rest = [['م', DAMMA]] + rest[0:0] + rest   # placeholder to keep indexes simple below
    # rest[0] is the new prefix مُ ; the old units follow
    last = rest[-1]
    vow = KASRA if kind == 'fa' else FATHA
    # defective (ends in ي / ى with no vowel)
    if last[0] in 'يى' and not re.search('[' + DAMMA + FATHA + KASRA + ']', last[1]) and len(rest) >= 3:
        rest.pop()
        p = rest[-1]
        if kind == 'fa':
            p[1] = setvowel(p[1], KASRAN)
        else:
            p[1] = setvowel(p[1], FATHAN); rest.append(['ى', ''])
        return build(rest)
    # final letter: damma -> dammatan
    last[1] = last[1].replace(DAMMA, DAMMAN)
    if DAMMAN not in last[1]: last[1] = last[1].replace(SUKUN, '') + DAMMAN
    if last[0] in HAMZA and last[0] != 'آ':
        last[0] = 'ئ' if kind == 'fa' else 'أ'
        if kind == 'fa' and rest[-2][1].find(KASRA) < 0 and rest[-2][0] not in 'يا': last[0] = 'ء'
    p = rest[-2]; q = rest[-3] if len(rest) >= 3 else None
    # hollow IV / X : ...ق(kasra) ي(sukun) م  or ...ق(fatha) ا م
    if vf in ('4', '10') and p[0] in 'يوا' and p[1] in ('', SUKUN) and q is not None:
        if kind == 'fa':
            q[1] = setvowel(q[1], KASRA); p[0] = 'ي'; p[1] = ''
        else:
            q[1] = setvowel(q[1], FATHA); p[0] = 'ا'; p[1] = ''
        return build(rest)
    if p[0] == 'ا':                      # VII / VIII hollow, III: long alif is itself the vowel carrier
        if len(rest) >= 3 and vf in ('7', '8', '3', '6'):
            return build(rest) if vf in ('7', '8') else build(rest)
    if p[0] in HAMZA and p[0] != 'آ': p[0] = 'ئ' if kind == 'fa' else 'أ'
    p[1] = setvowel(p[1], vow)
    if p[0] in 'يو' and p[1] == '': pass
    return build(rest)

def classify(root):
    r = list(root)
    if len(r) != 3: return None
    r1, r2, r3 = r
    return r1, r2, r3

def form1(root, kind, stative=False, madi='', mud=''):
    c = classify(root)
    if not c: return ''
    r1, r2, r3 = c
    W = 'وي'
    if (r1, r2, r3) in (('ج', 'ي', 'أ'), ('ش', 'ي', 'أ')):
        return {'fa': r1 + FATHA + 'ا' + 'ءٍ', 'mf': ''}[kind]       # جَاءٍ، شَاءٍ
    if kind == 'fa':
        if stative and r2 not in W and r3 not in W and r2 != r3 and r1 not in HAMZA and r2 not in HAMZA and r3 not in HAMZA:
            return r1 + FATHA + r2 + KASRA + 'ي' + r3 + DAMMAN
        if r3 in W and r2 == r3: return r1 + FATHA + r2 + SHADDA + DAMMAN         # حَيٌّ (doubly weak)
        if r3 in W:   # defective
            a = r1 if r1 not in HAMZA else 'آ'
            if r1 in HAMZA: return 'آ' + r2 + KASRAN
            return r1 + FATHA + 'ا' + ('ء' if r2 in HAMZA else r2) + KASRAN
        if r2 == r3 and r2 not in W: return (r1 if r1 not in HAMZA else 'آ') + (FATHA + 'ا' if r1 not in HAMZA else '') + r2 + SHADDA + DAMMAN
        if r1 in HAMZA: return 'آ' + r2 + KASRA + r3 + DAMMAN
        if r2 in W or r2 in HAMZA:   # hollow / hamza in the middle
            return r1 + FATHA + 'ا' + 'ئ' + KASRA + (('ئ' if r3 in HAMZA else r3)) + DAMMAN
        if r3 in HAMZA: return r1 + FATHA + 'ا' + r2 + KASRA + 'ئ' + DAMMAN
        return r1 + FATHA + 'ا' + r2 + KASRA + r3 + DAMMAN
    # maf'ul
    if r3 in W and r2 == r3: return ''
    if r3 in W:        # defective
        if r1 in HAMZA: r1 = 'أ'
        r2s = ('ؤ' if (parse(mud)[-1][0] == 'و' if mud else r3 == 'و') else 'ئ') if r2 in HAMZA else r2
        base = 'م' + FATHA + r1 + SUKUN + r2s
        wawi = (parse(mud)[-1][0] == 'و') if mud else (r3 == 'و')
        if wawi: return base + DAMMA + 'و' + SHADDA + DAMMAN
        return base + KASRA + 'ي' + SHADDA + DAMMAN
    if r2 in W and r2 not in HAMZA and r3 not in HAMZA:   # hollow
        if r2 == 'و': return 'م' + FATHA + r1 + DAMMA + 'و' + r3 + DAMMAN
        return 'م' + FATHA + r1 + KASRA + 'ي' + r3 + DAMMAN
    if r1 in HAMZA: r1 = 'أ'
    r2s = 'ؤ' if r2 in HAMZA else r2
    r3s = 'ء' if r3 in HAMZA else r3
    return 'م' + FATHA + r1 + SUKUN + r2s + DAMMA + 'و' + r3s + DAMMAN

SKIP_MADI = {x for x in ('لَيْسَ', 'عَسَى', 'نِعْمَ', 'بِئْسَ', 'هَاتَى', 'لَاتَ', 'يَذَرَ', 'كَادَ', 'حَيَّ', 'طَفِقَ', 'أَلَا', 'وَدَعَ', 'دَامَ', 'بَرِحَ', 'فَتِئَ', 'زَالَ', 'زَالَ')}

def letters_count(madi):
    s = re.sub('[ً-ِْٰـ]', '', madi)      # keep shadda
    return len(re.sub('[ّ]', '', s)) + s.count('ّ') + s.count('آ')

def make(madi, mud, vf_set, root, transitive):
    """returns (fa, mf)."""
    if madi in SKIP_MADI or not mud: return '', ''
    passive = bool(re.match('^.' + DAMMA, madi))
    form1_like = len(root) == 3 and letters_count(madi) == 3
    stative = bool(re.match('^.' + FATHA + '.' + DAMMA + '.' + FATHA + '$', madi))
    if form1_like:
        fa = form1(root, 'fa', stative and not passive, madi)
        mf = form1(root, 'mf', mud=mud) if transitive and not stative else ''
        return fa, mf
    vf = None
    for v in sorted(vf_set, key=lambda x: -int(x) if x.isdigit() else 0):
        vf = v; break
    # form guess from madi for odd tags
    m = N(madi)
    if re.match('^استف|^است', m) and len(m) > 5: vf = '10'
    fa = derived(mud, vf, 'fa')
    mf = derived(mud, vf, 'mf') if transitive else ''
    return fa, mf

if __name__ == '__main__':
    tests = [('أَنْزَلَ', 'يُنْزِلُ', {'4'}, 'نزل', True), ('أَدْرَى', 'يُدْرِي', {'4'}, 'دري', True), ('تَنَزَّلَ', 'يَتَنَزَّلُ', {'5'}, 'نزل', False),
             ('كَتَبَ', 'يَكْتُبُ', {'1'}, 'كتب', True), ('قَالَ', 'يَقُولُ', {'1'}, 'قول', True), ('دَعَا', 'يَدْعُو', {'1'}, 'دعو', True), ('رَمَى', 'يَرْمِي', {'1'}, 'رمي', True),
             ('مَدَّ', 'يَمُدُّ', {'1'}, 'مدد', True), ('أَخَذَ', 'يَأْخُذُ', {'1'}, 'أخذ', True), ('قَرَأَ', 'يَقْرَأُ', {'1'}, 'قرأ', True), ('سَأَلَ', 'يَسْأَلُ', {'1'}, 'سأل', True),
             ('وَعَدَ', 'يَعِدُ', {'1'}, 'وعد', True), ('بَاعَ', 'يَبِيعُ', {'1'}, 'بيع', True), ('أَقَامَ', 'يُقِيمُ', {'4'}, 'قوم', True), ('اِسْتَقَامَ', 'يَسْتَقِيمُ', {'10'}, 'قوم', False),
             ('اِخْتَارَ', 'يَخْتَارُ', {'8'}, 'خير', True), ('كَلَّمَ', 'يُكَلِّمُ', {'2'}, 'كلم', True), ('قَاتَلَ', 'يُقَاتِلُ', {'3'}, 'قتل', True), ('تَوَلَّى', 'يَتَوَلَّى', {'5'}, 'ولي', False),
             ('أَنْبَأَ', 'يُنْبِئُ', {'4'}, 'نبأ', True), ('أَمَدَّ', 'يُمِدُّ', {'4'}, 'مدد', True), ('اِشْتَرَى', 'يَشْتَرِي', {'8'}, 'شري', True), ('أَوْحَى', 'يُوحِي', {'4'}, 'وحي', True),
             ('حَسُنَ', 'يَحْسُنُ', {'1'}, 'حسن', False), ('اِتَّخَذَ', 'يَتَّخِذُ', {'8'}, 'أخذ', True), ('قُطِعَ', 'يُقْطَعُ', {'1'}, 'قطع', True), ('أُوذِيَ', 'يُؤْذَى', {'4'}, 'أذي', True),
             ('جَاءَ', 'يَجِيءُ', {'1'}, 'جيأ', False), ('رَأَى', 'يَرَى', {'1'}, 'رأي', True), ('وَقَى', 'يَقِي', {'1'}, 'وقي', True), ('أَتَى', 'يَأْتِي', {'1'}, 'أتي', True)]
    for t in tests:
        print(t[0], t[3], '->', *make(*t))
