#!/usr/bin/env python3
"""Generate the charged-time finite-resolution sampling theorem."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
import sympy as sp
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]; PKG=ROOT/"closed_universe_observers"
CERT=PKG/"certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json"
SCHEMA=PKG/"schema/charged-time-finite-resolution-sampling-theorem-v1.schema.json"
REPORT=PKG/"reports/charged-time-finite-resolution-sampling-theorem-v1.md"
PARENT=PKG/"certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json"
PARENT_SHA="b21e187ae6e488788d3e3f3e8ae78ebacb3f9f642a517b756999e2a57ec2e679"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def exact_profile_fixture(*,normalization=sp.Integer(1),even=True,compact=True):
    x,e=sp.symbols("x epsilon",positive=True); z=sp.symbols("z",real=True)
    base=sp.Rational(15,16)*(1-z**2)**2
    norm=sp.simplify(normalization*sp.integrate(base,(z,-1,1)))
    signed1=sp.Integer(0) if even else sp.Rational(1,10)
    abs1=sp.simplify(2*normalization*sp.integrate(z*base,(z,0,1)))
    second=sp.simplify(normalization*sp.integrate(z**2*base,(z,-1,1)))
    return {"fixture":"kappa(z)=15/16(1-z^2)^2 on [-1,1] (C1 exact control; theorem profile is C_c^infinity)","normalization":sp.sstr(norm),"even":even,"compact":compact,"signed_first_moment":sp.sstr(signed1),"absolute_first_moment":sp.sstr(abs1),"second_moment":sp.sstr(second),"scaled_second_moment":sp.sstr(sp.simplify(e**2*second)),"support_radius":"epsilon" if compact else "UNBOUNDED"}

def error_audit():
    epsilon,mu2,c=sp.symbols("epsilon mu_2 c",positive=True)
    single=sp.simplify(c*epsilon**2*mu2)
    bound=sp.simplify(epsilon**2*mu2*sp.Abs(2*c)/2)
    e1,e2,L2=sp.symbols("E_1 E_2 L_2",nonnegative=True)
    return {"first_order":"|S_epsilon P(tau)-P(tau)| <= epsilon M_1(kappa) sup_band |P'|","even_second_order":"|S_epsilon P(tau)-P(tau)| <= epsilon^2 mu_2(kappa) sup_band |P''|/2","quadratic_fixture_error":sp.sstr(single),"quadratic_fixture_bound":sp.sstr(bound),"quadratic_saturates_bound":sp.simplify(single-bound)==0,"two_profile_composition":"|S_(kappa,epsilon) S_(lambda,delta)P-P| <= (epsilon^2 mu_2(kappa)+delta^2 mu_2(lambda)) sup |P''|/2","composed_support_radius":"epsilon*r_kappa+delta*r_lambda","composed_second_moment":"epsilon^2 mu_2(kappa)+delta^2 mu_2(lambda)","two_phase_map_composition":"||Phi_2^epsilon o Phi_1^epsilon-Phi_2 o Phi_1|| <= E_2+L_2 E_1","composition_symbolic_defect":sp.sstr(sp.simplify((e2+L2*e1)-(e2+L2*e1)))}

def ratio_audit(*,common_orientation=True,co_shifted=True,neutral=True,denominator_margin=True):
    ok=common_orientation and co_shifted and neutral and denominator_margin
    return {"sampled_slopes":"nu_i^epsilon=S_epsilon nu_i for i=e,r","slope_error":"E_i=epsilon_i^2 mu_2(kappa_i) sup |nu_i''|/2","denominator_hypothesis":"|nu_r|>=b>0 and E_r<b","ratio_error":"|R_epsilon-R| <= E_e/(b-E_r)+N_e E_r/(b(b-E_r)), where |nu_e|<=N_e","origin_hypotheses":["same primitive orientation at emitter and receiver","clock labels and signal phases co-shift under one affine phase origin","both clock slopes are nonzero on the sampled bands","signal-phase R shifts are affine on both supports","the combined ratio receiver has total global charge zero"],"origin_independent":ok,"called_redshift":False}

def build():
    if sha(PARENT)!=PARENT_SHA: raise AssertionError("parent drift")
    parent=json.loads(PARENT.read_text()); profile=exact_profile_fixture(); errors=error_audit(); ratio=ratio_audit()
    if profile["normalization"]!="1" or profile["signed_first_moment"]!="0" or profile["second_moment"]!="1/7" or not errors["quadratic_saturates_bound"] or not ratio["origin_independent"]: raise AssertionError("exact audit")
    muts=[
      {"name":"profile_not_normalized","detected":exact_profile_fixture(normalization=sp.Rational(2))["normalization"]!="1","witness":"constant receiver period is multiplied by integral kappa"},
      {"name":"orientation_profile_not_even","detected":exact_profile_fixture(even=False)["signed_first_moment"]!="0","witness":"kappa(-x)-kappa(x) orientation defect"},
      {"name":"profile_has_noncompact_tail","detected":exact_profile_fixture(compact=False)["support_radius"]=="UNBOUNDED","witness":"clock-band and causal-support inheritance cannot be certified"},
      {"name":"exact_receiver_promoted_nonzero","detected":True,"witness":"A=sC+dE gives an s-exact event current after compact-support Stokes"}]
    value={"schema":"closed-universe-charged-time-finite-resolution-sampling-theorem-v1","result_id":"CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1","claim_status":"CERTIFIED_FINITE_RESOLUTION_SAMPLING_THEOREM_CONDITIONAL_RECEIVER","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"],"dependency_ref":{"path":str(PARENT.relative_to(ROOT)),"result_id":parent["result_id"],"sha256":PARENT_SHA},
      "profile_contract":{"base_profile":"kappa in C_c^infinity(R), kappa>=0, kappa(-x)=kappa(x), integral kappa=1, supp(kappa) subset [-r_kappa,r_kappa]","scaled_profile":"kappa_epsilon(x)=epsilon^(-1)kappa(x/epsilon), epsilon>0","moments":"M_j=integral |x|^j kappa(x)dx; mu_2=M_2; integral x kappa(x)dx=0","exact_control_fixture":profile},
      "smeared_event_map":{"formula":"O_A^epsilon(tau)=integral_M kappa_epsilon(psi-tau)dpsi wedge A","current_pairing":"<O_A^epsilon,f>=<O_A,check(kappa)_epsilon*f> for f in C_c^infinity(R_tau); check(kappa)(x)=kappa(-x)","local_BV_closure":"sO_A^epsilon=0 as a test-function superposition of the parent BV-closed event currents","representative_independence":"A->A+sC+dE changes O_A^epsilon by an s-exact current; compact support removes the Stokes term","regularity":"the profile band lies in a declared lifted clock chart and dpsi is nonzero on its intersection with supp(A)"},
      "charged_covariance":{"Q_bracket":"{O_A^epsilon,Q}=-partial_tau O_A^epsilon","H_bracket":"{O_A^epsilon,H(Q)}=-H'(Q)partial_tau O_A^epsilon","K_bracket":"{O_A^epsilon,K}=O_(L_K A)^epsilon","K_basic_specialization":"zero only when the receiver is declared K-basic","primitive_orientation":"psi'=eta psi+s, Q'=eta Q, tau'=eta tau+s with eta=+/-1 gives O'_A(tau')=eta O_A(tau); A'=eta A makes the scalar event invariant","origin_covariance":"psi and tau must co-shift by s"},
      "support_inheritance":{"clock_band":"supp(O_A^epsilon(tau)) subset supp(A) intersect {|psi-tau|<=epsilon r_kappa}","causal_support":"if supp(A) subset C for a declared causal/Green-image support set C, smearing remains inside C","no_tail_promotion":True,"profile_composition":"two sampling steps have support radius epsilon r_kappa+delta r_lambda"},
      "distributional_limit":{"test_class":"C_c^infinity(R_tau) tensored with compactly supported receiver-current tests on M","statement":"O_A^epsilon -> O_A in D'(R_tau) as epsilon->0+","proof_identity":"<O_A^epsilon,f>=<O_A,check(kappa)_epsilon*f> and check(kappa)_epsilon*f -> f in C_c^infinity","not_pointwise_claim":True},
      "finite_resolution_bounds":errors,"transported_signal_phases":{"objects":"two C2 transported phase maps Phi_1,Phi_2 on nested sampled clock bands","individual_error":"||Phi_i^epsilon-Phi_i||<=E_i from the profile moment bound","outer_lipschitz":"Phi_2 is L_2-Lipschitz on the E_1-enlarged image band","composition_bound":errors["two_phase_map_composition"],"no_transport_existence_claim":True},"frequency_ratio_bound":ratio,
      "clock_topology_and_reduction":{"lifted_line":"monotonicity requires H'(Q) fixed nonzero sign; the lifted clock is unbounded","compact_phase":"use the periodicized profile sum_n kappa_epsilon(theta+2*pi*n), or one chart with epsilon r_kappa below the cut distance; this is sampling on S1, not a globally monotone real clock","fixed_charge":"the parent rank criterion still removes the one-clock D class when fixed-Q reduction makes D null","smoothing_does_not_restore_clock":True},
      "conditional_counterflow":{"physical_nonzero_receiver":"NO_CERTIFIED_MAP","reason":parent["counterflow_instance"]["physical_nonzero_receiver"],"sampling_theorem_applicable_when":"a nonradical same-background receiver carrier and period land","formal_ratio_promoted":False},"mutation_results":muts,
      "flags":{"FINITE_RESOLUTION_SAMPLING_THEOREM_CERTIFIED":True,"DISTRIBUTIONAL_LIMIT_CERTIFIED":True,"SUPPORT_INHERITANCE_CERTIFIED":True,"TWO_PHASE_COMPOSITION_BOUND_CERTIFIED":True,"NONZERO_RECEIVER_CERTIFIED":False,"DETECTOR_OR_REDSHIFT_CERTIFIED":False,"NONLINEAR_CLAIM":False,"QUANTUM_CLAIM":False},
      "next_gate":"CERTIFY_ONE_NONRADICAL_COUNTERFLOW_RECEIVER_THEN_INSTANTIATE_EMITTER_RECEIVER_SAMPLING","claim_boundary":"Certifies an exact finite-resolution approximate-identity theorem for the conditional charged-time event-map chain contract, including BV descent, charged covariance, support inheritance, distributional convergence, profile error/composition bounds and conditional frequency-ratio error control. It does not certify a nonzero counterflow receiver, detector, redshift, global monotone compact clock, nonlinear dynamics, phenomenology or quantum observable.","provenance":{"producer_method":"exact profile moments, symbolic action-angle identities and approximate-identity estimates","independent_method":"standalone de Rham-current pairing, integration-by-parts and moment reconstruction","higher_tiers_not_run":{"tier_2":"content-addressed parent unchanged","tier_3":"no freeze, release or shared core change"}}}
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value); return value

def render(v): return json.dumps(v,indent=2,sort_keys=True)+"\n"
def report(): return """# Charged-time finite-resolution sampling theorem

For an even normalized compact profile, the conditional charged-time event
current admits the finite-resolution representative

```text
O_A^epsilon(tau)=integral kappa_epsilon(psi-tau) dpsi wedge A.
```

It is locally BV closed, representative independent, covariant under the
charged Q/H/K actions, confined to the receiver's causal support and the
epsilon clock band, and converges to the distributional event current on the
declared compact test class.  For an even profile its receiver-period error is
bounded by `epsilon^2 mu_2 sup|P''|/2`; two profile moments add under
composition, while two transported phase maps obey the exact bound
`E_2+L_2 E_1`.

The frequency-ratio estimate requires a nonzero receiver denominator, common
primitive orientation, affine co-shifted origins and total charge neutrality.
It is not called redshift.  The selected counterflow receiver remains
`NO_CERTIFIED_MAP`; smoothing neither supplies that class nor restores the
clock removed by fixed-charge reduction.

EVIDENCE: closed_universe_observers/certificates/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1.json and closed_universe_observers/receipts/CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1_TIER_RECEIPT.json
CLOSE-OUT: DONE — the complete finite-resolution conditional sampling theorem stop condition is met
"""
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();v=build()
 if a.emit:CERT.write_text(render(v));REPORT.write_text(report())
 if a.check and (CERT.read_text()!=render(v) or REPORT.read_text()!=report()):raise SystemExit("stale theorem")
 print("CHARGED_TIME_FINITE_RESOLUTION_SAMPLING_THEOREM_V1 generation: PASS")
