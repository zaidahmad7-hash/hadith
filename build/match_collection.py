"""Map a small collection (Nawawi 40, Qudsi 40) to HadeethEnc ids by Arabic text. Prints the mapping for review."""
import json, sys, collections
sys.path.insert(0, '.')
from match_numbers_lib import norm, shingles
HAPI, ALL, ED = sys.argv[1:4]
items = json.load(open(ALL))['items']
inv = collections.defaultdict(set); size = {}
for x in items:
    s = shingles(norm(x['ar']['text'])); size[x['id']] = len(s)
    for sh in s: inv[sh].add(x['id'])
col = json.load(open(f'{HAPI}/ara-{ED}1.json'))['hadiths']
en = {h['hadithnumber']: h['text'] for h in json.load(open(f'{HAPI}/eng-{ED}.json'))['hadiths']}
out = {}
for h in col:
    q = shingles(norm(h['text']))
    c = collections.Counter()
    for s in q:
        for i in inv.get(s, ()): c[i] += 1
    top = [(i, round(max(n/len(q), n/max(size[i],1)), 2)) for i, n in c.most_common(4)]
    out[int(h['hadithnumber'])] = top
    print(h['hadithnumber'], top, '|', en.get(h['hadithnumber'], '')[:70].replace('\n',' '))
json.dump(out, open(f'../work/map-{ED}.json', 'w'))
