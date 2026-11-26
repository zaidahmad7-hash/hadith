"""Compare the app's data files with the official HadeethEnc Excel files, field by field."""
import json, glob, sys, openpyxl, unicodedata, re
sys.path.insert(0, 'build')
from hinglish import to_hinglish
M = '/home/claude/src/mirror/source/excel/'
def load(lang):
    ws = openpyxl.load_workbook(glob.glob(M + f'HadeethEnc.com_{lang}-*.xlsx')[0], read_only=True).active
    rows = list(ws.iter_rows(values_only=True)); hdr = rows[1]
    return {str(int(r[0])) if not isinstance(r[0], str) else r[0].strip(): dict(zip(hdr, r)) for r in rows[2:] if r[0]}
src = {l: load(l) for l in ('en', 'ur', 'hi')}
idx = json.load(open('app/data/index.json'))
D = {l: json.load(open(f'app/data/{l}.json')) for l in ('en', 'ur', 'hi', 'ar', 'hd')}
F = [('title', 0), ('hadith_text', 1), ('explanation', 2), ('benefits', 3), ('grade', 4), ('takhrij', 5)]
c = lambda v: v if isinstance(v, str) else ''
problems = []
ids = [i['id'] for i in idx['items']]
for i in ids:
    for l in ('en', 'ur'):
        s = src[l].get(i); d = D[l].get(i)
        if s is None and d is None: continue
        if (s is None) != (d is None): problems.append((i, l, 'presence')); continue
        for f, k in F:
            if c(s[f]) != d[k]: problems.append((i, l, f))
    s = src['hi'].get(i); d = D['hi'].get(i); h = D['hd'].get(i)
    if (s is None) != (d is None): problems.append((i, 'hi', 'presence'))
    elif s:
        for f, k in F:
            if to_hinglish(c(s[f])) != d[k]: problems.append((i, 'hi', f))
        for f, k in F[:3]:
            if c(s[f]) != h[k]: problems.append((i, 'hd', f))
    a = D['ar'].get(i); e = src['en'][i]
    if not a or a[0] != c(e['title_ar']) or a[1] != c(e['hadith_text_ar']): problems.append((i, 'ar', 'text'))
print('items checked', len(ids), 'problems', len(problems), problems[:10])
# extra ids in data not in index
for l in D:
    extra = set(D[l]) - set(ids)
    if extra: print('extra ids in', l, len(extra))
# empty titles/texts
for l in ('en',):
    for i in ids:
        r = D[l][i]
        if not r[0].strip() or not r[1].strip(): print('empty', l, i)
# leftover Devanagari in Hinglish, odd characters
dev = [(i, k) for i, r in D['hi'].items() for k, v in enumerate(r) if re.search('[ऀ-ॿ]', v or '')]
print('Devanagari left in Hinglish:', len(dev), dev[:5])
