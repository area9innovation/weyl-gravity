"""Attach corpus mentions to an editorial proposal; never publish definitions."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'foundations/editorial/core-terminology-proposal.json'
CORPUS=ROOT/'foundations/results/TERM_EXTRACTION_V1.json.gz'
RESULT=ROOT/'foundations/results/CORE_TERMINOLOGY_PROPOSAL_V1.json'
REPORT=ROOT/'foundations/reports/core-terminology-proposal-v1.md'
SCOPE_ORDER=['reading','ladder','atlas','dictionary','matrix','papers']


def generate():
    proposal=json.loads(SOURCE.read_text())
    corpus=json.loads(gzip.decompress(CORPUS.read_bytes()))
    units=sorted(corpus['units'],key=lambda u:(SCOPE_ORDER.index(u['scope']),u['id']))
    entries=[]
    for row in proposal['entries']:
        pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(p) for p in sorted(row['source_search_phrases'],key=len,reverse=True))+r')(?!\w)',re.I)
        hits=[]
        for unit in units:
            match=pattern.search(unit['text'])
            if match:
                hits.append(dict(unit_id=unit['id'],source=unit['source'],location=unit['location'],scope=unit['scope'],start=match.start(),end=match.end(),matched_text=match.group(),context=unit['text'][max(0,match.start()-100):match.end()+180]))
        # Keep representative evidence from up to three distinct scopes, preferring
        # the reader-facing material. Counts measure mentioning units, not importance.
        samples=[]
        for scope in SCOPE_ORDER:
            found=next((hit for hit in hits if hit['scope']==scope),None)
            if found:samples.append(found)
            if len(samples)==3:break
        entries.append(dict(row,evidence_basis=('reader-facing mention' if any(h['scope'] in ['reading','ladder','atlas'] for h in hits) else 'background prerequisite; matrix/paper evidence only'),mentioning_units=len(hits),scope_unit_counts=dict(Counter(h['scope'] for h in hits)),evidence=samples))
    inputs=[SOURCE,CORPUS,ROOT/'foundations/editorial/reading-content.json',ROOT/'foundations/editorial/dictionary.json']
    result=dict(schema_version=1,status=proposal['status'],scientific_claims_promoted=False,public_dictionary_changed=False,dependency_tags=[],selection_method=proposal['selection_method'],boundaries=proposal['boundaries'],source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},counts={'total':len(entries),'category':dict(Counter(e['category'] for e in entries)),'batch':dict(Counter(str(e['batch']) for e in entries)),'existing_dictionary_entries':sum(bool(e['existing_dictionary_id']) for e in entries),'without_mentions':sum(not e['evidence'] for e in entries)},entries=entries)
    lines=['# Proposed core terminology: 150 concepts','',
           '**Editorial proposal for review; no public entries or definitions are changed.**','',
           'Start with the 67 batch-1 concepts, including seven existing dictionary entries to review and improve. The 76 batch-2 concepts support atlas reading; seven batch-3 concepts cover specialist construction details. These are writing priorities, not reader ability levels: each approved entry should serve all four perspectives.','',
           'The proposal replaces frequency as the admission criterion with reader need, relevance to current explanations, and a distinct explanatory purpose. Corpus mentions help locate source material; they do not prove that every occurrence has the proposed meaning. The current introductions take precedence over superseded paper claims.','',
           '## How to review and use this list','',
           'For each row, choose keep, fold into another entry, defer, or remove. Compound headings group related questions; they do not make their parts synonyms. Source-search phrases are retrieval probes, never automatic annotation aliases. Papers-only or generic mention evidence needs contextual review before drafting.','',
           'After selection, write the General explanation around a concrete example, Physics around modeling and measurement, Mathematics around structures and hypotheses, and Specialist around the exact role and limits. Expand every acronym on first use. Link prerequisite explanations rather than repeating them. Publish a term only when its four explanations and crosslinks have passed editorial review.','',
           '## Consolidation rules','',
           '- Keep ACA₀ and RCA₀ separate; link both to comprehension, base theory and logical strength. Bare ACA and RCA are not automatic aliases.','- Treat finite energy as a subtopic of energy; keep positive energy distinct from positivity of a quantum state.','- Explain ordinary, supplied-rate and fast Cauchy representations together through crosslinks; do not merge their different information requirements.','- Explain observational residuals separately from residual cohomology.','- Keep ghost meanings visibly separated inside the ghost entry; link gauge bookkeeping to BRST and negative-probability issues to state positivity.','- Give dependency tags short scope-specific entries linked to one shared dependency-tag explanation. Do not repeat the scientific introduction in each.','- Project case entries explain what was held fixed and what remains open; link to foundational definitions instead of making each phrase another entry.','',
           '## Proposed entries','',
           'Batch 1 = introduction essentials; 2 = atlas bridges; 3 = specialist details. “Existing” identifies a current dictionary entry, not approval of the new proposed scope.','']
    for category in ['Mathematics','Physics','Project']:
        lines += [f'### {category} ({result["counts"]["category"][category]})','','| Batch | Proposed concept | Why include it | Source evidence |','| --- | --- | --- | --- |']
        for e in entries:
            if e['category']!=category:continue
            evidence=e['evidence'][0] if e['evidence'] else None
            source=(f'`{evidence["source"]}` · `{evidence["location"]}`' if evidence else 'No exact mention found; prerequisite proposal')
            title=e['title']+(' (existing)' if e['existing_dictionary_id'] else '')
            lines.append(f'| {e["batch"]} | {title} | {e["reason"]} | {source} |')
        lines.append('')
    lines += ['## Evidence and limitations','',
              '145 proposals have mentions in the reading accounts, ladder or atlas. Five are explicit background exceptions supported by matrix/paper mentions: Cocycle and coboundary; Boundary condition; Equation of motion; Curvature and Weyl tensor; BFV boundary formalism. Their reasons are prerequisite value, not frequency. Review these exceptions before commissioning explanations.','',
              'The [machine-readable proposal](../editorial/core-terminology-proposal.json) owns the selection. The [evidence inventory](../results/CORE_TERMINOLOGY_PROPOSAL_V1.json) pins the corpus and current reading sources and records scope counts and original source spans. Search can find generic or overloaded mentions; those are navigation aids, not definition validation. This is AI editorial work, not independent human approval.','',
              'Run `python3 foundations/build_core_terminology_proposal.py --check` for deterministic reproduction and `python3 foundations/verify_core_terminology_proposal.py` for independent structural and source-span checks. The [receipt](../receipts/core-terminology-proposal-v1.json) records commands, timings and test-tier boundaries. No website build is needed because this proposal does not alter publication inputs.','']
    return {RESULT:(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode(),REPORT:'\n'.join(lines).encode()}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for path,content in generate().items():
        if args.check:
            if not path.exists() or path.read_bytes()!=content:raise SystemExit(f'DRIFT: {path}')
        else:path.write_bytes(content)
    print('PASS: core terminology proposal '+('reproduced' if args.check else 'generated'))
