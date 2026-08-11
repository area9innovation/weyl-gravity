#!/usr/bin/env python3
import argparse,hashlib,itertools,json,os
from fractions import Fraction
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics/schema/reverse-physics-bt-inclusive-physical-coefficient-v1.schema.json")
def load(p):
 with open(p) as f:return json.load(f)
def q(x):return Fraction(x["numerator"],x["denominator"])
def mat(a):return [[q(x) for x in r] for r in a]
def tp(a):return [list(r) for r in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in tp(b)] for r in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def tr(a):return sum(a[i][i] for i in range(len(a)))
def sha(p):
 h=hashlib.sha256()
 with open(os.path.join(ROOT,p),"rb") as f:
  for b in iter(lambda:f.read(65536),b""):h.update(b)
 return h.hexdigest()
def verify(c):
 checks={};errs=list(Draft202012Validator(load(SCHEMA)).iter_errors(c));checks["schema"]=not errs
 exact=True
 for row in c.get("orthogonal_detector_lemma",{}).get("fixtures",[]):
  a0,a1,a2=mat(row["A0"]),mat(row["A1"]),mat(row["A2"]);c2=add(add(mm(tp(a0),a2),mm(tp(a2),a0)),mm(tp(a1),a1));exact=exact and all(not any(r) for r in a0) and c2==mm(tp(a1),a1)==mat(row["Born_order_two"])
 checks["orthogonal_lemma"]=exact
 g=[[0,1],[1,0]];h0=[[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]];kern=True
 for row in c.get("complete_signed_kernel",{}).get("fixtures",[]):
  s1,s2=row["signs"];e1,e2=row["e1"],row["e2"];k=[[Fraction(s1*e1+s2*e2,2*e1*e2),0,0,0],[0,Fraction(-s2,2*e1),Fraction(-s1,2*e2),0]];h=[[4*e1*e2*x for x in r] for r in h0];gram=mm(mm(k,h),tp(k));kern=kern and gram==mat(row["parent_gram"]) and tr(mm(g,gram))==q(row["raised_trace"])==0
 checks["kernel_trace"]=kern
 masks=c.get("inclusive_detector_limit",{}).get("finite_cell_masks",[]);checks["detector_net"]=len(masks)==64 and {x["mask"] for x in masks}=={"".join(map(str,m)) for m in itertools.product((0,1),repeat=6)} and all(q(x["coefficient"])==0 for x in masks)
 phys=c.get("physical_coefficient",{});disp=c.get("disposition",{});checks["physical_boundary"]=q(phys.get("leading_real_collinear_generalized_Born_coefficient",{}))==0 and phys.get("status")=="PHYSICAL_REAL_COLLINEAR_COEFFICIENT_COMPUTED" and phys.get("complete_NLO_probability")=="NOT_COMPUTED" and disp.get("Eq19_all_orders")=="NOT_PROVED"
 inputs=c.get("provenance",{}).get("inputs",[]);checks["hashes"]=len(inputs)==6 and all(x["sha256"]==sha(x["path"]) for x in inputs)
 led=c.get("checks",{});checks["ledger"]=led.get("passed")==led.get("total")==20 and led.get("failures")==[] and all(led.get("details",{}).values())
 if errs:
  for e in errs:print("schema",list(e.path),e.message)
 bad=[k for k,v in checks.items() if not v]
 if bad:print("BT INCLUSIVE PHYSICAL COEFFICIENT VERIFY: FAIL",*bad,sep="\n  ");return False,checks
 return True,checks
def main():
 p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args();ok,c=verify(load(a.verify));
 if not ok:return 1
 print(f"BT INCLUSIVE PHYSICAL COEFFICIENT VERIFY: ALL PASS ({sum(c.values())}/{len(c)})");return 0
if __name__=="__main__":raise SystemExit(main())
