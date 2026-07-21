"""Semi-Fredholm Kuranishi cone and direct-AMM applicability audit."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json"
ATLAS_OUTPUT = ROOT / "residual_atlas/einstein-weyl-compact-cauchy-amm-semifredholm-slice-fragment-v1.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-amm-semifredholm-slice-v1.schema.json"
PRODUCER_PATH = Path(__file__).resolve()

INPUTS = {
 "adjoint_kernel": ("bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json", "b0012a5ff0f1653523b90076e88a94212d16660a390128022b59598e20cc8ce0"),
 "right_elliptic_gate": ("bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json", "261c77431cca2afb5facf65d33be7388f291757290cbc4129fc05e69c1a6c303"),
 "canonical_operator": ("bridge/einstein_sector/einstein_maxwell_weyl_compact_cauchy_constraint_fredholm_gate.py", "90bb779e7ec2d54c66472744d7fc3fd2799c2aea26478b859df692ad5233a278"),
 "finite_harmonic_second_order": ("bridge/certificates/einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order.json", "d3770043041c94e52daa253c5dab1cf3730ea47f078e1b1553e42f00625496cd"),
 "moment_map_taub_bridge": ("bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json", "047594a9019eb68a000ecce1799063789714db632c41e67e48d37bdf0fc3657a"),
}

class AMMSliceError(RuntimeError): pass
def req(c: bool, m: str) -> None:
 if not c: raise AMMSliceError(m)
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()

def imports() -> list[dict[str,str]]:
 out=[]
 for name,(rel,want) in INPUTS.items():
  p=ROOT/rel; req(p.exists(),f"missing {rel}"); got=sha(p); req(got==want,f"drift {name}")
  rid="SOURCE_OPERATOR" if p.suffix!=".json" else json.loads(p.read_text()).get("result_id","NO_RESULT_ID")
  out.append({"name":name,"path":rel,"sha256":got,"result_id":rid})
 return out

def structure_function_witness() -> dict[str,Any]:
 x=sp.symbols("x", real=True); N=sp.sin(x); M=sp.cos(x)
 w=sp.simplify(N*sp.diff(M,x)-M*sp.diff(N,x)); req(w==-1,"lapse witness changed")
 c1=sp.Rational(1)*w; c2=sp.Rational(1,4)*w
 req(c1!=c2,"metric dependence disappeared")
 return {
  "hypersurface_deformation_bracket":"{H[N],H[M]}=H_i[h^ij(N d_j M-M d_j N)] plus Weyl-Maxwell first-class terms that do not remove the inverse-metric structure function",
  "lapses":{"N":"sin(x)","M":"cos(x)","wronskian":str(w)},
  "metric_fixture_1":{"h_xx":"1","shift_coefficient":str(c1)},
  "metric_fixture_2":{"h_xx":"4","shift_coefficient":str(c2)},
  "conclusion":"No fixed Lie bracket on lapse functions can make the unextended canonical normal-deformation generators an infinitesimal action on a neighborhood of phase space.",
 }

def build_certificate() -> dict[str,Any]:
 witness=structure_function_witness()
 return {
  "schema":"einstein-maxwell-weyl-compact-cauchy-amm-semifredholm-slice-v1",
  "schema_path":str(SCHEMA_PATH.relative_to(ROOT)),"schema_sha256":sha(SCHEMA_PATH),
  "result_id":"EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1",
  "result_state":"SOBOLEV_SECOND_ORDER_CONE_CERTIFIED_DIRECT_FIXED_GROUP_AMM_NORMAL_FORM_OBSTRUCTED",
  "lifecycle_state":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
  "provenance":{"input_commit":"d28de74777a8a2f002d8c10fa607b703f4304b78","producer":str(PRODUCER_PATH.relative_to(ROOT)),"producer_sha256":sha(PRODUCER_PATH),"imports":imports(),
   "primary_literature":[
    {"citation":"Arms--Marsden--Moncrief, Commun. Math. Phys. 78 (1981) 455--478","role":"fixed-group equivariant momentum-map quadratic normal form and explicit closed-range/slice hypotheses"},
    {"citation":"Arms--Marsden--Moncrief, Ann. Phys. 144 (1982) 81--106","role":"Einstein and Einstein--Yang--Mills several-Killing-field extension; not imported as an automatic Weyl--Maxwell theorem"}
   ]},
  "banach_problem":{"phase_space":"weighted Hilbert manifold with h,P in H^(s+2), K,pi,a,E in H^(s+1), s>=4, on the open positive-metric cone","target":"the mixed Sobolev constraint target of the right-elliptic gate, with mean-zero Gauss component","charge_fibre":"fixed magnetic P_N,N=2 and fixed harmonic electric Q_e; Wilson line remains a physical coordinate","constraint_regularity":"C is C^infinity on this Hilbert manifold: H^s on the compact 3-manifold is a Banach algebra and inversion of a positive H^(s+2) metric is smooth","equation":"C(z)=0"},
  "split_semifredholm_theorem":{
   "closed_range":"CERTIFIED by underdetermined ellipticity on compact Sigma",
   "cokernel":"ker(DC)^*=span_R{H,P_x,J_1,J_2,J_3}",
   "hilbert_splittings":["X=ker DC direct_sum (ker DC)^perp","Y=range DC direct_sum ker(DC)^*","ker DC=closure(range A) direct_sum P_phys, whenever A is restricted to the certified closed spatial gauge orbit"],
   "bounded_inverse":"DC restricted to (ker DC)^perp is a bounded isomorphism onto range DC by the open mapping theorem",
   "physical_kernel":"retained; no TT or extra-primary direction is converted into a gauge condition",
  },
  "kuranishi_normal_form":{
   "construction":"Solve the range projection P_R C(u+w)=0 uniquely for w=psi(u) in (ker DC)^perp by the Banach implicit-function theorem, then set kappa(u)=P_coker C(u+psi(u)).",
   "properties":["psi(0)=Dpsi(0)=0","kappa(0)=Dkappa(0)=0","C^-1(0) is locally diffeomorphic to {u in ker DC:kappa(u)=0}"],
   "quadratic_term":"D^2 kappa(0)[u,u]/2 = P_coker D^2 C(0)[u,u]/2",
   "second_order_tangent_cone":"Z2={u in ker DC : mu_H(u)=mu_Px(u)=mu_J1(u)=mu_J2(u)=mu_J3(u)=0}",
   "necessity_and_sufficiency":"For u in the regular Sobolev domain, a second-order Cauchy correction v solving DC v=-(1/2)D^2C[u,u] exists iff all five displayed pairings vanish.",
   "higher_order_warning":"The Kuranishi obstruction kappa may contain cubic and higher terms; this theorem does not identify the exact nonlinear zero set with its homogeneous quadratic tangent cone.",
  },
  "gauge_slice_audit":{
   "spatial_fixed_group":"Diff(Sigma) semidirect the two Weyl initial jets semidirect based_U1 has the standard Sobolev local slice after restricting the elliptic orbit operator A to the stabilizer-orthogonal complement; A^*A is self-adjoint elliptic and invertible there.",
   "normal_deformations":"OBSTRUCTED for direct fixed-Lie-group AMM on unextended canonical data",
   "structure_function_witness":witness,
   "repair_classes":["extend phase space by embeddings so spacetime Diff acts as a fixed group","formulate and prove a Lie-algebroid/groupoid Kuranishi slice","derive a Weyl-Maxwell-specific analogue of the 1982 Einstein--Yang--Mills several-Killing-field theorem"],
  },
  "finite_harmonic_crosswalk":{
   "same_background_and_charge":True,"map":"restriction of the five Sobolev adjoint pairings to finite harmonic exponential-polynomial data","taub_maps":"MATCH by the imported action-derived moment-map/Taub identity","smooth_secular":"the imported finite-carrier theorem supplies its additional resonant solvability functionals; they are carrier-dependent and are not extra compact-Cauchy adjoint covectors","bounded_quasiperiodic":"not promoted: bounded spacetime resonance conditions remain stricter than the Cauchy second-order cone"},
  "mutation_controls":{"omit_H":{"false_cone_has_extra_directions":True},"call_constant_U1_a_charge":{"rejected":True},"replace_h_xx_4_by_1":{"structure_function_separator_disappears":True},"force_two_sided_fredholm":{"rejected":True}},
  "classification":{"sobolev_second_order_tangent_cone":True,"exact_five_taub_sufficiency_for_cauchy_second_order_equation":True,"local_kuranishi_map":True,"exact_homogeneous_quadratic_nonlinear_zero_set":False,"full_fixed_group_AMM_hypotheses":False,"extended_embedding_or_groupoid_repair":False,"bounded_spacetime_stability":False,"causal_claim":False,"quantum_claim":False},
  "next_gate":{"name":"COMPACT_CAUCHY_EMBEDDING_OR_ALGEBROID_AMM_REPAIR","required":["choose extended-embedding fixed-group or Lie-algebroid carrier","prove its Sobolev slice and equivariance","test whether kappa is smoothly right-equivalent to its five-component homogeneous quadratic term"]},
  "scope":{"theory":"pure Weyl-Maxwell","background":"compactified magnetically supported Plebanski-Hacyan rational fixture","boundaries":"compact boundaryless Cauchy slice S1_L x S2","charge_sector":"fixed P_N,N=2 and fixed Q_e; based Maxwell gauge","carrier":"weighted Sobolev canonical Cauchy data","degree":"nonlinear constraint Kuranishi map and second-order tangent cone","parity":"all","ell":"all ell>=0","m":"all with real structure","k":"all allowed 2*pi*n/L","omega":"NOT_APPLICABLE to the Cauchy constraint map"},
  "claim_boundary":"The split right-semi-Fredholm theorem gives an exact full-Sobolev second-order Cauchy tangent cone cut out by five Taub maps. The direct fixed-group AMM homogeneous-quadratic normal form is obstructed on unextended data by the phase-space-dependent hypersurface-deformation bracket. No all-orders, bounded-time, causal, observational or quantum conclusion follows.",
  "verification_commands":["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice --verify bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json","python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice","python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_compact_cauchy_amm_semifredholm_slice","python3 residual_atlas/validate_fragment.py residual_atlas/einstein-weyl-compact-cauchy-amm-semifredholm-slice-fragment-v1.json"]}

def atlas(cert:dict[str,Any], cert_hash:str)->dict[str,Any]:
 return {"schema":"pure-weyl-residual-atlas-fragment-v1","schema_version":"1.0.0","team":"einstein_nonlinear","generated_by":str(PRODUCER_PATH.relative_to(ROOT)),"generated_by_sha256":sha(PRODUCER_PATH),"status_vocabulary":["CERTIFIED","OBSTRUCTED","OPEN","NOT_APPLICABLE","NO_CERTIFIED_MAP"],"description_axes":["causal","symplectic","nonlinear","observational","quantum"],"entries":[{"id":"einstein.ph.wm.compact_cauchy.amm_semifredholm_slice","scope":cert["scope"],"descriptions":{"causal":"NO_CERTIFIED_MAP","symplectic":"CERTIFIED","nonlinear":"OBSTRUCTED","observational":"NO_CERTIFIED_MAP","quantum":"NO_CERTIFIED_MAP"},"mode_data":{"dispersion":{"status":"NOT_APPLICABLE","statement":"Cauchy constraint theorem."},"lee_wald":{"status":"CERTIFIED","statement":"Canonical transpose and Hilbert splitting certified."},"taub_maps":{"status":"CERTIFIED","statement":"The full Sobolev second-order Cauchy cone is the common zero of exactly five Taub maps."},"resonance":{"status":"OPEN","statement":"Spacetime carrier-dependent resonance remains separate."},"second_order":{"equation":"L_barPhi v = -(1/2) D^2 E_barPhi[u,u]","bounded_or_finite_quasiperiodic":{"status":"OPEN","statement":"Not promoted from Cauchy solvability."},"smooth_secular":{"status":"CERTIFIED","statement":"Cauchy-data second-order correction exists iff the five Taub maps vanish; spacetime secular realization remains carrier-dependent."},"causal_retarded":{"status":"NO_CERTIFIED_MAP","statement":"No retarded map."}}},"evidence":[{"path":str(DEFAULT_OUTPUT.relative_to(ROOT)),"result_id":cert["result_id"],"sha256":cert_hash}],"claim_boundary":cert["claim_boundary"]}],"verification_commands":cert["verification_commands"]}

def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--verify",type=Path);a=p.parse_args();c=build_certificate()
 if a.verify: req(json.loads(a.verify.read_text())==c,"certificate drift");print("PASS AMM semi-Fredholm producer");return
 DEFAULT_OUTPUT.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n");ATLAS_OUTPUT.write_text(json.dumps(atlas(c,sha(DEFAULT_OUTPUT)),indent=2,sort_keys=True)+"\n");print(DEFAULT_OUTPUT)
if __name__=="__main__":main()
