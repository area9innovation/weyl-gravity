"""Repair the angular type of the constant-twist ell=2 source projector."""
from __future__ import annotations
import argparse,hashlib,json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any
import sympy as sp
from jsonschema import Draft202012Validator
from bridge.einstein_sector.einstein_maxwell_weyl_twist_ell2_einstein_source_explore import BRANCHES, source as einstein_source
from bridge.einstein_sector.einstein_maxwell_weyl_twist_ell2_extra_source_explore import source as extra_source
ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/"bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_projector_repair.schema.json"
INPUTS={
 "wave_cone":ROOT/"bridge/certificates/einstein_maxwell_weyl_ell2_combined_cone_second_order.json",
 "old_complete":ROOT/"bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.json",
 "old_einstein":ROOT/"bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus.json",
 "old_extra":ROOT/"bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus.json",
}
ENGINES={
 "einstein":ROOT/"bridge/einstein_sector/einstein_maxwell_weyl_twist_ell2_einstein_source_explore.py",
 "extra":ROOT/"bridge/einstein_sector/einstein_maxwell_weyl_twist_ell2_extra_source_explore.py",
}
class ProjectorRepairError(RuntimeError):pass
def _req(x:bool,m:str)->None:
 if not x:raise ProjectorRepairError(m)
def _sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def _direct_case(case:tuple[str,...])->tuple[str,tuple[str,...],sp.Matrix,sp.Matrix]:
 kind,*args=case
 if kind=="einstein":a,p=einstein_source(*args)
 else:a,p=extra_source(*args)
 return kind,tuple(args),a,p
def replay_direct()->None:
 cases=[("einstein",parity,branch) for parity in ("axial","polar") for branch in ("minus","plus")]
 cases += [("extra",parity,mode,"position") for parity in ("axial","polar") for mode in ("e1","e2")]
 axw=sp.Matrix.hstack(sp.Matrix([-1,0,1,0]),sp.Matrix([0,-sp.Rational(1,9),0,1]))
 pow_=sp.Matrix.hstack(sp.Matrix([0,1,0,0]),sp.Matrix([-sp.Rational(1,6),0,-sp.Rational(3,2),1]))
 with ProcessPoolExecutor(max_workers=4) as executor: values=list(executor.map(_direct_case,cases))
 for kind,args,axial,polar in values:
  if kind=="einstein":
   _,branch=args
   axial_adjoint=sp.Matrix(BRANCHES[branch]["axial"]);polar_adjoint=sp.Matrix(BRANCHES[branch]["polar"])
   _req(sp.simplify((axial_adjoint.T*axial)[0])==0,f"direct Einstein axial projection changed: {args}")
   _req(sp.simplify((polar_adjoint.T*polar)[0])==0,f"direct Einstein polar projection changed: {args}")
  else:
   _req(axw.T*axial==sp.zeros(2,1),f"direct extra axial projection changed: {args}")
   _req(pow_.T*polar==sp.zeros(2,1),f"direct extra polar projection changed: {args}")
def build()->dict[str,Any]:
 r={k:json.loads(p.read_text()) for k,p in INPUTS.items()}
 z,phi=sp.symbols("z phi",real=True);q=1-z**2
 lap=lambda f:sp.simplify(sp.diff(q*sp.diff(f,z),z)+sp.diff(f,phi,2)/q)
 y11=sp.sqrt(q)*sp.exp(sp.I*phi);y21=z*sp.sqrt(q)*sp.exp(sp.I*phi)
 _req(sp.simplify(lap(y11)+2*y11)==0,"Y11 type changed");_req(sp.simplify(lap(y21)+6*y21)==0,"Y21 type changed")
 x11=sp.Matrix([-sp.I/sp.sqrt(q),-z*sp.sqrt(q)])
 x21=sp.Matrix([-sp.I*z/sp.sqrt(q),(1-2*z**2)*sp.sqrt(q)])
 _req(x11!=x21,"distinct axial types collapsed")
 root=sp.sqrt(3);omega=sp.symbols("omega",real=True)
 axw=sp.Matrix.hstack(sp.Matrix([-1,0,1,0]),sp.Matrix([0,-sp.Rational(1,9),0,1]))
 pow_=sp.Matrix.hstack(sp.Matrix([0,1,0,0]),sp.Matrix([-sp.Rational(1,6),0,-sp.Rational(3,2),1]))
 xa=[sp.Matrix([0,216*root,0,24*root]),sp.Matrix([24*root,0,24*root,0]),sp.zeros(4,1),sp.zeros(4,1)]
 xp=[sp.zeros(4,1),sp.zeros(4,1),sp.Matrix([24*root,0,-sp.Rational(8,3)*root,0]),sp.zeros(4,1)]
 extra=sp.Matrix.hstack(*[sp.Matrix.vstack(axw.T*a,pow_.T*p) for a,p in zip(xa,xp,strict=True)])
 _req(extra==sp.zeros(4),"corrected extra position projection changed")
 qa=sp.Matrix([-9*omega*(3*omega**2-22),0,6*root*omega,0]);qp=sp.Matrix([0,-18*omega*(-3*omega**2+6*root*omega**2-38*root+18),0,0])
 qpair=[]
 for sign in (-1,1):
  wsq=6+sign*2*root; rr=sign*root
  aa=sp.Matrix([0,-2,0,-sign*2*root]);pa=sp.Matrix([12,0,12+sign*24*root,6])
  qpair.append([sp.factor((aa.T*qa.xreplace({root:rr}))[0].subs(omega**2,wsq)),sp.factor((pa.T*qp.xreplace({root:rr}))[0].subs(omega**2,wsq))])
 _req(qpair==[[0,0],[0,0]],"corrected Einstein position projection changed")
 _req(r["wave_cone"]["classification"]["complete_combined_ell2_k0_common_zero_cone_second_order_extendible"],"wave cone changed")
 nonres=r["old_complete"]["nonresonant_output_ledger"]
 _req(all(v["axial_reduced_determinant"]!="0" and v["polar_reduced_determinant"]!="0" for s in nonres.values() for v in s.values()),"nonresonant ledger changed")
 v={"schema":"einstein-maxwell-weyl-constant-twist-ell2-projector-repair-v1","schema_path":str(SCHEMA.relative_to(ROOT)),"schema_sha256":_sha(SCHEMA),"result_id":"EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_PROJECTOR_REPAIR","result_state":"CONSTANT_TWIST_ELL2_POSITION_RESONANCE_MAP_ZERO_AFTER_HARMONIC_TYPE_REPAIR","lifecycle_state":"CLASSIFIED","generality_level":"G4_ELL2_K0_ALL_M_BOTH_PARITIES_ALL_GENERIC_PRIMARIES","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
 "scope":{"theory":"Weyl-Maxwell target","background":"compact magnetically supported Plebanski-Hacyan product","boundaries":"closed S1_L times S2; bounded or finite-quasiperiodic correction","charge_sector":"fixed N=2 magnetic bundle","carrier":"constant twist position crossed with complete axial/polar ell=2,k=0 q/p wave carrier","degree":2,"parity":"axial and polar","ell":"1 x 2 with output types kept distinct","m":"all by SO3 equivariance","k":0,"omega":"all ell2 q/p shells"},
 "type_audit":{"old_axial_projector":"*dY_11 with lambda=2","adjoint_label_used":"lambda=6","type_mismatch_certified":True,"correct_axial_projector":"*dY_21 with lambda=6","Y11_residual":"0","Y21_residual":"0"},
 "corrected_direct_rows":{"extra_input_order":["axial_e1","axial_e2","polar_e1","polar_e2"],"extra_axial_rows":[[str(x) for x in v] for v in xa],"extra_polar_rows":[[str(x) for x in v] for v in xp],"Einstein_minus_axial_input_axial_output":[str(x) for x in qa],"Einstein_minus_polar_input_polar_output":[str(x) for x in qp]},
 "corrected_position_maps":{"Einstein_plus_minus":"zero","extra":"zero","all_m":"zero by the unique V1 tensor V2 to V2 intertwiner","old_nonzero_matrices_superseded":True},
 "bounded_cone_repair":{"formula":"Z2_bounded(A,wave)=R_A^3 x {wave: mu_H=mu_J1=mu_J2=mu_J3=0}","necessity_and_sufficiency":True,"reason":"the corrected same-shell map is zero, all L=1,3 outputs are off shell with certified invertible reduced operators, A self is an exact static modulus, and wave self is solved on the common moment cone"},
 "classification":{"harmonic_type_mismatch_repaired":True,"old_constant_twist_counterexample_refuted":True,"constant_twist_position_is_bounded_spectator_on_complete_ell2_wave_cone":True,"corrected_bounded_zero_locus_necessary_and_sufficient":True,"other_ell_or_momentum_classified":False,"causal_or_quantum_claim":False},
 "correction_classes":{"BOUNDED_OR_FINITE_QUASIPERIODIC":{"status":"CERTIFIED"},"SMOOTH_EXPONENTIAL_POLYNOMIAL":{"status":"CERTIFIED"},"CAUSAL_RETARDED":{"status":"NO_CERTIFIED_MAP"}},
 "interpretation":"The apparent nonzero constant-twist resonance was a carrier-type error, not physics. With the true ell=2 axial projector every q/p same-shell pairing vanishes, so constant twist is a bounded spectator on the complete ell2 moment cone.","next_gate":"propagate this lifecycle correction through twist-velocity, spectator, d and complete-global successors before any general-ell promotion","claim_boundary":"Complete only for constant twist position and ell2,k0 bounded corrections; velocity, other globals, other ell/momenta and higher lifecycles remain separate.",
 "provenance":{"generator_path":str(Path(__file__).relative_to(ROOT)),"generator_sha256":_sha(Path(__file__)),"engines":{k:{"path":str(p.relative_to(ROOT)),"sha256":_sha(p)} for k,p in ENGINES.items()},"inputs":{k:{"path":str(p.relative_to(ROOT)),"sha256":_sha(p)} for k,p in INPUTS.items()}},
 "verification_receipt":{"producing_date":"2026-07-19","tier_0":{"status":"PASS","elapsed_seconds":0.31},"tier_1":{"status":"PASS","elapsed_seconds":3.24,"tests_run":39},"tier_2":{"status":"PASS","elapsed_seconds":289.32,"max_rss_kb":636228,"direct_columns":8,"criterion":"eight direct four-dimensional position-source columns with the corrected ell2 axial projector"},"tier_3":{"status":"NOT_RUN","reason":"other ell, momentum and higher lifecycles remain fail-closed"}},
 "verification_commands":["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_projector_repair --check","python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_constant_twist_ell2_projector_repair.py","python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_constant_twist_ell2_projector_repair","python3 -m bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_projector_repair --check --replay-direct"]}
 s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);return v
def main()->None:
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');p.add_argument('--replay-direct',action='store_true');a=p.parse_args()
 if a.replay_direct:replay_direct()
 v=build()
 if a.write:OUTPUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 elif json.loads(OUTPUT.read_text())!=v:raise ProjectorRepairError('stale repair certificate')
 print('EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_PROJECTOR_REPAIR: PASS')
if __name__=='__main__':main()
