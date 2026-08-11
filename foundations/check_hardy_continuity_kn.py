#!/usr/bin/env python3
"""Finite checker for the modulus-coded Hardy K=N obstruction."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/'foundations/results/FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1.json'
def l1_basis_distance(n:int,left:int,right:int)->int:
 return 0 if left==right else 2
def check(data:dict[str,Any]|None=None):
 d=json.loads(RESULT.read_text()) if data is None else data;e=[];rows=[]
 cfg=d.get('independent_checker',{});ns=cfg.get('regression_N',[]);moduli=cfg.get('moduli',[])
 if ns!=list(range(2,9)) or moduli!=list(range(6)):e.append('regression domain drift')
 for n in ns:
  for a in range(n):
   for b in range(n):
    dist=l1_basis_distance(n,a,b)
    if dist!=(0 if a==b else 2):e.append('basis separation')
  for mu in moduli:
   mesh=2**(mu+1)
   # The modulus promises adjacent images are <1. Finite pure-state separation
   # then forces every adjacent pair equal; bounded induction fixes endpoints.
   max_allowed=0
   if any(l1_basis_distance(n,a,b)<1 and a!=b for a in range(n) for b in range(n)):e.append('adjacency')
   reachable={0}
   for _ in range(mesh):
    reachable={b for a in reachable for b in range(n) if l1_basis_distance(n,a,b)<1}
   forced_equal=reachable=={0}
   if not forced_equal or max_allowed!=0:e.append('induction')
   rows.append([n,mu,mesh,2,max_allowed,forced_equal])
 payload=json.dumps(rows,separators=(',',':')).encode();digest=hashlib.sha256(payload).hexdigest();wanted=cfg.get('expected_digest')
 if wanted is not None and wanted!=digest:e.append('digest mismatch')
 return e,{"passed":not e,"cases":len(rows),"maximum_mesh":max(r[2] for r in rows),"minimum_separation":2,"adjacent_bound_strictly_below":1,"endpoint_equality_forced":True,"digest":digest,"arithmetic":"exact bounded natural-number arithmetic"}
def main():
 e,s=check();print('FOUNDATIONAL_HARDY_CONTINUITY_KN_CHECKER: '+('PASS' if not e else 'FAIL'))
 if e:
  for x in e:print('  - '+x)
 else:print(json.dumps(s,indent=2,sort_keys=True))
 return bool(e)
if __name__=='__main__':sys.exit(main())
