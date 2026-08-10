#!/usr/bin/env python3
"""Independent verifier for the full off-resonant BT projector obstruction."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from fractions import Fraction as F
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_FULL_OFF_RESONANT_PROJECTOR_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-full-off-resonant-projector-v1.schema.json")
def frac(x):return F(x["numerator"],x["denominator"])
class QI(tuple):
 def __new__(cls,r=0,i=0):return tuple.__new__(cls,(F(r),F(i)))
 def __bool__(a):return bool(a[0] or a[1])
 def __add__(a,b):
  if isinstance(b,P):return NotImplemented
  b=qi(b);return QI(a[0]+b[0],a[1]+b[1])
 __radd__=__add__;__neg__=lambda a:QI(-a[0],-a[1]);__sub__=lambda a,b:a+(-qi(b));__rsub__=lambda a,b:qi(b)-a
 def __mul__(a,b):
  if isinstance(b,P):return NotImplemented
  b=qi(b);return QI(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
 __rmul__=__mul__
def qi(x):return x if isinstance(x,QI) else QI(x)
J=QI(0,1)
def comp(x):return QI(frac(x["real"]),frac(x["imag"]))
def sha(path):
 h=hashlib.sha256()
 with open(os.path.join(ROOT,path),"rb") as f:
  for b in iter(lambda:f.read(65536),b""):h.update(b)
 return h.hexdigest()
class P(dict):
 def __add__(a,b):
  b=pol(b);r=P(a)
  for m,c in b.items():r[m]=r.get(m,QI())+c
  return P({m:c for m,c in r.items() if c})
 __radd__=__add__;__neg__=lambda a:P({m:-c for m,c in a.items()});__sub__=lambda a,b:a+(-pol(b));__rsub__=lambda a,b:pol(b)-a
 def __mul__(a,b):
  b=pol(b);r=P()
  for m,c in a.items():
    for n,q in b.items():r[(m[0]+n[0],m[1]+n[1])]=r.get((m[0]+n[0],m[1]+n[1]),QI())+c*q
  return P({m:c for m,c in r.items() if c})
 __rmul__=__mul__
 def dt(a):return P({(r,t-1):c*t for (r,t),c in a.items() if t})
def pol(x):return x if isinstance(x,P) else P({(0,0):qi(x)}) if x else P()
def derive(e1,e2,d):
 # Independent two-variable algebra: powers are (soft-chart r,time); callers
 # pass Laurent polynomials for e1,d and a constant e2.
 S=e1+e2;Ep=S-d;om=lambda q:J*q.dt()+(Ep+S)*q;box=lambda q:q.dt().dt()-2*J*S*q.dt()+(Ep*Ep-S*S)*q
 t=P({(0,1):QI(1)});m1={"a2":pol(1),"a1":1+2*J*e1*t};m2={"a2":pol(1),"a1":1+2*J*e2*t};b1={"a2":pol(0),"a1":4*e1*e1};b2={"a2":pol(0),"a1":4*e2*e2};AO={};AU={}
 for a in m1:
  for b in m2:
   q=m1[a]*m2[b];AO[a,b]=om(q);AU[a,b]=om(box(q)-2*(m1[a]*b2[b]+b1[a]*m2[b]))
 i1={"a2":{"O":4*e1*e1,"U":-2*J*e1*t},"a1":{"O":pol(0),"U":pol(1)}};i2={"a2":{"O":4*e2*e2,"U":-2*J*e2*t},"a1":{"O":pol(0),"U":pol(1)}}
 def trans(A):
  out={}
  for L in("O","U"):
   for R in("O","U"):
    q=pol(0)
    for (a,b),v in A.items():q+=v*i1[a][L]*i2[b][R]
    out[L,R]=F(1,64)*(e1**-3 if isinstance(e1,F) else P({(-3,0):QI(1)}))*F(e2)**-3*q
  return out
 O,U=trans(AO),trans(AU);rows={"O":O,"U":U};opp={"O":"U","U":"O"};G={}
 for L in rows:
  for R in rows:
   q=pol(0)
   for a in("O","U"):
    for b in("O","U"):q+=rows[L][a,b]*rows[R][opp[a],opp[b]]
   G[L,R]=4*e1*e2*q
 return O,U,G
def const_value(q):return q.get((0,0),QI()) if all(t==0 for _,t in q) else None
def verify(path):
 with open(path,encoding="utf-8") as h:c=json.load(h)
 with open(SCHEMA,encoding="utf-8") as h:s=json.load(h)
 ch={"strict_schema":not list(Draft202012Validator(s).iter_errors(c))};rows=c.get("off_resonant_kernel",{}).get("samples",[]);sample_ok=len(rows)==3
 for row in rows:
  e1,e2,d=frac(row["e1"]),frac(row["e2"]),frac(row["deficit"]);O,U,G=derive(e1,e2,d);sample_ok&=(const_value(O["U","U"])==comp(row["delta_b_Omega_UpsilonUpsilon"]) and const_value(U["O","O"])==comp(row["delta_b_Upsilon_OmegaOmega"]) and const_value(G["O","U"])==comp(row["gram_cross"]))
 ch["independent_samples"]=sample_ok
 rays=[];ray_data=[]
 for alpha in (F(0),F(1,2),F(1),F(3,2),F(2)):
  r=P({(1,0):QI(1)});O,U,G=derive(r,F(1),alpha*r);cross=G["O","U"];power=min(k[0] for k in cross);residue=cross.get((-3,0));ray_data.append((power,residue));rays.append(power==-3 and residue==QI(F(-1,2)))
 ch["five_ray_soft_residue"]=all(rays)
 exchange=const_value(derive(F(2),F(3),F(1,2))[2]["O","U"])==const_value(derive(F(3),F(2),F(1,2))[2]["O","U"])
 measured_power=ray_data[0][0]+2;radial_sd=-measured_power;response=-ray_data[0][1]
 ch["measure_reduction"]=(all(x==ray_data[0] for x in ray_data) and measured_power==-1 and radial_sd-1==0 and response==QI(F(1,2)) and exchange and c.get("soft_blowup",{}).get("scaling_degree")==radial_sd and c.get("soft_blowup",{}).get("rescaling")=="I_(c*epsilon)-I_epsilon=+(1/2) log(c)")
 ch["input_hashes"]=len(c.get("provenance",{}).get("inputs",[]))==3 and all(x.get("sha256")==sha(x.get("path","")) for x in c.get("provenance",{}).get("inputs",[]))
 d=c.get("disposition",{});ch["claim_boundary"]=(d.get("full_off_resonant_kernel")=="DERIVED" and d.get("ordinary_parent_projector_composition")=="LOGARITHMICALLY_NON_TRACE_CLASS" and d.get("one_over_48")=="NOT_DERIVED" and d.get("physical_nlo_probability")=="NOT_ESTABLISHED")
 ok=all(ch.values());[print(f"[{'PASS' if v else 'FAIL'}] {n}") for n,v in ch.items()];print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(ch.values())}/{len(ch)})");return ok
def main(argv=None):p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args(argv);return 0 if verify(a.verify) else 1
if __name__=="__main__":sys.exit(main())
