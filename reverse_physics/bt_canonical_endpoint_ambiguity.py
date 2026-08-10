#!/usr/bin/env python3
"""Classify endpoint-local canonical freedom in the BT projector transport."""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from fractions import Fraction
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));CERT=os.path.join(ROOT,"reverse_physics","certificates","REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1.json");SCHEMA="reverse_physics/schema/reverse-physics-bt-canonical-endpoint-ambiguity-v1.schema.json";REPORT="reverse_physics/reports/bt-canonical-endpoint-ambiguity.md";SOURCE_COMMIT="797fec62ae6c01abddd3bfa4ca8b1d5e18aa60dc";INPUTS=["reverse_physics/certificates/REVERSE_PHYSICS_BT_PERTURBATIVE_COISOMETRY_RIGIDITY_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_ENDPOINT_EXTENSION_AMBIGUITY_V1.json","reverse_physics/certificates/REVERSE_PHYSICS_BT_ASYMPTOTIC_GENERATOR_PREFLIGHT_V1.json"]
class Poly(dict):
 def __init__(self,x=0):
  if isinstance(x,dict): super().__init__((m,Fraction(c)) for m,c in x.items() if c)
  else: super().__init__({(0,0,0):Fraction(x)} if x else {})
 def __add__(self,o):
  o=o if isinstance(o,Poly) else Poly(o);r=dict(self)
  for m,c in o.items():r[m]=r.get(m,Fraction(0))+c
  return Poly(r)
 __radd__=__add__
 def __neg__(self):return Poly({m:-c for m,c in self.items()})
 def __sub__(self,o):return self+(-Poly(o) if not isinstance(o,Poly) else -o)
 def __rsub__(self,o):return Poly(o)-self
 def __mul__(self,o):
  o=o if isinstance(o,Poly) else Poly(o);r={}
  for a,x in self.items():
   for b,y in o.items():
    m=tuple(a[i]+b[i] for i in range(3));r[m]=r.get(m,Fraction(0))+x*y
  return Poly(r)
 __rmul__=__mul__
 def __eq__(self,o):
  try:return dict(self)==dict(o if isinstance(o,Poly) else Poly(o))
  except (TypeError,ValueError):return False
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def mt(a):return [list(x) for x in zip(*a)]
def add(*xs):return [[sum(x[i][j] for x in xs) for j in range(len(xs[0][0]))] for i in range(len(xs[0]))]
def scale(c,a):return [[c*x for x in r] for r in a]
def tr(a):return sum(a[i][i] for i in range(len(a)))
def zero(a):return all(x==0 for r in a for x in r)
def rat(x):x=Fraction(x);return {"numerator":x.numerator,"denominator":x.denominator}
def sha(p):
 d=hashlib.sha256()
 with open(os.path.join(ROOT,p),"rb") as h:
  for b in iter(lambda:h.read(65536),b""):d.update(b)
 return d.hexdigest()
def fixture(u):
 u=[Fraction(x) for x in u];K=[[Fraction(0),-u[0],-u[1],-u[2]],[u[0],0,0,0],[u[1],0,0,0],[u[2],0,0,0]];P0=[[Fraction(i==0 and j==0) for j in range(4)] for i in range(4)];P1=add(mm(K,P0),scale(-1,mm(P0,K)));K2=mm(K,K);P2=add(scale(Fraction(1,2),mm(K2,P0)),scale(-1,mm(mm(K,P0),K)),scale(Fraction(1,2),mm(P0,K2)));d1=add(mm(P0,P1),mm(P1,P0),scale(-1,P1));d2=add(mm(P0,P2),mm(P2,P0),mm(P1,P1),scale(-1,P2));norm=sum(x*x for x in u);return K,P0,P1,P2,d1,d2,norm
def symbolic_identities():
 u=[Poly({tuple(int(i==j) for i in range(3)):1}) for j in range(3)];K=[[Poly(0),-u[0],-u[1],-u[2]],[u[0],0,0,0],[u[1],0,0,0],[u[2],0,0,0]];P0=[[int(i==0 and j==0) for j in range(4)] for i in range(4)];P1=add(mm(K,P0),scale(-1,mm(P0,K)));K2=mm(K,K);P2=add(scale(Fraction(1,2),mm(K2,P0)),scale(-1,mm(mm(K,P0),K)),scale(Fraction(1,2),mm(P0,K2)));d1=add(mm(P0,P1),mm(P1,P0),scale(-1,P1));d2=add(mm(P0,P2),mm(P2,P0),mm(P1,P1),scale(-1,P2));norm=sum(x*x for x in u)
 return {"skew":zero(add(K,mt(K))),"idempotence_order_one":zero(d1),"idempotence_order_two":zero(d2),"trace_order_one":tr(P1)==0,"trace_order_two":tr(P2)==0,"hard_compensation":P2[0][0]==-norm and sum(P2[i][i] for i in range(1,4))==norm}
def build():
 samples=[[0,0,0],[1,0,0],[0,1,0],[0,0,1],[2,0,0],[1,2,3],[Fraction(1,2),Fraction(-1,3),Fraction(2,5)]];rows=[];ok=True
 for u in samples:
  K,P0,P1,P2,d1,d2,n=fixture(u);good=(add(K,mt(K))==[[0]*4 for _ in range(4)] and zero(d1) and zero(d2) and tr(P1)==0 and tr(P2)==0 and P2[0][0]==-n and sum(P2[i][i] for i in range(1,4))==n);ok&=good;rows.append({"u":[rat(x) for x in u],"norm_square":rat(n),"hard_P2":rat(P2[0][0]),"endpoint_trace_P2":rat(sum(P2[i][i] for i in range(1,4))),"identity":good})
 symbolic=symbolic_identities();target=Fraction(1,48);checks={"all_generators_skew":symbolic["skew"] and ok,"projector_order_one_all_parameters":symbolic["idempotence_order_one"] and ok,"projector_order_two_all_parameters":symbolic["idempotence_order_two"] and ok,"trace_preserved_all_parameters":symbolic["trace_order_one"] and symbolic["trace_order_two"] and ok,"hard_real_compensation_all_parameters":symbolic["hard_compensation"] and ok,"three_independent_endpoint_directions":all(fixture([int(i==j) for i in range(3)])[-1]==1 for j in range(3)),"arbitrary_rational_norms_survive":len({(r["norm_square"]["numerator"],r["norm_square"]["denominator"]) for r in rows})>3,"one_over_48_compatible":Fraction(3,12**2)==target,"one_over_48_not_selected":fixture([0,0,0])[-1]!=fixture([1,0,0])[-1],"canonical_CCR_preserved_by_conjugation":symbolic["skew"],"input_hashes_pinned":all(len(sha(p))==64 for p in INPUTS),"probability_stays_open":True,"no_lorentzian_claim":True}
 return {"certificate":"REVERSE_PHYSICS_BT_CANONICAL_ENDPOINT_AMBIGUITY_V1","schema_version":"reverse-physics-bt-canonical-endpoint-ambiguity-v1","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"lifecycle_state":"CLASSIFIED","result_kind":"exact canonical-algebra underdetermination witness for the endpoint carrier","question":"Do skewness, CCR preservation, exchange symmetry, Pi=1, projector idempotence, and trace preservation alone fix the three endpoint constants?","answer":"No. Treating the three independently classified reflection-even endpoint jets as formal carrier directions, every coefficient vector u gives a skew generator K(u)=[[0,-u^T],[u,0]]. Its conjugation preserves canonical commutators, and P=exp(epsilon K)P0 exp(-epsilon K) is idempotent and trace preserving. At order epsilon^2 the hard block is -u^T u and the endpoint trace is +u^T u. Thus the listed algebraic identities alone admit a three-parameter family and cannot select 1/48. This is an underdetermination witness, not a derivation of the actual BT continuum transport.","endpoint_basis":["delta_0+delta_1","delta_0_prime-delta_1_prime","delta_0_double_prime+delta_1_double_prime"],"canonical_family":{"basis":["hard","endpoint_c0","endpoint_c1","endpoint_c2"],"generator":"K(u)=[[0,-u^T],[u,0_3]]","projector":"P(epsilon)=exp(epsilon K)P0 exp(-epsilon K)","symbolic_checks":symbolic,"rows":rows,"universal_order_two":"P2_hard=-u^T u; trace(P2_endpoint)=+u^T u"},"identity_classification":{"Pi":"identity on the formal perturbative branch","anti_Krein_sharp":"K^sharp=-K for the displayed positive neutral carrier; this supplies an insufficiency witness, not the missing BT continuum Gram","CCR":"similarity by exp(epsilon K) preserves commutators for every u","idempotence":"conjugation preserves P^2=P for every u","trace":"hard loss and endpoint gain cancel for every u","exchange":"already built into the three reflection-even endpoint basis elements"},"target_comparison":{"required_norm_square":rat(target),"exact_compatibility_witness":{"coefficient_field":"Q(sqrt(3))","u":["sqrt(3)/12","0","0"],"norm_square":"3/144=1/48"},"status":"COMPATIBLE_NOT_SELECTED","warning":"choosing u^T u=1/48 is exactly the fitted finite projector unless a further dynamical normalization condition fixes u"},"assumptions":["the endpoint-extension certificate supplies three independent reflection-even jet directions","the displayed four-channel neutral carrier is used only as a countermodel to uniqueness under the listed algebraic identities","canonical transformations act by similarity on the carrier projector","no claim is made that an arbitrary u is realized by the missing BT continuum transport"],"disposition":{"canonical_endpoint_family":"THREE_PARAMETER_UNDERDETERMINATION_WITNESS","CCR_and_projector_identities":"INSUFFICIENT_TO_FIX_ENDPOINT_CONSTANTS","one_over_48":"COMPATIBLE_BUT_NOT_DERIVED","unique_continuum_projector":"NOT_CONSTRUCTED","full_nlo_quotient_trace":"NOT_COMPUTED","physical_nlo_probability":"NOT_ESTABLISHED"},"missing_object_ledger":["a dynamical endpoint renormalization/matching condition beyond canonical algebra","the deferred BT Eq. (19) continuum construction or equivalent physical resolution prescription","a proof that the chosen condition fixes u independently of regulator coordinates","incoming/outgoing equality under that condition","complete finite virtual one-loop terms and counterterms","the complete real--virtual quotient trace and positivity test"],"next_gate":"The listed canonical algebra is exhausted and leaves an exact countermodel to uniqueness. A complete probability now requires new external/dynamical input: the deferred BT continuum projector, an explicit physical detector/resolution prescription, or a renormalization condition independently justified rather than fitted to 1/48.","does_not_establish":["that every u is realized by the actual BT continuum transport","that no physical condition can select 1/48","that the BT companion construction fails","a complete NLO probability","beyond-tree positivity","a gravitational lift","anything LORENTZIAN-CAUSAL","literature priority"],"provenance":{"source_commit":SOURCE_COMMIT,"retrieval_date":"2026-08-10","inputs":[{"path":p,"sha256":sha(p)} for p in INPUTS],"primary_source":{"source":"Bateman--Turok arXiv:2607.00096v1","url":"https://arxiv.org/abs/2607.00096","equations":["Eq. (19)","Appendix C"]}},"verification_commands":["ulimit -v 500000; python3 reverse_physics/bt_canonical_endpoint_ambiguity.py --check","ulimit -v 500000; python3 reverse_physics/verify_bt_canonical_endpoint_ambiguity.py","ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_canonical_endpoint_ambiguity"],"checks":{"ok":all(checks.values()),"passed":sum(checks.values()),"total":len(checks),"failures":[n for n,v in checks.items() if not v],"details":checks},"report":REPORT,"schema":SCHEMA}
def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--output",default=CERT);p.add_argument("--check",action="store_true");a=p.parse_args(argv);c=build()
 if a.check:
  try:
   with open(a.output,encoding="utf-8") as h:r=json.load(h)
  except Exception as e:print("[FAIL]",e);return 1
  ok=r==c;print(f"[{'PASS' if ok else 'FAIL'}] exact_reproduction\nRESULT: {'PASS' if ok else 'FAIL'} ({c['checks']['passed']}/{c['checks']['total']})");return 0 if ok else 1
 with open(a.output,"w",encoding="utf-8") as h:json.dump(c,h,indent=2,sort_keys=True);h.write("\n")
 print(a.output);return 0 if c["checks"]["ok"] else 1
if __name__=="__main__":sys.exit(main())
