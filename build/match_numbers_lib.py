import re
DIAC = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭـ]')


def norm(s):
    s = DIAC.sub('', s or '')
    s = re.sub('[إأآٱ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    s = re.sub(r'[^ء-ي\s]', ' ', s)
    return s.split()


def shingles(words, k=4):
    return {' '.join(words[i:i + k]) for i in range(len(words) - k + 1)}


