(() => {
  'use strict';
  const scopes=['ladder','matrix','atlas','reading','dictionary','papers'];
  const scope=document.getElementById('term-scope'), search=document.getElementById('term-search');
  const coverage=document.getElementById('term-coverage'),kind=document.getElementById('term-kind');
  const status=document.getElementById('review-status'),results=document.getElementById('term-results');
  const labels={UNEXPLAINED_CANDIDATE:'Unexplained candidate',VOCABULARY_MATCH_NO_EXPLANATION:'External vocabulary match; explanation missing',DICTIONARY_MATCH_REVIEW_SENSE:'Dictionary match; check the meaning in context'};
  let data=null,page=0,request=0;const selected=new Map(),size=40;
  function node(tag,text){const n=document.createElement(tag);n.textContent=text;return n;}
  function audience(){try{return new URLSearchParams(location.search).get('audience')||localStorage.getItem('reading-audience')||'general';}catch(_){return 'general';}}
  function context(c,o){const u=data.units[o[0]];return {source:u.source,location:u.location,scope:u.scope,normalized:u.normalized,text:u.text,start:o[1],end:o[2]};}
  function selectionStatus(){document.getElementById('download-brief').textContent=`Download drafting brief (${selected.size} selected)`;document.getElementById('download-brief').disabled=!selected.size;}
  function render(){
    if(!data)return;
    const q=search.value.trim().toLocaleLowerCase();
    const matches=data.candidates.filter(c=>(!q||c.phrase.toLocaleLowerCase().includes(q))&&(coverage.value==='all'||c.coverage===coverage.value)&&(kind.value==='all'||c.kind===kind.value));
    page=Math.min(page,Math.max(0,Math.ceil(matches.length/size)-1));results.replaceChildren();
    status.textContent=`${matches.length} candidates match in this source. ${data.candidates.length} extracted here. All await editorial review.`;
    for(const c of matches.slice(page*size,(page+1)*size)){
      const card=node('details','');card.className='term-candidate';card.dataset.candidate=c.id;
      card.append(node('summary',c.phrase),node('small',labels[c.coverage]+` · ${c.occurrences.length} occurrences · ${c.kind==='explanation-unit'?'short explanation task':'term candidate'}`));
      const label=node('label','');label.className='draft-choice';const box=document.createElement('input');box.type='checkbox';box.checked=selected.has(c.id);
      box.addEventListener('change',()=>{if(box.checked){selected.set(c.id,{...c,selected_scope:data.scope,contexts:c.occurrences.map(o=>context(c,o)),extraction_hash:data.extraction_hash});}else selected.delete(c.id);selectionStatus();});
      label.append(box,document.createTextNode(' Include in drafting brief'));card.append(label);
      card.append(node('p','Detected by: '+c.methods.join(', ')));
      card.append(node('p',c.dictionary_ids.length?'All four perspective entries exist for the matched term; contextual suitability is unreviewed.':'General, Physics, Mathematics and Specialist explanations are missing for this candidate.'));
      for(const id of c.dictionary_ids){const a=node('a','Read dictionary entry: '+id);a.href='dictionary.html?audience='+encodeURIComponent(audience())+'#'+encodeURIComponent(id);card.append(a,node('br',''));}
      for(const id of c.vocabulary_ids){const a=node('a','PhySH concept reference');a.href=id;card.append(a,node('br',''));}
      for(const o of c.occurrences.slice(0,5)){
        const u=data.units[o[0]],chars=Array.from(u.text),quote=node('blockquote','');quote.append(document.createTextNode(chars.slice(Math.max(0,o[1]-100),o[1]).join('')),node('mark',chars.slice(o[1],o[2]).join('')),document.createTextNode(chars.slice(o[2],o[2]+160).join('')));
        card.append(quote,node('small',u.source+' · '+u.location+(u.normalized?' · normalized block':'')));
      }
      if(c.occurrences.length>5)card.append(node('small','First five contexts shown; the brief contains all occurrences in the source where you selected this candidate.'));
      results.append(card);
    }
    document.getElementById('term-page').textContent=`Page ${matches.length?page+1:0} of ${Math.ceil(matches.length/size)}`;
    document.getElementById('previous-terms').disabled=page===0;document.getElementById('next-terms').disabled=(page+1)*size>=matches.length;
    selectionStatus();
  }
  async function load(){
    const token=++request;data=null;results.replaceChildren();status.textContent='Loading candidates…';
    const url=new URL(location.href);url.searchParams.set('scope',scope.value);history.replaceState(null,'',url);
    try{const response=await fetch('term-candidates-'+scope.value+'.json.gz');if(!response.ok)throw new Error('HTTP '+response.status);const stream=response.body.pipeThrough(new DecompressionStream('gzip'));const next=await new Response(stream).json();if(token!==request)return;data=next;page=0;render();}
    catch(error){if(token===request)status.textContent='Could not load candidates. Reload to retry. '+error.message;}
  }
  const requested=new URLSearchParams(location.search).get('scope');scope.value=scopes.includes(requested)?requested:'ladder';
  scope.addEventListener('change',load);for(const input of [search,coverage,kind])input.addEventListener('input',()=>{page=0;render();});
  document.getElementById('previous-terms').addEventListener('click',()=>{page--;render();});document.getElementById('next-terms').addEventListener('click',()=>{page++;render();});
  document.getElementById('clear-selection').addEventListener('click',()=>{selected.clear();render();});
  document.getElementById('download-brief').addEventListener('click',()=>{
    const brief={schema_version:1,task:'Review candidate meanings and draft explanations; do not publish without contextual review.',requirements:{general:'Expand abbreviations, explain ordinary prerequisites and give a concrete example.',physics:'Connect to modeling and explain unfamiliar logic.',mathematics:'Give the defining structures and conditions; explain physical interpretation.',specialist:'State exact role, hypotheses, contribution and limitations.'},decisions:['new dictionary entry','existing concept or alias','rewrite the surrounding claim','not a useful term'],candidates:[...selected.values()]};
    const blob=new Blob([JSON.stringify(brief,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=node('a','');a.href=url;a.download='term-drafting-brief.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  load();
})();
