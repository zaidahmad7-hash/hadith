"""Extract the authentic subset from the official HadeethEnc Excel files (verbatim, no text edits).

Selection: grade 'صحيح' and narrated by Bukhari, Muslim, or both (متفق عليه).
Output: work/all.json
"""
import glob, json, os, re, sys
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
info_hi, ver_hi, hi = load('hi')
api = {str(x['id']): x for x in json.load(open(os.path.join(SRC, 'source/api/hadeeths-ar.json')))}

BOOKS_AR = [('b', 'البخاري'), ('m', 'مسلم'), ('d', 'أبو داود'), ('t', 'الترمذي'), ('n', 'النسائي'), ('i', 'ابن ماجه'), ('k', 'مالك'), ('a', 'أحمد')]


NOT_MAIN = re.compile(r'البخاري في (الأدب المفرد|خلق أفعال العباد|التاريخ الكبير)|النسائي في (السنن )?الكبرى')


def books_of(tk):
    tk = (tk or '').split('تنبيه')[0]
    tk = re.sub(r'[^،,\n]*(تعليق|أصله)[^،,\n]*', '', tk)   # suspended (mu'allaq) mentions or "its origin is in..."
    tk = NOT_MAIN.sub('', tk)
    found = set()
    if 'متفق عليه' in tk:
        found |= {'b', 'm'}
    for k, name in BOOKS_AR:
        if name in tk:
            found.add(k)
    if 'البخاري' in tk and 'مسلم' in tk:
        found |= {'b', 'm'}
    return found


def grade_class(g):
    g = (g or '').strip()
    if not g or 'ضعيف' in g or 'موقوف' in g:
        return None
    if g.startswith('صحيح') or g.startswith('إسناده صحيح') or g.startswith('سنده صحيح') or g == 'صحيحة' or g.startswith('الحديثان صحيحان') or g.startswith('صحيحان'):
        return 'sahih'
    if g.startswith('حسن') or g.startswith('إسناده حسن') or 'حديث حسن' in g or 'بإسناد حسن' in g:
        return 'hasan'
    if 'حديث صحيح' in g or 'بإسناد صحيح' in g:
        return 'sahih'
    return None


out = []
for i, r in en.items():
    bk = books_of(r['takhrij_ar'])
    gc = grade_class(r['grade_ar'])
    a = api.get(i, {})
    item = {
        'id': i,
        'books': sorted(bk),
        'gc': gc,
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
    h = hi.get(i)
    if h:
        item['hi'] = {'title': clean(h['title']), 'text': clean(h['hadith_text']), 'expl': clean(h['explanation']),
                      'ben': clean(h['benefits']), 'grade': clean(h['grade']), 'takhrij': clean(h['takhrij'])}
    item['ref'] = a.get('reference', '')
    out.append(item)

out.sort(key=lambda x: int(x['id']))
meta = {'en': {'version': ver_en, 'info': info_en}, 'ur': {'version': ver_ur, 'info': info_ur}, 'hi': {'version': ver_hi, 'info': info_hi}}
cats = {lang: json.load(open(os.path.join(SRC, f'source/api/categories/{lang}.json'))) for lang in ('en', 'ur')}
json.dump({'meta': meta, 'cats': cats, 'items': out}, open(os.path.join(OUT, 'all.json'), 'w'), ensure_ascii=False)
print(len(out), 'hadith (all);', sum('ur' in x for x in out), 'with Urdu;', ver_en, ver_ur)
