"""Reproduce the English terminology snapshot from the pinned CC0 PhySH release."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'foundations/editorial/vocabularies/physh-2.8.0.json.gz'
OUT=ROOT/'foundations/editorial/vocabularies/physh-2.8.0-terms.json'
EXPECTED='4030abdc5ab09afbe67e4f3f8b3aa840f570e5c3a2bbe7e7af9bd0c6692171bf'
def generate():
    raw=RAW.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('PhySH input hash mismatch')
    terms=[];skos='http://www.w3.org/2004/02/skos/core#'
    for node in json.loads(gzip.decompress(raw)):
        if skos+'Concept' not in node.get('@type',[]):continue
        labels=[v['@value'] for v in node.get(skos+'prefLabel',[]) if v.get('@language')=='en']
        if not labels:continue
        aliases=sorted({v['@value'] for key in ['prefLabel','altLabel'] for v in node.get(skos+key,[]) if v.get('@language')=='en'})
        terms.append(dict(id=node['@id'],label=labels[0],aliases=aliases))
    result=dict(schema_version=1,provider='APS PhySH',version='2.8.0',license='CC0-1.0',source_url='https://raw.githubusercontent.com/physh-org/PhySH/v2.8.0/physh.json.gz',source_sha256=EXPECTED,meaning='Vocabulary matching evidence, not audience definitions or verified contextual sense.',terms=sorted(terms,key=lambda t:t['id']))
    return (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();content=generate()
    if args.check:assert OUT.read_bytes()==content,'vocabulary drift'
    else:OUT.write_bytes(content)
    print('PASS: pinned PhySH vocabulary')
