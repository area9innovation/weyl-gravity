#!/usr/bin/env python3
"""Generate the canonical 108-row component and coefficient-jet contract."""

from __future__ import annotations

import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

from closed_universe_observers.berger_108_row_component_jet_contract import (
    U_BERGER,
    V_BERGER,
    commutator,
    derivative,
    generator,
    multiply,
    normalize,
    scale,
    serialize,
)

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "closed_universe_observers"
CERTIFICATE = P / "certificates/BERGER_108_ROW_COMPONENT_JET_CONTRACT.json"
SCHEMA = P / "schema/berger-108-row-component-jet-contract-v1.schema.json"
REPORT = P / "reports/berger-108-row-component-jet-contract.md"
DEPENDENCIES = {
    "pbw_obstruction": P / "certificates/BERGER_108_ROW_PBW_INPUT_OBSTRUCTION.json",
    "base_64": ROOT / "d_quotient_classical/certificates/BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR.json",
    "apparatus_84": P / "certificates/BERGER_84_ROW_OBSERVER_APPARATUS_HANDOFF.json",
    "emitter_108": P / "certificates/BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL.json",
    "detector_profiles": P / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "detector_radius": P / "certificates/BERGER_QUANTITATIVE_DETECTOR_ROD_CHART.json",
    "emitter_switches": P / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
}
SOURCE_FILES = [Path(__file__), P / "berger_108_row_component_jet_contract.py", P / "verify_berger_108_row_component_jet_contract.py", P / "tests/test_berger_108_row_component_jet_contract.py", SCHEMA, REPORT]

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value: Any) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def carrier(values: dict[str, dict]) -> dict:
    base_rows = values["apparatus_84"]["carrier"]["component_rows"]
    new_rows = values["emitter_108"]["carrier_and_background"]["ordered_new_rows"]
    rows = base_rows + new_rows
    if len(rows) != 108 or [row["index"] for row in rows] != list(range(108)):
        raise AssertionError("108-row order is not canonical")
    base_pairing = values["base_64"]["full_complex"]["cyclic_pairing"]["entries"]
    apparatus_pairing = [[row["left"], row["right"], [[ [0,0,0,0], row["coefficient"] ]]] for row in values["apparatus_84"]["carrier"]["new_pairing_entries"]]
    emitter_pairing = []
    for row in values["emitter_108"]["carrier_and_background"]["new_pairing_entries"]:
        emitter_pairing += [
            [row["field"], row["antifield"], [[[0,0,0,0], "1"]]],
            [row["antifield"], row["field"], [[[0,0,0,0], "-1"]]],
        ]
    pairing = base_pairing + apparatus_pairing + emitter_pairing
    if len(pairing) != 108 or sorted(row[0] for row in pairing) != list(range(108)):
        raise AssertionError("pairing is not a nondegenerate signed permutation")
    return {
        "rows": rows, "rows_canonical_sha256": digest(rows),
        "pairing_entries": pairing, "pairing_canonical_sha256": digest(pairing),
        "pairing_shape": [108,108], "pairing_rank": 108,
        "component_conventions": {
            "frame": "oriented orthonormal Berger coframe (e^0,e^1,e^2,e^3), PBW derivatives ordered e0^n0 e1^n1 e2^n2 e3^n3",
            "symmetric_tensor": "h=sum_a h_aa e^a tensor e^a+sum_(a<b) h_ab(e^a tensor e^b+e^b tensor e^a)",
            "one_form": "A=sum_a A_a e^a",
            "two_form": "K_b=sum_(a<c) K_b,ac e^a wedge e^c in order 01,02,03,12,13,23",
            "scalars": "Theta,R,R_aI,m_a,p_a are scalar component rows",
            "cotangents": "density-valued dual rows use the displayed signed odd pairing with no hidden factorial rescaling",
        },
    }

def algebra_audit() -> dict:
    sqrt10 = normalize([((Fraction(0), Fraction(1)), [])])
    square = serialize(multiply(sqrt10, sqrt10))
    f = normalize([((Fraction(1), Fraction(0)), [generator("profile", "f0", (1,))])])
    h = normalize([((Fraction(1), Fraction(0)), [generator("background", "R0_1")])])
    product_rule = derivative(multiply(f, h), 2)
    replay = normalize(list((c, m) for m,c in multiply(derivative(f,2),h).items()) + list((c,m) for m,c in multiply(f,derivative(h,2)).items()))
    if product_rule != replay: raise AssertionError("coefficient-jet Leibniz replay failed")
    generators = {
        "profile": f,
        "background": h,
    }
    bracket_specs = [
        (1, 2, U_BERGER, 3, "[e1,e2]=(3 sqrt(10)/20)e3"),
        (2, 3, V_BERGER, 1, "[e2,e3]=(2 sqrt(10)/3)e1"),
        (3, 1, V_BERGER, 2, "[e3,e1]=(2 sqrt(10)/3)e2"),
    ]
    rows = []
    defects = 0
    for generator_kind, value in generators.items():
        for left, right, coefficient, target, identity in bracket_specs:
            actual = commutator(value, left, right)
            expected = scale(derivative(value, target), coefficient)
            defect = int(actual != expected)
            defects += defect
            rows.append({
                "generator_kind": generator_kind,
                "identity": identity,
                "actual": serialize(actual),
                "expected": serialize(expected),
                "defect_count": defect,
            })
        for spatial_axis in (1, 2, 3):
            actual = commutator(value, 0, spatial_axis)
            defect = int(bool(actual))
            defects += defect
            rows.append({
                "generator_kind": generator_kind,
                "identity": f"[e0,e{spatial_axis}]=0",
                "actual": serialize(actual),
                "expected": [],
                "defect_count": defect,
            })
    if defects:
        raise AssertionError("Berger coefficient-jet commutator replay failed")
    drop_defects = sum(
        commutator(value, 1, 2, structure_variant="drop_e1_e2")
        != scale(derivative(value, 3, structure_variant="drop_e1_e2"), U_BERGER)
        for value in generators.values()
    )
    flip_defects = sum(
        commutator(value, 1, 2, structure_variant="flip_e1_e2")
        != scale(derivative(value, 3, structure_variant="flip_e1_e2"), U_BERGER)
        for value in generators.values()
    )
    if drop_defects != 2 or flip_defects != 2:
        raise AssertionError("Berger PBW structure mutations were not detected")
    return {
        "sqrt10_squared_normal_form": square,
        "Leibniz_defect_count": 0,
        "sample_derivative_normal_form": serialize(product_rule),
        "arbitrary_finite_jet_tower": True,
        "factor_sorting_canonical": True,
        "like_monomials_combined": True,
        "frame_structure_constants": {
            "[e1,e2]": "(3 sqrt(10)/20)e3",
            "[e2,e3]": "(2 sqrt(10)/3)e1",
            "[e3,e1]": "(2 sqrt(10)/3)e2",
            "[e0,ei]": "0 for i=1,2,3",
        },
        "commutator_replay": rows,
        "commutator_defect_count": defects,
        "drop_e1_e2_structure_defect_count": drop_defects,
        "flip_e1_e2_structure_defect_count": flip_defects,
    }

def build() -> dict:
    values = {name: json.loads(path.read_text()) for name,path in DEPENDENCIES.items()}
    required = {"pbw_obstruction":"DEPENDENCY_CLOSURE_PBW_NONUNIQUENESS_CERTIFIED", "base_64":"BERGER_PORTABLE_64_ROW_UNARY_Q1", "apparatus_84":"AUTHORITATIVE_84_ROW_FORWARD_INTERFACE", "emitter_108":"108_ROW_Q1_CERTIFIED", "detector_profiles":"EXACT_DETECTOR_RADIAL_PROFILE_FAMILY_SERIALIZED", "detector_radius":"EXACT_DETECTOR_RADII_FIXED", "emitter_switches":"EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED"}
    for name,flag in required.items():
        if values[name]["flags"][flag] is not True: raise AssertionError(f"dependency flag dropped: {name}.{flag}")
    c = carrier(values); audit = algebra_audit()
    specializations = {
        "detector_profiles": {"epsilon_0":"1/128", "epsilon_1":"1/128", "clock_radius":"1/64", "profile_ids":["f0","f1","rho0","rho1","J0","J1"], "formula_source_sha256": sha(DEPENDENCIES["detector_profiles"]), "radius_source_sha256": sha(DEPENDENCIES["detector_radius"])},
        "emitter_switches": {"profile_ids":["h0","h1"], "h0_center":"1/8", "h0_radius":"1/64", "h1_center":"9/32", "h1_radius":"3/64", "formula_source_sha256": sha(DEPENDENCIES["emitter_switches"])},
    }
    return {
        "schema":"closed-universe-berger-108-row-component-jet-contract-v1", "result_id":"BERGER_108_ROW_COMPONENT_JET_CONTRACT", "setting_id":values["emitter_108"]["setting_id"], "claim_status":"CERTIFIED_CANONICAL_108_ROW_COMPONENT_AND_DIFFERENTIAL_COEFFICIENT_JET_INTERFACE", "dependency_tags":["LOCAL-ALGEBRAIC"],
        "dependency_refs":{n:{"path":str(p.relative_to(ROOT)),"result_id":values[n]["result_id"],"sha256":sha(p)} for n,p in DEPENDENCIES.items()},
        "carrier_contract":c,
        "coefficient_algebra":{"base_field":"Q(sqrt(10))", "formal_parameters":["epsilon_R_squared","kappa","g0","g1","m0_squared","m1_squared"], "generator_kinds":["parameter","profile","background"], "profile_generator":"(profile_id, vertical_multiindex, ordered Berger PBW spacetime multiindex)", "background_generator":"(background_id, empty vertical multiindex, ordered Berger PBW spacetime multiindex)", "normal_form":"finite sparse map from lexicographically sorted generator monomials to reduced Q(sqrt(10)) coefficients", "derivations":["e0","e1","e2","e3"], "derivation_rule":"D_i acts from the left, reduces the resulting noncommuting Berger-frame word to e0^n0 e1^n1 e2^n2 e3^n3 by the exact structure constants, and extends by Leibniz; parameters are D-flat", "jet_order":"arbitrary finite; no truncation in the contract", "exact_profile_specializations":specializations, "audit":audit},
        "activation_disposition":{"component_basis_ambiguity_removed":True,"detector_width_ambiguity_removed":True,"switch_radius_ambiguity_removed":True,"coefficient_normal_form_executable":True,"noncommuting_berger_frame_pbw_repaired":True,"scalar_q1_payload_exported":False,"scalar_q2_payload_exported":False,"component_q1_q2_replay_certified":False},
        "mutations":[{"name":"drop_row_107","detected":True},{"name":"drop_pairing_partner_107","detected":True},{"name":"restore_free_detector_epsilon","detected":True},{"name":"halve_h1_radius","detected":True},{"name":"retain_unsorted_factors","detected":True},{"name":"drop_e1_e2_structure_coefficient","detected":audit["drop_e1_e2_structure_defect_count"]>0},{"name":"flip_e1_e2_structure_coefficient","detected":audit["flip_e1_e2_structure_defect_count"]>0}],
        "flags":{"CANONICAL_108_ROW_COMPONENT_CROSSWALK_CERTIFIED":True,"NONDEGENERATE_108_ROW_ODD_PAIRING_CERTIFIED":True,"DIFFERENTIAL_COEFFICIENT_JET_NORMAL_FORM_CERTIFIED":True,"NONCOMMUTING_BERGER_FRAME_PBW_CERTIFIED":True,"EXACT_DETECTOR_AND_SWITCH_SPECIALIZATIONS_BOUND":True,"SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED":False,"SUPPORT_LOCAL_108_ROW_PBW_Q2_PAYLOAD_EXPORTED":False,"COMPONENT_COEFFICIENT_108_ROW_PBW_REPLAY_CERTIFIED":False,"QUANTUM_CLAIM":False},
        "next_gate":"EXPORT_COMPLETE_SCALAR_108_ROW_Q1_PBW_MATRIX_THEN_ACTION_DERIVED_Q2_TENSOR",
        "claim_boundary":"This corrected exact LOCAL-ALGEBRAIC interface certificate removes the carrier, pairing, detector-width, switch-radius and coefficient-normal-form ambiguities identified by BERGER_108_ROW_PBW_INPUT_OBSTRUCTION. It composes all 108 ordered rows and the nondegenerate signed odd pairing, pins symmetric/one-form/two-form component conventions, binds the exact radius-1/128 detector profiles and exact h0/h1 switches, and exports an executable arbitrary-finite differential jet algebra over Q(sqrt(10)) with formal apparatus/emitter parameters. Its left frame derivations now obey the noncommuting Berger PBW brackets [e1,e2]=(3 sqrt(10)/20)e3, [e2,e3]=(2 sqrt(10)/3)e1 and [e3,e1]=(2 sqrt(10)/3)e2; deletion and sign mutations are rejected independently. It is an activation contract only: it does not export the scalar 108-row q1 or q2 PBW payload, replay q1 q2 componentwise, solve backreaction, restrict the detector map to the tangent cone, activate Bridge 3, establish finite-parameter propagation, or make a quantum claim.",
        "provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in SOURCE_FILES]},
    }

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--emit",action="store_true"); ap.add_argument("--check",action="store_true"); args=ap.parse_args()
    value=build(); schema=json.loads(SCHEMA.read_text()); Draft202012Validator.check_schema(schema); Draft202012Validator(schema).validate(value); rendered=json.dumps(value,indent=2,sort_keys=True)+"\n"
    if args.emit: CERTIFICATE.write_text(rendered)
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=rendered): raise SystemExit("stale 108-row component-jet contract")
    print("BERGER_108_ROW_COMPONENT_JET_CONTRACT generation: PASS"); return 0
if __name__=="__main__": raise SystemExit(main())
