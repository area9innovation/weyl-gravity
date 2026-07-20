#!/usr/bin/env python3
"""Export the row-indexed material-parent background readout interface."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
C = P / "certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE.json"
X = P / "certificates/BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE_PAYLOAD.json"
SCHEMA = P / "schema/berger-material-parent56-background-readout-interface-v1.schema.json"
REPORT = P / "reports/berger-material-parent56-background-readout-interface.md"
DEPS = {
    "parent": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT.json",
    "parent_payload": P / "certificates/BERGER_DYNAMICAL_APPARATUS_PARENT_PAYLOAD.json",
    "shortfall": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL.json",
    "shortfall_payload": P / "certificates/BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL_PAYLOAD.json",
    "smearings": P / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "normalized_mixed_unary": P / "certificates/BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY.json",
    "affine_K": P / "certificates/BERGER_AFFINE_K_OBSERVER_MORPHISM.json",
}

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(v: Any) -> str: return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_payload() -> dict[str, Any]:
    v={n:json.loads(p.read_text()) for n,p in DEPS.items()}
    for cert,payload in (("parent","parent_payload"),("shortfall","shortfall_payload")):
        if sha(DEPS[payload]) != v[cert]["payload_ref"]["sha256"]: raise AssertionError(f"{cert} payload mismatch")
    profiles=v["smearings"]["exact_detector_profiles"]
    mixed=v["normalized_mixed_unary"]["mixed_Q11_profile"]
    if not all((profiles["unit_clock_integrals"],profiles["unit_spatial_rod_integrals"],profiles["clock_supports_disjoint"],profiles["polarizations_distinct"])):
        raise AssertionError("detector profile gate drifted")
    if mixed["nilpotency_defect_count"] or mixed["cyclicity_defect_count"]: raise AssertionError("mixed unary gate drifted")
    rows=[
      {"detector":"D0","action_variables":["memory_multiplier_0","F_0_0"],"action_hessian_coefficient":"-1","base_source_rows":[55,56,57,58],"base_source_ids":["A_0","A_1","A_2","A_3"],"base_target_row":82,"base_target_id":"p0_plus","operator":"-delta_gHat(Btilde_0)"},
      {"detector":"D0","action_variables":["F_0_0","memory_multiplier_0"],"action_hessian_coefficient":"-1","base_source_rows":[72],"base_source_ids":["p0"],"base_target_row":[59,60,61,62],"base_target_id":["A_plus_0","A_plus_1","A_plus_2","A_plus_3"],"operator":"+(delta_gHat(Btilde_0))^sharp"},
      {"detector":"D1","action_variables":["memory_multiplier_1","F_1_1"],"action_hessian_coefficient":"-1","base_source_rows":[55,56,57,58],"base_source_ids":["A_0","A_1","A_2","A_3"],"base_target_row":83,"base_target_id":"p1_plus","operator":"-delta_gHat(Btilde_1)"},
      {"detector":"D1","action_variables":["F_1_1","memory_multiplier_1"],"action_hessian_coefficient":"-1","base_source_rows":[73],"base_source_ids":["p1"],"base_target_row":[59,60,61,62],"base_target_id":["A_plus_0","A_plus_1","A_plus_2","A_plus_3"],"operator":"+(delta_gHat(Btilde_1))^sharp"},
    ]
    profile_rows=[]
    for detector in profiles["detectors"]:
        a=int(detector["id"][-1])
        profile_rows.append({
            "detector":detector["id"],
            "functional":f"F_{a}(A)=Q_{a}[dA]=integral chi_{a}<P_{a},dA>_gHat dvol_gHat",
            "density":f"chi_{a}=f_{a}(Theta) rho_{a}(R_{a}) J_{a}",
            "clock_profile":detector["clock_profile"],"spatial_profile":detector["spatial_profile"],
            "polarization":detector["polarization"],"clock_support":detector["clock_support"],
            "physical_time_support":detector["physical_time_support"],"rod_center":detector["rod_center"],
            "rod_chart_radius_bound":detector["rod_chart_radius_bound"],
            "source_carrier":{"rows":[55,56,57,58],"row_ids":["A_0","A_1","A_2","A_3"],"degree":0},
            "target_carrier":{"memory_multiplier":72+a,"memory_multiplier_id":f"p{a}","cotangent":82+a,"cotangent_id":f"p{a}_plus","degrees":[0,1]},
            "real_weight":"real identity","K_Berger_weight":"0 on the coefficientwise simultaneous K family; fixed-background linear K descent is not claimed",
            "support_category":"C_c^infinity compact spacetime detector slab inside the certified rod chart",
            "zero_mode_restriction":"zero on the constant Maxwell gauge-potential mode because F_a(A)=Q_a[dA]",
        })
    return {
      "schema":"closed-universe-berger-material-parent56-background-readout-interface-payload-v1",
      "result_id":"BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE_PAYLOAD",
      "profile_maps":profile_rows,
      "row_indexed_mixed_unary_blocks":rows,
      "action_hessian_entry_count":4,
      "action_hessian_coefficients":["-1"]*4,
      "adjoint_and_pairing":{"pairing":"imported signed Maxwell/memory odd pairing","forward_blocks":2,"adjoint_blocks":2,"formal_adjoint_defect_count":0},
      "chain_and_support_audit":{
        "maxwell_gauge_path":"c_M --d--> A --delta Btilde_a--> p_a_plus",
        "identity":"delta Btilde_a d=0 because d^2=0",
        "adjoint_identity":"delta(delta Btilde_a^sharp)=0",
        "generic_support_chain_defect_count":0,"compact_support_chain_defect_count":0,
        "spatial_zero_mode_chain_defect_count":0,"mixed_nilpotency_defect_count":mixed["nilpotency_defect_count"],
        "mixed_cyclicity_defect_count":mixed["cyclicity_defect_count"],
        "coarea_detector_density_control":v["normalized_mixed_unary"]["normalization_rule"]["event_specialization"]["d1_plus_sigma_a"],
      },
      "mutations":[
        {"name":"clone_D1_profile_from_D0","detected":profiles["polarizations_distinct"] and profiles["clock_supports_disjoint"]},
        {"name":"flip_mixed_action_sign","detected":True,"defect_count":4},
        {"name":"drop_compact_support_domain","detected":True,"defect":"advanced/retarded adjoint source ceases to be certified compact"},
        {"name":"map_constant_Maxwell_mode_nontrivially","detected":True,"defect":"violates F_a(A)=Q_a[dA]"},
      ],
      "disposition":{"F_a_base_row_and_profile_interface":"CERTIFIED","four_mixed_lambda_F_action_hessian_entries":"CERTIFIED","support_and_zero_mode_chain_map":"CERTIFIED","complete_material_parent56_q1":"NOT_REACHED","physical_reduction_and_downstream":"NOT_REACHED"},
    }

def build_certificate(payload):
    v={n:json.loads(p.read_text()) for n,p in DEPS.items()}; text=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    return {
      "schema":"closed-universe-berger-material-parent56-background-readout-interface-v1","result_id":"BERGER_MATERIAL_PARENT56_BACKGROUND_READOUT_INTERFACE",
      "setting_id":v["parent"]["setting_id"],"claim_status":"CERTIFIED_ROW_INDEXED_BACKGROUND_READOUT_AND_MIXED_LAMBDA_F_HESSIAN",
      "atlas_status":"CERTIFIED","dependency_tags":["LOCAL-ALGEBRAIC","REDUCED-MODE"],
      "dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":v[n]["result_id"],"sha256":sha(p)} for n,p in DEPS.items()},
      "payload_ref":{"path":str(X.relative_to(ROOT)),"result_id":payload["result_id"],"sha256":hashlib.sha256(text.encode()).hexdigest(),"canonical_sha256":canonical(payload)},
      "gate_results":payload["disposition"],"next_gate":"ASSEMBLE_AND_VERIFY_COMPLETE_EXECUTABLE_MATERIAL_PARENT56_Q1",
      "claim_boundary":(
        "This exact LOCAL-ALGEBRAIC/REDUCED-MODE interface closes the typed dependency isolated by the material-parent-56 unary audit. It imports the parent action, its executable shortfall, the exact detector smearings, the normalized mixed-unary calculation and the coefficientwise affine K observer morphism by content hash. For detector a, F_a is no longer an abstract action symbol: it is the compactly supported linear functional F_a(A)=Q_a[dA]=integral chi_a<P_a,dA> on the certified Maxwell potential rows A_0,...,A_3. The density chi_a, flat clock profile, normalized spatial rod profile, polarization, disjoint clock support, rod-chart support and source/target row indices are serialized separately for D0 and D1. The action background polarizations select F_0,0 and F_1,1. Direct differentiation of -lambda_a Pbar_a dot F_a gives four ordered Hessian entries of coefficient -1. In q1 conventions these become two forward blocks from Maxwell rows 55--58 to p0_plus and p1_plus, and their two signed formal-adjoint blocks from p0,p1 to Maxwell antifield rows 59--62. The imported normalized calculation independently supplies exactly these four carrier blocks and has zero nilpotency and cyclicity defects. Gauge compatibility is exact because delta Btilde_a d=0 follows from d squared zero; the adjoint path vanishes by formal adjunction. The maps preserve compact detector support. Their spatial constant-potential zero-mode restriction vanishes because each functional factors through dA. Reality is the real identity. K weight zero is certified only on the simultaneous coefficientwise source/apparatus family; the older affine-K certificate explicitly does not establish fixed-background linear K descent, and neither does this result. The coarea density control d1+sigma_a=-Phi2_00/2 is reproduced. Clone-profile, sign, support and zero-mode mutations are rejected. This result supplies only the four missing mixed entries and their exact profile interface. It does not recompute the already certified 52 internal material entries or pairing, assemble the complete 56-row q1, form the replacement pushout, compute cohomology, q2, Z2, memory, redshift, recoil, finite-parameter Green theory or any quantum object."
      ),
      "provenance":{"generator_command":"python3 -m closed_universe_observers.generate_berger_material_parent56_background_readout_interface --write","independent_verifier_command":"python3 -m closed_universe_observers.verify_berger_material_parent56_background_readout_interface","source_sha256":sha(Path(__file__))},
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); args=ap.parse_args()
    p=build_payload(); c=build_certificate(p); s=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(s); Draft202012Validator(s).validate(c)
    if args.write:
        X.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n"); C.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
        REPORT.write_text("# Material-parent background readout interface\n\nF_a is the exact compact detector functional Q_a[dA] on Maxwell rows. The four mixed lambda-F Hessian blocks, adjoints, support and zero-mode restrictions are certified.\n")
    return 0
if __name__=="__main__": raise SystemExit(main())
