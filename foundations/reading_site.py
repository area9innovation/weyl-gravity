"""Static audience editions over a shared, source-pinned scientific record."""
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'foundations/editorial/reading-content.json'
DICTIONARY=ROOT/'foundations/editorial/dictionary.json'
ASSETS=ROOT/'foundations/matrix_site_v2_assets'
PAPERS=['99-how-to-build-a-universe.pdf','98-physicist-executive-summary.pdf','00-ghosts-geometry-reality.pdf','21-reverse-foundations-of-physics.pdf']


def load():
    data=json.loads(CONTENT.read_text())
    dictionary=json.loads(DICTIONARY.read_text())
    seen=set()
    for term in dictionary['terms']:
        if set(term['definitions']) != set(data['audiences']): raise ValueError('missing dictionary perspective')
        for alias in term['aliases']:
            if not alias.strip() or alias.casefold() in seen: raise ValueError('ambiguous dictionary alias')
            seen.add(alias.casefold())
    data['concepts']={t['id']:dict(label=t['label'], **t['definitions']) for t in dictionary['terms']}
    for record in data['sources'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:
            raise ValueError('Editorial review required after source change: '+record['path'])
    for topic in data['topics'].values():
        if set(topic['versions'])!=set(data['audiences']):raise ValueError('missing audience edition')
        for sections in topic['versions'].values():
            if [s['id'] for s in sections]!=topic['section_ids']:raise ValueError('section identity drift')
        for c in topic['claim_ids']:
            if c not in data['claims']:raise ValueError('missing scientific record')
    return data


def e(text): return html.escape(text,quote=True)


def shell(title,body,active='introduction',audience=False):
    nav=[('introduction','index.html','Introduction'),('questions','questions.html','Questions'),('journeys','atlas.html#view=passports','Theory journeys'),('atlas','atlas.html','Research atlas'),('papers','papers.html','Papers'),('dictionary','dictionary.html','Dictionary')]
    links=''.join(f'<a href="{url}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for key,url,label in nav)
    selector=''
    if audience:
        perspectives=[('general','General','No specialist background'),('physics','Physics','University physics'),('mathematics','Mathematics','University mathematics'),('specialist','Specialist','Topic-specific research knowledge')]
        selector='<fieldset class="reading-controls"><legend>Reading perspectives</legend><p class="perspective-help">Choose one or more to read and compare. Physics and Mathematics assume different backgrounds, not a higher or lower level.</p><div class="perspective-options">'+''.join(f'<label class="perspective-option" data-perspective="{key}"><input type="checkbox" name="audience" value="{key}"'+(' checked' if key=='general' else '')+f'><span><strong>{label}</strong><small>{background}</small></span></label>' for key,label,background in perspectives)+'</div><div class="perspective-actions"><button type="button" id="show-all-perspectives">Compare all four</button><span id="audience-description" role="status" aria-live="polite">Showing General.</span></div></fieldset>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — Reverse Physics</title><meta name="description" content="Read the questions and evidence of reverse physics from a general, physics, mathematics or specialist perspective.">
<link rel="stylesheet" href="reading.css"><script src="reading.js" defer></script><link rel="stylesheet" href="dictionary.css"><script src="dictionary.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><a class="brand" href="index.html">Reverse Physics<span>Questions before conclusions</span></a><nav aria-label="Main navigation">{links}</nav></header>
{selector}<main id="main">{body}</main><footer>Living accounts, dated papers, explicit limits. <a href="papers.html">About the publications</a> · <a href="editorial-record.json">Scientific and editorial record</a> · <a href="manifest.json">Build provenance</a></footer></body></html>'''


def topic_page(data,key):
    topic=data['topics'][key]
    body=f'<header class="reading-hero"><p class="eyebrow">'+('The project' if key=='introduction' else 'Approximations and prediction')+f'</p><h1>{e(topic["title"])}</h1><p class="deck">{e(topic["deck"])}</p></header>'
    body+='<nav class="section-nav" aria-label="On this page">'+''.join(f'<a href="#{sid}">{label}</a>' for sid,label in zip(topic['section_ids'],['The question','The assumptions','The result','The limits']))+'</nav>'
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
    body+='</aside><section class="concepts"><h2>Terms used in this account</h2>'
    for concept in data['concepts'].values():
        body+=f'<details><summary>{e(concept["label"])}</summary>'
        for audience in data['audiences']:
            body+=f'<p data-edition="{audience}"'+(' hidden' if audience!='general' else '')+f'><span class="edition-label">{e(data["audiences"][audience]["label"])}</span> {e(concept[audience])}</p>'
        body+='</details>'
    body+='</section>'
    if key=='introduction':
        body+='<a class="next-reading" href="wave.html">Explore the wave example <span>When does an approximation justify a prediction? →</span></a>'
    else:
        body+='<section class="further"><h2>Follow the argument</h2><p><a href="atlas.html#view=ladder">Technical strength ladder</a> · <a href="atlas.html#view=graph">Implication map</a> · <a href="papers.html">Related papers</a></p><p>The ladder and atlas retain historical research records. Their stages are not substitutes for the current statement above.</p></section>'
    body+='<p class="review-note">Audience editions reviewed against pinned repository evidence on 8 September 2026 by the AI assistant. This is editorial review, not independent human approval or a new proof.</p><noscript><p>You are reading the general edition. Enable JavaScript to switch perspective; all evidence links remain available.</p></noscript>'
    return shell(topic['title'],body,'introduction' if key=='introduction' else 'questions',True)


def generated():
    data=load()
    outputs={'index.html':topic_page(data,'introduction').encode(),'wave.html':topic_page(data,'wave').encode(),
        'reading.css':(ASSETS/'reading.css').read_bytes(),'reading.js':(ASSETS/'reading.js').read_bytes(),
        'editorial-record.json':(json.dumps({k:v for k,v in data.items() if k!='concepts'},indent=2,ensure_ascii=False)+'\n').encode()}
    dictionary=json.loads(DICTIONARY.read_text())
    for name in ['dictionary.js','dictionary.css']:
        outputs[name]=(ASSETS/name).read_bytes()
    outputs['dictionary.json']=DICTIONARY.read_bytes()
    body='<h1>Dictionary</h1><p>Compare explanations for different backgrounds. Scope notes identify context-specific uses. Underlined terms elsewhere open these same definitions by hover, keyboard focus or tap.</p>'
    for term in dictionary['terms']:
        body+=f'<section class="reading-section" id="{e(term["id"])}"><h2>{e(term["label"])}</h2><p>{e(term["scope"])}</p>'
        for audience,definition in term['definitions'].items():
            body+=f'<div data-edition="{audience}"'+(' hidden' if audience!='general' else '')+f'><span class="edition-label">{e(data["audiences"][audience]["label"])}</span><p>{e(definition)}</p></div>'
        body+='</section>'
    outputs['dictionary.html']=shell('Dictionary',body,'dictionary',True).encode()
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
    return [Path(__file__).resolve(),CONTENT,DICTIONARY,ASSETS/'dictionary.js',ASSETS/'dictionary.css',ASSETS/'reading.css',ASSETS/'reading.js',*[ROOT/r['path'] for r in data['sources'].values()],*[ROOT/'paper'/p for p in PAPERS]]
