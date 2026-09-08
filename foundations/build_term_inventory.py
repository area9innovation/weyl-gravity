#!/usr/bin/env python3
"""Deterministic editorial inventory, not a semantic glossary or claim audit."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'foundations/results/TERM_INVENTORY_V1.json'
REPORT=ROOT/'foundations/reports/term-inventory-v1.md'
SEEDS='''observable|observables;convergence rate|convergence rates|cauchy modulus|modulus;RCA₀|RCA_0|RCA0;ACA₀|ACA_0|ACA0;reverse mathematics|reverse mathematical;axiom|axioms;comprehension;Cauchy|Cauchy sequence;completion|completed;continuity|continuous;uniform convergence;computable|computability;constructive;classical logic;choice|axiom of choice;weak König|WKL_0|WKL0;state|states;positivity|positive state;Hilbert space|Hilbert spaces;Krein|Krein space;inner product;operator|operators;self-adjoint;domain|domains;distribution|distributions;test function|test functions;Green function|Green functions|Green operator|Green operators;propagator|propagators;Hadamard;causal|causality;Lorentzian;Euclidean;spectral|spectrum;mode|modes;cutoff|cutoffs;continuum;gauge|gauge symmetry;BRST;BV|Batalin-Vilkovisky;BFV;cohomology;nilpotency|nilpotent;chain map|chain maps;homotopy|homotopies;contraction;cyclicity|cyclic;residual|residuals;pairing|pairings;ghost|ghosts;anomaly|anomalies;counterterm|counterterms;renormalization|renormalized;quantum master equation|QME;symplectic;Poisson;Weyl|conformal gravity;curvature;Bach;hyperbolic|hyperbolicity;well-posed|well posed;boundary|boundaries;detector|detectors;representation|representations;reconstruction;certificate|certificates;reversal|reversals;necessity|necessary;sufficiency|sufficient;carrier|carriers;obligation|obligations;local|locality;energy;unitarity|unitary;empirical;benchmark|benchmarks'''
STOP=set('the a an of to in and or for with on by from as is are be this that it we not no at over under into its these those which such can has have our their all any every same one two three four only more each than then also if when where how what through between without within using used use here there does do both but yet must may will would should result results theorem proof equation section table figure label cite ref begin end text mathrm mathsf leq right left frac quad cdot sum int partial top bottom alpha beta gamma delta lambda theta omega phi psi rho sigma tau mu nu xi operatorname emph textbf textit item document proposition lemma corollary remark definition align equation includegraphics documentclass usepackage'.split())
TEXT_KEYS={'title','label','question','meaning','plain_meaning','includes','summary','boundary','migration_rationale','statement','description','object','adds','establishes','does_not_establish','sufficient_base','rationale','scope','note','notes','paragraphs','heading','deck','background','purpose'}

def prose(value, key=''):
    if isinstance(value,dict):
        return '\n'.join(prose(v,k) for k,v in value.items())
    if isinstance(value,list):return '\n'.join(prose(v,key) for v in value)
    return value if isinstance(value,str) and key in TEXT_KEYS else ''

def normalize(text):
    text=re.sub(r'(?<!\\)%[^\n]*',' ',text)
    text=re.sub(r'\\(?:label|ref|eqref|cite\w*|url|path|includegraphics)\{[^}]*\}',' ',text)
    text=re.sub(r'\\(?:mathsf|mathrm|textbf|textit|emph|text)\{([^{}]*)\}',r'\1',text)
    text=re.sub(r'(RCA|ACA|WKL)\s*[_₀]\s*\{?0?\}?',r'\g<1>0',text)
    text=re.sub(r'\\[A-Za-z]+',' ',text)
    return re.sub(r'\s+',' ',text.replace('{',' ').replace('}',' ')).strip()

def corpus():
    inputs={};docs=[]
    def read(path):
        inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
        return path.read_text()
    matrix=ROOT/'foundations/site/data.json';data=json.loads(read(matrix))
    assert len(data['cells'])==576
    for cell in data['cells']:
        coord='/'.join(cell[k] for k in ['foundation','carrier','obligation'])
        docs.append({'id':'cell:'+coord,'kind':'cell','source':str(matrix.relative_to(ROOT)),'text':normalize(prose(cell))})
    for key in ['axes','evidence','ladder','graph','theory_passports','boundaries']:
        docs.append({'id':'atlas:'+key,'kind':'atlas','source':str(matrix.relative_to(ROOT))+'#'+key,'text':normalize(prose(data[key]))})
    papers=sorted((ROOT/'paper').glob('*.tex'))
    papers+=sorted(p for p in (ROOT/'paper').glob('*.md') if not p.with_suffix('.tex').exists())
    for p in papers:docs.append({'id':str(p.relative_to(ROOT)),'kind':'paper','source':str(p.relative_to(ROOT)),'text':normalize(read(p))})
    p=ROOT/'foundations/editorial/reading-content.json'
    docs.append({'id':'reading','kind':'reading','source':str(p.relative_to(ROOT)),'text':normalize(prose(json.loads(read(p))))})
    return docs,inputs

def generate():
    docs,inputs=corpus(); dictionary=ROOT/'foundations/editorial/dictionary.json'
    inputs[str(dictionary.relative_to(ROOT))]=hashlib.sha256(dictionary.read_bytes()).hexdigest()
    entries=json.loads(dictionary.read_text())['terms']
    aliases={normalize(a).casefold():t['id'] for t in entries for a in t['aliases']}
    candidates=[]
    for group in SEEDS.split(';'):
        names=group.split('|');pattern=re.compile(r'(?<!\w)(?:'+ '|'.join(re.escape(normalize(a)) for a in sorted(names,key=len,reverse=True))+r')(?!\w)',re.I)
        counts=Counter();hits=[];unique=set();examples=[]
        for doc in docs:
            matches=list(pattern.finditer(doc['text']))
            if not matches:continue
            counts[doc['kind']]+=len(matches);hits.append(doc['id']);unique.add(doc['text'])
            if len(examples)<4 and (doc['kind']!='cell' or not any(x['kind']=='cell' for x in examples)):
                m=matches[0];examples.append({'source':doc['source'],'document':doc['id'],'kind':doc['kind'],'excerpt':doc['text'][max(0,m.start()-80):m.end()+140]})
        candidates.append({'term':names[0],'aliases':names,'occurrences':sum(counts.values()),'counts_by_corpus':dict(counts),'cell_count':sum(x.startswith('cell:') for x in hits),'paper_count':sum(x.startswith('paper/') for x in hits),'distinct_text_count':len(unique),'documents':hits,'examples':examples,'dictionary_ids':sorted({aliases[normalize(a).casefold()] for a in names if normalize(a).casefold() in aliases}),'review_state':'NEEDS_EDITORIAL_REVIEW'})
    candidates.sort(key=lambda x:(-x['distinct_text_count'],-x['paper_count'],-x['occurrences'],x['term'].casefold()))
    frequencies=Counter();sources=defaultdict(set)
    for doc in docs:
        tokens=re.findall(r'[A-Za-z][A-Za-z-]{2,}',doc['text'].lower())
        for n in (1,2,3):
            for i in range(len(tokens)-n+1):
                words=tokens[i:i+n]
                if any(w in STOP for w in words):continue
                phrase=' '.join(words);frequencies[phrase]+=1;sources[phrase].add(doc['id'])
    discovery=[{'phrase':p,'occurrences':n,'document_count':len(sources[p]),'example_documents':sorted(sources[p])[:3]} for p,n in frequencies.items() if len(sources[p])>=3]
    discovery.sort(key=lambda x:(-x['document_count'],-x['occurrences'],x['phrase']))
    payload={'schema_version':1,'kind':'EDITORIAL_TERM_INVENTORY','scientific_claims_promoted':False,'inputs_sha256':inputs,'corpus_counts':dict(Counter(d['kind'] for d in docs)),'method':'Explicit alias families plus automatic 1–3 word discovery. Rank by distinct normalized document text, then paper reach and occurrences. Cells retain repeated templates; distinct-text counts expose repetition. TeX cleanup is heuristic, not a parser. Matched vocabulary is not endorsed science.','exclusions':['PDFs and matching Markdown editions when a same-stem TeX exists','generated site HTML/JS copies','machine keys, identifiers and non-prose JSON values','unlinked reports, notes and quantum-weyl source tree outside the declared corpus'],'candidates':candidates,'automatic_discovery':discovery[:200],'limits':['Frequency is not reader difficulty or mathematical importance','Automatic phrases may be fragments or TeX debris; require manual review','Historical papers can contain superseded claims; inventory does not validate them','Selected atlas prose and all cells, not every nested certificate field']}
    lines=['# Terminology inventory — first corpus pass','',f"Scanned **576 cells**, **{payload['corpus_counts']['paper']} paper/source documents**, six atlas prose collections and the current reading account. Source hashes and individual matching document IDs are in `../results/TERM_INVENTORY_V1.json`.",'','Counts are lexical reach, not understanding scores. Repeated cell templates inflate frequency. The distinct-text column collapses identical whole document texts; it does not remove repeated sentences. The automatic discovery list is a review queue, not published definitions.','', '| Term family | Cells | Papers | Distinct texts | Occurrences | Dictionary |','|---|---:|---:|---:|---:|---|']
    for t in candidates:lines.append(f"| {t['term']} | {t['cell_count']} | {t['paper_count']} | {t['distinct_text_count']} | {t['occurrences']} | {', '.join(t['dictionary_ids']) or 'pending'} |")
    lines+=['','## Editorial sequence','','1. Reading prerequisites: state, observable, carrier, axiom, representation, convergence, completion and reverse mathematics. Explain what each lets a reader understand.','2. Bridge vocabulary: positivity, inner product, operator/domain, distribution/test function, mode/cutoff, Green operator, causality. Include examples and explicit contrasts between meanings.','3. Research vocabulary: BRST/BV, cohomology, nilpotency, contraction, cyclicity, residual classes, Hadamard, anomaly and quantum master equation. Lead specialist entries with the defining condition, hypotheses and project boundary.','','This order is editorial judgment informed by the inventory, not an automatic ranking of importance. State, carrier, domain, local, residual and ghost need sense separation before automatic annotation. A mathematical ghost variable and a negative-norm excitation must not share an unqualified definition.','','## Method and limits','',payload['method'],'',*['- '+s for s in payload['exclusions']+payload['limits']],'','Reproduce: `python3 foundations/build_term_inventory.py`; check freshness: `python3 foundations/build_term_inventory.py --check`. No scientific lifecycle is promoted.']
    return {OUT:(json.dumps(payload,indent=2,ensure_ascii=False)+'\n').encode(),REPORT:('\n'.join(lines)+'\n').encode()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for path,content in generate().items():
        if args.check:
            if not path.exists() or path.read_bytes()!=content:raise SystemExit('STALE: '+str(path))
        else:path.write_bytes(content)
    print('PASS: terminology inventory '+('current' if args.check else 'generated'))
