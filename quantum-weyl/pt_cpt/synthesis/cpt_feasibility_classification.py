#!/usr/bin/env python3
"""Independently join the three Phase-2 structured-CPT inputs."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any
import sympy as sp
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from symbolic.verify_conformal_generator_all_levels import representation_space

OUTPUT=HERE/"certificates/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1.json"
PAPER=ROOT/"planning/paper-coverage/phase2-cpt-paper15-correction-request.json"
SCHEMA=HERE/"schema/phase2-cpt-feasibility-classification-v1.schema.json"
INPUTS={
 "quartet":("quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json","377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a"),
 "compact":("quantum-weyl/pt_cpt/compact_blocks/certificates/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1.json","8852a5503f1549e2bcfc05bbf72b714be8b7079708bd06d8059eee1ea2139fd4"),
 "cylinder":("quantum-weyl/pt_cpt/cylinder_brst/certificates/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1.json","1505dbbff6e6756a2c4472d607b66a02084c184bf0c50092bf7aab3f8dd4d532"),
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(x): return (json.dumps(x,indent=2,sort_keys=True)+"\n").encode()
def mat(rows,lam): return sp.Matrix([[sp.sympify(v.replace("lambda","lam"),locals={"lam":lam}) for v in row] for row in rows])

def replay():
 refs={}; src={}
 for role,(rel,h) in INPUTS.items():
  p=ROOT/rel
  if sha(p)!=h: raise AssertionError(f"input drift {role}")
  refs[role]={"path":rel,"sha256":h}; src[role]=json.loads(p.read_text())
 lam,k=sp.symbols("lambda k",positive=True,real=True); root=sp.sqrt(2*lam)
 vals=[k**2+lam-root,k**2+lam+root,k**2+lam-sp.Rational(2,3)]
 h2=sp.diag(vals[0],vals[0],vals[1],vals[1],*[vals[2]]*4)
 ys=sp.symbols("y0:64"); y=sp.Matrix(8,8,ys)
 dim=len(sp.linsolve(list(y*h2-h2*y),ys).free_symbols)
 if dim!=24: raise AssertionError("compact commutant")
 compact_checks={}
 for parity in ("axial","polar"):
  row=src["compact"]["generic_blocks"]["exact_blocks"][parity]
  G=mat(row["restricted_Weyl_q_form"],lam); C=mat(row["q_fundamental_symmetry_C0"],lam); eta=mat(row["q_eta0_equals_Gq_C0"],lam)
  if sp.simplify(C*C-sp.eye(2))!=sp.zeros(2) or sp.simplify(G*C-eta)!=sp.zeros(2): raise AssertionError("compact C")
  compact_checks[parity]={"C_squared_identity":True,"eta_determinant":str(sp.factor(eta.det()))}
 cylinder={}
 for chi in (-1,1):
  s=representation_space(5,chi); C=s.form
  compact_ranks=[(C*m-m*C).rank() for m in [s.energy,*s.left.values(),*s.right.values()]]
  proper=[]
  for m in [*s.lowering.values(),*s.raising.values()]: proper.append(C*m-m*C)
  cylinder[str(chi)]={"compact_ranks":compact_ranks,"proper_ranks":[int(x.rank()) for x in proper],"stacked_BRST_defect_rank":int(sp.Matrix.vstack(*proper).rank())}
  if compact_ranks!=[0]*7 or cylinder[str(chi)]["proper_ranks"]!=[32]*8: raise AssertionError("cylinder ranks")
 q=src["quartet"]["selected_counterflow_negative_control"]
 A=sp.Matrix([[sp.sympify(v,locals={"I":sp.I}) for v in row] for row in q["real_companion_generator_A"]]); z=sp.symbols("z")
 disc=sp.Integer(q["y_equals_z_squared_discriminant"])
 if disc!=-2151 or sp.simplify((z*sp.eye(4)-A).det()-(40*z**4+773*z**2+3748)/40)!=0: raise AssertionError("quartet replay")
 return refs,{"compact":{"full_commutant_complex_dimension":dim,"full_commutant":"M_2(C) direct-sum M_2(C) direct-sum M_4(C)","Hamiltonian":"positive spectral square root of H^2","H_and_H2_same_commutant":True,"q_checks":compact_checks},"cylinder":cylinder,"quartet":{"discriminant":str(disc),"H_has_nonreal_spectrum":True}}

def build():
 refs,replays=replay()
 rows=[
  {"claim":"structured_positive_eta","compact_blocks":"EXACT_NONEMPTY_CONE_CLASSIFIED","cylinder_reduced":"ETA0_EQUALS_IDENTITY","counterflow_quartet":"EXACTLY_INFEASIBLE","type":"REDUCED_MODE_METRIC_FEASIBILITY"},
  {"claim":"unique_fundamental_symmetry","compact_blocks":"UNIQUE_C0_MINUS_I2_PLUS_I2_PLUS_I4","cylinder_reduced":"C0_EXISTS_BUT_NOT_CHAIN_MAP","counterflow_quartet":"NO_POSITIVE_ETA_SO_GATE_NOT_REACHED","type":"G_RELATIVE_INVOLUTION"},
  {"claim":"genuine_Mannheim_C","compact_blocks":"NOT_ESTABLISHED_MISSING_INDEPENDENT_PT","cylinder_reduced":"NOT_ESTABLISHED","counterflow_quartet":"SPECTRALLY_EXCLUDED","type":"C_OPERATOR_WITH_PT_DATA"},
  {"claim":"residual_BRST_descent","compact_blocks":"INVARIANT_STATE_ORBIT_QUOTIENT_NOT_ESTABLISHED","cylinder_reduced":"OBSTRUCTED_IN_DECLARED_INVARIANT_COMMUTANT","counterflow_quartet":"NOT_APPLICABLE_CHANGED_THEORY_NEGATIVE_CONTROL","type":"CHAIN_AND_COHOMOLOGY_GATE"},
  {"claim":"broken_PT_negative_control","compact_blocks":"NOT_APPLICABLE","cylinder_reduced":"NOT_APPLICABLE","counterflow_quartet":"UNRESCUABLE_COMPLEX_SPECTRUM","type":"SPECTRAL_NO_GO"},
  {"claim":"nontrivial_ghost_normalizer_route","compact_blocks":"NOT_CLASSIFIED","cylinder_reduced":"NOT_CLASSIFIED_OUTSIDE_DECLARED_INVARIANT_COMMUTANT","counterflow_quartet":"CANNOT_REPAIR_COMPLEX_SPECTRUM","type":"OPEN_ROUTE"},
 ]
 c={"$schema":"../schema/phase2-cpt-feasibility-classification-v1.schema.json","schema":"pure-weyl-phase2-cpt-feasibility-classification-v1","result_id":"PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1","result_state":"FINITE_STRUCTURED_ETA_POSITIVE_C0_PARTIAL_GENUINE_C_AND_BRST_OPEN_OR_OBSTRUCTED_QUARTET_NO_GO","lifecycle_state":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"source_refs":refs,"independent_replays":replays,"typed_classification":rows,"definition_crosswalk":{"H":"positive-frequency generator; compact H is the positive spectral square root of the displayed H^2","dagger":"declared coefficient-space Hermitian adjoint in each finite reduced carrier","real_structure":"conjugate opposite-frequency/momentum completion; not time reversal by itself","P_T":"absent on compact fixed-N=2 and cylinder inputs","eta":"strictly positive Hermitian pseudo-Hermitian metric, not C by definition","C":"requires involution, dynamics, PT convention and BRST chain compatibility","Q":"residual CE/BRST differential on the cylinder; no positive-self-adjoint Q condition","cohomology":"requires explicit chain descent before positivity"},"scoped_analogy":{"Pais_Uhlenbeck_equal_frequency_Jordan":"secular logarithms/Jordan structure at characteristic shells are an algebraic analogy to the equal-frequency PU limit only","does_not_establish":["zero-norm decoupling","a Mannheim C operator","equivalence of compact/cylinder blocks to the PU oscillator"]},"decision":{"finite_positive_eta":"YES_ON_COMPACT_AND_STATIONARY_CYLINDER_REDUCED_BLOCKS","genuine_Mannheim_C":"NONE_CERTIFIED","residual_BRST_C":"CYLINDER_OBSTRUCTED_IN_DECLARED_COMMUTANT","ghost_normalizer":"OPEN","counterflow":"POSITIVE_ETA_SPECTRALLY_IMPOSSIBLE","conformal_gravity_unitarity":"NOT_ESTABLISHED"},"mutation_expectations":{"eta_equals_C":"REJECT","compact_commutant_dim12":"REJECT","H_equals_H2":"REJECT","cylinder_chain_map":"REJECT","quartet_rescued":"REJECT","ghost_normalizer_closed":"REJECT","PU_analogy_promoted":"REJECT","unitarity":"REJECT"},"claim_boundary":{"establishes":["the exact six-row terminal structured-CPT classification","independent exact replay of the compact commutant/C0, cylinder commutator defects and quartet discriminant"],"does_not_establish":["a genuine Mannheim C on strict conformal gravity","a nontrivial ghost-normalizer no-go","a full-BV Hadamard state, particles, scattering, anomaly cancellation, QME restoration or unitarity"]},"provenance":{"generator":str(Path(__file__).relative_to(ROOT)),"science_forge_identity":"phase2-cpt-review-1","work_item":"sf:program/work/phase2-cpt-feasibility-classification"}}
 Draft202012Validator(json.loads(SCHEMA.read_text())).validate(c); return c

def paper_request(c):
 return {"schema":"paper15-correction-request-v1","result_id":"PHASE2_CPT_PAPER15_CORRECTION_REQUEST_V1","paper":"15","status":"REQUEST_ONLY_NO_PAPER_EDIT","source_claim_map":{"path":str(OUTPUT.relative_to(ROOT)),"result_id":c["result_id"]},"requested_corrections":[{"location":"Level-4/CPT column","text":"Report exact positive eta and unique fundamental symmetry on compact reduced blocks, while stating that no genuine Mannheim C is certified because independent P/T data are absent."},{"location":"cylinder row","text":"Report stationary eta0 positivity together with exact failure of residual BRST descent in the declared invariant commutant; leave nontrivial ghost normalizers open."},{"location":"counterflow row","text":"State that the Hamiltonian-Hopf quartet has complex spectrum and admits no positive pseudo-Hermitian metric, so an inner-product redefinition cannot rescue it."},{"location":"Jordan/log remark","text":"Mention the equal-frequency Pais-Uhlenbeck Jordan comparison only as a scoped algebraic analogy, with no zero-norm decoupling or C-operator inference."}],"forbidden_promotions":["finite reduced eta to unitarity","fundamental symmetry to genuine C","declared-commutant obstruction to all ghost actions","analogy to theorem","CPT result to anomaly cancellation"]}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); a=ap.parse_args(); c=build(); outs={OUTPUT:dump(c),PAPER:dump(paper_request(c))}
 if a.check:
  for p,b in outs.items():
   if not p.exists() or p.read_bytes()!=b: raise SystemExit(f"stale {p}")
  print("PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1 outputs: CURRENT"); return
 for p,b in outs.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)

if __name__=="__main__": main()
