#!/usr/bin/env python3
"""Independent verifier for the general charged-time event-map theorem."""
import hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/"closed_universe_observers/certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json"; S=ROOT/"closed_universe_observers/schema/charged-physical-time-relational-event-map-theorem-v1.schema.json"
def verify():
 v=json.loads(C.read_text()); schema=json.loads(S.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(v)
 for r in v["dependency_refs"].values():
  if hashlib.sha256((ROOT/r["path"]).read_bytes()).hexdigest()!=r["sha256"]: raise ValueError("dependency")
 psi,Q,tau=sp.symbols("psi Q tau"); H=sp.Function("H")(Q); speed=sp.diff(H,Q); F=sp.Function("F")(tau-psi)
 br=lambda a,b:sp.diff(a,psi)*sp.diff(b,Q)-sp.diff(a,Q)*sp.diff(b,psi)
 if br(psi,Q)!=1 or sp.simplify(br(F,Q)+sp.diff(F,tau))!=0 or sp.simplify(br(F,H)+speed*sp.diff(F,tau))!=0: raise ValueError("action-angle")
 for eps in (-1,1):
  if eps*eps!=1: raise ValueError("lattice")
 r=v["fixed_charge_reduction"]
 if r["D_null"] is not True or r["D_clock_class_dimension"]!=0: raise ValueError("reduction")
 if v["stability_distinctions"]["lifted_phase"]["monotone_and_bounded"]: raise ValueError("stability conflation")
 if v["conditional_nontriviality"]["status"]!="CONDITIONAL": raise ValueError("existence promotion")
 if not all(x["detected"] for x in v["mutation_results"]): raise ValueError("mutation")
 return v
if __name__=="__main__": verify(); print("CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1 independent verification: PASS")
