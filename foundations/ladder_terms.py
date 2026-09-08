"""Index the ladder's displayed fields, independently of scientific grading."""
import hashlib
import html
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'foundations/editorial/ladder-terms.json'
DICTIONARY=ROOT/'foundations/editorial/dictionary.json'

def displayed_fields(step):
    """Mirror the displayed field selection, preserving the field as provenance."""
    result={'level':step['level'],'status':step['status'],'object':step['object']}
    result['base']=step.get('sufficient_base') or step.get('candidate_upper_bound') or 'Not classified'
    result['adds']=step.get('adds',[])
    result['establishes']=step.get('establishes') or step.get('establishes_if_formalized') or []
    result['excluded']=step.get('open') or step.get('does_not_establish') or ([step['boundary']] if step.get('boundary') else [])
    if step.get('separation'):result['separation']=step['separation']
    return [(key,text) for key,value in result.items() for text in (value if isinstance(value,list) else [value])]

def inventory(steps):
    registry=json.loads(REGISTRY.read_text());dictionary=json.loads(DICTIONARY.read_text())
    dictionary_ids={t['id'] for t in dictionary['terms']};ids=set();terms=[]
    for term in registry['terms']:
        if term['id'] in ids:raise ValueError('duplicate ladder term ID')
        ids.add(term['id'])
        if term['dictionary_id'] and term['dictionary_id'] not in dictionary_ids:raise ValueError('unknown dictionary target')
        pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(a) for a in sorted(term['aliases'],key=len,reverse=True))+r')(?!\w)',re.I)
        matches=[]
        for step in steps:
            for field,text in displayed_fields(step):
                if (field=='status')!=(term['kind']=='stage-status'):continue
                # Underscores delimit words in the visibly displayed stage names.
                matcher=re.compile(pattern.pattern.replace(r'\w', '[A-Za-z0-9]'),re.I) if field=='level' else pattern
                for match in matcher.finditer(text):
                    matches.append({'level':step['level'],'field':field,'text':text,'start':match.start(),'end':match.end()})
        if not matches:raise ValueError('unmatched ladder term: '+term['label'])
        terms.append(dict(term,matches=matches,coverage='RELATED_DICTIONARY_ENTRY' if term['dictionary_id'] else 'DEFINITION_PENDING'))
    return {'schema_version':1,'kind':'LADDER_TERMINOLOGY_INDEX','scientific_claims_promoted':False,'scope':registry['scope'],'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REGISTRY,DICTIONARY]},'ladder_sha256':hashlib.sha256(json.dumps(steps,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'stage_count':len(steps),'term_count':len(terms),'dictionary_links':sum(t['dictionary_id'] is not None for t in terms),'terms':sorted(terms,key=lambda t:t['label'].casefold()),'limitations':['Curated first-pass vocabulary, not a semantic completeness claim','Related dictionary entries may cover only part of the indexed phrase','Historical stage grades are not revalidated by this index']}

def render(data):
    e=html.escape
    text='<details class="ladder-terminology" data-no-dictionary><summary>Terms on this page · alphabetical index</summary><p>Find a term, jump to its stage, or read a related dictionary entry. “Definition pending” means its four-perspective explanation has not yet been written. Stage labels describe historical records; this index does not validate them.</p><ul>'
    for term in data['terms']:
        stages=list(dict.fromkeys(m['level'] for m in term['matches']))
        text+=f'<li id="{e(term["id"])}"><strong>{e(term["label"])}</strong> <span>'+ ' · '.join(f'<a href="#view=ladder&amp;termStage={e(s)}">{e(s.split("_")[0])}</a>' for s in stages)+'</span> — '
        if term['dictionary_id']:text+=f'<a href="dictionary.html#{e(term["dictionary_id"])}">Related definition</a>'
        else:text+='<span class="muted">Definition pending</span>'
        text+='</li>'
    return text+'</ul><p><a href="term-review.html?scope=ladder">Review automatically extracted phrases and explanation gaps →</a></p><p><a href="ladder-terms.json">Index and exact source locations</a></p></details>'
