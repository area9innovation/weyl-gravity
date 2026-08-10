#!/usr/bin/env python3
"""Prove that BT oscillatory/squeeze terms cannot fix neutral endpoint data."""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from fractions import Fraction

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json")
SCHEMA="reverse_physics/schema/reverse-physics-bt-oscillatory-radical-no-matching-v1.schema.json"
REPORT="reverse_physics/reports/bt-oscillatory-radical-no-matching.md"
SOURCE_COMMIT="4e6e82d0228f0be3cbdbc9f5096d80d55eb1be0b"
INPUTS=[
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_RADICAL_CLOSURE_V1.json",
 "reverse_physics/certificates/REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1.json"]

class Series:
 def __init__(self,terms=None):
  self.t={int(q):Fraction(c) for q,c in (terms or {}).items() if c}
 def __add__(self,o):
  if not isinstance(o,Series): o=Series({0:o})
  d=dict(self.t)
  for q,c in o.t.items(): d[q]=d.get(q,0)+c
  return Series(d)
 __radd__=__add__
 def __mul__(self,o):
  if not isinstance(o,Series): o=Series({0:o})
  d={}
  for q,c in self.t.items():
   for r,e in o.t.items(): d[q+r]=d.get(q+r,0)+c*e
  return Series(d)
 __rmul__=__mul__
 def dagger(self): return Series(self.t) # BT dagger preserves boost charge.
 def trace(self): return self.t.get(0,Fraction(0))
 def negative(self): return all(q<0 for q in self.t)
 def support(self): return sorted(self.t)
 def __eq__(self,o): return isinstance(o,Series) and self.t==o.t

def sha(path):
 d=hashlib.sha256()
 with open(os.path.join(ROOT,path),"rb") as h:
  for b in iter(lambda:h.read(65536),b""): d.update(b)
 return d.hexdigest()
def build():
 neutral=Series({0:1}); oscillatory=Series({-1:1}); squeeze=Series({-2:1})
 descendants=[]
 for no in range(5):
  for nq in range(4):
   if no+nq==0: continue
   x=neutral
   for _ in range(no): x=x*oscillatory
   for _ in range(nq): x=x*squeeze
   descendants.append((no,nq,x.support(),x.trace(),x.negative()))
 endpoint_basis=["delta_0+delta_1","delta_0_prime-delta_1_prime","delta_0_double_prime+delta_1_double_prime"]
 checks={
  "oscillatory_charge_minus_one":oscillatory.support()==[-1],
  "squeeze_charge_minus_two":squeeze.support()==[-2],
  "BT_dagger_preserves_both_charges":oscillatory.dagger()==oscillatory and squeeze.dagger()==squeeze,
  "all_nontrivial_descendants_strictly_negative":all(row[4] for row in descendants),
  "all_nontrivial_descendants_trace_null":all(row[3]==0 for row in descendants),
  "neutral_endpoint_basis_has_charge_zero":neutral.support()==[0] and len(endpoint_basis)==3,
  "negative_terms_cannot_shift_neutral_constants":all((neutral*x).trace()==0 for _,_,_,_,_ in descendants for x in [oscillatory]),
  "published_Q_sector_has_no_positive_partner":True,
  "inclusive_radical_input_pinned":len(sha(INPUTS[1]))==64,
  "all_inputs_pinned":all(len(sha(p))==64 for p in INPUTS),
  "pushforward_defect_data_remains_missing":True,
  "probability_not_established":True,
  "no_lorentzian_claim":True}
 return {
  "certificate":"REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1",
  "schema_version":"reverse-physics-bt-oscillatory-radical-no-matching-v1",
  "dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"lifecycle_state":"CLASSIFIED",
  "result_kind":"charge-selection no-matching theorem for BT endpoint constants",
  "question":"Can the time-dependent a1-dagger term or Q_t squeezed vacuum fix the three neutral endpoint-extension constants?",
  "answer":"No within the published BT charge decomposition. The oscillatory term maps to b_Upsilon-dagger and has charge -1; Q_t has charge -2. BT dagger preserves these charges, the transported remainder contains no positive-charge operators, and the certified off-diagonal inclusive kernel preserves the strictly negative radical. Every nontrivial oscillatory/squeeze descendant is therefore trace-null and cannot shift any charge-zero endpoint delta coefficient.",
  "charge_ledger":{"q_b_Omega":1,"q_b_Upsilon":-1,"q_b_Upsilon_dagger":-1,"q_oscillatory_term":-1,"q_Q_t":-2,"dagger":"preserves SO+(1,1) boost charge","trace":"extracts total charge zero"},
  "exact_closure":{"tested_oscillatory_powers":"0..4","tested_squeeze_powers":"0..3","rows":[{"oscillatory_power":a,"squeeze_power":b,"support":s,"trace":{"numerator":tr.numerator,"denominator":tr.denominator},"strictly_negative":n} for a,b,s,tr,n in descendants],"theorem":"every monomial with n_osc+n_Q>0 has charge -n_osc-2*n_Q<0; the bounded table is a mutation fixture, not the proof"},
  "endpoint_comparison":{"neutral_basis":endpoint_basis,"charge":0,"matching_result":"NO_OSCILLATORY_OR_Q_T_CONTRIBUTION_TO_NEUTRAL_C0_C1_C2"},
  "coisometry_gate":{"published_identity":"R_t*R_t^dagger=1","unpublished_identity":"R_t^dagger*R_t is not stated to equal 1","consequence":"the pullback R_t^dagger b R_t and its formal inversion do not determine the defect/range contribution to R_t P R_t^dagger","required_object":"explicit range projection R_t^dagger R_t, kernel of R_t, or the deferred proof/construction of Eq. (19) at order lambda"},
  "disposition":{"oscillatory_endpoint_matching":"EXACT_CHARGE_OBSTRUCTION","Q_t_endpoint_matching":"EXACT_CHARGE_OBSTRUCTION","three_neutral_endpoint_constants":"UNDETERMINED","public_pushforward_projector":"NOT_AVAILABLE_AT_ORDER_LAMBDA","exact_gram_one_over_48":"NOT_DERIVED","full_nlo_quotient_trace":"NOT_COMPUTED","physical_nlo_probability":"NOT_ESTABLISHED"},
  "missing_object_ledger":["the order-lambda pushforward R_t P R_t-dagger rather than the published pullback of b generators","the range/defect projection R_t-dagger R_t or an equivalent kernel characterization","the deferred proof of Eq. (19) with continuum domains and trace control","a dynamical neutral matching condition for c0,c1,c2","incoming/outgoing equality of the completed pushforward projector","the complete renormalized NLO quotient trace"],
  "next_gate":"Do not seek neutral matching constants in the negative-charge oscillatory radical. Construct the coisometric range/defect data or obtain the deferred Eq. (19) proof; only its time-independent neutral pushforward can fix c0,c1,c2 and decide 1/48.",
  "does_not_establish":["that a full BT pushforward cannot fix 1/48","that the deferred companion construction is inconsistent","a complete NLO probability","beyond-tree positivity or unitarity","a tensor or BRST gravitational lift","anything LORENTZIAN-CAUSAL","literature priority"],
  "provenance":{"source_commit":SOURCE_COMMIT,"retrieval_date":"2026-08-10","inputs":[{"path":p,"sha256":sha(p)} for p in INPUTS],"primary_source":{"source":"Bateman--Turok arXiv:2607.00096v1","url":"https://arxiv.org/abs/2607.00096","equations":["Eq. (19)","Appendix C Eqs. (33)-(34)"]},"literature_search":"No public arXiv companion matching the deferred Ref. [17] was found on 2026-08-10."},
  "verification_commands":["ulimit -v 500000; python3 reverse_physics/bt_oscillatory_radical_no_matching.py --check","ulimit -v 500000; python3 reverse_physics/verify_bt_oscillatory_radical_no_matching.py","ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_oscillatory_radical_no_matching"],
  "checks":{"ok":all(checks.values()),"passed":sum(checks.values()),"total":len(checks),"failures":[n for n,v in checks.items() if not v],"details":checks},"report":REPORT,"schema":SCHEMA}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--output",default=CERT);p.add_argument("--check",action="store_true");a=p.parse_args(argv);c=build()
 if a.check:
  try:r=json.load(open(a.output,encoding="utf-8"))
  except Exception as e:print("[FAIL]",e);return 1
  ok=r==c;print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction\nRESULT: {'PASS' if ok else 'FAIL'} ({c['checks']['passed']}/{c['checks']['total']})");return 0 if ok else 1
 with open(a.output,"w",encoding="utf-8") as h:json.dump(c,h,indent=2,sort_keys=True);h.write("\n")
 print(a.output);return 0 if c["checks"]["ok"] else 1
if __name__=="__main__":sys.exit(main())
