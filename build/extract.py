"""Extract the authentic subset from the official HadeethEnc Excel files (verbatim, no text edits).

Selection: grade 'صحيح' and narrated by Bukhari, Muslim, or both (متفق عليه).
Output: work/all.json
"""
import glob, json, os, sys
import openpyxl

SRC = sys.argv[1]  # path to hadeethenc-mirror checkout
OUT = os.path.join(os.path.dirname(__file__), '..', 'work')
os.makedirs(OUT, exist_ok=True)

TIERS = {'متفق عليه': 'both', 'رواه البخاري': 'bukhari', 'رواه مسلم': 'muslim'}


def load(lang):
    f = glob.glob(os.path.join(SRC, f'source/excel/HadeethEnc.com_{lang}-*.xlsx'))[0]
    ws = openpyxl.load_workbook(f, read_only=True).active
    rows = list(ws.iter_rows(values_only=True))
    info = rows[0][0]
    hdr = rows[1]
    data = {}
    for r in rows[2:]:
        if r[0] is None:
            continue
        d = dict(zip(hdr, r))
        d['id'] = str(int(d['id'])) if not isinstance(d['id'], str) else d['id'].strip()
        data[d['id']] = d
    version = os.path.basename(f).split('-v')[1].rsplit('.xlsx', 1)[0]
    return info, version, data


def clean(s):
    # container-format only: Excel gives None for empty cells; keep text exactly
    return s if isinstance(s, str) else ''


info_en, ver_en, en = load('en')
info_ur, ver_ur, ur = load('ur')
api = {str(x['id']): x for x in json.load(open(os.path.join(SRC, 'source/api/hadeeths-ar.json')))}

out = []
for i, r in en.items():
    tier = TIERS.get((r['takhrij_ar'] or '').strip())
    if (r['grade_ar'] or '').strip() != 'صحيح' or not tier:
        continue
    a = api.get(i, {})
    item = {
        'id': i,
        'tier': tier,
        'cats': a.get('categories', []),
        'ar': {'title': clean(r['title_ar']), 'text': clean(r['hadith_text_ar']),
               'grade': clean(r['grade_ar']), 'takhrij': clean(r['takhrij_ar'])},
        'en': {'title': clean(r['title']), 'text': clean(r['hadith_text']), 'expl': clean(r['explanation']),
               'ben': clean(r['benefits']), 'grade': clean(r['grade']), 'takhrij': clean(r['takhrij'])},
    }
    u = ur.get(i)
    if u:
        item['ur'] = {'title': clean(u['title']), 'text': clean(u['hadith_text']), 'expl': clean(u['explanation']),
                      'ben': clean(u['benefits']), 'grade': clean(u['grade']), 'takhrij': clean(u['takhrij'])}
    out.append(item)

out.sort(key=lambda x: int(x['id']))
meta = {'en': {'version': ver_en, 'info': info_en}, 'ur': {'version': ver_ur, 'info': info_ur}}
cats = {lang: json.load(open(os.path.join(SRC, f'source/api/categories/{lang}.json'))) for lang in ('en', 'ur')}
json.dump({'meta': meta, 'cats': cats, 'items': out}, open(os.path.join(OUT, 'all.json'), 'w'), ensure_ascii=False)
print(len(out), 'hadith;', sum('ur' in x for x in out), 'with Urdu;', ver_en, ver_ur)
