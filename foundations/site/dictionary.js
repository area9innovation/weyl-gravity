(async () => {
  'use strict';
  if (location.pathname.endsWith('/dictionary.html')) return;
  let dictionary;
  try {
    const response = await fetch('dictionary.json');
    if (!response.ok) return;
    dictionary = await response.json();
  } catch (_) { return; } // Reading remains available if definitions cannot load.
  const labels = {general:'General', physics:'Physics', mathematics:'Mathematics', specialist:'Specialist'};
  const aliases = dictionary.terms.flatMap(term => term.aliases.map(alias => ({alias, term})))
    .sort((a,b) => b.alias.length-a.alias.length);
  const escape = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const pattern = new RegExp('(?<![\\p{L}\\p{N}_])(' + aliases.map(x=>escape(x.alias)).join('|') + ')(?![\\p{L}\\p{N}_])', 'giu');
  const byAlias = new Map(aliases.map(x=>[x.alias.toLowerCase(),x.term]));
  const popup = document.createElement('aside');
  popup.className = 'dictionary-popup'; popup.id = 'dictionary-popup'; popup.hidden = true;
  popup.setAttribute('aria-label','Term definition'); document.body.append(popup);
  let active, timer;
  function hide() { popup.hidden = true; active?.setAttribute('aria-expanded','false'); active = null; }
  function delayHide() { clearTimeout(timer); timer = setTimeout(hide, 350); }
  function show(button, term) {
    clearTimeout(timer); active?.setAttribute('aria-expanded','false'); active = button;
    button.setAttribute('aria-expanded','true'); popup.replaceChildren();
    const heading = document.createElement('strong'); heading.textContent = term.label; popup.append(heading);
    const scope = document.createElement('p'); scope.textContent = term.scope; popup.append(scope);
    let raw = new URLSearchParams(location.search).get('audience');
    try { raw ??= localStorage.getItem('reading-audience'); } catch (_) {}
    const edition = button.closest('[data-edition]')?.dataset.edition;
    let selected = edition ? [edition] : (raw || 'general').split(',').filter(x=>labels[x]);
    if (!selected.length) selected = ['general'];
    for (const key of selected) {
      const p = document.createElement('p'); p.dataset.perspective = key;
      const label = document.createElement('strong'); label.textContent = labels[key]+': ';
      p.append(label,document.createTextNode(term.definitions[key])); popup.append(p);
    }
    const link = document.createElement('a'); link.href = 'dictionary.html?audience=general,physics,mathematics,specialist#'+term.id;
    link.textContent = 'Compare all four definitions'; popup.append(link);
    const close = document.createElement('button'); close.type = 'button'; close.textContent = 'Close';
    close.addEventListener('click',()=>{ const previous=active; hide(); previous?.focus(); hide(); }); popup.append(close);
    popup.hidden = false;
    position();
  }
  function position() {
    if (!active || popup.hidden) return;
    const rect = active.getBoundingClientRect();
    popup.style.left = Math.max(8,Math.min(rect.left,innerWidth-popup.offsetWidth-8))+'px';
    const below = rect.bottom + 6;
    const top = below + popup.offsetHeight <= innerHeight - 8 ? below : rect.top - popup.offsetHeight - 6;
    popup.style.top = Math.max(8, top)+'px';
  }
  popup.addEventListener('mouseenter',()=>clearTimeout(timer)); popup.addEventListener('mouseleave',delayHide);
  popup.addEventListener('focusin',()=>clearTimeout(timer));
  popup.addEventListener('focusout',event=>{ if (!popup.contains(event.relatedTarget)) delayHide(); });
  document.addEventListener('keydown',event=>{ if(event.key==='Escape') { const previous=active; hide(); if(popup.contains(document.activeElement)) { previous?.focus(); hide(); } } });
  document.addEventListener('click',event=>{ if (!popup.contains(event.target) && !event.target.closest('.dictionary-term')) hide(); });
  window.addEventListener('scroll',position,{passive:true});
  window.addEventListener('resize',position);
  const excluded = 'a,button,input,textarea,select,option,script,style,code,pre,math,mjx-container,.MathJax,svg,nav,header,footer,[contenteditable],.concepts,.dictionary-popup,[data-no-dictionary]';
  function annotate(root) {
    if (root.nodeType!==1 || root.closest(excluded)) return;
    const walker = document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    const nodes=[]; while(walker.nextNode()) if(!walker.currentNode.parentElement.closest(excluded)) nodes.push(walker.currentNode);
    for (const node of nodes) {
      pattern.lastIndex=0; const matches=[...node.textContent.matchAll(pattern)]; if(!matches.length) continue;
      const fragment=document.createDocumentFragment(); let start=0;
      for(const match of matches) {
        fragment.append(document.createTextNode(node.textContent.slice(start,match.index)));
        const button=document.createElement('button'); button.type='button'; button.className='dictionary-term'; button.textContent=match[0];
        button.setAttribute('aria-label',match[0]+': definition'); button.setAttribute('aria-controls',popup.id); button.setAttribute('aria-expanded','false');
        const term=byAlias.get(match[0].toLowerCase());
        button.addEventListener('mouseenter',()=>show(button,term)); button.addEventListener('mouseleave',delayHide);
        button.addEventListener('focus',()=>show(button,term)); button.addEventListener('blur',event=>{if(!popup.contains(event.relatedTarget)) delayHide();});
        button.addEventListener('click',()=>show(button,term)); fragment.append(button); start=match.index+match[0].length;
      }
      fragment.append(document.createTextNode(node.textContent.slice(start))); node.replaceWith(fragment);
    }
  }
  annotate(document.body);
  // The atlas renders inspectors and filtered cells after initial page load.
  new MutationObserver(records=>{
    for(const record of records) for(const node of record.addedNodes) {
      if(node.nodeType===1) annotate(node);
      else if(node.nodeType===3 && node.parentElement) annotate(node.parentElement);
    }
  }).observe(document.body,{childList:true,subtree:true});
})();
