# MyHadithApp

Read and understand authentic hadith: 2,175 hadith graded Sahih or Hasan from Bukhari, Muslim, Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah and Muwatta Malik (with a Bukhari & Muslim only setting), plus Imam Nawawi's 40 and Hadith Qudsi, in Arabic (Indo-Pak script), English, Urdu and Hinglish, with explanations and lessons.

- Hadith text, translations, explanations and lessons: [HadeethEnc.com](https://hadeethenc.com) (Encyclopedia of Translated Prophetic Hadiths), shown unchanged. English v1.25.0, Urdu v1.36.0, Hindi v1.59.0. Hinglish = HadeethEnc's Hindi translation written in Roman letters by `build/hinglish.py` (same words, different script).
- Install on iPhone: open the site in Safari → Share → Add to Home Screen. Android: Chrome ⋮ → Install app.
- Works offline after the first open. Progress is stored on each phone.

## Rebuilding the data
1. Get the official HadeethEnc Excel files (en, ur) and the Arabic API dump.
2. `python3 build/extract.py <source folder>` then `cd build && python3 make_data.py`.
3. Bump `CACHE` in `sw.js` and `VERSION` in `index.html` for each release.

## Hadith numbers
HadeethEnc's own references are used first. Otherwise numbers are found by matching the Arabic text against the full collections in [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (The Unlicense) with `build/match_numbers.py` (only numbers are taken, no text). Matches below a 0.5 similarity score are not shown.
