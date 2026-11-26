"""Find hadith numbers by matching HadeethEnc's Arabic text against the full collections
(fawazahmed0/hadith-api, The Unlicense). Only numbers are taken from those files; no text.

Usage: python3 match_numbers.py <hapi folder> <all.json> <out.json>
"""
import json, re, sys, collections

HAPI, ALL, OUT = sys.argv[1:4]
BOOKS = {'b': 'bukhari', 'm': 'muslim', 'd': 'abudawud', 't': 'tirmidhi', 'n': 'nasai', 'i': 'ibnmajah', 'k': 'malik'}

DIAC = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭـ]')


def norm(s):
    s = DIAC.sub('', s or '')
    s = re.sub('[إأآٱ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    s = re.sub(r'[^ء-ي\s]', ' ', s)
    return s.split()


def shingles(words, k=4):
    return {' '.join(words[i:i + k]) for i in range(len(words) - k + 1)}


index, df, nums, size = {}, collections.Counter(), {}, {}
for key, book in BOOKS.items():
    d = json.load(open(f'{HAPI}/ara-{book}1.json'))['hadiths']
    inv = collections.defaultdict(set)
    for h in d:
        num = h.get('arabicnumber') or h['hadithnumber']
        num = int(float(num))
        uid = (key, num)
        shs = shingles(norm(h['text']))
        size[uid] = max(size.get(uid, 0), len(shs))
        for sh in shs:
            inv[sh].add(uid)
    index[key] = inv
    for sh, s in inv.items():
        df[sh] += len(s)
    print(book, len(d), file=sys.stderr)

data = json.load(open(ALL))['items']
out = {}
for it in data:
    q = shingles(norm(it['ar']['text']))
    q = {s for s in q if df.get(s, 0) <= 40}   # drop chain-of-narration boilerplate
    if len(q) < 3:
        continue
    res = {}
    for key, inv in index.items():
        c = collections.Counter()
        for s in q:
            for uid in inv.get(s, ()):
                c[uid] += 1
        scored = sorted(((uid[1], max(n / len(q), n / max(size[uid], 1)) if n >= 6 else n / len(q)) for uid, n in c.most_common(12)), key=lambda x: -x[1])
        hits = [(num, sc) for num, sc in scored if sc >= 0.35]
        if hits:
            best = hits[0][1]
            res[key] = {'n': [n for n, sc in hits if sc >= best - 0.05][:3], 's': round(best, 3)}
    out[it['id']] = res
json.dump(out, open(OUT, 'w'))
print(len(out), 'matched', file=sys.stderr)
