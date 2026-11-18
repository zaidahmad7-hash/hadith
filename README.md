# MyHadithApp

Read and understand the most authentic hadith: 1,498 hadith graded Sahih and narrated by al-Bukhari and/or Muslim, in English, Urdu and Arabic, with explanations and lessons.

- Hadith text, translations, explanations and lessons: [HadeethEnc.com](https://hadeethenc.com) (Encyclopedia of Translated Prophetic Hadiths), shown unchanged. English v1.25.0, Urdu v1.36.0.
- Install on iPhone: open the site in Safari → Share → Add to Home Screen. Android: Chrome ⋮ → Install app.
- Works offline after the first open. Progress is stored on each phone.

## Rebuilding the data
1. Get the official HadeethEnc Excel files (en, ur) and the Arabic API dump.
2. `python3 build/extract.py <source folder>` then `cd build && python3 make_data.py`.
3. Bump `CACHE` in `sw.js` and `VERSION` in `index.html` for each release.
