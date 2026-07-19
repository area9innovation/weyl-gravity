#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from fractions import Fraction
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.schema.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(x): return sp.sympify(x,locals={"sqrt":sp.sqrt,"pi":sp.pi})

def verify():
 v=json.loads(CERT.read_text()); s=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(v); assert v["schema_sha256"]==sha(SCHEMA)
 pp=ROOT/v["provenance"]["parent"]; assert v["provenance"]["parent_sha256"]==sha(pp); parent=json.loads(pp.read_text())
 fibres=[f for f in parent["physical_fibres"] if f["candidate_index"] in (1,16)]; assert [f["candidate_index"] for f in fibres]==[1,16]
 for f,item in zip(fibres,v["decompositions"],strict=True):
  assert item["candidate_index"]==f["candidate_index"] and item["fibre_id"]==f["fibre_id"]
  expected={t["first_parity"][0]+t["second_parity"][0]:[parse(x[0][0]) for x in t["coefficient_matrices"]] for q in f["target_equations"] for t in q["terms"]}
  c={k:[parse(x) for x in z] for k,z in item["coefficients"].items()}; assert c==expected
  for j in range(2):
   assert (c["pp"][j]+3*c["aa"][j]).equals(0) and (c["pa"][j]+c["ap"][j]).equals(0)
  indexed={f"same_{j}":c["aa"][j] for j in range(2)}|{f"cross_{j}":c["ap"][j] for j in range(2)}
  for k,x in indexed.items():
   w=item["nonzero_intervals"][k]; lo,hi=Fraction(w["lower"]),Fraction(w["upper"]); assert w["excludes_zero"] and (lo>0 or hi<0) and sp.N(lo,80)<sp.N(x,80)<sp.N(hi,80)
  assert (item["zero_variety"]["ambient_dimension_over_C"],item["zero_variety"]["dimension_over_C"],item["zero_variety"]["irreducible_components_over_C"])==(20,12,1)
 x11,x12,x21,x22=sp.symbols("x11 x12 x21 x22"); same=x11-3*x22; cross=x12-x21
 assert sp.expand((x11+sp.sqrt(3)*x12-sp.sqrt(3)*x21-3*x22)-(same+sp.sqrt(3)*cross))==0
 assert sp.expand((x11-sp.sqrt(3)*x12+sp.sqrt(3)*x21-3*x22)-(same-sp.sqrt(3)*cross))==0
 assert v["target_reduction"]["factorization"]==["T1(A_a-sqrt(3)A_p,B_a+sqrt(3)B_p)=0","T1(A_a+sqrt(3)A_p,B_a-sqrt(3)B_p)=0"]
 cl=v["classification"]; assert cl["both_target_doublet_L3_zero_varieties_classified"] and cl["all_m_irreducible_decomposition_classified"] and cl["target_rows_reduced_exactly"]
 assert not any(cl[k] for k in ["other_nineteen_parent_fibre_zero_varieties_classified","same_fibre_quadratic_sources_classified","taub_common_zero_intersection_classified","complete_two_fibre_tangent_cone_classified","smooth_secular_classified","causal_or_quantum_claim"])
if __name__=="__main__": verify(); print("EINSTEIN_MAXWELL_WEYL_ELL2_TWO_ABS_MOMENTUM_TARGET_DOUBLET_L3_ZERO_VARIETIES independent verification: PASS")
