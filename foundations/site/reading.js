(() => {
  'use strict';
  // Historical index.html permalinks remain atlas permalinks, including filters.
  const legacy = new URLSearchParams(location.hash.slice(1));
  if (location.pathname.endsWith('/') || location.pathname.endsWith('/index.html')) {
    if (['view','cell','q','f','c','o','s','passport','assembly','panel','seeded'].some(key => legacy.has(key))) {
      location.replace('atlas.html' + location.search + location.hash); return;
    }
  }
  const labels = {general: 'General', physics: 'Physics', mathematics: 'Mathematics', specialist: 'Specialist'};
  const order = Object.keys(labels);
  const choices = [...document.querySelectorAll('input[name="audience"]')];
  const params = new URLSearchParams(location.search);
  let saved = 'general';
  try { saved = localStorage.getItem('reading-audience') || saved; } catch (_) { /* Storage is optional. */ }
  function normalize(raw) {
    const requested = new Set(raw.split(','));
    const selected = order.filter(key => requested.has(key));
    return selected.length ? selected : ['general'];
  }
  let selected = normalize(params.has('audience') ? params.get('audience') : saved);
  function apply(values, updateURL) {
    selected = values;
    const value = values.join(',');
    document.body.dataset.comparing = String(values.length > 1);
    document.querySelectorAll('[data-edition]').forEach(node => { node.hidden = !values.includes(node.dataset.edition); });
    choices.forEach(choice => { choice.checked = values.includes(choice.value); });
    const current = document.getElementById('perspective-current');
    if (current) current.textContent = values.map(key => labels[key]).join(' + ');
    const status = document.getElementById('audience-description');
    if (status) status.textContent = (values.length > 1 ? 'Comparing ' : 'Showing ') + values.map(key => labels[key]).join(' · ') + '.';
    try { localStorage.setItem('reading-audience', value); } catch (_) { /* URL still carries choice. */ }
    if (updateURL) {
      const url = new URL(location.href); url.searchParams.set('audience', value);
      history.replaceState(null, '', url);
    }
    document.querySelectorAll('a[href]').forEach(link => {
      const url = new URL(link.getAttribute('href'), location.href);
      if (url.origin === location.origin && /\/(index|wave|questions|papers|dictionary|atlas|cutoff-positivity)\.html$/.test(url.pathname)) {
        url.searchParams.set('audience', value);
        link.setAttribute('href', url.pathname.split('/').pop() + url.search + url.hash);
      }
    });
  }
  function change(values) {
    // Preserve the section currently being read when comparison changes its height.
    const section = [...document.querySelectorAll('.reading-section')].find(node => {
      const rect = node.getBoundingClientRect(); return rect.top <= 100 && rect.bottom > 100;
    });
    const offset = section?.getBoundingClientRect().top;
    apply(values, true);
    if (section) window.scrollBy(0, section.getBoundingClientRect().top - offset);
  }
  const menu=document.getElementById('perspective-menu');
  document.addEventListener('click',event=>{if(menu && !menu.contains(event.target)) menu.open=false;});
  document.addEventListener('keydown',event=>{if(event.key==='Escape' && menu?.open){menu.open=false;menu.querySelector('summary').focus();}});
  apply(selected, false);
  choices.forEach(choice => choice.addEventListener('change', () => {
    const values = choices.filter(input => input.checked).map(input => input.value);
    if (!values.length) {
      choice.checked = true;
      document.getElementById('audience-description').textContent = 'Keep at least one perspective visible.';
      return;
    }
    change(values);
  }));
  document.getElementById('show-all-perspectives')?.addEventListener('click', () => change(order));
})();
