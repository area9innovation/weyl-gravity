#!/usr/bin/env python3
"""Construct exact finite Peter-Weyl Maxwell and massive-two-form Green kernels."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
import sympy as sp
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import laplacian

ROOT=Path(__file__).resolve().parents[1];PACKAGE=ROOT/"closed_universe_observers";CERTIFICATE=PACKAGE/"certificates/BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS.json";SCHEMA=PACKAGE/"schema/berger-finite-mode-maxwell-emitter-green-kernels-v1.schema.json";REPORT=PACKAGE/"reports/berger-finite-mode-maxwell-emitter-green-kernels.md"
DEPENDENCIES={"spectral":PACKAGE/"certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json","unary":PACKAGE/"certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json","profiles":PACKAGE/"certificates/BERGER_POSITIVE_ENERGY_DETECTOR_SELECTED_EMITTER_PROFILES.json"};SOURCE_FILES={"producer":Path(__file__),"verifier":PACKAGE/"verify_berger_mode_green_kernels.py","tests":PACKAGE/"tests/test_berger_mode_green_kernels.py","schema":SCHEMA,"report":REPORT}
def _sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def sine_kernel_series(A:sp.Matrix,tau:sp.Symbol,order:int=5,wrong_sign:bool=False)->sp.Matrix:
 sign=1 if wrong_sign else -1
 return sp.simplify(sum((sign**n*A**n*tau**(2*n+1)/sp.factorial(2*n+1) for n in range(order+1)),sp.zeros(A.rows)))
def wave_audit(two_j:int,p:int,mass2:sp.Expr=sp.Integer(0),wrong_sign:bool=False)->dict[str,Any]:
 tau=sp.symbols("tau",real=True);A=laplacian(two_j,p)+mass2*sp.eye(laplacian(two_j,p).rows);S=sine_kernel_series(A,tau,5,wrong_sign);res=sp.expand(sp.diff(S,tau,2)+A*S);defects=sum(sp.simplify(x.coeff(tau,k))!=0 for x in res for k in range(10))
 return {"two_j":two_j,"form_degree":p,"dimension":A.rows,"mass_squared":sp.sstr(mass2),"spatial_operator_rank":A.rank(),"initial_value_defect_count":sum(x!=0 for x in S.subs(tau,0)),"initial_derivative_defect_count":sum(x!=0 for x in sp.diff(S,tau).subs(tau,0)-sp.eye(A.rows)),"ode_coefficient_defect_count_through_tau9":defects,"kernel":"S_A(tau)=sum_n>=0 (-A)^n tau^(2n+1)/(2n+1)! = sin(tau sqrt(A))/sqrt(A), with zero-eigenvalue limit tau","retarded":"H(t-s) S_A(t-s)","advanced":"-H(s-t) S_A(t-s)=H(s-t) S_A(s-t)"}
def build()->dict[str,Any]:
 v={k:json.loads(p.read_text()) for k,p in DEPENDENCIES.items()};req={"spectral":"EXACT_FORM_LAPLACIAN_BLOCKS_EXPORTED","unary":"MASSIVE_TWO_FORM_ADVANCED_RETARDED_GREEN_CERTIFIED","profiles":"OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED"}
 for n,f in req.items():
  if v[n].get("flags",{}).get(f) is not True:raise AssertionError(f"dependency dropped: {n}.{f}")
 m0,m1=sp.symbols("m0_squared m1_squared",positive=True);audits=[]
 for j in range(3):
  audits += [wave_audit(j,0),wave_audit(j,1),wave_audit(j,1,m0),wave_audit(j,2,m1)]
 if any(a["initial_value_defect_count"] or a["initial_derivative_defect_count"] or a["ode_coefficient_defect_count_through_tau9"] for a in audits):raise AssertionError("mode Green audit failed")
 mutation=wave_audit(1,1,wrong_sign=True)
 if mutation["ode_coefficient_defect_count_through_tau9"]==0:raise AssertionError("Green sign mutation escaped")
 boundary="This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result constructs the retarded and advanced time kernels in every finite Berger Peter-Weyl form block by the entire matrix function S_A(tau)=sin(tau sqrt(A))/sqrt(A), defined by its exact power series and the zero-eigenvalue limit S_0=tau. Maxwell one-forms split into spatial Delta_0 and Delta_1 wave blocks; massive spacetime two-forms split into Delta_1+m_b^2 and Delta_2+m_b^2 blocks. Exact audits through two_j=2 verify the Cauchy jump and wave equation coefficientwise, including the Maxwell zero mode, while the imported Proca correction (I+m_b^-2 d delta) converts the normally hyperbolic two-form Green kernel to the physical Euler Green operator. A finite spectral block is not support-local and is not used as evidence for a full causal Green theorem. Compact-profile coefficients, infinite-sum tail bounds, evaluated Green images, and the absolute-g3 recoil coefficient remain open. No finite-parameter interacting or quantum claim is made."
 return {"schema":"closed-universe-berger-finite-mode-maxwell-emitter-green-kernels-v1","result_id":"BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS","setting_id":v["profiles"]["setting_id"],"claim_status":"EXACT_FINITE_MODE_GREEN_KERNELS_EXPORTED_INFINITE_PROFILE_SUM_OPEN","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{k:{"path":str(p.relative_to(ROOT)),"result_id":v[k]["result_id"],"sha256":_sha256(p)} for k,p in DEPENDENCIES.items()},"block_decomposition":{"Maxwell_one_form":"dt wedge Omega^0(S3) direct_sum Omega^1(S3), operators Delta_0 and Delta_1","massive_two_form":"dt wedge Omega^1(S3) direct_sum Omega^2(S3), operators Delta_1+m_b^2 and Delta_2+m_b^2","physical_emitter_Euler_green":"(I+m_b^-2 d delta) G_(P2+m_b^2),ret/adv"},"audited_kernels":audits,"mutation_results":[{"name":"flip_sine_kernel_recurrence_sign","detected":True,"defect_count":mutation["ode_coefficient_defect_count_through_tau9"]}],"flags":{"EXACT_FINITE_MODE_MAXWELL_GREEN_KERNELS_EXPORTED":True,"EXACT_FINITE_MODE_MASSIVE_TWO_FORM_GREEN_KERNELS_EXPORTED":True,"MAXWELL_ZERO_MODE_LIMIT_INCLUDED":True,"MODE_CAUCHY_JUMP_AND_ODE_CERTIFIED":True,"FINITE_TRUNCATION_SUPPORT_LOCAL":False,"PROFILE_HARMONIC_COEFFICIENTS_EVALUATED":False,"VALIDATED_INFINITE_MODE_TAIL_BOUND_EXPORTED":False,"ADVANCED_GREEN_IMAGES_EVALUATED":False,"DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED":False,"QUANTUM_CLAIM":False},"next_gate":"INTERVAL_ENCLOSE_FIXED_BUMP_MODE_COEFFICIENTS_AND_INFINITE_TAIL_THEN_COMPOSE_THE_EXACT_MODE_KERNELS","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES.values()]}}
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--emit",action="store_true");ap.add_argument("--check",action="store_true");z=ap.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n";CERTIFICATE.write_text(r) if z.emit else None
 if z.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale mode Green certificate")
 print("BERGER_FINITE_MODE_MAXWELL_EMITTER_GREEN_KERNELS generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
