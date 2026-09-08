#!/usr/bin/env python3
"""Independent structural/provenance checks; not a semantic prose verifier."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'foundations/site'
CONTENT=ROOT/'foundations/editorial/reading-content.json'


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=[];self.editions=[];self.claims=[];self.perspectives=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'data-edition' in a:self.editions.append(a['data-edition'])
        if 'data-claim' in a:self.claims.append(a['data-claim'])
        if tag=='input' and a.get('name')=='audience':
            assert a.get('type')=='checkbox','perspective must support multiple selections'
            self.perspectives.append(a['value'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])


def verify():
    d=json.loads(CONTENT.read_text())
    assert json.loads((SITE/'editorial-record.json').read_text())==d,'editorial record drift'
    dictionary=json.loads((ROOT/'foundations/editorial/dictionary.json').read_text())
    assert json.loads((SITE/'dictionary.json').read_text())==dictionary
    assert all(set(t['definitions'])==set(d['audiences']) for t in dictionary['terms'])
    dp=Page((SITE/'dictionary.html').read_text())
    assert len(dp.ids)==len(set(dp.ids)), 'dictionary duplicate anchors'
    terms=sorted(dictionary['terms'],key=lambda t:t['label'].casefold())
    assert [i for i in dp.ids if i in {t['id'] for t in terms}]==[t['id'] for t in terms]
    for term in terms:
        if term.get('abbreviation'):assert term['expansion'] in term['definitions']['general']
        assert set(term['explanations'])==set(d['audiences'])
        for source in term['sources']:
            content=(ROOT/source['path']).read_bytes()
            assert hashlib.sha256(content).hexdigest()==source['sha256']
            assert (SITE/'sources'/source['path']).read_bytes()==content
        for perspective,blocks in term['explanations'].items():
            assert blocks and all(block['text'] for block in blocks)
    assert 'Alphabetical word list' in (SITE/'dictionary.html').read_text()
    assert set(d['audiences'])=={'general','physics','mathematics','specialist'}
    for r in d['sources'].values():
        assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],'source review stale'
        assert (SITE/'sources'/r['path']).read_bytes()==(ROOT/r['path']).read_bytes(),'source copy drift'
    repair=json.loads((ROOT/d['sources']['repair']['path']).read_text())
    assert repair['claims']['full_transfer_accepted'] is False
    assert d['claims']['gravity']['status']=='Full export currently rejected'
    assert 'not a claim that laboratory physics requires' in d['claims']['wave']['boundary']
    for name,topic in [('index.html','introduction'),('wave.html','wave')]:
        p=Page((SITE/name).read_text());t=d['topics'][topic]
        assert len(p.ids)==len(set(p.ids)),'duplicate section identity'
        assert all(s in p.ids for s in t['section_ids'])
        assert p.claims==t['claim_ids'],'separate or missing status record'
        assert set(p.editions)==set(d['audiences'])
        assert p.perspectives==list(d['audiences']),'checkbox coverage/order'
        for a in d['audiences']:
            assert [s['id'] for s in t['versions'][a]]==t['section_ids']
    for name in ['index.html','wave.html','questions.html','papers.html','atlas.html','cutoff-positivity.html','dictionary.html','term-review.html']:
        page_text=(SITE/name).read_text()
        assert page_text.count('aria-label="Main navigation"')==1
        assert 'id="perspective-menu"' in page_text and 'href="site-shell.css"' in page_text
        for href in Page((SITE/name).read_text()).links:
            url=urlsplit(href)
            if url.scheme or url.netloc:continue
            target=SITE/unquote(url.path) if url.path else SITE/name
            assert target.is_file(),(name,href)
    assert 'historical records' in (SITE/'atlas.html').read_text()
    assert 'Correction to earlier full-transfer claims' in (SITE/'papers.html').read_text()
    print('PASS: audience coverage, shared section/status identity, input hashes, local links and correction boundaries; semantic prose review remains editorial')


if __name__=='__main__':verify()
