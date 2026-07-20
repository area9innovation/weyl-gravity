#!/usr/bin/env python3
"""Independent character replay of the order-one invariant lift ansatz."""

from collections import Counter
import hashlib, json
from itertools import combinations_with_replacement
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/'d_quotient_classical/certificates/EINSTEIN_WEYL_RELATIVE_ORDER_ONE_INVARIANT_ANSATZ_V1.json'
SCHEMA=ROOT/'d_quotient_classical/schema/relative-order-one-invariant-ansatz-v1.schema.json'

def main():
    value=json.loads(CERT.read_text()); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value)
    for artifact in value['dependencies'].values():
        path=ROOT/artifact['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']: raise AssertionError(f'dependency drift: {path}')
    tangent=[0,0,1,-1]
    reps=[({0:8,1:5,-1:5,2:1,-2:1},{0:6,1:3,-1:3,2:1,-2:1}),({0:3,1:1,-1:1},{0:4,1:1,-1:1})]
    dimensions=[[],[]]
    sym=[]
    for order in range(3):
        weights=Counter(sum(tangent[i] for i in monomial) for monomial in combinations_with_replacement(range(4),order)); sym.append(weights)
        for index,(source,target) in enumerate(reps):
            domain=Counter()
            for a,m in source.items():
                for b,n in weights.items(): domain[a+b]+=m*n
            dimensions[index].append(sum(domain[w]*n for w,n in target.items()))
    if dimensions != [[80,284,626],[14,42,86]]: raise AssertionError(dimensions)
    recorded=value['homogeneous_symbol_dimensions']['symmetric_covector_weights']
    if [{int(k):v for k,v in item['weights'].items()} for item in recorded] != [dict(x) for x in sym]: raise AssertionError('symmetric-power characters drifted')
    if value['order_one_solver_contract']['total_free_symbol_and_lower_coefficients'] != 80+284+42: raise AssertionError('solver count drifted')
    print(json.dumps({'status':'PASS','A1_dimensions':dimensions[0],'A2_dimensions':dimensions[1],'order_one_free_coefficients':406,'current_order_two_jets_required':True},indent=2,sort_keys=True))

if __name__=='__main__': main()
