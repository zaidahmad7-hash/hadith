"""Spot places where fawazahmed0's Muslim numbering (arabicnumber) drifts from the Abdul-Baqi numbering, so
matched Muslim numbers near them can be withheld."""
import json, re, collections
CH = re.compile(r'(بهذا الاسناد|بمثله|مثله|نحوه|بنحوه|حديثهم|بمعناه|بمعنى حديث|نحو حديث)\s*[.\s"]*$')


def load(hapi):
    H = json.load(open(f'{hapi}/ara-muslim1.json'))['hadiths']
    groups = collections.OrderedDict(); entry = {}
    for h in H:
        a = h.get('arabicnumber')
        if not a:
            continue
        n = int(float(a)); groups.setdefault(n, []).append(h['text'])
    chain = {n for n, g in groups.items() if (len(g[0]) < 350 and CH.search(g[0].strip())) or ('بهذا الاسناد' in g[0] and len(g[0]) < 300)}
    return groups, chain


def suspicious(n, groups, chain, text=None):
    if any(m in chain for m in range(n - 3, n + 1)):
        return True
    if n - 1 not in groups or n + 1 not in groups:
        return True
    if text is not None:
        g = groups[n]
        if len(g) > 1 and g.index(text) == len(g) - 1 and (n + 1 in chain):
            return True
    return False
