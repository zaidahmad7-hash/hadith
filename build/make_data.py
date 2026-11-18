"""Build the app data files from work/all.json.

All hadith text is copied exactly as published by HadeethEnc.com; only the container format changes.
Writes: app/data/index.json, app/data/en.json, app/data/ur.json, app/data/ar.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
src = json.load(open(os.path.join(ROOT, 'work/all.json')))
OUT = os.path.join(ROOT, 'app/data')
os.makedirs(OUT, exist_ok=True)

# The 665xx series repeats hadith already in the main series (a Nawawi-based set); skip to avoid duplicates.
items = [x for x in src['items'] if not 66500 <= int(x['id']) <= 66560]
byid = {x['id']: x for x in items}

cats_en = {c['id']: c for c in src['cats']['en']}
cats_ur = {c['id']: c for c in src['cats']['ur']}


def ancestors(cid):
    out = []
    while cid and cid in cats_en:
        out.append(cid)
        cid = cats_en[cid]['parent_id']
    return out


# App themes -> HadeethEnc category roots
THEMES = [
    ('faith', ['3'], 'Faith', 'ایمان'),
    ('worship', ['121'], 'Worship', 'عبادات'),
    ('character', ['265', '266', '267'], 'Character & manners', 'اخلاق و آداب'),
    ('dhikr', ['268'], 'Dhikr & duas', 'ذکر و دعا'),
    ('heart', ['269'], 'Softening the heart', 'دل کی نرمی'),
    ('family', ['124'], 'Family', 'خاندان'),
    ('quran', ['1', '2'], "Qur'an & Sunnah", 'قرآن و سنت'),
    ('seerah', ['7'], 'Life of the Prophet ﷺ', 'سیرتِ نبوی ﷺ'),
    ('life', ['122', '123', '125', '126'], 'Daily life & work', 'روزمرہ زندگی'),
    ('society', ['6', '127', '128', '129', '132', '4'], 'Society & rulings', 'معاشرہ و احکام'),
]

import curation  # noqa: E402  (local module with hand-picked id lists)

themes_out = []
item_out = []
assigned = {}
for x in items:
    anc = set()
    for c in x['cats']:
        anc.update(ancestors(c))
    th, subs = [], []
    for key, roots, _, _ in THEMES:
        if key == 'society':
            # catch-all for jurisprudence branches not covered by the worship/family/life themes
            covered = {'121', '124', '122', '123', '125', '126'}
            hit = (anc & {'6', '127', '128', '129', '132'}) or ('4' in anc and not (anc & covered))
        else:
            hit = anc & set(roots)
        if hit:
            th.append(key)
            # sub-category = child of a theme root on the item's ancestor chain
            for c in x['cats']:
                chain = ancestors(c)
                for r in roots:
                    if r in chain:
                        i = chain.index(r)
                        sub = chain[i - 1] if i > 0 else r
                        subs.append(sub)
    if not th:
        th = ['society']
    assigned[x['id']] = th
    item_out.append({'id': x['id'], 't': x['tier'], 'th': th, 's': sorted(set(subs), key=int),
                     'f': 1 if '4' in anc else 0, 'u': 1 if 'ur' in x else 0,
                     'n': len(x['en']['text'])})

for key, roots, en, ur in THEMES:
    if key == 'society':
        roots = ['6', '127', '128', '129', '132']
    members = [i for i in item_out if key in i['th']]
    subcount = {}
    for i in members:
        for s in i['s']:
            if s in roots or not set(roots) & set(ancestors(s)):
                continue
            subcount[s] = subcount.get(s, 0) + 1
    subs = [{'id': s, 'en': cats_en[s]['title'], 'ur': cats_ur.get(s, {}).get('title', cats_en[s]['title']), 'n': n}
            for s, n in sorted(subcount.items(), key=lambda kv: -kv[1]) if n >= 3]
    themes_out.append({'key': key, 'en': en, 'ur': ur, 'n': len(members), 'subs': subs})

# Curated paths: verify every id exists in the authentic subset
for name, ids in (('start', curation.START), ('kids', curation.KIDS)):
    missing = [i for i in ids if i not in byid]
    assert not missing, (name, missing)
    assert len(ids) == len(set(ids)), name

# Hadith of the day pool: curated + short "agreed upon" hadith
pool = list(dict.fromkeys(curation.START + curation.KIDS +
                          [i['id'] for i in item_out if i['t'] == 'both' and i['n'] <= 600 and i['id'] not in ('1751',)]))

index = {
    'meta': src['meta'],
    'themes': themes_out,
    'items': item_out,
    'paths': {'start': curation.START, 'kids': curation.KIDS},
    'daily': pool,
}
json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), ensure_ascii=False, separators=(',', ':'))

F = ('title', 'text', 'expl', 'ben', 'grade', 'takhrij')
for lang in ('en', 'ur'):
    d = {x['id']: [x[lang][k] for k in F] for x in items if lang in x}
    json.dump(d, open(os.path.join(OUT, f'{lang}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
d = {x['id']: [x['ar']['title'], x['ar']['text']] for x in items}
json.dump(d, open(os.path.join(OUT, 'ar.json'), 'w'), ensure_ascii=False, separators=(',', ':'))

for f in os.listdir(OUT):
    print(f, round(os.path.getsize(os.path.join(OUT, f)) / 1e6, 2), 'MB')
print(len(item_out), 'hadith; pool', len(pool))
for t in themes_out:
    print(t['key'], t['n'], [s['en'] for s in t['subs']][:8])
