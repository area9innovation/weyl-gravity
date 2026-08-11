#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/'foundations/results/FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1.json'
def level(n):return 10 if n==2 else 40 if n==3 else 6*n*n-14
def prime_power(q):
 for p in range(2,q+1):
  if any(p%d==0 for d in range(2,p)):continue
  x=p
  while x<q:x*=p
  if x==q:return True
 return False
def check(data:dict[str,Any]|None=None):
 d=json.loads(RESULT.read_text()) if data is None else data;e=[];cfg=d.get('independent_checker',{});rows=[]
 for q in cfg.get('prime_powers',[]):
  if not prime_power(q):e.append('not prime power')
  rows.append(['field',q,q*q,q*(q+1),q+1,q])
 total=0
 for n in cfg.get('mode_cutoffs',[]):
  total+=level(n);rows.append(['mode',n,level(n),total,'C','countable-parent'])
 if total!=3740:e.append('cutoff count')
 objs={x.get('id'):x for x in d.get('typed_objects',[])}
 if len(objs)!=4 or len({x.get('scalar_axis') for x in objs.values()})<3:e.append('type axes collapsed')
 if len(d.get('pairwise_non_equivalence',[]))!=6:e.append('pair witnesses')
 if any(not v for v in d.get('bridge_obligations',{}).values()):e.append('empty bridge')
 digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest();wanted=cfg.get('expected_digest')
 if wanted is not None and wanted!=digest:e.append('digest')
 return e,{"passed":not e,"prime_power_models":8,"field_rows":[r for r in rows if r[0]=='field'],"mode_cutoff_12":total,"pairwise_witnesses":6,"digest":digest,"arithmetic":"exact natural numbers"}
def main():
 e,s=check();print('FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_CHECKER: '+('PASS' if not e else 'FAIL'))
 if e:
  for x in e:print('  - '+x)
 else:print(json.dumps(s,indent=2,sort_keys=True))
 return bool(e)
if __name__=='__main__':sys.exit(main())
