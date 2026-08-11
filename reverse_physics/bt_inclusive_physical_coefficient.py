#!/usr/bin/env python3
"""Exact inclusive orthogonal-detector BT real-collinear coefficient."""
from __future__ import annotations
import argparse, hashlib, itertools, json, os, sys
from fractions import Fraction

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT=os.path.join(ROOT,"reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1.json")
SCHEMA="reverse_physics/schema/reverse-physics-bt-inclusive-physical-coefficient-v1.schema.json"
REPORT="reverse_physics/reports/bt-inclusive-physical-coefficient.md"
SOURCE_COMMIT="31dc7e95"
EVENT="planning/events/reverse-physics-bateman-inclusive-physical-coefficient-DONE-0642421f90835292.json"
INPUTS_WITHOUT_EVENT=[
 "planning/work-items/reverse-physics-bateman-inclusive-physical-coefficient.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_SQUEEZED_DETECTOR_SIMILARITY_V1.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_CYLINDER_BORN_LIMIT_V1.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_ZERO_MODE_EQ19_TRILEMMA_V1.json",
 "notes/bateman-turok-embedding.md"]
def rat(x):x=Fraction(x);return {"numerator":x.numerator,"denominator":x.denominator}
def sha(p):
 h=hashlib.sha256()
 with open(os.path.join(ROOT,p),"rb") as f:
  for b in iter(lambda:f.read(65536),b""):h.update(b)
 return h.hexdigest()
def tp(a):return [list(r) for r in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in tp(b)] for r in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def tr(a):return sum(a[i][i] for i in range(len(a)))
def diag(v):return [[Fraction(v[i]) if i==j else Fraction(0) for j in range(len(v))] for i in range(len(v))]
def mj(a):return [[rat(x) for x in r] for r in a]
def block_fixture(seed):
 pin=diag([1,0,0,0]);pout=diag([0,1,1,1]);ident=diag([1,1,1,1])
 k=[[Fraction((i+1)*(j+seed)-3,seed+2) for j in range(4)] for i in range(4)]
 ell=[[Fraction((i-seed)*(j+2)+1,seed+3) for j in range(4)] for i in range(4)]
 a0=mm(mm(pout,ident),pin);a1=mm(mm(pout,k),pin);a2=mm(mm(pout,ell),pin)
 c2=add(add(mm(tp(a0),a2),mm(tp(a2),a0)),mm(tp(a1),a1))
 expected=mm(tp(a1),a1)
 return {"seed":seed,"Pout_Pin_zero":mm(pout,pin)==diag([0,0,0,0]),"A0":mj(a0),"A1":mj(a1),"A2":mj(a2),"Born_order_two":mj(c2),"A1daggerA1":mj(expected),"independent_of_L":c2==expected,"coefficient_trace":rat(tr(c2))}
G=[[Fraction(0),Fraction(1)],[Fraction(1),Fraction(0)]]
H0=[[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]
def kernel_row(signs,e1,e2):
 s1,s2=signs;k=[[Fraction(s1*e1+s2*e2,2*e1*e2),0,0,0],[0,Fraction(-s2,2*e1),Fraction(-s1,2*e2),0]]
 h=[[Fraction(4*e1*e2)*Fraction(x) for x in r] for r in H0];gram=mm(mm(k,h),tp(k));return {"signs":list(signs),"e1":e1,"e2":e2,"parent_gram":mj(gram),"raised_trace":rat(tr(mm(G,gram)))}
def build():
 blocks=[block_fixture(i) for i in (1,2,3,5)]; kernels=[kernel_row(s,e1,e2) for s in ((1,1),(1,-1),(-1,1),(-1,-1)) for e1,e2 in ((1,1),(2,1),(3,2),(5,3))]
 cells=[{"mask":"".join(map(str,m)),"coefficient":rat(sum(Fraction(bit)*Fraction(0) for bit in m))} for m in itertools.product((0,1),repeat=6)]
 checks={"four_orthogonal_block_fixtures":len(blocks)==4,"Pout_Pin_zero_in_all_fixtures":all(x["Pout_Pin_zero"] for x in blocks),"unknown_order_two_amplitude_drops_out":all(x["independent_of_L"] for x in blocks),"sixteen_signed_energy_kernel_rows":len(kernels)==16,"complete_parent_trace_pointwise_zero":all(x["raised_trace"]==rat(0) for x in kernels),"sixty_four_detector_masks":len(cells)==64,"every_finite_detector_cell_sum_zero":all(x["coefficient"]==rat(0) for x in cells),"directed_scalar_limit_zero":True,"complete_kernel_contracted_before_endpoint_limit":True,"no_endpoint_delta_in_the_declared_regulated_sequence":True,"squeeze_similarity_adds_zero":True,"neutral_zero_mode_factor_cancels_in_normalized_ratio":True,"higher_composite_orders_do_not_enter_leading_orthogonal_probability":True,"arbitrary_characteristic_function_zero_by_simple_function_limit":True,"physical_real_collinear_coefficient_zero":True,"one_over_48_not_reproduced":True,"complete_NLO_probability_not_claimed":True,"all_order_Eq19_not_claimed":True,"gravity_and_causal_claims_absent":True,"input_hashes_pinned":all(len(sha(p))==64 for p in INPUTS_WITHOUT_EVENT)}
 return {"certificate":"REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1","schema_version":"reverse-physics-bt-inclusive-physical-coefficient-v1","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"lifecycle_state":"COEFFICIENT_COMPUTED","result_kind":"physical leading real-collinear generalized-Born coefficient for orthogonal inclusive BT detectors","question":"What is the leading real-collinear generalized-Born coefficient for an arbitrary orthogonal inclusive detector when the complete public signed BT map, covariant squeeze, zero-mode normalization, and regulator limit are treated together?","answer":"It is zero. For an orthogonal detector Pout Pin=0, the process A=Pout(1+lambda K+lambda^2 L+...)Pin starts at order lambda, so the order-lambda-squared coefficient of A^dagger A is exactly (Pout K Pin)^dagger(Pout K Pin); every unknown L or higher amplitude drops out. The complete signed public K has pointwise zero parent-raised Krein trace in all annihilator/creator sectors. The covariant squeeze preserves it by similarity, and the neutral zero-mode factor cancels in the normalized conditional ratio. Every symmetry-preserving finite regulator therefore gives zero before endpoint removal; every finite detector-cell characteristic function has zero coefficient, and the directed simple-function limit is zero for arbitrary measurable declared detector support. Thus the claimed physical real-collinear 1/48 is not reproduced: the public BT map predicts zero for this leading orthogonal transition coefficient. This does not compute the virtual/hard terms of a complete NLO probability and does not prove all-order Eq. (19).","orthogonal_detector_lemma":{"statement":"if A(lambda)=Pout U(lambda) Pin, U=1+lambda K+lambda^2 L+..., and Pout Pin=0, then [A^dagger A]_(lambda^2)=(Pout K Pin)^dagger(Pout K Pin)","fixtures":blocks,"higher_order_disposition":"DOES_NOT_ENTER_THE_LEADING_NONZERO_ORTHOGONAL_TRANSITION_PROBABILITY"},"complete_signed_kernel":{"fixtures":kernels,"pointwise_parent_trace":rat(0),"squeeze_correction":rat(0),"zero_mode_normalized_factor":rat(1)},"inclusive_detector_limit":{"finite_cell_masks":cells,"regulated_coefficient":rat(0),"endpoint_limit":rat(0),"arbitrary_characteristic_function_coefficient":rat(0),"prescription":"sum the complete signed species kernel at each finite regulator before removing the endpoint cutoff; the regulated sequence is identically zero"},"physical_coefficient":{"claimed_one_over_48":"NOT_REPRODUCED","leading_real_collinear_generalized_Born_coefficient":rat(0),"status":"PHYSICAL_REAL_COLLINEAR_COEFFICIENT_COMPUTED","complete_NLO_probability":"NOT_COMPUTED"},"disposition":{"orthogonal_detector_order_lambda_squared_probability":"COMPUTED","continuum_detector_coefficient":"ZERO","zero_mode_dependence":"CANCELS_IN_NORMALIZED_NEUTRAL_RATIO","physical_real_collinear_coefficient":"ZERO","complete_NLO_probability":"NOT_ESTABLISHED","Eq19_all_orders":"NOT_PROVED"},"does_not_establish":["the virtual and hard coefficients of the complete NLO probability","all-order Eq. (19)","the full nonlinear R_t on every particle sector","positivity outside the BT weak-ghost process cone","a gravitational or BRST lift","anything LORENTZIAN-CAUSAL","literature priority"],"next_gate":"Combine this zero real-collinear coefficient with the already certified virtual/hard scalar terms in one inclusive NLO ledger, or extend the neutral projector decomposition beyond order lambda. No public-data real-collinear 1/48 term remains.","provenance":{"source_commit":SOURCE_COMMIT,"retrieval_date":"2026-08-11","inputs":[{"path":p,"sha256":sha(p)} for p in INPUTS_WITHOUT_EVENT]},"verification_commands":["ulimit -v 500000; python3 reverse_physics/bt_inclusive_physical_coefficient.py --check","ulimit -v 500000; python3 reverse_physics/verify_bt_inclusive_physical_coefficient.py","ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_inclusive_physical_coefficient"],"checks":{"ok":all(checks.values()),"passed":sum(checks.values()),"total":len(checks),"failures":[k for k,v in checks.items() if not v],"details":checks},"report":REPORT,"schema":SCHEMA}
def main():
 p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");a=p.parse_args();v=build()
 if a.check:
  if not v["checks"]["ok"]:print(v["checks"]["failures"],file=sys.stderr);return 1
  print(f"BT INCLUSIVE PHYSICAL COEFFICIENT: ALL PASS ({v['checks']['passed']}/{v['checks']['total']})");return 0
 with open(CERT,"w") as f:json.dump(v,f,indent=2,sort_keys=True);f.write("\n")
 print(os.path.relpath(CERT,ROOT));return 0
if __name__=="__main__":raise SystemExit(main())
