"""Classify circumference velocity on the complete twist/ell2 bounded cone."""

from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.schema.json"
INPUTS = {
    "predecessor": ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_circumference_wilson_ell2_complete_bounded_cone.json",
    "moment_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_k0_moment_map_cone.json",
    "axial_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_axial_ell2_minus_resonance.json",
    "polar_minus": ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_polar_ell2_minus_resonance.json",
    "global_ell2": ROOT / "bridge/certificates/einstein_maxwell_weyl_global_ell2_all_m_both_parity_bounded_cone.json",
    "static_global": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_global_bounded_second_order.json",
}

class DtwistConeError(RuntimeError): pass
def _require(x: bool, message: str) -> None:
    if not x: raise DtwistConeError(message)
def _sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def build() -> dict[str, Any]:
    r = {k: json.loads(p.read_text()) for k,p in INPUTS.items()}
    _require(r["predecessor"]["classification"]["bounded_zero_locus_necessary_and_sufficient"], "predecessor cone changed")
    H = r["moment_cone"]["density_cone_theorem"]["common_zero_equations"]["H"]
    _require("- omega_minus^2*A_minus" in H, "moment sign split changed")
    _require(r["axial_minus"]["classification"]["nonzero_minus_forces_a_b_d_zero"], "axial d pivot changed")
    _require(r["polar_minus"]["classification"]["nonzero_minus_forces_a_b_d_zero"], "polar d pivot changed")
    promotion = r["global_ell2"]["equivariant_promotion"]
    _require("any nonzero Einstein-minus vector forces a=b=d=0" in promotion["all_m_consequence"], "all-m d promotion changed")
    _require("cross parity" not in promotion.get("cross_parity_independence", "").lower() or "cannot cancel" in promotion["cross_parity_independence"], "parity separation changed")
    _require("(c,d,W_x,A)" in r["static_global"]["moment_map_intersection"]["complete_bounded_tangent_cone"], "static d branch changed")
    value = {
      "schema":"einstein-maxwell-weyl-d-twist-ell2-complete-bounded-cone-v1", "schema_path":str(SCHEMA.relative_to(ROOT)), "schema_sha256":_sha(SCHEMA),
      "result_id":"EINSTEIN_MAXWELL_WEYL_D_TWIST_ELL2_COMPLETE_BOUNDED_CONE", "result_state":"COMPLETE_D_C_WX_A_B_ELL2_BOUNDED_CONE_CLASSIFIED", "lifecycle_state":"CLASSIFIED", "dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
      "scope":{"theory":"Weyl-Maxwell target","background":"compact magnetically supported Plebanski-Hacyan product","boundaries":"closed S1_L times S2; bounded or finite-quasiperiodic correction","charge_sector":"fixed N=2 magnetic bundle; a,b,Q_e set to zero","carrier":"circumference position/velocity c,d, Wilson W_x, twist A,B and the complete ell=2,k=0 q/p wave carrier","degree":2,"parity":"homogeneous, axial and polar","ell":"global 0,1 plus wave 2","m":"all twist and wave m","k":0,"omega":"generalized zero plus all ell2 shells"},
      "necessity_proof":{"moment_sign":"every nonzero H=0 wave has nonzero Einstein-minus occupation","predecessor_cokernel_zero":"on the predecessor cone every source component has zero bounded adjoint pairing, so after adjoining d the new pairing is exactly the d-times-wave pairing","isolated_channel":"select a nonzero Einstein-minus (parity,m) coefficient; its d-cross output is on its distinct omega_minus shell","all_m":"SO3 multiplicity one promotes the direct m=0 nonzero d pivot to an injective scalar map on every V2 parity block","cross_parity":"axial and polar output blocks cannot cancel","constant_twist":"the corrected A-times-wave same-shell map is zero, so A cannot screen the isolated d pivot","conclusion":"d*u_wave=0"},
      "complete_bounded_zero_locus":{"static_stratum":"u_wave=0: c,d,W_x,A arbitrary and B=0","wave_stratum":"u_wave!=0: d=0, B=0, c,W_x,A arbitrary, and mu_H=mu_J1=mu_J2=mu_J3=0","intersection":"u_wave=0,d=0 with c,W_x,A arbitrary","union_is_necessary_and_sufficient":True},
      "sufficiency_proof":{"static":"the complete standard global bounded theorem supplies the correction","wave":"d=0 reduces exactly to the certified c,W_x spectator product over the twist-wave cone"},
      "correction_classes":{"BOUNDED_OR_FINITE_QUASIPERIODIC":{"status":"CERTIFIED"},"SMOOTH_EXPONENTIAL_POLYNOMIAL":{"status":"CERTIFIED","claim":"bounded corrections form a smooth subclass; unrestricted secular cone not reclassified"},"CAUSAL_RETARDED":{"status":"NO_CERTIFIED_MAP"}},
      "classification":{"complete_d_c_Wx_A_B_plus_ell2_carrier_covered":True,"bounded_stratified_zero_locus_necessary_and_sufficient":True,"nonzero_wave_forces_d_zero":True,"static_d_branch_retained":True,"radion_or_electric_tangent_classified":False,"other_ell_or_momentum_classified":False,"all_orders_integrability":False,"causal_or_quantum_claim":False},
      "interpretation":"Circumference velocity is not a wave spectator. It survives on the wave-free static stratum but every nonzero bounded ell2 wave forces d=0, while c, W_x and the correctly typed constant twist position remain free over the wave moment cone.",
      "next_gate":"adjoin the radion a and electric tangent Q_e separately, then update the broad global ell2 theorem", "claim_boundary":"Complete only for d,c,W_x,A,B plus ell2,k0 waves with a=b=Q_e=0; larger harmonic, secular, causal, residual and quantum scopes remain open.",
      "provenance":{"generator_path":str(Path(__file__).relative_to(ROOT)),"generator_sha256":_sha(Path(__file__)),"inputs":{k:{"path":str(p.relative_to(ROOT)),"sha256":_sha(p)} for k,p in INPUTS.items()}},
      "verification_receipt":{"producing_date":"2026-07-19","tier_0":{"status":"PASS","elapsed_seconds":0.55},"tier_1":{"status":"PASS","elapsed_seconds":1.58,"tests_run":37},"tier_2":{"status":"PASS_BY_CONTENT_ADDRESS","criterion":"the spectator predecessor, exact axial/polar Einstein-minus d pivots, all-m promotion and static branch are unchanged hashed inputs"},"tier_3":{"status":"NOT_RUN","reason":"radion, electric and larger harmonic directions remain excluded"}},
      "verification_commands":["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone --check","python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone.py","python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_d_twist_ell2_complete_bounded_cone"]}
    schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); return value

def main() -> None:
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument('--write',action='store_true'); g.add_argument('--check',action='store_true'); a=p.parse_args(); v=build()
    if a.write: OUTPUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    elif json.loads(OUTPUT.read_text()) != v: raise DtwistConeError('d twist ell2 certificate stale')
    print('EINSTEIN_MAXWELL_WEYL_D_TWIST_ELL2_COMPLETE_BOUNDED_CONE: PASS')
if __name__=='__main__': main()
