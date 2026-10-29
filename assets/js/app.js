/* All learning content is static HTML. Enhancements fail independently. */
(() => {
  'use strict';
  const root = document.body.dataset.root || '';
  const $ = (s, p = document) => p.querySelector(s);
  const $$ = (s, p = document) => [...p.querySelectorAll(s)];
  const safeRead = (k, fallback) => { try { return JSON.parse(localStorage.getItem(k)) || fallback; } catch (_) { return fallback; } };
  const safeWrite = (k, value) => { try { localStorage.setItem(k, JSON.stringify(value)); return true; } catch (_) { return false; } };
  let toastTimer;
  function toast(msg) { const el = $('#toast'); if (!el) return; el.textContent = msg; el.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('visible'), 3200); }
  let lastFocus;
  function show(dialog) { lastFocus = document.activeElement; if (typeof dialog.showModal === 'function') dialog.showModal(); else { dialog.setAttribute('open', ''); dialog.setAttribute('role', 'dialog'); dialog.setAttribute('aria-modal', 'true'); } }
  function close(dialog) { if (typeof dialog.close === 'function') dialog.close(); else dialog.removeAttribute('open'); if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus(); }
  $$('[data-close]').forEach(b => b.addEventListener('click', () => close(b.closest('dialog'))));
  $$('dialog').forEach(d => { d.addEventListener('click', e => { if (e.target === d && d.id !== 'image-dialog') close(d); }); d.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); close(d); } }); });
  const menu = $('.menu-button');
  if (menu) menu.addEventListener('click', () => { const open = document.body.classList.toggle('menu-open'); menu.setAttribute('aria-expanded', String(open)); if (open) $('.sidebar a')?.focus(); });
  document.addEventListener('click', e => { if (document.body.classList.contains('menu-open') && !e.target.closest('.sidebar,.menu-button')) { document.body.classList.remove('menu-open'); menu.setAttribute('aria-expanded','false'); } });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { const wasOpen=document.body.classList.contains('menu-open'); document.body.classList.remove('menu-open'); if (menu) { menu.setAttribute('aria-expanded','false'); if (wasOpen) menu.focus(); } } });

  const lang = $('#language');
  function setLang(value) { document.body.classList.remove('lang-zh','lang-en'); if (value !== 'both') document.body.classList.add('lang-' + value); if (lang) lang.value = value; }
  setLang(safeRead('a2-review-language','both'));
  if (lang) lang.addEventListener('change', () => { setLang(lang.value); safeWrite('a2-review-language',lang.value); toast('已调整对照阅读；核心教学解释保持可读'); });

  let progress = safeRead('a2-review-progress', {});
  if (!progress || typeof progress !== 'object' || Array.isArray(progress)) progress = {};
  const validIds = new Set($$('[data-progress-link]').map(a => a.dataset.progressLink));
  function updateProgress() {
    const count = [...validIds].filter(id => progress[id]).length;
    $$('[data-progress-count]').forEach(el => el.textContent = count + ' / 24');
    $$('[data-progress-bar]').forEach(el => { el.value = count; el.textContent = count + ' / 24'; });
    $$('[data-progress-link]').forEach(el => el.classList.toggle('done', Boolean(progress[el.dataset.progressLink])));
    $$('[data-complete]').forEach(el => el.checked = Boolean(progress[el.dataset.complete]));
  }
  updateProgress();
  $$('[data-complete]').forEach(el => el.addEventListener('change', () => { progress[el.dataset.complete] = el.checked; const stored = safeWrite('a2-review-progress',progress); updateProgress(); toast(stored ? (el.checked ? '已记录掌握进度' : '已取消掌握标记') : '存储不可用，本页仍可记录；关闭后可能不保留'); }));
  $$('[data-reset-progress]').forEach(b => b.addEventListener('click', () => { progress = {}; safeWrite('a2-review-progress',progress); updateProgress(); toast('已清除本教材的学习标记'); }));
  const question = $('.lesson[data-question]');
  if (question && !document.body.dataset.page.includes('complete')) safeWrite('a2-review-resume','pages/q'+question.dataset.question.replaceAll('.','-')+'.html');
  const resume = safeRead('a2-review-resume','pages/q1-1-1.html');
  if (typeof resume === 'string' && /^pages\/q[1-4](?:-\d+){1,2}\.html$/.test(resume)) $$('[data-resume]').forEach(a => a.href = root + resume);

  function manualCopy(text) { const dialog = $('#copy-dialog'); const area = $('textarea',dialog); area.value = text; show(dialog); area.focus(); area.select(); area.setSelectionRange(0,text.length); }
  $$('[data-manual-copy]').forEach(button => button.addEventListener('click', () => { try { manualCopy(JSON.parse($('.raw-code',button.closest('.code-block')).textContent)); } catch (_) { toast('请从下载文件复制代码'); } }));
  $$('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const block = button.closest('.code-block'); let text;
    try { text = JSON.parse($('.raw-code', block).textContent); } catch (_) { return toast('无法读取代码，请从下载文件复制'); }
    try { if (!navigator.clipboard || !window.isSecureContext) throw new Error('manual'); await navigator.clipboard.writeText(text); toast('完整代码已复制（不含网页行号）'); }
    catch (_) { manualCopy(text); }
  }));
  $$('[data-line-jump]').forEach(button => button.addEventListener('click', () => {
    const block = button.closest('.code-block'); const input = $('input',block);
    const number = Math.max(1,Math.min(Number(input.max),Number(input.value)||1)); input.value=number;
    const target = document.getElementById('q-'+block.dataset.codeId+'-L'+number); if (!target) return;
    location.hash = target.id; target.scrollIntoView({block:'center',inline:'nearest'});
    target.setAttribute('tabindex','-1'); target.focus({preventScroll:true});
  }));
  // Deep links can point into an internally scrollable code area.
  function revealHash() { if (!location.hash) return; let el; try { el = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (_) { return; } if (el && el.classList.contains('code-line')) el.scrollIntoView({block:'center',inline:'nearest'}); }
  window.addEventListener('hashchange',revealHash); setTimeout(revealHash,150);

  $$('[data-image]').forEach(link => link.addEventListener('click', e => {
    e.preventDefault(); const dialog = $('#image-dialog'); const img = $('#zoom-image'); const caption = link.dataset.caption || $('img',link)?.alt || '原始证据';
    img.src = link.href; img.alt=caption; $('#image-title').textContent=caption; $('#image-caption').textContent='原图未重绘 · 可切换原尺寸并横向滚动查看 · Esc关闭'; $('#image-original').href=link.href; $('.image-viewport').classList.remove('original-size'); show(dialog);
  }));
  $('[data-image-size]')?.addEventListener('click', () => $('.image-viewport').classList.toggle('original-size'));
  $$('[data-filter]').forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    $$('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    $$('[data-figure-group]').forEach(el => el.hidden=filter!=='all'&&el.dataset.figureGroup!==filter);
  }));

  const searchDialog=$('#search-dialog'), searchInput=$('#search-input'), searchResults=$('#search-results');
  function openSearch(){show(searchDialog);searchInput.focus();}
  $('.search-trigger')?.addEventListener('click',openSearch);
  document.addEventListener('keydown',e=>{if ((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault(); if (!searchDialog.open) openSearch();}});
  function search(){
    const query=searchInput.value.trim().toLowerCase();searchResults.replaceChildren();
    if (!query){$('#search-status').textContent='输入题号、函数或中英文关键词。';return;}
    const tokens=query.split(/\s+/).filter(Boolean);
    const results=(window.A2_SEARCH||[]).map(item=>({item,score:tokens.every(t=>(item.title+' '+item.text).toLowerCase().includes(t))?tokens.reduce((s,t)=>s+(item.title.toLowerCase().includes(t)?20:1),0):0})).filter(x=>x.score).sort((a,b)=>b.score-a.score).slice(0,35);
    $('#search-status').textContent=results.length?'找到 '+results.length+' 个相关题目或知识点':'未找到结果。可缩短关键词，例如 NULL、窗口、4.2。';
    results.forEach(({item})=>{
      const a=document.createElement('a');a.className='search-result';a.href=root+item.url;
      const small=document.createElement('small');small.textContent=item.tag;
      const strong=document.createElement('strong');strong.textContent=item.title;
      const p=document.createElement('p');const text=item.text.replace(/\s+/g,' ');const at=text.toLowerCase().indexOf(tokens[0]);const start=Math.max(0,at-35);p.textContent=(start?'…':'')+text.slice(start,start+145)+'…';
      a.append(small,strong,p);searchResults.append(a);
    });
  }
  searchInput?.addEventListener('input',search);
  searchInput?.addEventListener('keydown',e=>{if (e.key==='ArrowDown') {e.preventDefault();$('a',searchResults)?.focus();}});
  const toc=$$('.page-toc a');
  if (toc.length && 'IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if (!visible.length)return;const id=visible[0].target.id;toc.forEach(a=>{const current=a.hash==='#'+id;a.classList.toggle('current',current);if(current)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});},{rootMargin:'-90px 0px -60% 0px',threshold:0});
    $$('.lesson-section').forEach(s=>observer.observe(s));
  }
  $$('[data-print]').forEach(b=>b.addEventListener('click',()=>{
    // Quiz solutions and line explanations are printed; raw source transcripts stay optional.
    $$('.quiz-answer').forEach(d=>d.open=true);$$('img[loading="lazy"]').forEach(img=>img.loading='eager');
    window.print();
  }));
})();
