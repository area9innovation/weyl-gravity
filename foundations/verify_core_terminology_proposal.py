"""Independent structural/provenance checks, not semantic approval."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def verify():
    source=json.loads((ROOT/'foundations/editorial/core-terminology-proposal.json').read_text())
    result=json.loads((ROOT/'foundations/results/CORE_TERMINOLOGY_PROPOSAL_V1.json').read_text())
    corpus=json.loads(gzip.decompress((ROOT/'foundations/results/TERM_EXTRACTION_V1.json.gz').read_bytes()))
    units={u['id']:u for u in corpus['units']}
    dictionary=json.loads((ROOT/'foundations/editorial/dictionary.json').read_text())
    dictionary_ids={entry['id'] for entry in dictionary['terms']}
    entries=result['entries']
    assert len(entries)==150==len(source['entries'])
    assert len({e['id'] for e in entries})==150
    assert len({e['title'].casefold() for e in entries})==150
    assert result['status']==source['status']=='PROPOSED_FOR_HUMAN_REVIEW'
    assert result['scientific_claims_promoted'] is False and result['public_dictionary_changed'] is False
    assert set(source['audiences'])=={'general','physics','mathematics','specialist'}
    assert result['counts']['category']==dict(Counter(e['category'] for e in entries))
    assert result['counts']['batch']==dict(Counter(str(e['batch']) for e in entries))
    assert result['counts']['existing_dictionary_entries']==7
    assert sum(e['evidence_basis']=='reader-facing mention' for e in entries)==145
    assert result['counts']['without_mentions']==sum(not e['evidence'] for e in entries)
    for path,digest in result['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    for authored,e in zip(source['entries'],entries):
        for key,value in authored.items():assert e[key]==value,(e['id'],key)
        assert e['decision']=='PROPOSED' and e['batch'] in (1,2,3)
        assert len(e['reason'])>40 and e['source_search_phrases']
        assert e['existing_dictionary_id'] is None or e['existing_dictionary_id'] in dictionary_ids
        assert e['mentioning_units']==sum(e['scope_unit_counts'].values())
        assert len({h['scope'] for h in e['evidence']})==len(e['evidence'])
        for hit in e['evidence']:
            u=units[hit['unit_id']]
            for key in ['source','location','scope']:assert hit[key]==u[key]
            assert 0<=hit['start']<hit['end']<=len(u['text'])
            assert u['text'][hit['start']:hit['end']]==hit['matched_text']
            assert hit['matched_text'].casefold() in {p.casefold() for p in e['source_search_phrases']}
            assert hit['matched_text'] in hit['context'] and hit['context'] in u['text']
    report=(ROOT/'foundations/reports/core-terminology-proposal-v1.md').read_text()
    for e in entries:assert e['title'] in report and e['reason'] in report
    print('PASS: 150 distinct proposed concepts; priorities, dictionary references, source hashes and mention spans; no semantic certification')


if __name__=='__main__':verify()
