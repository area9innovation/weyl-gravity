#!/usr/bin/env python3
"""Independent verifier for the terminal structured-CPT claim map."""
from __future__ import annotations
import copy,hashlib,json,sys
from functools import lru_cache
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator,ValidationError
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from symbolic.verify_conformal_generator_all_levels import representation_space
CERT=HERE/"certificates/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1.json"; SCHEMA=HERE/"schema/phase2-cpt-feasibility-classification-v1.schema.json"; RECEIPT=HERE/"receipts/PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1_TIER_RECEIPT.json"; REPORT=ROOT/"reports/phase2-cpt-feasibility-classification-2026-07-22.md"; PAPER=ROOT/"planning/paper-coverage/phase2-cpt-paper15-correction-request.json"
INPUTS={"quartet":("quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json","377f699d854724f743188b854e4f5be3f29540ba1f5bc2beee3ec9204e7dbf6a"),"compact":("quantum-weyl/pt_cpt/compact_blocks/certificates/COMPACT_BLOCK_STRUCTURED_CPT_FEASIBILITY_V1.json","8852a5503f1549e2bcfc05bbf72b714be8b7079708bd06d8059eee1ea2139fd4"),"cylinder":("quantum-weyl/pt_cpt/cylinder_brst/certificates/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1.json","1505dbbff6e6756a2c4472d607b66a02084c184bf0c50092bf7aab3f8dd4d532")}
OUTPUTS={"producer":HERE/"cpt_feasibility_classification.py","verifier":Path(__file__),"schema":SCHEMA,"certificate":CERT,"tests":HERE/"tests/test_cpt_feasibility_classification.py","report":REPORT,"paper_request":PAPER}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
@lru_cache(maxsize=1)
def exact_replay():
 lam,k=sp.symbols("lambda k",positive=True,real=True); r=sp.sqrt(2*lam); vals=[k*k+lam-r,k*k+lam+r,k*k+lam-sp.Rational(2,3)]; H2=sp.diag(vals[0],vals[0],vals[1],vals[1],*[vals[2]]*4); xs=sp.symbols("x0:64"); X=sp.Matrix(8,8,xs)
 dim=len(sp.linsolve(list(X*H2-H2*X),xs).free_symbols); cylinder={}
 for chi in (-1,1):
  s=representation_space(5,chi); C=s.form; proper=[C*m-m*C for m in [*s.lowering.values(),*s.raising.values()]]; cylinder[str(chi)]=([int(x.rank()) for x in proper],int(sp.Matrix.vstack(*proper).rank()))
 return dim,cylinder
def verify(c,pins=True):
 Draft202012Validator(json.loads(SCHEMA.read_text())).validate(c)
 if pins:
  for role,(rel,h) in INPUTS.items():
   if sha(ROOT/rel)!=h or c["source_refs"][role]!={"path":rel,"sha256":h}: raise AssertionError("pin")
 dim,cylinder=exact_replay()
 if dim!=24 or c["independent_replays"]["compact"]["full_commutant_complex_dimension"]!=24: raise AssertionError("compact")
 if c["independent_replays"]["compact"]["Hamiltonian"]!="positive spectral square root of H^2": raise AssertionError("H2")
 for chi in (-1,1):
  row=c["independent_replays"]["cylinder"][str(chi)]; ranks,stacked=cylinder[str(chi)]
  if row["proper_ranks"]!=ranks or ranks!=[32]*8 or row["stacked_BRST_defect_rank"]!=stacked: raise AssertionError("cylinder")
 if c["independent_replays"]["quartet"]!={"discriminant":"-2151","H_has_nonreal_spectrum":True}: raise AssertionError("quartet")
 rows={x["claim"]:x for x in c["typed_classification"]}
 if set(rows)!={"structured_positive_eta","unique_fundamental_symmetry","genuine_Mannheim_C","residual_BRST_descent","broken_PT_negative_control","nontrivial_ghost_normalizer_route"}: raise AssertionError("rows")
 if rows["genuine_Mannheim_C"]["compact_blocks"]!="NOT_ESTABLISHED_MISSING_INDEPENDENT_PT" or rows["residual_BRST_descent"]["cylinder_reduced"]!="OBSTRUCTED_IN_DECLARED_INVARIANT_COMMUTANT" or rows["nontrivial_ghost_normalizer_route"]["cylinder_reduced"]!="NOT_CLASSIFIED_OUTSIDE_DECLARED_INVARIANT_COMMUTANT": raise AssertionError("scope")
 if c["decision"]["conformal_gravity_unitarity"]!="NOT_ESTABLISHED" or c["decision"]["ghost_normalizer"]!="OPEN" or "analogy" not in c["scoped_analogy"]["Pais_Uhlenbeck_equal_frequency_Jordan"]: raise AssertionError("promotion")
def verify_receipt(r,c):
 if r["subject_result_id"]!=c["result_id"] or set(r["output_hashes"])!=set(OUTPUTS): raise AssertionError("receipt")
 for role,p in OUTPUTS.items():
  if r["output_hashes"][role]!=sha(p): raise AssertionError(role)
def main():
 c=json.loads(CERT.read_text()); verify(c); muts=[lambda x:x["independent_replays"]["compact"].update(full_commutant_complex_dimension=12),lambda x:x["independent_replays"]["compact"].update(Hamiltonian="H^2"),lambda x:x["typed_classification"][2].update(compact_blocks="CERTIFIED"),lambda x:x["typed_classification"][3].update(cylinder_reduced="DESCENDS"),lambda x:x["independent_replays"]["quartet"].update(H_has_nonreal_spectrum=False),lambda x:x["typed_classification"][5].update(cylinder_reduced="EXCLUDED"),lambda x:x["scoped_analogy"].update(Pais_Uhlenbeck_equal_frequency_Jordan="theorem"),lambda x:x["decision"].update(conformal_gravity_unitarity="ESTABLISHED")]
 for m in muts:
  q=copy.deepcopy(c);m(q)
  try:verify(q,pins=False)
  except (AssertionError,KeyError,TypeError,ValidationError):continue
  raise AssertionError("mutation accepted")
 verify_receipt(json.loads(RECEIPT.read_text()),c);print(f"PHASE2_CPT_FEASIBILITY_CLASSIFICATION_V1 independent verification: PASS ({len(muts)} mutations rejected)")
if __name__=="__main__":main()
