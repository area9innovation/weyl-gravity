"""Publish one global dictionary, with optional editorial tools in the index."""
import gzip,hashlib,json,re
from html import escape
from pathlib import Path
from foundations import reading_site
from foundations.extract_editorial_terms import OUT,check_cached
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'foundations/matrix_site_v2_assets'
MIN_OCCURRENCES=5
POLICY=ROOT/'foundations/editorial/term-publication-policy.json'


def publication_candidates(candidates):
    """Merge explicit aliases, then apply lexical and corpus-frequency gates."""
    policy=json.loads(POLICY.read_text())
    aliases={alias.casefold():row['canonical'] for row in policy['canonical_forms']
             for alias in [row['canonical'],*row['aliases']]}
    retained={word.casefold() for word in policy['retained_single_words']}
    retained.update(row['canonical'].casefold() for row in policy['canonical_forms'])
    groups={}
    for candidate in candidates:
        phrase=candidate['phrase']
        canonical=aliases.get(phrase.casefold(),phrase)
        key=(candidate['kind'],canonical.casefold())
        if key not in groups:
            groups[key]=dict(candidate,phrase=canonical,aliases=[],source_candidate_ids=[],occurrences=[],
                             dictionary_ids=[],vocabulary_ids=[],methods=[],scopes=[])
        group=groups[key]
        group['aliases'].append(phrase)
        group['source_candidate_ids'].append(candidate['id'])
        for field in ['occurrences','dictionary_ids','vocabulary_ids','methods','scopes']:
            group[field].extend(candidate[field])
    published=[]
    for group in groups.values():
        for field in ['aliases','source_candidate_ids','dictionary_ids','vocabulary_ids','methods','scopes']:
            group[field]=sorted(set(group[field]))
        group['occurrences']=[list(o) for o in sorted(set(map(tuple,group['occurrences'])))]
        group['global_occurrence_count']=len(group['occurrences'])
        # A single lexical word needs explicit evidence of technical use. Hyphenated
        # phrases remain phrases; capitalization alone is not evidence (e.g. Appendix).
        single=bool(re.fullmatch(r"[^\W\d_]+",group['phrase'],re.UNICODE))
        supported=bool(group['dictionary_ids'] or group['vocabulary_ids'] or
                       group['phrase'].casefold() in retained)
        if single and not supported:
            continue
        if group['global_occurrence_count']<MIN_OCCURRENCES and not group['dictionary_ids']:
            continue
        group['id']=hashlib.sha256((group['kind']+':'+group['phrase'].casefold()).encode()).hexdigest()[:20]
        group['coverage']=('DICTIONARY_MATCH_REVIEW_SENSE' if group['dictionary_ids'] else
                           'VOCABULARY_MATCH_NO_EXPLANATION' if group['vocabulary_ids'] else
                           'UNEXPLAINED_CANDIDATE')
        published.append(group)
    return sorted(published,key=lambda c:(-c['global_occurrence_count'],c['phrase'].casefold()))


def generated(matrix_bytes,dictionary_page=None):
    data=check_cached(matrix_bytes)
    published=publication_candidates(data['candidates'])
    publication_filter=dict(min_occurrences=MIN_OCCURRENCES,counting_unit="occurrences across the whole corpus, including repeated representations",dictionary_match_exception=True,raw_candidates=len(data['candidates']),published_candidates=len(published),raw_to_published_reduction=len(data['candidates'])-len(published),canonicalization="explicit reviewed aliases; unique source spans counted after merging",single_word_policy="dictionary, vocabulary or explicit project list",policy_sha256=hashlib.sha256(POLICY.read_bytes()).hexdigest())
    body='''<section id="editorial-terminology-index" class="term-review" data-no-dictionary>
<h3>Extracted phrases for editorial review</h3>
<p>Search across the whole project, or narrow the index to a page or collection. Automatically extracted phrases appear here after at least five occurrences across the project; matches to existing dictionary entries are retained at any frequency. Notation variants share one entry. Single words require a dictionary or vocabulary match, or inclusion in the project’s technical-term list. Indexed phrases without an explanation are marked <strong>Definition pending</strong>. Automatic indexing can include noisy phrases; a related dictionary entry may use a different meaning.</p>
<div class="review-filters"><label>Search terms<input id="term-search" type="search" placeholder="e.g. chiral, PRA, residual"></label><label>Used in<select id="term-scope"><option value="all">Whole project</option><option value="ladder">Strength ladder</option><option value="matrix">576 matrix cells</option><option value="atlas">Other atlas prose</option><option value="reading">Reading accounts</option><option value="dictionary">Dictionary explanations</option><option value="papers">Papers</option></select></label><label>Explanation<select id="term-coverage"><option value="all">All terms</option><option value="UNEXPLAINED_CANDIDATE">Definition pending</option><option value="VOCABULARY_MATCH_NO_EXPLANATION">External reference only</option><option value="DICTIONARY_MATCH_REVIEW_SENSE">Related dictionary entry</option></select></label><label>Order<select id="term-sort"><option value="alphabetical">Alphabetical</option><option value="frequency">Most widely used</option></select></label></div>
<p><label><input id="editing-tools" type="checkbox"> Show editing tools</label></p>
<div class="editorial-only"><label>Candidate type<select id="term-kind"><option value="term-candidate">Term candidates</option><option value="all">Terms and short claims</option><option value="explanation-unit">Short explanation tasks</option></select></label><p>All extracted candidates await contextual review. Select phrases to prepare explanations for General, Physics, Mathematics and Specialist readers.</p></div>
<p id="review-status" role="status">Loading the index…</p><div class="review-actions editorial-only"><button id="download-brief" type="button" disabled>Download drafting brief (0 selected)</button><button id="clear-selection" type="button">Clear selection</button></div>
<div id="term-results"></div><div class="review-actions"><button id="previous-terms" type="button">Previous</button><span id="term-page"></span><button id="next-terms" type="button">Next</button></div>
<noscript><p>The A–Z links open full dictionary pages without JavaScript. Download the <a href="term-candidates-all.json.gz">filtered index with source contexts</a> to browse the published index offline.</p></noscript>
<details class="editorial-only"><summary>Indexing and drafting details</summary><p>The scan combines spaCy, KeyphraseVectorizers, nested phrases, abbreviations, the dictionary and APS’s PhySH vocabulary. Matches identify possible concepts, not verified meanings. Short claims are separate explanation tasks.</p><p>Downloaded briefs contain source contexts and requirements for all four perspectives. Decide whether a candidate needs an entry, a link to an existing concept, a clearer sentence or no action. Selections last for this page session and retain contexts from the source where selected. Downloads do not publish definitions.</p><p>Offsets count Unicode code points. Paper contexts use normalized blocks and retain the original starting line. Counts include repeated representations of the same material. Frequency is not reader difficulty or scientific importance. The complete extraction is retained in the repository for review.</p><p><a href="term-extraction-summary.json">Provenance and counts</a> · <a href="https://physh.org/releases">PhySH vocabulary</a></p></details>
</section>'''
    if dictionary_page is None:dictionary_page=reading_site.generated()['dictionary.html']
    dictionary=json.loads(reading_site.DICTIONARY.read_text())
    ordered=sorted(dictionary['terms'],key=lambda t:t['label'].casefold())
    public='<section id="terminology-index" class="core-dictionary-index" data-no-dictionary><h2>Dictionary A–Z</h2><p>Search by name or abbreviation. Hover, focus or tap a term for its explanation; open the full entry to compare perspectives.</p><label>Find an explained concept<input id="dictionary-search" type="search" placeholder="Name or abbreviation, e.g. ACA_0, energy, ghost"></label><p id="dictionary-index-status" role="status">'+str(len(ordered))+' explained concepts</p><ul id="dictionary-word-list">'
    for term in ordered:
        names=' '.join([term['label'],*term['aliases'],term.get('expansion','')])
        public+='<li data-search="'+escape(names.casefold(),quote=True)+'"><a class="dictionary-term" data-dictionary-id="'+escape(term['id'],quote=True)+'" href="term-'+escape(term['id'],quote=True)+'.html">'+escape(term['label'])+'</a></li>'
    public+='</ul><details id="editorial-inventory"><summary>Editorial inventory — extracted phrases awaiting review</summary><p>This discovery queue is not the public dictionary. A detected phrase may be ordinary language, notation or a different sense of an explained term.</p>'+body+'</details></section>'
    page=dictionary_page.decode().replace('<!-- GLOBAL_TERMINOLOGY_INDEX -->',public)
    page=page.replace('</head>','<link rel="stylesheet" href="term-review.css"><script src="term-review.js" defer></script></head>')
    # Retain incoming links without keeping a competing destination or interface.
    redirect=reading_site.shell('Terminology has moved','<h1>Terminology &amp; dictionary</h1><p><a href="dictionary.html#terminology-index">Open the site-wide dictionary</a></p>','dictionary')
    redirect=redirect.replace('</head>','<script>location.replace("dictionary.html"+location.search+"#terminology-index");</script></head>')
    outputs={'dictionary.html':page.encode(),'term-review.html':redirect.encode()}
    for name in ['term-review.js','term-review.css']:outputs[name]=(ASSETS/name).read_bytes()
    summary={k:v for k,v in data.items() if k not in ['units','candidates']}
    if 'source_filtering' in summary:
        filtering=summary['source_filtering']
        summary['source_filtering']={k:v for k,v in filtering.items() if k not in ['excluded_spans','kept_symbolic_terms']}
        summary['source_filtering'].update(excluded_span_count=len(filtering['excluded_spans']),kept_symbolic_term_count=len(filtering['kept_symbolic_terms']),unclosed_span_count=sum(bool(s.get('unclosed')) for s in filtering['excluded_spans']))
    summary['publication_filter']=publication_filter
    outputs['term-extraction-summary.json']=(json.dumps(summary,ensure_ascii=False,indent=2)+'\n').encode()
    extraction_hash=hashlib.sha256(OUT.read_bytes()).hexdigest()
    for scope in ['all','ladder','matrix','atlas','reading','dictionary','papers']:
        units={u['id']:u for u in data['units'] if scope=='all' or u['scope']==scope}
        candidates=[]
        for c in published:
            occurrences=[o for o in c['occurrences'] if o[0] in units]
            if occurrences:candidates.append(dict(c,occurrences=occurrences))
        referenced={o[0] for c in candidates for o in c['occurrences']}
        units={key:value for key,value in units.items() if key in referenced}
        payload=dict(schema_version=1,scope=scope,units=units,candidates=candidates,extraction_hash=extraction_hash,publication_filter=publication_filter)
        outputs['term-candidates-'+scope+'.json.gz']=gzip.compress((json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
    return outputs


def inputs():return [Path(__file__).resolve(),POLICY,OUT,ASSETS/'term-review.js',ASSETS/'term-review.css']
