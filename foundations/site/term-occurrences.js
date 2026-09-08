(async () => {
  'use strict';
  const section=document.querySelector('.term-occurrences');if(!section)return;
  const status=section.querySelector('.occurrence-status'),list=section.querySelector('.occurrence-results');
  const previous=section.querySelector('.occurrence-previous'),next=section.querySelector('.occurrence-next');
  let passages=[],page=0;const size=8;
  function render(){
    list.replaceChildren();list.start=page*size+1;
    status.textContent=passages.length ? `${page*size+1}–${Math.min((page+1)*size,passages.length)} of ${passages.length} indexed passages` : 'No occurrences in other indexed passages yet.';
    for(const u of passages.slice(page*size,(page+1)*size)){
      const item=document.createElement('li'),link=document.createElement('a');
      link.href=u.reading_url;link.textContent=u.source;item.append(link);
      const location=document.createElement('small');location.textContent=' · '+u.location+(u.normalized?' · normalized text':'');item.append(location);
      const quote=document.createElement('div');quote.className='occurrence-excerpt';quote.innerHTML=u.rendered_html;item.append(quote);list.append(item);
    }
    previous.disabled=page===0;next.disabled=(page+1)*size>=passages.length;
  }
  previous.addEventListener('click',()=>{page--;render();});next.addEventListener('click',()=>{page++;render();});
  try{const response=await fetch('term-uses-'+section.dataset.term+'.json');if(!response.ok)throw Error('fetch');const data=await response.json();passages=data.passages;render();}
  catch(_){status.textContent='Could not load indexed passages. Try the download link below.';}
})();
