from playwright.sync_api import sync_playwright
import json
MOCK = """
(() => {
  const voices = [{name:'Majed',lang:'ar-SA',localService:true},{name:'Daniel',lang:'en-GB',localService:true},{name:'Lekha',lang:'hi-IN',localService:true}];
  const sp = {getVoices:()=>voices, onvoiceschanged:null, speaking:false, pending:false, paused:false, speak(u){}, cancel(){}, pause(){}, resume(){}};
  Object.defineProperty(window,'speechSynthesis',{value:sp});
  window.SpeechSynthesisUtterance = function(t){ this.text=t; };
})();
"""
JS_ALL = r"""
async (mode) => {
  const bad = []; const BADRE = /\b(undefined|NaN|null|\[object Object\])\b/;
  if (mode === 'all') { S.set.langs = ['ar','en','ur','hi']; } else { S.set.langs = ['ar','en']; }
  await need(); if (!D.hd) D.hd = await getJSON('hd');
  const ids = IDX.items.map(i => i.id);
  for (const id of ids) {
    for (const tab of ['h','m','l']) {
      TAB = tab;
      try { renderRead('theme', themeOf(id), id, {}); } catch(e) { bad.push([id, tab, 'EXC ' + e.message]); continue; }
      const txt = document.getElementById('app').innerText;
      if (BADRE.test(txt)) bad.push([id, tab, txt.match(BADRE)[0]]);
      if (tab === 'h' && !document.querySelector('.source b').innerText.trim()) bad.push([id, 'nosource']);
    }
    for (const m of LMODES) { S.set.lMode = m; try { const s = segsFor(id); if (!s.length) bad.push([id, 'listen-empty', m]); if (s.some(x => !x.need && !String(x.text).trim())) bad.push([id,'listen-blank',m]); } catch(e) { bad.push([id, 'listen-exc', m, e.message]); } }
  }
  TAB = 'h';
  return {n: ids.length, bad: bad.slice(0, 50), nbad: bad.length};
}
"""
JS_LISTS = r"""
async () => {
  const bad = []; const BADRE = /\b(undefined|NaN|null|\[object Object\])\b/;
  const check = (label) => { const t = document.getElementById('app').innerText; if (BADRE.test(t)) bad.push([label, t.match(BADRE)[0]]); };
  const run = (type, key, q) => { try { renderList(type, key, q || {}); check(type+'/'+key+JSON.stringify(q||{})); } catch(e) { bad.push([type, key, JSON.stringify(q), 'EXC '+e.message]); } };
  for (const scope of ['all','bm']) {
    S.set.scope = scope;
    for (const th of IDX.themes) {
      for (const tier of ['', 'bm', 'both', 'other', 'bukhari', 'muslim']) {
        run('theme', th.key, {tier});
        for (const s of th.subs) run('theme', th.key, {sub: s.id, tier});
      }
    }
    for (const k of ['b','m','d','t','n','i','k']) run('book', k);
    run('tier', 'both');
    for (const p of Object.keys(IDX.paths)) run('path', p);
    try { renderHome(); check('home-'+scope); } catch(e) { bad.push(['home', e.message]); }
    try { await renderExplore({}); check('explore-'+scope); } catch(e) { bad.push(['explore', e.message]); }
    try { renderSaved(); check('saved'); } catch(e) { bad.push(['saved', e.message]); }
  }
  S.set.scope = 'all';
  // empty lists must show something sensible
  const emptyLists = [];
  for (const th of IDX.themes) for (const s of th.subs) for (const tier of ['both','other']) if (!listFor('theme', th.key, {sub:s.id, tier}).length) emptyLists.push(th.key+'/'+s.id+'/'+tier);
  // search
  if (!SIX) await buildSearch();
  const q = {}; for (const w of ['anger','intention','غضب','نیت','gussa','الصلاة','neighbour','neighbor','prayer']) q[w] = searchIds(w).length;
  // quiz
  const qbad = [];
  for (const lang of [['en'],['ur'],['hi'],['ar','en']]) { S.set.langs = ['ar', ...lang.filter(x=>x!=='ar')]; for (let r = 0; r < 40; r++) { newQuiz(); if (QZ.qs.length < 5) qbad.push(['few', lang, QZ.qs.length]); for (const x of QZ.qs) { if (!x.line.includes(x.ans)) qbad.push(['ans', x.id]); if (new Set(x.opts.map(o=>o.toLowerCase())).size !== x.opts.length || x.opts.length < 3) qbad.push(['opts', x.id, x.opts]); } } }
  S.set.langs = ['ar','en'];
  // strings
  const missUr = Object.keys(T.en).filter(k => !(k in T.ur));
  return {bad: bad.slice(0, 40), nbad: bad.length, emptyLists: emptyLists.length, emptyEx: emptyLists.slice(0,8), search: q, quiz: qbad.slice(0,10), nquiz: qbad.length, missUr};
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
    ctx = b.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True, service_workers='block')
    ctx.add_init_script(MOCK)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto('http://localhost:8765/'); pg.wait_for_timeout(2500)
    pg.set_default_timeout(600000)
    print('all hadith, ar+en:', json.dumps(pg.evaluate(JS_ALL, 'en'), ensure_ascii=False)[:1500])
    print('all hadith, all langs:', json.dumps(pg.evaluate(JS_ALL, 'all'), ensure_ascii=False)[:1500])
    print('lists etc:', json.dumps(pg.evaluate(JS_LISTS), ensure_ascii=False)[:3000])
    # Urdu UI
    pg.evaluate("() => { S.set.ui = 'ur'; applyLook(); }")
    print('urdu lists:', json.dumps(pg.evaluate(JS_LISTS), ensure_ascii=False)[:800])
    # service worker files
    sw = pg.evaluate("fetch('sw.js').then(r => r.text())")
    import re
    files = re.findall(r"'([^']+\.(?:html|json|png|woff2|webmanifest))'", sw)
    st = pg.evaluate("async (fs) => { const out = {}; for (const f of fs) { const r = await fetch(f); out[f] = r.status; } return out; }", files)
    print('sw files not 200:', {k:v for k,v in st.items() if v != 200}, 'checked', len(st))
    print('page errors:', errs[:10])
    b.close()
