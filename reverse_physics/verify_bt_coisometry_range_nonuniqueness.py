#!/usr/bin/env python3
import argparse,json,os,sys
from fractions import Fraction
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-coisometry-range-nonuniqueness-v1.schema.json")
def f(x):return Fraction(x["numerator"],x["denominator"])
def verify(path):
 c=json.load(open(path,encoding="utf-8"));s=json.load(open(SCHEMA,encoding="utf-8"));ch={"strict_schema":not list(Draft202012Validator(s).iter_errors(c))};m=c.get("finite_krein_model",{});rows=m.get("rows",[]);ch["fixed_coisometry"]=(m.get("coisometry")=="R=[[1,0,0],[0,1,0]]" and m.get("range_projection")=="Pi=diag(1,1,0)");ch["exact_family"]=(len(rows)==4 and [f(r["pushforward_trace"]) for r in rows]==[1,Fraction(16,25),Fraction(9,25),0] and all(r["identity"] for r in rows));u=c.get("universal_identities",{});ch["defect_identity"]=("-R P (1-Pi) P R_sharp" in u.get("idempotence_defect","") and u.get("trace_overlap")=="tr(R P R_sharp)=tr(P Pi)");t=c.get("target_witness",{});ch["target_compatible_not_selected"]=(f(t.get("target",{}))==Fraction(1,48) and t.get("field")=="Q(sqrt(47))" and t.get("status")=="COMPATIBLE_NOT_SELECTED");d=c.get("disposition",{});ch["boundary"]=(d.get("right_unit_identity")=="INSUFFICIENT" and d.get("range_projection")=="NOT_PUBLISHED" and d.get("physical_nlo_probability")=="NOT_ESTABLISHED");ok=all(ch.values());[print(f"[{'PASS' if v else 'FAIL'}] {n}") for n,v in ch.items()];print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(ch.values())}/{len(ch)})");return ok
def main(argv=None):p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args(argv);return 0 if verify(a.verify) else 1
if __name__=="__main__":sys.exit(main())
