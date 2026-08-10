#!/usr/bin/env python3
"""Independent verifier for BT perturbative coisometry rigidity."""
from __future__ import annotations
import argparse,json,os,sys
from fractions import Fraction
from jsonschema import Draft202012Validator
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json");SCHEMA=os.path.join(ROOT,"reverse_physics","schema","reverse-physics-bt-perturbative-coisometry-rigidity-v1.schema.json")
def f(x):return Fraction(x["numerator"],x["denominator"])
def verify(path):
 with open(path,encoding="utf-8") as h:c=json.load(h)
 with open(SCHEMA,encoding="utf-8") as h:s=json.load(h)
 ch={"strict_schema":not list(Draft202012Validator(s).iter_errors(c))};rows=c.get("free_CCR_gate",{}).get("rows",[]);ch["independent_CCR"]=(len(rows)==4 and all(f(r["a_cross_commutator"])/f(r["Omega_denominator"])==f(r["BT_cross_CCR"])==2*f(r["energy"]) and r["identity"] for r in rows));rec=c.get("formal_projection_rigidity",{}).get("mutation_fixture_rows",[]);ch["independent_recursion"]=(len(rec)==12 and all(f(r["Pi_degree"])==0 and f(r["projection_coefficient"])==0 for r in rec));sup=c.get("supersession",{});ch["scope_correction"]=(sup.get("status")=="SCOPE_RESTRICTED_TO_NONPERTURBATIVE_OR_DISCONNECTED_BRANCHES" and "cannot model" in sup.get("superseded_application",""));d=c.get("disposition",{});ch["boundary"]=(d.get("formal_perturbative_range_projection")=="IDENTITY_TO_ALL_ORDERS" and d.get("canonical_endpoint_extension")=="NOT_CONSTRUCTED" and d.get("physical_nlo_probability")=="NOT_ESTABLISHED");ok=all(ch.values());[print(f"[{'PASS' if v else 'FAIL'}] {n}") for n,v in ch.items()];print(f"RESULT: {'PASS' if ok else 'FAIL'} ({sum(ch.values())}/{len(ch)})");return ok
def main(argv=None):p=argparse.ArgumentParser();p.add_argument("--verify",default=CERT);a=p.parse_args(argv);return 0 if verify(a.verify) else 1
if __name__=="__main__":sys.exit(main())
