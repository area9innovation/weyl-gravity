(() => {
  'use strict';
  // Historical index.html permalinks remain atlas permalinks, including filters.
  const legacy = new URLSearchParams(location.hash.slice(1));
  if (location.pathname.endsWith('/') || location.pathname.endsWith('/index.html')) {
    if (['view','cell','q','f','c','o','s','passport','assembly','panel','seeded'].some(key => legacy.has(key))) {
      location.replace('atlas.html' + location.search + location.hash); return;
    }
  }
  const descriptions = {
    general: 'No specialist background assumed.',
    physics: 'University physics; no mathematical logic assumed.',
    mathematics: 'University mathematics; no field theory or reverse mathematics assumed.',
    specialist: 'Research detail; topic-specific prerequisites are stated in the text.'
  };
  const choice = document.getElementById('audience');
  const params = new URLSearchParams(location.search);
  let saved = 'general';
  try { saved = localStorage.getItem('reading-audience') || saved; } catch (_) { /* Storage is optional. */ }
  let audience = params.get('audience') || saved;
  if (!Object.hasOwn(descriptions, audience)) audience = 'general';
  function apply(value, updateURL) {
    document.querySelectorAll('[data-edition]').forEach(node => { node.hidden = node.dataset.edition !== value; });
    if (choice) {
      choice.value = value;
      document.getElementById('audience-description').textContent = descriptions[value];
    }
    try { localStorage.setItem('reading-audience', value); } catch (_) { /* URL still carries choice. */ }
    if (updateURL) {
      const url = new URL(location.href); url.searchParams.set('audience', value);
      history.replaceState(null, '', url);
    }
    document.querySelectorAll('a[href]').forEach(link => {
      const url = new URL(link.getAttribute('href'), location.href);
      if (url.origin === location.origin && /\/(index|wave|questions|papers|atlas|cutoff-positivity)\.html$/.test(url.pathname)) {
        url.searchParams.set('audience', value);
        link.setAttribute('href', url.pathname.split('/').pop() + url.search + url.hash);
      }
    });
  }
  apply(audience, false);
  if (choice) choice.addEventListener('change', () => {
    apply(choice.value, true);
    const target = document.getElementById(location.hash.slice(1));
    if (target) target.scrollIntoView({block:'start'});
  });
})();
