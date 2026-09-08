"""Publish one global dictionary, with optional editorial tools in the index."""
import gzip,hashlib,json
from pathlib import Path
from foundations import reading_site
from foundations.extract_editorial_terms import OUT,check_cached
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'foundations/matrix_site_v2_assets'


def generated(matrix_bytes,dictionary_page=None):
    data=check_cached(matrix_bytes)
    body='''<section id="terminology-index" class="term-review" data-no-dictionary>
<h2>Alphabetical word list</h2>
<p>Search across the whole project, or narrow the index to a page or collection. Indexed phrases without an explanation are marked <strong>Definition pending</strong>. Automatic indexing can include noisy phrases; a related dictionary entry may use a different meaning.</p>
<div class="review-filters"><label>Search terms<input id="term-search" type="search" placeholder="e.g. chiral, PRA, residual"></label><label>Used in<select id="term-scope"><option value="all">Whole project</option><option value="ladder">Strength ladder</option><option value="matrix">576 matrix cells</option><option value="atlas">Other atlas prose</option><option value="reading">Reading accounts</option><option value="dictionary">Dictionary explanations</option><option value="papers">Papers</option></select></label><label>Explanation<select id="term-coverage"><option value="all">All terms</option><option value="UNEXPLAINED_CANDIDATE">Definition pending</option><option value="VOCABULARY_MATCH_NO_EXPLANATION">External reference only</option><option value="DICTIONARY_MATCH_REVIEW_SENSE">Related dictionary entry</option></select></label><label>Order<select id="term-sort"><option value="alphabetical">Alphabetical</option><option value="frequency">Most widely used</option></select></label></div>
<p><label><input id="editing-tools" type="checkbox"> Show editing tools</label></p>
<div class="editorial-only"><label>Candidate type<select id="term-kind"><option value="term-candidate">Term candidates</option><option value="all">Terms and short claims</option><option value="explanation-unit">Short explanation tasks</option></select></label><p>All extracted candidates await contextual review. Select phrases to prepare explanations for General, Physics, Mathematics and Specialist readers.</p></div>
<p id="review-status" role="status">Loading the index…</p><div class="review-actions editorial-only"><button id="download-brief" type="button" disabled>Download drafting brief (0 selected)</button><button id="clear-selection" type="button">Clear selection</button></div>
<div id="term-results"></div><div class="review-actions"><button id="previous-terms" type="button">Previous</button><span id="term-page"></span><button id="next-terms" type="button">Next</button></div>
<noscript><p>The full dictionary entries below work without JavaScript. Download the <a href="term-candidates-all.json.gz">complete index with source contexts</a> to browse the automatic extraction offline.</p></noscript>
<details class="editorial-only"><summary>Indexing and drafting details</summary><p>The scan combines spaCy, KeyphraseVectorizers, nested phrases, abbreviations, the dictionary and APS’s PhySH vocabulary. Matches identify possible concepts, not verified meanings. Short claims are separate explanation tasks.</p><p>Downloaded briefs contain source contexts and requirements for all four perspectives. Decide whether a candidate needs an entry, a link to an existing concept, a clearer sentence or no action. Selections last for this page session and retain contexts from the source where selected. Downloads do not publish definitions.</p><p>Offsets count Unicode code points. Paper contexts use normalized blocks and retain the original starting line. Frequency is not reader difficulty.</p><p><a href="term-extraction-summary.json">Provenance and counts</a> · <a href="https://physh.org/releases">PhySH vocabulary</a></p></details>
</section>'''
    if dictionary_page is None:dictionary_page=reading_site.generated()['dictionary.html']
    page=dictionary_page.decode().replace('<!-- GLOBAL_TERMINOLOGY_INDEX -->',body)
    page=page.replace('</head>','<link rel="stylesheet" href="term-review.css"><script src="term-review.js" defer></script></head>')
    # Retain incoming links without keeping a competing destination or interface.
    redirect=reading_site.shell('Terminology has moved','<h1>Terminology &amp; dictionary</h1><p><a href="dictionary.html#terminology-index">Open the site-wide dictionary</a></p>','dictionary')
    redirect=redirect.replace('</head>','<script>location.replace("dictionary.html"+location.search+"#terminology-index");</script></head>')
    outputs={'dictionary.html':page.encode(),'term-review.html':redirect.encode()}
    for name in ['term-review.js','term-review.css']:outputs[name]=(ASSETS/name).read_bytes()
    summary={k:v for k,v in data.items() if k not in ['units','candidates']}
    outputs['term-extraction-summary.json']=(json.dumps(summary,ensure_ascii=False,indent=2)+'\n').encode()
    extraction_hash=hashlib.sha256(OUT.read_bytes()).hexdigest()
    for scope in ['all','ladder','matrix','atlas','reading','dictionary','papers']:
        units={u['id']:u for u in data['units'] if scope=='all' or u['scope']==scope}
        candidates=[]
        for c in data['candidates']:
            occurrences=[o for o in c['occurrences'] if o[0] in units]
            if occurrences:candidates.append(dict(c,occurrences=occurrences))
        payload=dict(schema_version=1,scope=scope,units=units,candidates=candidates,extraction_hash=extraction_hash)
        outputs['term-candidates-'+scope+'.json.gz']=gzip.compress((json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0)
    return outputs


def inputs():return [Path(__file__).resolve(),OUT,ASSETS/'term-review.js',ASSETS/'term-review.css']
