#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction
import hashlib,json
from math import factorial
from pathlib import Path
import sys
from typing import Any
ROOT=Path(__file__).resolve().parents[1];RESULT=ROOT/'foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json'
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def add(a,b):return [[a[i][j]+b[i][j] for j in range(2)] for i in range(2)]
def scale(c,a):return [[c*x for x in row] for row in a]
I=[[Fraction(1),Fraction(0)],[Fraction(0),Fraction(1)]]
def power(a,n):
 r=I
 for _ in range(n):r=mul(r,a)
 return r
def check(data:dict[str,Any]|None=None):
 d=json.loads(RESULT.read_text()) if data is None else data;e=[];rows=[]
 G=[[Fraction(1),Fraction(1,2)],[Fraction(0),Fraction(2)]];N=[[Fraction(0),Fraction(1)],[Fraction(1,3),Fraction(0)]];T=mul(G,N);U=mul(N,G)
 for m in d.get('independent_checker',{}).get('truncations',[]):
  sol=[[Fraction(0),Fraction(0)],[Fraction(0),Fraction(0)]];src=[[Fraction(0),Fraction(0)],[Fraction(0),Fraction(0)]]
  for k in range(m+1):sol=add(sol,scale((-1)**k,power(T,k)));src=add(src,scale((-1)**k,power(U,k)))
  rem=scale((-1)**m,power(T,m+1));rems=scale((-1)**m,power(U,m+1))
  if mul(add(I,T),sol)!=add(I,rem):e.append('solution remainder')
  if mul(add(I,U),src)!=add(I,rems):e.append('source remainder')
  if mul(sol,G)!=mul(G,src):e.append('push through')
  c=Fraction(3,2);terms=[c**n/Fraction(factorial(n)) for n in range(m+1)]
  for n in range(len(terms)-1):
   if terms[n+1]/terms[n]!=c/Fraction(n+1):e.append('factorial ratio')
  rows.append([m,[[str(x) for x in z] for z in sol],[[str(x) for x in z] for z in src],[str(x) for x in terms]])
 digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest();wanted=d.get('independent_checker',{}).get('expected_digest')
 if wanted is not None and wanted!=digest:e.append('digest')
 return e,{"passed":not e,"truncations":len(rows),"noncommuting":mul(G,N)!=mul(N,G),"push_through_all":not any(x=='push through' for x in e),"digest":digest,"arithmetic":"exact rational matrices"}
def main():
 e,s=check();print('FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_CHECKER: '+('PASS' if not e else 'FAIL'))
 if e:
  for x in e:print('  - '+x)
 else:print(json.dumps(s,indent=2,sort_keys=True))
 return bool(e)
if __name__=='__main__':sys.exit(main())
