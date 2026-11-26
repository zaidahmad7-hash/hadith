"""Write Devanagari (HadeethEnc's Hindi translation) in Roman letters, Hinglish style.

Only the script changes: every word is the translator's own word, in the same order.
"""
import re
import unicodedata

V_IND = {'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai',
         'ओ': 'o', 'औ': 'au', 'ऑ': 'o', 'ऍ': 'e', 'ॲ': 'a'}
MATRA = {'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
         'ॉ': 'o', 'ॅ': 'e', 'ॆ': 'e', 'ॊ': 'o'}
CONS = {'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'n', 'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'n',
        'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
        'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'w', 'श': 'sh',
        'ष': 'sh', 'स': 's', 'ह': 'h', 'ळ': 'l'}
NUKTA = {'क': 'q', 'ख': 'kh', 'ग': 'gh', 'ज': 'z', 'फ': 'f', 'ड': 'r', 'ढ': 'rh', 'य': 'y', 'र': 'r', 'न': 'n'}
PRE = {'क़': 'क़', 'ख़': 'ख़', 'ग़': 'ग़', 'ज़': 'ज़', 'ड़': 'ड़', 'ढ़': 'ढ़', 'फ़': 'फ़', 'य़': 'य़'}
DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')
VIRAMA, NUK, ANUS, CHANDRA, VISARGA = '्', '़', 'ं', 'ँ', 'ः'

# Common Islamic terms written the way Hinglish readers expect
WORDS = {
    'अल्लाह': 'Allah', 'अल्लाहु': 'Allahu', 'सल्लल्लाहु': 'sallallahu', 'अलैहि': 'alaihi', 'सल्लम': 'sallam',
    'रज़ियल्लाहु': 'radiyallahu', 'अनहु': 'anhu', 'अनहा': 'anha', 'अनहुमा': 'anhuma', 'अनहुम': 'anhum',
    'व': 'wa', 'रसूल': 'Rasool', 'नबी': 'Nabi', 'मुहम्मद': 'Muhammad', 'इस्लाम': 'Islam', 'क़ुरआन': "Qur'an",
    'है': 'hai', 'हैं': 'hain', 'में': 'mein', 'नहीं': 'nahin', 'यह': 'yeh', 'वह': 'woh', 'कहा': 'kaha',
    'और': 'aur', 'कि': 'ki', 'की': 'ki', 'भी': 'bhi', 'ही': 'hi', 'जी': 'ji', 'तो': 'to', 'पर': 'par',
    'जन्नत': 'Jannat', 'जहन्नम': 'Jahannam', 'रमज़ान': 'Ramzan', 'नमाज़': 'namaz', 'ज़कात': 'zakat',
    'हज': 'Hajj', 'एवं': 'evam', 'अथवा': 'athva', 'उमरा': 'Umrah', 'जिब्रील': 'Jibreel', 'बुख़ारी': 'Bukhari', 'मुस्लिम': 'Muslim',
}


def syllables(word):
    """Split a Devanagari word into units: (consonant_roman | None, vowel_roman | None, has_inherent)."""
    units = []
    i, n = 0, len(word)
    while i < n:
        ch = word[i]
        if ch in CONS:
            base = ch
            r = CONS[ch]
            i += 1
            if i < n and word[i] == NUK:
                r = NUKTA.get(base, r)
                i += 1
            if i < n and word[i] == VIRAMA:
                units.append([r, '', False])
                i += 1
            elif i < n and word[i] in MATRA:
                units.append([r, MATRA[word[i]], False])
                i += 1
            else:
                units.append([r, 'a', True])
        elif ch in V_IND:
            units.append(['', V_IND[ch], False])
            i += 1
        elif ch in (ANUS, CHANDRA):
            units.append(['', 'n', False, 'nasal'])
            i += 1
        elif ch == VISARGA:
            # after a vowel sign the source uses ः as a colon (कहाः = "kaha:"); after a bare consonant it is "h" (अतः = atah)
            prev = units[-1] if units else None
            if prev and len(prev) == 3 and not prev[2] and prev[1]:
                units.append([':', '', False, 'other'])
            else:
                units.append(['', 'h', False, 'nasal'])
            i += 1
        elif ch in MATRA or ch in (VIRAMA, NUK):
            # stray sign with no consonant before it (a typing slip in the source): nothing to pronounce
            i += 1
        elif ch == '\u097d':
            units.append(['?', '', False, 'other'])
            i += 1
        else:
            units.append([ch, '', False, 'other'])
            i += 1
    return units


def roman_word(word):
    word = unicodedata.normalize('NFD', word)
    for k, v in PRE.items():
        word = word.replace(k, unicodedata.normalize('NFD', v))
    key = unicodedata.normalize('NFC', word)
    if key in WORDS:
        return WORDS[key]
    u = syllables(word)
    cons_idx = [k for k, x in enumerate(u) if len(x) == 3 and x[0]]
    # final schwa deletion (not after a consonant cluster like "-ndr" handled simply)
    real = [k for k, x in enumerate(u) if len(x) == 3]
    if real:
        last = real[-1]
        followed_by_visarga = last + 1 < len(u) and len(u[last + 1]) == 4 and u[last + 1][3] == 'nasal'
        if u[last][2] and len(real) > 1 and not followed_by_visarga:
            u[last][1] = ''
            u[last][2] = False
    # medial schwa deletion, right to left: V C(a) C V  ->  drop the a
    for k in range(len(u) - 2, 0, -1):
        x = u[k]
        if len(x) != 3 or not x[2]:
            continue
        prev, nxt = u[k - 1], u[k + 1]
        prev_has_vowel = len(prev) == 3 and prev[1] != '' or (len(prev) == 4 and prev[3] == 'nasal')
        nxt_is_cons_with_vowel = len(nxt) == 3 and nxt[0] and nxt[1] != ''
        if prev_has_vowel and nxt_is_cons_with_vowel and k >= 1:
            x[1] = ''
            x[2] = False
    # व in a cluster sounds 'v' (vyakti, swayam); elsewhere 'w' (wa, riwaayat)
    for k, x in enumerate(u):
        if x[0] == 'w' and len(x) == 3 and (x[1] == '' or (k > 0 and len(u[k-1]) == 3 and u[k-1][1] == '' and u[k-1][0])):
            x[0] = 'v'
    # independent e after i/ee/aa sounds 'ye' (liye, jaaye, chahiye)
    for k in range(1, len(u)):
        if len(u[k]) == 3 and u[k][0] == '' and u[k][1] == 'e' and len(u[k-1]) == 3 and u[k-1][1] in ('i', 'ee', 'aa'):
            u[k][1] = 'ye'
    if len(u) >= 2 and len(u[-1]) == 4 and u[-1][3] == 'nasal' and u[-1][1] == 'n' and len(u[-2]) == 3 and u[-2][2]:
        u[-1][1] = 'm'
    out = ''.join(x[0] + x[1] for x in u)
    # Hinglish spelling habits
    out = re.sub(r'ee$', 'i', out)          # ki, bhi, nabi
    out = re.sub(r'oo$', 'u', out)          # tu, hu
    out = re.sub(r'aa(?=:?$)', 'a', out)    # ka, tha, milega, kaha:
    out = re.sub(r'aay', 'ay', out)          # farmaya, kiya, liya
    out = out.replace('llaah', 'llah')       # Bismillah, Insha'Allah
    out = re.sub(r'(a)(aa)(?=[^a]|$)', r"\1'\2", out) if 'aaa' in out else out   # ta'aala, jama'aat
    out = out.replace('eee', "ee'e").replace('ooo', "oo'o").replace('iii', "ii'i")
    out = re.sub(r'^chaahiye$', 'chahiye', out)
    return out


def to_hinglish(text):
    if not text:
        return text
    text = text.translate(DIGITS).replace('।', '.').replace('॥', '.')
    parts = re.split(r'([ऀ-ॿ]+)', text)
    out = []
    for p in parts:
        if p and re.match(r'[ऀ-ॿ]', p):
            out.append(roman_word(p))
        else:
            out.append(p)
    s = ''.join(out)
    # capitalise the start of each sentence and line
    s = re.sub(r'(^[\'"“(]*|[.!?:"“]\s*[\'"“(]*|\n\s*[\'"“(]*)([a-z])', lambda m: m.group(1) + m.group(2).upper(), s)
    return s


if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        print(to_hinglish(line.rstrip('\n')))
