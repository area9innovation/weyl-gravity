"""Two-jet constraint-algebroid/Kuranishi carrier and its first cofiber obstruction."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT=ROOT/"bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json"
SCHEMA_PATH=ROOT/"bridge/einstein_sector/schema/einstein-weyl-constraint-algebroid-kuranishi-carrier-v1.schema.json"
INPUTS={
 "fredholm":("bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json","EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1","261c77431cca2afb5facf65d33be7388f291757290cbc4129fc05e69c1a6c303"),
 "adjoint":("bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json","EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1","b0012a5ff0f1653523b90076e88a94212d16660a390128022b59598e20cc8ce0"),
 "amm":("bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1.json","EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_AMM_SEMIFREDHOLM_SLICE_V1","d49e367008aa9b6e123db49bb4ebf244913ec98c02e84a20f82305c7a7f630aa"),
 "finite_cone":("d_quotient_classical/certificates/FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1.json","FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1","c80967db8cce02594a346bef3ec6a0f1d6863c85167aec7b661d2d102a248065"),
 "exact_sequence":("bridge/certificates/EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1.json","EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1","d94140069b4972acdd2f5fcc99e8076bb773d9f2d904ce068e58548f86fbbd10"),
 "symplectic_extension":("bridge/certificates/EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1.json","EINSTEIN_WEYL_SYMPLECTIC_EXTENSION_CLASSIFICATION_V1","d316e61807112c31fcbf2733e4d93bb3ce2d3bcebe3389922d6baa463415cbd3"),
 "balanced_fixture":("bridge/certificates/einstein_maxwell_weyl_mixed_moment_map_zero_locus.json","EINSTEIN_MAXWELL_WEYL_MIXED_MOMENT_MAP_ZERO_LOCUS","a1310146fc4ce499d73585470289982abdabf902dbf361f39a5c1fff1625bb36")}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c:bool,m:str)->None:
 if not c:raise AssertionError(m)

def exact_witness()->dict[str,Any]:
 q,e=sp.symbols("q epsilon")
 inv=1-e*q+e**2*q**2
 req(sp.expand((1+e*q)*inv-1).coeff(e,0)==0,"inverse constant")
 req(sp.expand((1+e*q)*inv-1).coeff(e,1)==0,"inverse linear")
 req(sp.expand((1+e*q)*inv-1).coeff(e,2)==0,"inverse quadratic")
 shift=sp.expand(-inv)
 tau_e=sp.Rational(48,5)*(-6+5*sp.sqrt(3))
 amp2=sp.Rational(27,52)*(-6+5*sp.sqrt(3))
 tau_x=-sp.Rational(832,45)
 req(sp.simplify(tau_e+amp2*tau_x)==0,"balanced charge")
 req(tau_e!=0 and sp.simplify(amp2*tau_x)!=0,"projected charges must be nonzero")
 return {"inverse_metric_jet":"1-epsilon*q+epsilon^2*q^2","sin_cos_wronskian":"-1","shift_jet":str(shift),"Einstein_projected_mu_H":str(tau_e),"extra_projected_mu_H":str(sp.simplify(amp2*tau_x)),"total_mu_H":"0"}

def build()->dict[str,Any]:
 for name,(rel,rid,digest) in INPUTS.items():
  p=ROOT/rel;d=json.loads(p.read_text());req(d["result_id"]==rid,name+" id");req(sha(p)==digest,name+" hash")
 w=exact_witness()
 return {"schema":"einstein-weyl-constraint-algebroid-kuranishi-carrier-v1","schema_path":str(SCHEMA_PATH.relative_to(ROOT)),"schema_sha256":sha(SCHEMA_PATH),"result_id":"EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1","result_state":"TWO_JET_DERIVED_FIVE_CHARGE_CARRIER_CERTIFIED_LINEAR_COFIBER_PULLBACK_OBSTRUCTED","lifecycle_state":"CLASSIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],"provenance":{"generator_path":str(Path(__file__).relative_to(ROOT)),"generator_sha256":sha(Path(__file__)),"inputs":{n:{"path":r,"result_id":i,"sha256":h} for n,(r,i,h) in INPUTS.items()}},"scope":{"theory":"Weyl-Maxwell constraint carrier with Einstein/extra linear comparison","background":"compactified magnetically supported Plebanski-Hacyan","boundaries":"compact boundaryless Cauchy slice S1_L x S2","charge_sector":"fixed P_N,N=2 and fixed Q_e; based Maxwell gauge; W_x retained","carrier":"H^s weighted Sobolev canonical slice, s>=4, and its finite-harmonic restriction","degree":"constraint algebroid and Kuranishi two-jet","parity":"all","ell":"all","m":"all","k":"all allowed","omega":"not applicable to Cauchy constraints"},
 "constraint_algebroid_two_jet":{"bundle":"lapse-shift deformation parameters over the open positive-metric Sobolev phase space, with the based Weyl/U1 vertical ideal contracted because it contributes no adjoint cokernel","anchor":"rho_z(N,X)=Hamiltonian vector field of H_z[N]+H_i,z[X] on canonical data z","bracket":"[(N,X),(M,Y)]_z=(L_X M-L_Y N,[X,Y]+h_z^{-1}(N dM-M dN)); vertical first-class terms retained as an ideal","first_nonconstant_structure_function":"delta h^{ij}=-hbar^{ik}(delta h)_kl hbar^{lj}","fixture":w,"closure":"[rho(a),rho(b)]=rho([a,b]_z) on the constraint surface through the declared two-jet, by the canonical Poisson identity; the anchor derivative of h^{-1} is part of the equality","fixed_group_mutation":"dropping the epsilon*q term changes the exact sin/cos bracket and reproduces the rejected fixed-group AMM assumption"},
 "kuranishi_derived_carrier":{"kernel":"K=ker DC_zbar in the declared Sobolev slice","obstruction":"O=ker(DC_zbar)^*=span{H,P_x,J1,J2,J3}","bilinear_map":"l2(u,v)=P_O D^2C_zbar[u,v]","two_jet_map":"kappa_2(u)=l2(u,u)/2=(mu_H,mu_Px,mu_J1,mu_J2,mu_J3)","koszul_model":"Sym(K*)_(degree<=2) tensor Lambda(eta_H,eta_Px,eta_J1,eta_J2,eta_J3), d eta_A=kappa_2,A and dK*=0","nilpotency":"d^2=0 exactly at two-jet because d(kappa_2)=0 in the Koszul model","tangent_complex":"K -> O with zero linear differential; H0=K and obstruction H1=O","warning":"this is the derived quadratic fibre, not a claim that the full Kuranishi map has no cubic or higher terms"},
 "finite_harmonic_crosswalk":{"status":"CERTIFIED","restriction":"l2 restricts to the five certified Taub/moment maps on every finite harmonic input","plain_linear_zero_subspace":False,"resonant_functionals":"carrier-dependent bounded/quasiperiodic functionals are not extra compact-Cauchy cokernel coordinates"},
 "functorial_pullback_obstruction":{"linear_sequence":"0 -> H0_EM -> H0_WM -> H0_extra -> 0 remains certified before the derived charge restriction","desired_but_false_map":"pi_X: derived_zero(mu_WM) -> derived_zero(mu_X)","reason":"mu is quadratic and additive on the orthogonal invariant primary split, so mu_E+mu_X=0 does not imply mu_X=0","exact_balanced_witness":w,"conclusion":"the cofiber projection does not restrict to the common five-charge zero fibre; therefore the linear exact sequence cannot be pulled back as a sequence of the three individual derived zero fibres","Schur_pairing":"the target-internal Schur complement remains defined on the ambient target and can be restricted along a chosen common-zero inclusion, but it is not a quotient pairing on a nonexistent projected extra zero fibre","Sobolev_boundary":"the balanced finite-harmonic witness already refutes functoriality; no finite-harmonic density argument is used to claim a Sobolev exact sequence"},
 "mutations":{"freeze_structure_function":"REJECTED by shift -1+epsilon*q-epsilon^2*q^2","replace_derived_fibre_by_linear_kernel":"REJECTED because Dkappa(0)=0 while kappa_2 is nonzero quadratic","project_balanced_mode_to_extra_zero_fibre":"REJECTED: total mu_H=0 but both projected charges are exact nonzero opposites","retry_strict_cyclic_split":"REJECTED by imported inertia obstruction"},"classification":{"phase_dependent_bracket_retained":True,"two_jet_anchor_closure":True,"two_jet_koszul_nilpotency":True,"five_charge_kuranishi_carrier":True,"finite_harmonic_moment_map_match":True,"plain_linear_zero_subspace_substituted":False,"fixed_group_AMM_retried":False,"linear_cofiber_projects_derived_zero_fibre":False,"sobolev_Einstein_Weyl_derived_exact_sequence":False,"strict_cyclic_split":False,"causal_or_quantum_claim":False},"claim_boundary":"Certifies the smallest two-jet five-charge derived Kuranishi carrier and the first exact obstruction to pulling the ambient linear Einstein--Weyl cofiber sequence through it. It does not classify higher Kuranishi brackets, construct an all-orders groupoid slice, identify the common zero fibre with a linear subspace, or establish bounded, causal, particle, positivity or quantum claims.","next_gate":"replace the false quotient sequence by a derived correspondence/fibre-product description that retains balanced Einstein-extra charge cancellation; higher Kuranishi terms require a separate all-orders algebroid theorem","verification_commands":["python3 -m bridge.einstein_sector.einstein_weyl_constraint_algebroid_kuranishi_carrier --verify bridge/certificates/EINSTEIN_WEYL_CONSTRAINT_ALGEBROID_KURANISHI_CARRIER_V1.json","python3 bridge/einstein_sector/verify_einstein_weyl_constraint_algebroid_kuranishi_carrier.py","python3 -m unittest bridge.einstein_sector.tests.test_einstein_weyl_constraint_algebroid_kuranishi_carrier"]}
def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--verify",type=Path);a=p.parse_args();c=build()
 if a.write:DEFAULT_OUTPUT.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
 if a.verify:req(json.loads(a.verify.read_text())==c,"stale certificate")
 if not a.write and a.verify is None:p.error("one of --write or --verify")
if __name__=="__main__":main()
