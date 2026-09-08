#!/usr/bin/env python3
"""Fail closed on direct nilpotency prerequisites; a pass is not a full import gate."""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GRAPH=ROOT/'quantum-weyl/classical_import/certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json'
BASIS=ROOT/'quantum-weyl/classical_import/certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json'


def check(graph, basis):
    blocks=defaultdict(set)
    for r in basis['component_basis']['rows']: blocks[r['block']].add(r['index'])
    tables=graph['graph_q1_serialization']['tables']
    if len(tables)!=27: raise ValueError('unsupported graph inventory; full revalidation required')
    q=defaultdict(Fraction)
    for table in tables:
        for c in table['coefficients']:
            for i,j,v in c['entries']: q[tuple(c['multiindex']),i,j]+=Fraction(v)
    q={k:v for k,v in q.items() if v}
    results={}
    for name,target,source in [('metric','ENDPOINT_M','CONE_Y_ID_SHARP'),('trace','CONE_Y_ID','ENDPOINT_E')]:
        left=[(k,v) for k,v in q.items() if k[1] in blocks[target]]
        right=[(k,v) for k,v in q.items() if k[2] in blocks[source]]
        out=defaultdict(Fraction)
        for (m,i,k),a in left:
            for (n,h,j),b in right:
                if k!=h: continue
                if any(m) and any(n): raise ValueError('unproved covariant derivative composition')
                out[tuple(x+y for x,y in zip(m,n)),i,j]+=a*b
        results[name]=[[list(m),i,j,str(v)] for (m,i,j),v in sorted(out.items()) if v]
    passed=not any(results.values())
    return {'dependency_tags':['LOCAL-ALGEBRAIC'],
            'status':'SELECTED_PREREQUISITES_PASS_FULL_GATE_REQUIRED' if passed else 'FAIL_CLOSED',
            'selected_nilpotency_prerequisites_pass':passed,'full_transfer_accepted':False,
            'defect_counts':{name:len(rows) for name,rows in results.items()},
            'witnesses':{name:rows[:1] for name,rows in results.items()}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--graph',type=Path,default=GRAPH)
    args=parser.parse_args()
    try:
        result=check(json.loads(args.graph.read_text()),json.loads(BASIS.read_text()))
        result['inputs']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (args.graph,BASIS)]
    except (OSError,ValueError,KeyError,TypeError) as error:
        result={'status':'FAIL_CLOSED','full_transfer_accepted':False,'error':str(error)}
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result.get('selected_nilpotency_prerequisites_pass') else 1)
