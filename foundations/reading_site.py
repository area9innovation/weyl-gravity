"""Static audience editions over a shared, source-pinned scientific record."""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'foundations/editorial/reading-content.json'
DICTIONARY=ROOT/'foundations/editorial/dictionary.json'
ASSETS=ROOT/'foundations/matrix_site_v2_assets'
PAPERS=['99-how-to-build-a-universe.pdf','98-physicist-executive-summary.pdf','00-ghosts-geometry-reality.pdf','21-reverse-foundations-of-physics.pdf']


def load():
    data=json.loads(CONTENT.read_text())
    dictionary=json.loads(DICTIONARY.read_text())
    seen=set(); ids=set()
    for term in dictionary['terms']:
        if term['id'] in ids: raise ValueError('duplicate dictionary ID')
        ids.add(term['id'])
        if term.get('abbreviation') and (not term.get('expansion') or term['expansion'] not in term['definitions']['general']): raise ValueError('expand abbreviation in general definition')
        if not term['scope'].strip(): raise ValueError('missing dictionary scope')
        if set(term['explanations']) != set(data['audiences']): raise ValueError('missing expanded perspective')
        for blocks in term['explanations'].values():
            if not blocks or any(not b['heading'].strip() or not b['text'].strip() for b in blocks): raise ValueError('empty expanded explanation')
        for source in term['sources']:
            if hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()!=source['sha256']: raise ValueError('dictionary source review required: '+source['path'])
        if set(term['definitions']) != set(data['audiences']): raise ValueError('missing dictionary perspective')
        for alias in term['aliases']:
            if not alias.strip() or alias.casefold() in seen: raise ValueError('ambiguous dictionary alias')
            seen.add(alias.casefold())
    if any(r not in ids for t in dictionary['terms'] for r in t['related']): raise ValueError('unknown related dictionary term')
    data['concepts']={t['id']:dict(label=t['label'], **t['definitions']) for t in dictionary['terms']}
    for record in data['sources'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('Editorial review required after source change: '+record['path'])
    for topic in data['topics'].values():
        if set(topic['versions'])!=set(data['audiences']):raise ValueError('missing audience edition')
        for sections in topic['versions'].values():
            if [s['id'] for s in sections]!=topic['section_ids']:raise ValueError('section identity drift')
        if len(topic.get('section_labels',topic['section_ids']))!=len(topic['section_ids']): raise ValueError('section label mismatch')
        for refs in topic.get('section_sources',{}).values():
            if any(ref not in data['sources'] for ref in refs): raise ValueError('unknown introduction source')
        for c in topic['claim_ids']:
            if c not in data['claims']:raise ValueError('missing scientific record')
    return data


def e(text): return html.escape(text,quote=True)


def site_header(active='introduction', editions=False):
    nav=[('introduction','index.html','Introduction'),('questions','questions.html','Questions'),('journeys','atlas.html#view=passports','Theory journeys'),('atlas','atlas.html','Research atlas'),('papers','papers.html','Papers'),('dictionary','dictionary.html','Dictionary')]
    links=''.join(f'<a href="{url}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for key,url,label in nav)
    perspectives=[('general','General','No specialist background'),('physics','Physics','University physics'),('mathematics','Mathematics','University mathematics'),('specialist','Specialist','Topic-specific research knowledge')]
    choices=''.join(f'<label class="perspective-option" data-perspective="{key}"><input type="checkbox" name="audience" value="{key}"'+(' checked' if key=='general' else '')+f'><span><strong>{label}</strong><small>{background}</small></span></label>' for key,label,background in perspectives)
    context='Changes the account and term explanations on this page.' if editions else 'Changes term explanations and your reading preference. This page has one shared account; atlas research views remain specialist.'
    menu='<details class="perspective-menu" id="perspective-menu"><summary>Reading perspectives <span id="perspective-current">General</span></summary><div class="perspective-panel"><fieldset class="reading-controls"><legend>Reading perspectives</legend><p class="perspective-help">Choose one or more to read and compare. Physics and Mathematics assume different backgrounds, not a higher or lower level.</p><div class="perspective-options">'+choices+'</div><div class="perspective-actions"><button type="button" id="show-all-perspectives">Compare all four</button><span id="audience-description" role="status" aria-live="polite">Showing General.</span></div><p class="perspective-context">'+context+'</p><noscript>JavaScript is needed to change perspective. The general account remains readable.</noscript></fieldset></div></details>'
    return f'<header class="site-header"><a class="brand" href="index.html">Reverse Physics<span>Questions before conclusions</span></a><nav aria-label="Main navigation">{links}</nav>{menu}</header>'


def shell(title,body,active='introduction',audience=False):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — Reverse Physics</title><meta name="description" content="Read the questions and evidence of reverse physics from a general, physics, mathematics or specialist perspective.">
<link rel="stylesheet" href="reading.css"><link rel="stylesheet" href="site-shell.css"><script src="reading.js" defer></script><link rel="stylesheet" href="dictionary.css"><script src="dictionary.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>{site_header(active,audience)}<main id="main">{body}</main><footer>Living accounts, dated papers, explicit limits. <a href="papers.html">About the publications</a> · <a href="editorial-record.json">Scientific and editorial record</a> · <a href="manifest.json">Build provenance</a></footer></body></html>'''


def linked_text(text, terms, current):
    """Link unambiguous dictionary vocabulary in authored prose, excluding self."""
    aliases={a.casefold():t['id'] for t in terms if t['id']!=current and t.get('auto_annotate',True) for a in t['aliases']}
    if not aliases:return e(text)
    pattern=re.compile(r'(?<!\w)('+ '|'.join(re.escape(a) for a in sorted(aliases,key=len,reverse=True))+r')(?!\w)',re.I)
    parts=[];start=0;seen=set()
    for match in pattern.finditer(text):
        id=aliases[match.group().casefold()]
        parts.append(e(text[start:match.start()]))
        parts.append(e(match.group()) if id in seen else f'<a class="dictionary-crosslink" href="term-{e(id)}.html">{e(match.group())}</a>')
        seen.add(id);start=match.end()
    return ''.join(parts)+e(text[start:])


def topic_page(data,key):
    topic=data['topics'][key]
    body=f'<header class="reading-hero"><p class="eyebrow">'+('The project' if key=='introduction' else 'Approximations and prediction')+f'</p><h1>{e(topic["title"])}</h1><p class="deck">{e(topic["deck"])}</p></header>'
    if key=='introduction':
        body+='<p class="intro-provenance">The living introduction, adapted from <a href="papers/99-how-to-build-a-universe.pdf">How to Build a Universe</a> and the <a href="papers/98-physicist-executive-summary.pdf">physicist introduction</a>. The same programme and section outline at four perspectives, updated against the current evidence.</p>'
    body+='<nav class="section-nav" aria-label="On this page">'+''.join(f'<a href="#{sid}">{label}</a>' for sid,label in zip(topic['section_ids'],topic.get('section_labels',['The question','The assumptions','The result','The limits'])))+'</nav>'
    for sid in topic['section_ids']:
        body+=f'<section id="{sid}" class="reading-section">'
        for audience,sections in topic['versions'].items():
            section=next(s for s in sections if s['id']==sid)
            brief=data['audiences'][audience]
            body+=f'<div data-edition="{audience}"'+(' hidden' if audience!='general' else '')+f'><div class="edition-header"><span class="edition-label">{e(brief["label"])}</span><span class="edition-background">{e(brief["background"])}</span></div><h2>{e(section["heading"])}</h2>'+''.join(f'<p>{e(p)}</p>' for p in section['paragraphs'])+'</div>'
        body+='</section>'
    body+='<aside class="shared-status" aria-label="Current scientific status"><p class="eyebrow">Shared across all perspectives</p><h2>What is established?</h2>'
    for cid in topic['claim_ids']:
        claim=data['claims'][cid]
        body+=f'<article data-claim="{cid}"><h3>{e(claim["status"])}</h3><p>{e(claim["summary"])}</p><p class="boundary">{e(claim["boundary"])}</p><details><summary>Statement and evidence</summary>'
        if claim.get('precise_statement'): body+=f'<p>{e(claim["precise_statement"])}</p>'
        body+='<ul>'
        for source in claim['sources']:
            path=data['sources'][source]['path']
            body+=f'<li><a href="sources/{e(path)}">{e(Path(path).name)}</a></li>'
        body+='</ul></details></article>'
    body+='</aside><p class="dictionary-help">Hover, focus or tap an underlined term for an explanation, or <a href="dictionary.html">browse the dictionary A–Z</a>.</p>'
    if key=='introduction':
        body+='<a class="next-reading" href="wave.html">Explore the wave example <span>When does an approximation justify a prediction? →</span></a>'
    else:
        body+='<section class="further"><h2>Follow the argument</h2><p><a href="atlas.html#view=ladder">Technical strength ladder</a> · <a href="atlas.html#view=graph">Implication map</a> · <a href="papers.html">Related papers</a></p><p>The ladder and atlas retain historical research records. Their stages are not substitutes for the current statement above.</p></section>'
    body+='<p class="review-note">Audience editions reviewed against pinned repository evidence on 8 September 2026 by the AI assistant. This is editorial review, not independent human approval or a new proof.</p><noscript><p>You are reading the general edition. Enable JavaScript to switch perspective; all evidence links remain available.</p></noscript>'
    return shell(topic['title'],body,'introduction' if key=='introduction' else 'questions',True)


def display_label(term):
    label=term['label']
    return label.capitalize() if label in {'LOCAL-ALGEBRAIC','EUCLIDEAN-SPECTRAL','REDUCED-MODE','LORENTZIAN-CAUSAL'} else label


def generated():
    data=load()
    outputs={'index.html':topic_page(data,'introduction').encode(),'wave.html':topic_page(data,'wave').encode(),
        'reading.css':(ASSETS/'reading.css').read_bytes(),'reading.js':(ASSETS/'reading.js').read_bytes(),
        'editorial-record.json':(json.dumps({k:v for k,v in data.items() if k!='concepts'},indent=2,ensure_ascii=False)+'\n').encode()}
    dictionary=json.loads(DICTIONARY.read_text())
    for name in ['dictionary.js','dictionary.css','site-shell.css','term-occurrences.js']:
        outputs[name]=(ASSETS/name).read_bytes()
    outputs['dictionary.json']=DICTIONARY.read_bytes()
    ordered=sorted(dictionary['terms'],key=lambda t:t['label'].casefold())
    body='<header class="reading-hero"><p class="eyebrow">Concepts and connections</p><h1>Terminology &amp; dictionary</h1><p class="deck">Explanations for General, Physics, Mathematics and Specialist readers.</p></header>'
    body+='<!-- GLOBAL_TERMINOLOGY_INDEX -->'
    outputs['dictionary.html']=shell('Dictionary',body,'dictionary',True).encode()
    labels={t['id']:display_label(t) for t in ordered}
    for term in ordered:
        body=f'<section class="reading-section dictionary-entry" id="{e(term["id"])}"><header class="dictionary-entry-heading"><a class="dictionary-back" href="dictionary.html">Back to A–Z</a><h1>{e(display_label(term))}</h1><p>{e(term["scope"])}</p>'+ (f'<p class="abbreviation-expansion"><strong>Stands for:</strong> {e(term["expansion"])}</p>' if term.get('expansion') else '')+'</header>'
        for audience,definition in term['definitions'].items():
            body+=f'<div data-edition="{audience}"'+(' hidden' if audience!='general' else '')+f'><span class="edition-label">{e(data["audiences"][audience]["label"])}</span><p class="definition-summary">{linked_text(definition,ordered,term['id'])}</p>'
            for block in term['explanations'][audience]:
                body+=f'<h3>{e(block["heading"])}</h3><p>{linked_text(block["text"],ordered,term['id'])}</p>'
            body+='</div>'
        body+='<footer class="dictionary-entry-sources"><p>Related: '+ ' · '.join(f'<a href="term-{e(id)}.html">{e(labels[id])}</a>' for id in term['related'])+'</p><details><summary>Sources and editorial scope</summary><p>AI editorial review against these sources; no independent expert approval. Historical source claims remain subject to the current project status.</p><ul>'
        for source in term['sources']:
            body+=f'<li><a href="sources/{e(source["path"])}">{e(Path(source["path"]).name)}</a></li>'
            outputs['sources/'+source['path']]=(ROOT/source['path']).read_bytes()
        for ref in term.get('references',[]):
            body+=f'<li><a href="{e(ref["url"])}">{e(ref["title"])}</a></li>'
        body+='</ul></details><a href="dictionary.html">Back to word list</a></footer></section>'
        body+=f'<section class="term-occurrences" data-term="{e(term["id"])}" data-no-dictionary><h2>Where this term appears</h2><p>Indexed phrase matches, not confirmation that every passage uses the same meaning. Repeated representations may be counted separately.</p><p class="occurrence-status" role="status">Loading indexed passages…</p><ol class="occurrence-results"></ol><button class="occurrence-previous" type="button" disabled>Previous</button> <button class="occurrence-next" type="button" disabled>Next</button><p><a href="term-uses-{e(term["id"])}.json">Download all indexed passages and source hashes</a></p><noscript><p>Use the download link to read the indexed passages without JavaScript.</p></noscript></section><script src="term-occurrences.js" defer></script>'
        outputs['term-'+term['id']+'.html']=shell(display_label(term),body,'dictionary',True).encode()
    questions='''<header class="reading-hero"><p class="eyebrow">Explore a question</p><h1>Where do the assumptions enter?</h1><p class="deck">Begin with one problem. Follow its explanation to the precise result and its evidence.</p></header>
<div class="question-grid"><a class="question-card" href="wave.html"><span class="eyebrow">Physics and reverse mathematics</span><h2>When does an approximation justify a prediction?</h2><p>The same wave and detector, with and without a supplied error schedule.</p><span>General · Physics · Mathematics · Specialist →</span></a>
<a class="question-card" href="cutoff-positivity.html"><span class="eyebrow">Finite models and the continuum</span><h2>Can every finite test pass while the full model fails?</h2><p>A conditional reduced-model positivity result and its limits.</p><span>Existing interactive account · audience migration pending →</span></a></div>'''
    outputs['questions.html']=shell('Questions',questions,'questions').encode()
    papers='''<header class="reading-hero"><p class="eyebrow">Publication archive</p><h1>Living explanations. Dated papers.</h1><p class="deck">The introduction is the current reading route. Papers preserve a citable account of the work at a particular date.</p></header>
<section class="reading-section"><h2>Introductions</h2><p>Papers 99 and 98 supplied the public and physicist source material for the <a href="index.html">unified introduction</a>. They remain publications, rather than competing current entrances.</p><ul>
<li><a href="papers/99-how-to-build-a-universe.pdf">Paper 99 — How to Build a Universe</a> · general introduction, 17 August 2026.</li>
<li><a href="papers/98-physicist-executive-summary.pdf">Paper 98 — Executive Summary for Physicists</a> · 17 August 2026.</li>
<li><a href="papers/00-ghosts-geometry-reality.pdf">Paper 00 — Ghosts, Geometry, and Reality</a> · programme guide.</li></ul>
<aside class="archive-correction"><h3>Correction to earlier full-transfer claims</h3><p>The later audit rejects the current serialized full complex. The trace/ghost candidate is a partial repair, not an accepted full construction. Read the <a href="index.html#limits">current introduction</a> and <a href="sources/foundations/reports/tt-trace-repair-v1.md">repair report</a> alongside affirmative transfer statements in earlier publications.</p></aside></section>
<section class="reading-section"><h2>Mathematical account and evidence</h2><p><a href="papers/21-reverse-foundations-of-physics.pdf">Paper 21 — Reverse Foundations of Physics</a> · working mathematical account, including the recent export audit.</p><p>The <a href="wave.html">wave topic</a> links the exact reconstruction statement and reversal proof separately; do not infer the full statement from an older ladder entry.</p><p><a href="https://github.com/area9innovation/weyl-gravity/tree/master/paper">Complete paper collection and supplements</a></p></section>
<section class="reading-section"><h2>Research and authorship</h2><p>AI systems contribute derivations, programming, checking and drafting. Asger Alstrup Palm is the accountable human contact. The reviewed website editions do not imply independent peer review. Evidence records distinguish human arguments, finite computational checks and unresolved claims.</p></section>'''
    outputs['papers.html']=shell('Papers',papers,'papers').encode()
    for record in data['sources'].values(): outputs['sources/'+record['path']]=(ROOT/record['path']).read_bytes()
    for name in PAPERS:outputs['papers/'+name]=(ROOT/'paper'/name).read_bytes()
    return outputs


def inputs():
    data=load()
    return [Path(__file__).resolve(),CONTENT,DICTIONARY,*[ROOT/s['path'] for t in json.loads(DICTIONARY.read_text())['terms'] for s in t['sources']],ASSETS/'dictionary.js',ASSETS/'term-occurrences.js',ASSETS/'dictionary.css',ASSETS/'site-shell.css',ASSETS/'reading.css',ASSETS/'reading.js',*[ROOT/r['path'] for r in data['sources'].values()],*[ROOT/'paper'/p for p in PAPERS]]
