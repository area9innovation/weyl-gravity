#!/usr/bin/env python3
"""Independent verifier for the BT canonical endpoint underdetermination witness."""
from __future__ import annotations
import argparse,hashlib,itertools,json,os,sys
from fractions import Fraction
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-canonical-endpoint-ambiguity-v1.schema.json")
def f(x):return Fraction(x["numerator"],x["denominator"])
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def add(*xs):return [[sum(x[i][j] for x in xs) for j in range(len(xs[0][0]))] for i in range(len(xs[0]))]
def scale(c,a):return [[c*x for x in r] for r in a]
def zero(a):return all(x==0 for r in a for x in r)
def direct_coefficients(u):
 n=sum(x*x for x in u);P0=[[Fraction(i==0 and j==0) for j in range(4)] for i in range(4)];P1=[[Fraction(0) for _ in range(4)] for _ in range(4)];P2=[[Fraction(0) for _ in range(4)] for _ in range(4)];P2[0][0]=-n
 for i,x in enumerate(u,1):P1[0][i]=x;P1[i][0]=x
 for i,x in enumerate(u,1):
  for j,y in enumerate(u,1):P2[i][j]=x*y
 d1=add(mm(P0,P1),mm(P1,P0),scale(-1,P1));d2=add(mm(P0,P2),mm(P2,P0),mm(P1,P1),scale(-1,P2));return n,zero(d1),zero(d2),sum(P1[i][i] for i in range(4))==0,sum(P2[i][i] for i in range(4))==0
def file_sha(path):
 h=hashlib.sha256()
 with open(os.path.join(ROOT,path),"rb") as src:
  for block in iter(lambda:src.read(65536),b""):h.update(block)
 return h.hexdigest()
def verify(path):
 with open(path,encoding="utf-8") as h:c=json.load(h)
 with open(SCHEMA,encoding="utf-8") as h:s=json.load(h)
 ch={"strict_schema":not list(Draft202012Validator(s).iter_errors(c))}
 rows=c.get("canonical_family",{}).get("rows",[]);row_ok=len(rows)==7
 for row in rows:
  u=[f(x) for x in row.get("u",[])];n,d1,d2,t1,t2=direct_coefficients(u) if len(u)==3 else (None,False,False,False,False)
  row_ok&=(n==f(row["norm_square"]) and -n==f(row["hard_P2"]) and n==f(row["endpoint_trace_P2"]) and d1 and d2 and t1 and t2 and row.get("identity") is True)
 ch["independent_rows"]=row_ok
 ch["degree_two_grid_identity"]=all(all(direct_coefficients([Fraction(x),Fraction(y),Fraction(z)])[1:]) for x,y,z in itertools.product((-1,0,1),repeat=3))
 norms={f(r["norm_square"]) for r in rows};ch["nonuniqueness"]={Fraction(0),Fraction(1),Fraction(4),Fraction(14)}.issubset(norms)
 t=c.get("target_comparison",{});ch["exact_target_witness"]=(f(t.get("required_norm_square",{"numerator":0,"denominator":1}))==Fraction(1,48) and Fraction(3,12**2)==Fraction(1,48) and t.get("status")=="COMPATIBLE_NOT_SELECTED")
 ch["input_hashes"]=all(x.get("sha256")==file_sha(x.get("path","")) for x in c.get("provenance",{}).get("inputs",[])) and len(c.get("provenance",{}).get("inputs",[]))==3
 d=c.get("disposition",{});ch["claim_boundary"]=(d.get("canonical_endpoint_family")=="THREE_PARAMETER_UNDERDETERMINATION_WITNESS" and d.get("unique_continuum_projector")=="NOT_CONSTRUCTED" and d.get("physical_nlo_probability")=="NOT_ESTABLISHED" and any("no claim is made" in x for x in c.get("assumptions",[])))
 ok=all(ch.values());[print(f"[{'PASS' if v else 'FAIL'}] {n}") for n,v in ch.items()];print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(ch.values())}/{len(ch)})");return ok
def main(argv=None):p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args(argv);return 0 if verify(a.verify) else 1
if __name__=="__main__":sys.exit(main())
