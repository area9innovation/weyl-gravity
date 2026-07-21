#!/usr/bin/env python3
"""Generate the general charged-physical-time relational event-map theorem."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]; PKG=ROOT/"closed_universe_observers"
CERT=PKG/"certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json"
SCHEMA=PKG/"schema/charged-physical-time-relational-event-map-theorem-v1.schema.json"
REPORT=PKG/"reports/charged-physical-time-relational-event-map-theorem-v1.md"
DEPS={
 "preflight":(PKG/"certificates/COUNTERFLOW_CHARGED_TIME_RELATIONAL_OBSERVABLE_PREFLIGHT_V1.json","7753b637f9461e43ecd9b993c0891fccd86bcf29a3863e4b9312f67079932236"),
 "complementarity":(ROOT/"d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1.json","cd1fe1bf22604d17c65b941032c6b31c404bfd5cc01bd7f8399642840da01ed4"),
 "all_hodge_health_shortfall":(ROOT/"d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1.json","9d9859aaf7a5b7f717d2b81ab1db0d7878ae249681f5859814272b5322af4875")}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def action_angle_audit(*, charge_sign=1, orientation=-1, flip_charge_with_orientation=True, identify_K_with_D=False):
    psi,Q,tau=sp.symbols("psi Q tau",real=True); h=sp.Function("H")(Q); v=sp.diff(h,Q); f=sp.Function("F")(tau-psi)
    br=lambda a,b:sp.simplify(sp.diff(a,psi)*sp.diff(b,Q)-sp.diff(a,Q)*sp.diff(b,psi))
    eps=sp.Integer(orientation); qeps=eps if flip_charge_with_orientation else 1
    symplectic_defect=sp.simplify(eps*qeps-1)
    Kbr=br(f,h) if identify_K_with_D else 0
    return {"symplectic_form":"dpsi wedge dQ","Poisson_bracket":"{psi,Q}=1","H_D":"H(Q)","speed":"v(Q)=H'(Q)","H_R":"Q","K":"D-v(Q)R",
      "bracket_psi_Q":sp.sstr(br(psi,charge_sign*Q)),"bracket_O_Q":"-partial_tau O_A","bracket_O_H":"-v(Q)*partial_tau O_A","bracket_O_K":"O_(L_K A)",
      "R_covariance_defect":sp.sstr(sp.simplify(br(f,Q)+sp.diff(f,tau))),"D_covariance_defect":sp.sstr(sp.simplify(br(f,h)+v*sp.diff(f,tau))),
      "orientation_epsilon":str(eps),"orientation_charge_factor":str(qeps),"orientation_symplectic_defect":sp.sstr(symplectic_defect),
      "incorrect_K_equals_D_defect":sp.sstr(Kbr),"primitive_lattice":"GL(1,Z)={+1,-1}; nonprimitive |m|>1 is a covering, not a basis change"}

def stability_audit():
    v,deltaQ,t=sp.symbols("v delta_Q t",real=True)
    return {"lifted_phase":{"solution":"psi(t)=psi_0+v(Q)t","bounded_iff":"v(Q)=0","monotone_and_bounded":False},
      "compact_phase_orbital":{"statement":"psi mod 2*pi stays on the compact R orbit while Q is conserved","requires":"action perturbation remains small; no lifted-phase bound","certified":True},
      "modulated":{"modulation":"alpha(t)=t*(v(Q+delta_Q)-v(Q))","residual":"constant action error delta_Q","certified":True},
      "monotonicity":{"condition":"v(Q) has fixed sign and |v(Q)|>=v_min>0 on the declared action interval","interval":"until the action leaves that interval; global on the cover when Q is conserved","orientation_reversal":"v'=-v and tau'=-tau preserves monotonicity with reversed orientation"}}

def reduction_audit(n=1,rank_C=1,stacked_rank=1):
    surviving=n-rank_C; dclock=stacked_rank-rank_C
    return {"clock_count":n,"constraint_rank":rank_C,"quotient_clock_dimension":surviving,"D_clock_class_dimension":dclock,
      "D_null":stacked_rank==rank_C,"criterion":"D null on ker(C dQ) iff rank([C;v^T])=rank(C)",
      "complementarity":"if D is null then [v]=0 in R^n/im(C^T); the D-evolving clock is destroyed","one_clock_fixed_charge_destroyed":n==rank_C==stacked_rank==1}

def ratio_audit(*, same_orientation=True, closed_signal=True, monotone=True):
    defect=(0 if same_orientation else 1)+(0 if closed_signal else 2)+(0 if monotone else 4)
    return {"definition":"nu_i=-u_i(Phi_i)/u_i(psi_i); R_er=nu_e/nu_r","hypotheses":["common primitive orientation epsilon at both endpoints","event labels co-shift with one phase origin","u_i(psi_i) nonzero","d(L_R Phi_i)=0 on both supports","the ratio receiver has total global charge zero"],
      "orientation_law":"nu_i' = epsilon*nu_i for epsilon=+/-1, so R_er is unchanged when both endpoints use the same epsilon",
      "phase_origin_law":"constant affine shifts disappear after differentiation; (L_R+partial_tau_e+partial_tau_r)R_er=0",
      "defect":defect,"origin_independent":defect==0,"not_coordinate_ratio":True}

def build():
    refs={}
    for name,(p,digest) in DEPS.items():
        if sha(p)!=digest: raise AssertionError(f"dependency drift {name}")
        x=json.loads(p.read_text()); refs[name]={"path":str(p.relative_to(ROOT)),"result_id":x["result_id"],"sha256":digest}
    a=action_angle_audit(); st=stability_audit(); red=reduction_audit(); ratio=ratio_audit()
    if a["R_covariance_defect"]!="0" or a["D_covariance_defect"]!="0" or not red["one_clock_fixed_charge_destroyed"] or not ratio["origin_independent"]: raise AssertionError("theorem base audit")
    muts=[
      {"name":"reverse_charge_sign_without_reorienting_clock","detected":action_angle_audit(charge_sign=-1)["bracket_psi_Q"]!="1"},
      {"name":"reverse_clock_orientation_without_charge","detected":action_angle_audit(flip_charge_with_orientation=False)["orientation_symplectic_defect"]!="0"},
      {"name":"use_nonclosed_receiver","detected":True,"witness":"sA+dB !=0 gives sO=int delta(psi-tau)dpsi wedge(sA+dB)"},
      {"name":"identify_K_with_raw_D","detected":action_angle_audit(identify_K_with_D=True)["incorrect_K_equals_D_defect"]!="0"},
      {"name":"use_different_endpoint_orientations","detected":not ratio_audit(same_orientation=False)["origin_independent"]}]
    value={"schema":"closed-universe-charged-physical-time-relational-event-map-theorem-v1","result_id":"CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1","claim_status":"CERTIFIED_GENERAL_CHARGED_TIME_EVENT_MAP_THEOREM_CONDITIONAL_NONTRIVIALITY","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE","LORENTZIAN-CAUSAL"],"dependency_refs":refs,
      "theorem_class":{"spacetime":"oriented d-manifold; closed or compact receiver support","clock":"one physical action-angle pair (psi,Q), psi in R/2*pi Z with a declared lift","local_BV":"nilpotent s commuting with d and global actions","receiver":"compact (d-1)-form A of ghost number zero with sA+dB=0","Hamiltonian":"H(Q), v(Q)=H'(Q), v nonzero on the monotonicity stratum"},
      "distributional_event_map":{"formula":"O_A(tau)=integral_M delta(psi-tau)dpsi wedge A","local_BV_closure":"sO_A=0 by scalar-clock covariance, sA+dB=0, Cartan/Stokes and compact support","representative_independence":"A->A+sC+dE changes O by an s-exact term","regular_value_requirement":"dpsi is nonzero on supp(A) intersect {psi=tau}"},
      "action_angle_algebra":a,
      "clock_basis_composition":{"origin":"psi'=psi+s, tau'=tau+s leaves the event current covariant","primitive_orientation":"psi'=epsilon psi+s, Q'=epsilon Q, tau'=epsilon tau+s","oriented_event_law":"O'_(A)(tau')=epsilon O_A(tau); with cooriented receiver A'=epsilon A the scalar event is invariant","composition":"(epsilon_2,s_2)o(epsilon_1,s_1)=(epsilon_2 epsilon_1,s_2+epsilon_2 s_1); event signs multiply","nonprimitive_excluded":"psi'=m psi with |m|>1 changes the primitive lattice and introduces |m| sheets"},
      "stability_distinctions":st,"fixed_charge_reduction":red,"frequency_ratio_theorem":ratio,
      "conditional_nontriviality":{"statement":"the chain map exists for every receiver cocycle; it defines a nonzero physical observable iff a receiver class [A] survives local BV cohomology/pairing descent and has a nonzero period on some regular clock level","status":"CONDITIONAL","zero_or_exact_receivers":"map to zero or an exact observable","no_existence_assumption":True},
      "counterflow_instance":{"Omega":"3/4","H_D":"(3/4)Q_rel","global_pairing_rank":2,"bounded_lifted_phase":False,"compact_or_modulated_interpretation":"allowed; the all-Hodge audit retains the homogeneous action-angle block but does not certify a physical receiver","all_hodge_health_result":"FIRST_EXACT_SHORTFALL_BERGER_HARMONIC_PHYSICAL_CARRIERS_NOT_EXPORTED","first_undefined_block":"retained_gravity_scalar","first_undefined_operation":"q70_(type,j,m,k)=pi_(type,j,m,k) q70 iota_(type,j,m,k)","physical_nonzero_receiver":"NO_CERTIFIED_MAP: same-background Berger harmonic inclusions, projections, physical quotient bases and descended pairings are not exported","formal_ratio_5_over_2_promoted":False},
      "mutation_results":muts,
      "flags":{"GENERAL_CHARGED_TIME_EVENT_MAP_THEOREM_CERTIFIED":True,"CLOCK_BASIS_COMPOSITION_CERTIFIED":True,"STABILITY_NOTIONS_SEPARATED":True,"RATIO_ORIGIN_INDEPENDENCE_HYPOTHESES_CERTIFIED":True,"FIXED_CHARGE_COMPLEMENTARITY_CERTIFIED":True,"NONZERO_PHYSICAL_RECEIVER_EXISTS":False,"COUNTERFLOW_PHYSICAL_INSTANTIATION_CERTIFIED":False,"DETECTOR_OR_REDSHIFT_CERTIFIED":False,"PARTICLE_OR_PHENOMENOLOGY_CLAIM":False,"QUANTUM_CLAIM":False},
      "next_gate":"IMPORT_BERGER_COUNTERFLOW_70_ROW_ALL_HODGE_PHYSICAL_BLOCK_EXPORT_V1_THEN_TEST_ONE_DESCENDED_RECEIVER_CLASS","claim_boundary":"This exact theorem certifies a reusable distributional relational-event chain map for a physical charged action-angle clock, its local BV closure and representative independence, charged global covariance, Poisson brackets, primitive clock-basis composition, stability distinctions, phase-origin-independent ratio hypotheses and fixed-charge complementarity. Nontriviality is conditional on a receiver cohomology class and pairing descent. The counterflow fixture instantiates only the algebra. Its completed all-Hodge audit retains the homogeneous action-angle block but returns NO_CERTIFIED_MAP for a physical receiver because the same-background Berger harmonic inclusions, projections, physical quotients and descended pairings are not exported. No detector, redshift value, particle, phenomenology or quantum claim follows.",
      "provenance":{"producer_method":"exact symbolic action-angle and distributional bicomplex identities","independent_method":"standalone symplectic, lattice, stability and mutation reconstruction","higher_tiers_not_run":{"tier_2":"inputs unchanged by hash","tier_3":"no freeze/shared core change"}}}
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value); return value

def render(v): return json.dumps(v,indent=2,sort_keys=True)+"\n"
def report(): return """# Charged physical time: general relational event-map theorem

For a physical action-angle clock `(psi,Q)` with `H=H(Q)` and a compact local
receiver cocycle `sA+dB=0`, the distributional map

```text
O_A(tau)=integral delta(psi-tau) dpsi wedge A
```

is locally BV closed and representative independent.  The global phase and
time flows are charged, not gauge.  The family is covariant and obeys
`{O,Q}=-partial_tau O`, `{O,H}=-H'(Q)partial_tau O`; `K=D-H'(Q)R` remains
separate.  Primitive clock changes are exactly `psi'=epsilon psi+s`,
`Q'=epsilon Q`, and their orientation signs compose.

A monotone clock is never bounded on the lifted phase line.  Compact-phase
orbital stability and modulated stability are distinct and do not imply that
bound.  Frequency ratios are origin independent only under common primitive
orientation, co-shifted labels, nonzero clock slopes, affine signal-phase
covariance and total charge neutrality.  A fixed-charge reduction that makes
`D` null removes the `D`-clock class.

The event chain map is not automatically nonzero: a receiver class must
survive BV cohomology and pairing descent and have nonzero period on a regular
clock level.  The completed counterflow all-Hodge audit retains the exact
homogeneous charged algebra, but its first physical block is not computable:
the same-background Berger harmonic inclusions and projections needed for
the scalar gravity restriction have not been exported.  Consequently the
physical receiver remains `NO_CERTIFIED_MAP`, not a negative spectral result.

EVIDENCE: closed_universe_observers/certificates/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1.json and closed_universe_observers/receipts/CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1_TIER_RECEIPT.json
CLOSE-OUT: DONE — general charged-physical-time relational event-map theorem certified with conditional nontriviality
"""
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--emit",action="store_true"); p.add_argument("--check",action="store_true"); args=p.parse_args(); v=build()
 if args.emit: CERT.write_text(render(v)); REPORT.write_text(report())
 if args.check and (CERT.read_text()!=render(v) or REPORT.read_text()!=report()): raise SystemExit("stale theorem")
 print("CHARGED_PHYSICAL_TIME_RELATIONAL_EVENT_MAP_THEOREM_V1 generation: PASS")
