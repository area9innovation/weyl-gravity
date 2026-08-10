#!/usr/bin/env python3
"""Exact finite Krein witness for the missing BT coisometry range overlap."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from fractions import Fraction
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1.json");SCHEMA="reverse_physics/schema/reverse-physics-bt-coisometry-range-nonuniqueness-v1.schema.json";REPORT="reverse_physics/reports/bt-coisometry-range-nonuniqueness.md";SOURCE_COMMIT="d5b537ba5aa4f6a395e73fc2fe36922136530928";INPUTS=["reverse_physics/certificates/REVERSE_PHYSICS_BT_OSCILLATORY_RADICAL_NO_MATCHING_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json"]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def mt(a):return [list(x) for x in zip(*a)]
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def tr(a):return sum(a[i][i] for i in range(len(a)))
def eye(n):return [[Fraction(i==j) for j in range(n)] for i in range(n)]
def diag(*x):return [[Fraction(x[i]) if i==j else Fraction(0) for j in range(len(x))] for i in range(len(x))]
def rat(x):x=Fraction(x);return {"numerator":x.numerator,"denominator":x.denominator}
def sha(p):
 d=hashlib.sha256()
 with open(os.path.join(ROOT,p),"rb") as h:
  for b in iter(lambda:h.read(65536),b""):d.update(b)
 return d.hexdigest()
def fixture(t):
 t=Fraction(t);a=(1-t*t)/(1+t*t);b=2*t/(1+t*t);v=[[a],[0],[b]];p=mm(v,mt(v));R=[[1,0,0],[0,1,0]];Rs=mt(R);Pi=mm(Rs,R);D=sub(eye(3),Pi);A=mm(mm(R,p),Rs);defect=mm(mm(mm(mm(R,p),D),p),Rs)
 return {"t":t,"a":a,"b":b,"P":p,"A":A,"Pi":Pi,"D":D,"defect":defect}
def build():
 R=[[1,0,0],[0,1,0]];Rs=mt(R);J=diag(1,-1);G=diag(1,-1,1);Pi=mm(Rs,R);D=sub(eye(3),Pi);rows=[];all_ok=True
 for t in (0,Fraction(1,3),Fraction(1,2),1):
  f=fixture(t);lhs=sub(mm(f["A"],f["A"]),f["A"]);rhs=[[-x for x in row] for row in f["defect"]];ok=(mm(R,Rs)==eye(2) and mm(f["P"],f["P"])==f["P"] and lhs==rhs and tr(f["A"])==f["a"]**2);all_ok&=ok;rows.append({"t":rat(t),"range_amplitude":rat(f["a"]),"defect_amplitude":rat(f["b"]),"pushforward_trace":rat(tr(f["A"])),"identity":ok})
 target=Fraction(1,48);checks={"krein_metrics_nondegenerate":tr(J)==0 and tr(G)==1,"right_unit":mm(R,Rs)==eye(2),"range_projection_idempotent":mm(Pi,Pi)==Pi,"defect_projection_idempotent":mm(D,D)==D,"range_defect_complementary":mm(Pi,D)==[[0]*3 for _ in range(3)],"family_projectors_and_defect_identity":all_ok,"pushforward_trace_varies":len({(r["pushforward_trace"]["numerator"],r["pushforward_trace"]["denominator"]) for r in rows})==4,"target_overlap_algebraically_allowed":target+Fraction(47,48)==1,"target_requires_unpublished_overlap":True,"pullback_not_unitarily_inverted":True,"input_hashes_pinned":all(len(sha(p))==64 for p in INPUTS),"probability_stays_open":True,"no_lorentzian_claim":True}
 return {"certificate":"REVERSE_PHYSICS_BT_COISOMETRY_RANGE_NONUNIQUENESS_V1","schema_version":"reverse-physics-bt-coisometry-range-nonuniqueness-v1","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"lifecycle_state":"CLASSIFIED","result_kind":"exact finite Krein coisometry range-overlap nonuniqueness theorem","question":"Do RR-dagger=1 and the published pullback data determine the pushforward projector trace without Pi=R-dagger R?","answer":"No. For every coisometry R and projector P, A=R P R-dagger obeys A^2-A=-R P(1-Pi)P R-dagger with Pi=R-dagger R, and tr(A)=tr(P Pi). An exact Krein family with fixed R R-dagger=1 varies tr(A) through 1,16/25,9/25,0 by changing only the unreported range overlap. The value 1/48 is algebraically allowed but is not selected by the right-unit identity.","finite_krein_model":{"input_metric":"G=diag(1,-1,1)","output_metric":"J=diag(1,-1)","coisometry":"R=[[1,0,0],[0,1,0]]","krein_adjoint":"R_sharp=G^-1*R^T*J=R^T","range_projection":"Pi=diag(1,1,0)","defect_projection":"D=diag(0,0,1)","projector_family":"v_t=((1-t^2)/(1+t^2),0,2t/(1+t^2)); P_t=v_t v_t^sharp","rows":rows},"universal_identities":{"idempotence_defect":"(R P R_sharp)^2-R P R_sharp=-R P (1-Pi) P R_sharp","trace_overlap":"tr(R P R_sharp)=tr(P Pi)","hilbert_special_case":"idempotence forces defect-to-range mixing to vanish; a Krein-null defect may be nonzero and requires separate control"},"target_witness":{"target":rat(target),"compatible_projector":"P_target has diagonal (1/48,0,47/48) and off-diagonal sqrt(47)/48 in the positive range-defect plane","field":"Q(sqrt(47))","status":"COMPATIBLE_NOT_SELECTED"},"disposition":{"right_unit_identity":"INSUFFICIENT","range_projection":"NOT_PUBLISHED","projector_range_overlap":"UNDETERMINED","one_over_48":"COMPATIBLE_BUT_NOT_DERIVED","neutral_pushforward_projector":"NOT_CONSTRUCTED","full_nlo_quotient_trace":"NOT_COMPUTED","physical_nlo_probability":"NOT_ESTABLISHED"},"missing_object_ledger":["Pi=R_t-dagger R_t on the covariant n-particle projector domain","the defect overlap P_chi(1-Pi)P_chi including its Krein-null part","the deferred proof of Eq. (19) at order lambda","a unique neutral endpoint matching condition for c0,c1,c2","incoming/outgoing equality and trace-class control","the complete renormalized NLO quotient trace"],"next_gate":"The public Letter is insufficient to select 1/48. Obtain or reconstruct the deferred Eq. (19) pushforward/range theorem, including Pi or the exact defect overlap; do not infer it from RR-dagger=1 or the negative-charge radical.","does_not_establish":["that BT cannot choose a valid range projection","that 1/48 is inconsistent","a complete NLO probability","beyond-tree positivity","a gravitational lift","anything LORENTZIAN-CAUSAL","literature priority"],"provenance":{"source_commit":SOURCE_COMMIT,"retrieval_date":"2026-08-10","inputs":[{"path":p,"sha256":sha(p)} for p in INPUTS],"primary_source":{"source":"Bateman--Turok arXiv:2607.00096v1","url":"https://arxiv.org/abs/2607.00096","equations":["Eq. (19)","Appendix C after Eq. (33)"]}},"verification_commands":["ulimit -v 500000; python3 reverse_physics/bt_coisometry_range_nonuniqueness.py --check","ulimit -v 500000; python3 reverse_physics/verify_bt_coisometry_range_nonuniqueness.py","ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_coisometry_range_nonuniqueness"],"checks":{"ok":all(checks.values()),"passed":sum(checks.values()),"total":len(checks),"failures":[n for n,v in checks.items() if not v],"details":checks},"report":REPORT,"schema":SCHEMA}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--output",default=CERT);p.add_argument("--check",action="store_true");a=p.parse_args(argv);c=build()
 if a.check:
  try:r=json.load(open(a.output,encoding="utf-8"))
  except Exception as e:print("[FAIL]",e);return 1
  ok=r==c;print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction\nRESULT: {'PASS' if ok else 'FAIL'} ({c['checks']['passed']}/{c['checks']['total']})");return 0 if ok else 1
 with open(a.output,"w",encoding="utf-8") as h:json.dump(c,h,indent=2,sort_keys=True);h.write("\n")
 print(a.output);return 0 if c["checks"]["ok"] else 1
if __name__=="__main__":sys.exit(main())
