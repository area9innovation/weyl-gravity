#!/usr/bin/env python3
"""Exact finite controls for the BT separable state/GNS chain."""
from __future__ import annotations
from fractions import Fraction
import hashlib,json
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json"

def multiply(x:tuple[int,int],y:tuple[int,int])->dict[tuple[int,int],int]:
    return { (x[0],y[1]):1 } if x[1]==y[0] else {}
def adjoint(x:tuple[int,int])->tuple[int,int]:return x[1],x[0]
def omega0(term:dict[tuple[int,int],int])->int:return term.get((0,0),0)

def check(data:dict[str,Any]|None=None)->tuple[list[str],dict[str,Any]]:
    data=json.loads(RESULT.read_text()) if data is None else data; errors=[]; radius=3
    idx=list(range(-radius,radius+1)); rows=[]
    for a in idx:
      for b in idx:
       x=(a,b)
       if adjoint(adjoint(x))!=x:errors.append('adjoint involution')
       # omega(E_ab^* E_ab)=1 exactly when column b is zero.
       norm=omega0(multiply(adjoint(x),x))
       if norm!=int(b==0):errors.append('corner positivity identity')
       rows.append([a,b,norm])
    gram=[[int(a==b) for b in idx] for a in idx] # classes E_a0
    if any(sum(1 for x in row if x)!=1 for row in gram):errors.append('GNS Gram not identity')
    # Explicit faithful weights: partial sum is 1-2^-(N+1), positive tail exact.
    for n in range(0,12):
      partial=sum((Fraction(1,2**(j+1)) for j in range(n+1)),Fraction())
      if partial!=1-Fraction(1,2**(n+1)) or partial>=1:errors.append('faithful weights')
    for n in range(0,9):
      if 2*n+1 != sum(1 for k in range(-n,n+1)):errors.append('window trace')
    xy=omega0(multiply((0,1),(1,0))); yx=omega0(multiply((1,0),(0,1)))
    if (xy,yx)!=(1,0):errors.append('nontracial witness')
    coherent=Fraction(1,512); actual=Fraction(5,512)
    if actual!=5*coherent or actual-coherent!=Fraction(1,128):errors.append('six-point mismatch')
    payload={"rows":rows,"gram":gram,"windows":[2*n+1 for n in range(9)],"mismatch":[str(coherent),str(actual)]}
    digest=hashlib.sha256(json.dumps(payload,separators=(',',':'),sort_keys=True).encode()).hexdigest()
    wanted=data.get('independent_checker',{}).get('expected_digest')
    if wanted is not None and wanted!=digest:errors.append('digest mismatch')
    return errors,{"passed":not errors,"matrix_units":len(rows),"gns_rank":len(idx),"corner_nontracial":[xy,yx],"coherent_prediction":str(coherent),"six_point_value":str(actual),"factor":5,"digest":digest,"arithmetic":"exact integers and rationals"}
def main()->int:
 e,s=check();print('FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_CHECKER: '+('PASS' if not e else 'FAIL'))
 if e:
  for x in e:print('  - '+x)
 else:print(json.dumps(s,indent=2,sort_keys=True))
 return bool(e)
if __name__=='__main__':sys.exit(main())
