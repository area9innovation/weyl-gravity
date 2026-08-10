#!/usr/bin/env python3
"""Independent verifier for the BT endpoint-extension ambiguity."""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from fractions import Fraction
from jsonschema import Draft202012Validator

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json")
SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-endpoint-extension-ambiguity-v1.schema.json")

def frac(x): return Fraction(x["numerator"],x["denominator"])
def sha(path):
 d=hashlib.sha256()
 with open(os.path.join(ROOT,path),"rb") as h:
  for b in iter(lambda:h.read(65536),b""): d.update(b)
 return d.hexdigest()
def verify(path):
 with open(path,encoding="utf-8") as h: c=json.load(h)
 with open(SCHEMA,encoding="utf-8") as h: s=json.load(h)
 errors=list(Draft202012Validator(s).iter_errors(c)); checks={"strict_schema":not errors}
 shape=c.get("interior_kernel",{})
 checks["partial_fraction"]=(shape.get("partial_fraction")=="h(z)=-(1/2)*(z^-3+(1-z)^-3)" and all(-(1-3*z+3*z*z)/(2*z**3*(1-z)**3)==-Fraction(1,2)*(z**-3+(1-z)**-3) for z in (Fraction(1,4),Fraction(3,10),Fraction(4,9))))
 ext=c.get("extension_classification",{}); target=c.get("target_test",{})
 checks["two_extensions_disagree"]=(frac(ext.get("triple_plus_on_one",{}))==0 and frac(ext.get("symmetric_cutoff_fp_on_one",{}))==Fraction(1,2))
 matrix=[[frac(x) for x in row] for row in ext.get("jet_action_matrix",[])]
 if len(matrix)==3 and all(len(row)==3 for row in matrix):
  a=matrix; det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
 else: det=Fraction(0)
 checks["three_independent_jets"]=(det!=0 and det==frac(ext.get("jet_matrix_determinant",{})))
 checks["target_is_fitted_not_derived"]=(frac(target.get("required_gram",{}))==Fraction(1,48) and frac(target.get("constant_ambiguity_action",{}))==2 and frac(target.get("coefficient_that_fits_target_from_plus_base",{}))==Fraction(1,96))
 disp=c.get("disposition",{}); checks["claim_boundary"]=(disp.get("one_over_48_from_current_data")=="UNDERDETERMINED" and disp.get("oscillatory_and_vacuum_matching_condition")=="NOT_COMPUTED" and disp.get("physical_nlo_probability")=="NOT_ESTABLISHED")
 inputs=c.get("provenance",{}).get("inputs",[]); checks["hashes"]=(len(inputs)==2 and all(x.get("sha256")==sha(x.get("path","")) for x in inputs))
 ok=all(checks.values())
 for n,v in checks.items(): print(f"[{'PASS' if v else 'FAIL'}] {n}")
 print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)})"); return ok
def main(argv=None):
 p=argparse.ArgumentParser(); p.add_argument("--verify",default=CERT); a=p.parse_args(argv); return 0 if verify(a.verify) else 1
if __name__=="__main__": sys.exit(main())
