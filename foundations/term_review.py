"""Publish the validated offline extraction as a static editorial review tool."""
import gzip,json
from pathlib import Path
from foundations import reading_site
from foundations.extract_editorial_terms import OUT,check_cached
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'foundations/matrix_site_v2_assets'

def generated(matrix_bytes):
    data=check_cached(matrix_bytes)
    body='''<header class="reading-hero"><p class="eyebrow">Help explain the research</p><h1>Terminology review</h1><p class="deck">Find words, phrases and claims that readers may need explained. These are automatically extracted candidates, not approved dictionary entries.</p></header>
<p>The scan combines spaCy, KeyphraseVectorizers, nested phrase and abbreviation rules, our dictionary, and APS’s PhySH vocabulary. A vocabulary match does not establish the meaning in this passage. Short claims are kept as separate explanation tasks.</p>
<section class="term-review" data-no-dictionary>
<div class="review-filters"><label>Search phrases<input id="term-search" type="search" placeholder="e.g. chiral, PRA, residual"></label><label>Source<select id="term-scope"><option value="ladder">Strength ladder</option><option value="matrix">576 matrix cells</option><option value="atlas">Other atlas prose</option><option value="reading">Reading accounts</option><option value="dictionary">Dictionary explanations</option><option value="papers">Papers</option></select></label><label>Explanation status<select id="term-coverage"><option value="all">All statuses</option><option value="UNEXPLAINED_CANDIDATE">Unexplained candidate</option><option value="VOCABULARY_MATCH_NO_EXPLANATION">External vocabulary only</option><option value="DICTIONARY_MATCH_REVIEW_SENSE">Dictionary match: check meaning</option></select></label><label>Candidate type<select id="term-kind"><option value="all">Terms and short claims</option><option value="term-candidate">Term candidates</option><option value="explanation-unit">Short explanation tasks</option></select></label></div>
<p id="review-status" role="status">Loading the selected source…</p><div class="review-actions"><button id="download-brief" type="button" disabled>Download drafting brief (0 selected)</button><button id="clear-selection" type="button">Clear selection</button></div>
<div id="term-results"></div><div class="review-actions"><button id="previous-terms" type="button">Previous</button><span id="term-page"></span><button id="next-terms" type="button">Next</button></div>
<noscript><p>Enable JavaScript to browse the review queue. The <a href="term-candidates-ladder.json.gz">ladder extraction</a> and <a href="term-extraction-summary.json">extraction summary</a> remain downloadable.</p></noscript></section>
<section class="further"><h2>From candidate to explanation</h2><p>Select phrases and download a drafting brief containing their contexts, locations, matches and requirements for all four perspectives. Review whether each phrase needs a dictionary entry, links to existing concepts, a clearer sentence, or no action. Selections last for this page session and retain contexts from the source where selected. Offsets count Unicode code points. The download does not approve a definition or change the site.</p><p>Each occurrence has a source and location. For papers, offsets refer to a normalized text block and the original starting line is retained. Dictionary and external matches remain unreviewed until their sense is checked. Frequency is not reader difficulty.</p><p><a href="dictionary.html">Read the dictionary</a> · <a href="term-extraction-summary.json">Extraction provenance and counts</a> · <a href="https://physh.org/releases">PhySH source vocabulary</a></p></section>'''
    page=reading_site.shell('Terminology review',body,'dictionary')
    page=page.replace('</head>','<link rel="stylesheet" href="term-review.css"><script src="term-review.js" defer></script></head>')
    outputs={'term-review.html':page.encode()}
    for name in ['term-review.js','term-review.css']:outputs[name]=(ASSETS/name).read_bytes()
    summary={k:v for k,v in data.items() if k not in ['units','candidates']}
    outputs['term-extraction-summary.json']=(json.dumps(summary,ensure_ascii=False,indent=2)+'\n').encode()
    for scope in ['ladder','matrix','atlas','reading','dictionary','papers']:
        units={u['id']:u for u in data['units'] if u['scope']==scope}
        candidates=[]
        for c in data['candidates']:
            occurrences=[o for o in c['occurrences'] if o[0] in units]
            if occurrences:candidates.append(dict(c,occurrences=occurrences))
        payload=dict(schema_version=1,scope=scope,units=units,candidates=candidates,extraction_hash=__import__('hashlib').sha256(OUT.read_bytes()).hexdigest())
        outputs['term-candidates-'+scope+'.json.gz']=gzip.compress((json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
    return outputs

def inputs():return [Path(__file__).resolve(),OUT,ASSETS/'term-review.js',ASSETS/'term-review.css']
