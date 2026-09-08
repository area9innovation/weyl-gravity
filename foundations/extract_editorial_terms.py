#!/usr/bin/env python3
"""Automatic candidate discovery; never automatically publishes dictionary prose."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from foundations.build_term_inventory import TEXT_KEYS,normalize
from foundations.ladder_terms import displayed_fields
OUT=ROOT/'foundations/results/TERM_EXTRACTION_V1.json.gz'
VOCAB=ROOT/'foundations/editorial/vocabularies/physh-2.8.0-terms.json'
DICTIONARY=ROOT/'foundations/editorial/dictionary.json'
MODEL='en_core_web_sm'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def paper_paths():
    return sorted((ROOT/'paper').glob('*.tex'))+sorted(p for p in (ROOT/'paper').glob('*.md') if not p.with_suffix('.tex').exists())

def corpus():
    units=[];inputs={}
    def read(p):inputs[str(p.relative_to(ROOT))]=digest(p);return p.read_text()
    def add(text,source,location,scope,normalized=False):
        if text.strip():units.append(dict(id=len(units),source=source,location=location,scope=scope,text=text,normalized=normalized))
    def walk(value,source,scope,path='',key=''):
        if isinstance(value,dict):
            for k,v in value.items():walk(v,source,scope,path+'/'+k.replace('~','~0').replace('/','~1'),k)
        elif isinstance(value,list):
            for i,v in enumerate(value):walk(v,source,scope,path+'/'+str(i),key)
        elif isinstance(value,str) and key in TEXT_KEYS:add(value,source,path,scope)
    from foundations.build_matrix_site_v2 import build_dataset
    matrix=ROOT/'foundations/site/data.json';data=build_dataset();source=str(matrix.relative_to(ROOT))
    inputs['@generated:matrix-data']=hashlib.sha256((json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()).hexdigest()
    assert len(data['cells'])==576
    for i,cell in enumerate(data['cells']):walk(cell,source,'matrix','/cells/'+str(i))
    for key in ['axes','evidence','graph','theory_passports','boundaries']:walk(data[key],source,'atlas','/'+key)
    for i,step in enumerate(data['ladder']):
        for j,(field,text) in enumerate(displayed_fields(step)):
            add(text,source,f'/ladder/{i}/display/{field}/{j}','ladder')
    p=ROOT/'foundations/editorial/reading-content.json';walk(json.loads(read(p)),str(p.relative_to(ROOT)),'reading')
    dictionary=json.loads(read(DICTIONARY))
    for t in dictionary['terms']:
        for a,text in t['definitions'].items():add(text,str(DICTIONARY.relative_to(ROOT)),f'{t["id"]}/definitions/{a}','dictionary')
        for a,blocks in t['explanations'].items():
            for i,b in enumerate(blocks):add(b['text'],str(DICTIONARY.relative_to(ROOT)),f'{t["id"]}/explanations/{a}/{i}','dictionary')
    for p in paper_paths():
        source=str(p.relative_to(ROOT));raw=read(p);offset=0
        for block in re.split(r'\n\s*\n',raw):
            start=raw.find(block,offset);offset=start+len(block)
            text=normalize(block)
            if text:add(text,source,f'line:{raw[:start].count(chr(10))+1}','papers',True)
    inputs[str(VOCAB.relative_to(ROOT))]=digest(VOCAB)
    return units,inputs

def extract(units):
    import spacy
    from spacy.matcher import PhraseMatcher
    from keyphrase_vectorizers import KeyphraseCountVectorizer
    nlp=spacy.load(MODEL,exclude=['ner'])
    texts=sorted({u['text'] for u in units});docs=dict(zip(texts,nlp.pipe(texts,batch_size=64)))
    print(f'Parsed {len(texts)} distinct text units',flush=True)
    # The library owns its tokenization and document delimiters. Source spans
    # are subsequently recovered against each original unit, never across units.
    # KPV flattens documents before its grammar pass; bound batches to avoid
    # pathological regex costs. No corpus-frequency pruning is applied.
    features=set()
    with nlp.select_pipes(disable=['parser','lemmatizer']):
        for offset in range(0,len(texts),32):
            vectorizer=KeyphraseCountVectorizer(spacy_pipeline=nlp,stop_words=None,workers=1,spacy_exclude=[])
            vectorizer.fit(texts[offset:offset+32])
            features.update(vectorizer.get_feature_names_out())
    features=sorted(features)
    phrases=PhraseMatcher(nlp.vocab,attr='LOWER');phrases.add('KPV',[nlp.make_doc(str(f)) for f in features])
    known=PhraseMatcher(nlp.vocab,attr='LOWER');known_meta={}
    dictionary=json.loads(DICTIONARY.read_text())['terms'];vocabulary=json.loads(VOCAB.read_text())['terms']
    for provider,terms in [('dictionary',dictionary),('physh',vocabulary)]:
        for i,term in enumerate(terms):
            key=provider+':'+str(i);known_meta[key]=(provider,term['id'])
            known.add(key,[nlp.make_doc(a) for a in term['aliases']])
    candidates={};cached={}
    for text,doc in docs.items():
        spans=defaultdict(lambda:dict(methods=set(),dictionary=set(),physh=set()))
        def put(start,end,method,provider=None,target=None):
            if start>=end:return
            value=text[start:end].strip()
            # Generic parsers can label punctuation or articles as noun chunks.
            if len(value)<2 or not any(ch.isalpha() for ch in value):return
            if not any(ch.isspace() for ch in value) and nlp.vocab[value].is_stop:return
            item=spans[(start,end)];item['methods'].add(method)
            if provider:item[provider].add(target)
        for _,start,end in phrases(doc):put(doc[start].idx,doc[end-1].idx+len(doc[end-1]),'keyphrase-vectorizers')
        for chunk in doc.noun_chunks:
            start=chunk.start
            while start<chunk.end and doc[start].is_stop:start+=1
            if start<chunk.end:put(doc[start].idx,chunk.end_char,'spacy-noun-phrase')
            # Preserve nested concepts rather than keeping only the longest phrase.
            for i in range(start,chunk.end):
                for j in range(i+1,min(chunk.end,i+8)+1):
                    ts=doc[i:j]
                    if ts[0].is_stop or ts[-1].pos_ not in ['NOUN','PROPN']:continue
                    if all(t.pos_ in ['NOUN','PROPN','ADJ','NUM'] or t.tag_ in ['VBN','VBG','HYPH'] or t.text=='-' for t in ts):
                        put(ts.start_char,ts.end_char,'nested-noun-phrase')
        for token in doc:
            if not token.is_stop and len(token.text)>1 and token.pos_ in ['NOUN','PROPN','ADJ'] and token.is_alpha:
                put(token.idx,token.idx+len(token),'content-word')
        for m in re.finditer(r'(?<!\w)[A-Z][A-Z0-9_₀]{1,}(?!\w)',text):put(*m.span(),'abbreviation')
        for m in re.finditer(r'\b\w+(?:[-–]\w+)+\b',text):put(*m.span(),'hyphenated-compound')
        # Keep short bullets/claims as explanation tasks, separately from term detection.
        if len(doc)<=35:put(0,len(text),'short-explanation-unit')
        for match,start,end in known(doc):
            provider,target=known_meta[nlp.vocab.strings[match]]
            put(doc[start].idx,doc[end-1].idx+len(doc[end-1]),provider+'-match',provider,target)
        cached[text]=spans
    for unit in units:
        for (start,end),span in cached[unit['text']].items():
            text=unit['text'][start:end];key=' '.join(text.casefold().split())
            if not key:continue
            c=candidates.setdefault(key,dict(id=hashlib.sha256(key.encode()).hexdigest()[:20],phrase=text,methods=set(),dictionary_ids=set(),vocabulary_ids=set(),occurrences=[],scopes=set()))
            c['methods'].update(span['methods']);c['dictionary_ids'].update(span['dictionary']);c['vocabulary_ids'].update(span['physh']);c['scopes'].add(unit['scope'])
            c['occurrences'].append([unit['id'],start,end])
    result=[]
    for c in candidates.values():
        for key in ['methods','dictionary_ids','vocabulary_ids','scopes']:c[key]=sorted(c[key])
        c['kind']='explanation-unit' if c['methods']==['short-explanation-unit'] else 'term-candidate'
        c['coverage']='DICTIONARY_MATCH_REVIEW_SENSE' if c['dictionary_ids'] else 'VOCABULARY_MATCH_NO_EXPLANATION' if c['vocabulary_ids'] else 'UNEXPLAINED_CANDIDATE'
        c['perspectives']={a:('ENTRY_AVAILABLE_SENSE_UNREVIEWED' if c['dictionary_ids'] else 'MISSING') for a in ['general','physics','mathematics','specialist']}
        c['review_state']='UNREVIEWED';result.append(c)
    result.sort(key=lambda c:(-len({m[0] for m in c['occurrences']}),c['phrase'].casefold()))
    versions={p:importlib.metadata.version(p) for p in ['spacy','keyphrase-vectorizers','en-core-web-sm','numpy','scikit-learn','scipy','nltk','psutil','thinc','blis']}
    package=Path(__import__(MODEL).__file__).parent
    model_hashes={str(p.relative_to(package)):digest(p) for p in sorted(package.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    return result,dict(packages=versions,model_files_sha256=model_hashes,keyphrase_feature_count=len(features),pipeline='spaCy tagging/parser + KeyphraseVectorizers + nested phrases + acronym/compound rules + PhraseMatcher')

def build():
    units,inputs=corpus();terms,engine=extract(units)
    inputs[str(Path(__file__).relative_to(ROOT))]=digest(Path(__file__))
    inputs['foundations/build_term_inventory.py']=digest(ROOT/'foundations/build_term_inventory.py')
    inputs['foundations/ladder_terms.py']=digest(ROOT/'foundations/ladder_terms.py')
    for p in ['foundations/editorial-nlp-requirements.txt','foundations/setup_editorial_nlp.sh','foundations/import_editorial_vocabulary.py','foundations/editorial/vocabularies/physh-2.8.0.json.gz','foundations/editorial/vocabularies/PHYSH-LICENSE.md']:
        inputs[p]=digest(ROOT/p)
    result=dict(schema_version=1,kind='AUTOMATIC_EDITORIAL_CANDIDATES',scientific_claims_promoted=False,inputs_sha256=inputs,engine=engine,counts=dict(units=len(units),candidates=len(terms),coverage=dict(Counter(t['coverage'] for t in terms)),kinds=dict(Counter(t['kind'] for t in terms))),units=units,candidates=terms,limits=['Candidate discovery is not proof of technical meaning or complete reader coverage','Generic English tagging may misparse mathematical phrases','Dictionary/PhySH lexical matches require contextual sense review','Paper offsets refer to normalized blocks; original source line is retained','No external vocabulary supplies the four audience explanations','No automatic dictionary publication; no scientific claim is promoted'])
    return result

def check_cached(matrix_bytes=None):
    data=json.loads(gzip.decompress(OUT.read_bytes()))
    recorded={p for p in data['inputs_sha256'] if p.startswith('paper/')}
    current={str(p.relative_to(ROOT)) for p in paper_paths()}
    if current!=recorded:raise ValueError('Extraction stale: paper corpus membership changed')
    for p,h in data['inputs_sha256'].items():
        if p=='@generated:matrix-data':
            if matrix_bytes is None:
                from foundations.build_matrix_site_v2 import build_dataset
                matrix_bytes=(json.dumps(build_dataset(),indent=2,ensure_ascii=False)+'\n').encode()
            actual=hashlib.sha256(matrix_bytes).hexdigest()
        else:actual=digest(ROOT/p)
        if actual!=h:raise ValueError('Extraction stale: '+p)
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--reproduce',action='store_true');args=parser.parse_args()
    if args.check:check_cached();print('PASS: extraction inputs current')
    else:
        content=gzip.compress((json.dumps(build(),ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
        if args.reproduce:assert OUT.read_bytes()==content,'extraction reproduction drift'
        else:OUT.write_bytes(content)
        print('PASS: automatic editorial candidate extraction')
