"""Construct nonzero bounded second-order points on collision candidates 16--21."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.schema.json"
INPUTS = {
    "scalar_classifier": ROOT / "bridge/certificates/einstein_maxwell_weyl_collision_scalar_separation_classification.json",
    "same_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json",
    "isolated": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "zero_block": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_bounded_zero_block.json",
    "finite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "candidate16": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_target_doublet_L3_zero_varieties.json",
    "candidate17_20": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "candidate18": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_multiplicity_two_L3_zero_varieties.json",
    "candidate19": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "candidate21": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    for row in rows:
        if row.get("candidate_index") == index:
            return row
    raise AssertionError(f"candidate {index} zero variety missing")


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    scalar = records["scalar_classifier"]
    if scalar["summary"]["positive_farkas_candidate_indices"] != list(range(16, 22)):
        raise AssertionError("Farkas candidate set changed")
    if not records["same_fibre"]["classification"]["all_864_target_shell_defects_nonzero"]:
        raise AssertionError("same-fibre gate changed")
    if not records["zero_block"]["classification"]["five_stabilizers_plus_circle_pressure_complete_on_finite_generic_zero_block"]:
        raise AssertionError("bounded zero-block gate changed")
    if not records["finite_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]:
        raise AssertionError("finite cone sufficiency changed")
    ledger = records["isolated"]["candidate_ledger"]
    if ledger["distinct_positive_rho_values"] != 21:
        raise AssertionError("collision backgrounds merged")
    isolated_rows = {index: row for index, row in enumerate(ledger["rows"], 1)}

    scalar_rows = {row["candidate_index"]: row for row in scalar["candidate_rows"]}
    c16 = decomposition(records["candidate16"], 16)
    c17 = decomposition(records["candidate17_20"], 17)
    c18 = decomposition(records["candidate18"], 18)
    c19 = decomposition(records["candidate19"], 19)
    c20 = decomposition(records["candidate17_20"], 20)
    c21 = decomposition(records["candidate21"], 21)
    if c16["fibre_id"] != "L3_candidate_16" or c17["fibre_id"] != "L1_candidate_17" or c18["fibre_id"] != "L3_candidate_18" or c19["fibre_id"] != "L4_candidate_19" or c20["fibre_id"] != "L1_candidate_20" or c21["fibre_id"] != "L4_candidate_21":
        raise AssertionError("zero-variety crosswalk changed")
    zero_variety_gates = {
        "candidate16": "both_target_doublet_L3_zero_varieties_classified",
        "candidate17_20": "all_three_scalar_L1_zero_varieties_classified",
        "candidate18": "all_three_multiplicity_two_L3_zero_varieties_classified",
        "candidate19": "three_regular_pencil_L4_zero_varieties_classified",
        "candidate21": "complete_scalar_internal_L4_zero_varieties_classified",
    }
    for input_name, gate in zero_variety_gates.items():
        if not records[input_name]["classification"][gate]:
            raise AssertionError(f"{input_name} zero-variety classification changed")
    mixed = [row for row in c21["irreducible_components_over_C"] if row["component_id"] == "mixed_plus"]
    if (
        len(mixed) != 1
        or not c21["r_squared_interval"]["positive"]
        or not mixed[0].get("r")
        or not mixed[0].get("s")
    ):
        raise AssertionError("candidate-21 real mixed component changed")
    if (
        clebsch_gordan(2, 2, 3, 0, 0, 0) != 0
        or clebsch_gordan(2, 2, 1, 0, 0, 0) != 0
    ):
        raise AssertionError("axisymmetric odd-L Clebsch-Gordan zero changed")

    expected_resonances = {
        16: ("q_minus", "q_minus", "p_extra", "SUM", 3),
        17: ("q_minus", "q_plus", "extra", "DIFFERENCE", 1),
        18: ("p_extra", "q_minus", "q_plus", "SUM", 3),
        19: ("p_extra", "q_minus", "p_extra", "SUM", 4),
        20: ("q_plus", "q_minus", "extra", "DIFFERENCE", 1),
        21: ("q_plus", "q_minus", "q_plus", "SUM", 4),
    }
    for index, expected in expected_resonances.items():
        row = isolated_rows[index]
        actual = (
            row["first_branch"],
            row["second_branch"],
            row["target_branch"],
            row["admissible_temporal_channel"],
            row["output_ell"],
        )
        if row["canonical_signed_momenta"] != [1, 2] or actual != expected:
            raise AssertionError(f"candidate {index} isolated resonance crosswalk changed")

    dispositions = {
        16: {"method": "AXISYMMETRIC_ODD_L_ZERO", "reason": "only q_minus(1)*q_minus(2) resonates at L=3; choose every supported mode axial m=0, so the sole M=0 Clebsch-Gordan coefficient vanishes"},
        17: {"method": "RESONANT_FACTOR_ABSENT", "reason": "the resonance is q_minus(1)*q_plus(2), while the exact Farkas support sets q_plus(2)=0"},
        18: {"method": "RESONANT_FACTOR_ABSENT", "reason": "the resonance is p_extra(1)*q_minus(2), while the exact Farkas support sets p_extra(1)=0"},
        19: {"method": "RESONANT_FACTOR_ABSENT", "reason": "the resonance is p_extra(1)*q_minus(2), while the exact Farkas support sets p_extra(1)=0"},
        20: {"method": "AXISYMMETRIC_ODD_L_ZERO", "reason": "only q_plus(1)*q_minus(2) resonates at L=1; choose every supported mode axial m=0, so the sole M=0 Clebsch-Gordan coefficient vanishes"},
        21: {
            "method": "REAL_MIXED_PARITY_L4_COMPONENT",
            "reason": "put q_plus(1),q_minus(2) on the certified mixed-plus component A_polar=r*A_axial, B_polar=s*B_axial and scale the two fibres independently to the Farkas occupations",
            "r": mixed[0]["r"],
            "s": mixed[0]["s"],
            "amplitude_factorization": "if y_A,y_B are the prescribed positive absolute-current occupations, set |A_axial|^2=y_A/kappa_A(r) and |B_axial|^2=y_B/kappa_B(s), where kappa_A(r),kappa_B(s)>0 are the exact action-derived absolute-current norms of the real parity vectors (1,r),(1,s); then A_polar=r*A_axial and B_polar=s*B_axial",
        },
    }
    rows = []
    for index in range(16, 22):
        source = scalar_rows[index]
        rows.append({
            "candidate_index": index,
            "rho": source["rho"],
            "positive_absolute_current_occupations": source["positive_weights"],
            "support": source["support"],
            "angular_choice": "m=0 for every occupied branch; candidate 21 uses the displayed real mixed parity ratios on its resonant pair",
            "rotation_moment_maps": "mu_J1=mu_J2=mu_J3=0 by axisymmetry and diagonal shell support",
            "scalar_receiver": "mu_H=mu_Px=R_c=0 by the exact positive Farkas dependence",
            "cross_fibre_resonance": dispositions[index],
            "same_fibre_resonance": "none by the six-candidate 864-defect census",
            "isolated_resonance_crosswalk": isolated_rows[index],
            "bounded_verdict": "NONZERO_POINT_IN_Z2_BOUNDED_CERTIFIED",
        })
    return {
        "schema": "einstein-maxwell-weyl-same-sign-collision-bounded-witnesses-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_BOUNDED_WITNESSES",
        "result_state": "ALL_SIX_SAME_SIGN_COLLISION_CONES_HAVE_EXPLICIT_NONZERO_BOUNDED_POINTS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EXPLICIT_NONZERO_POINT_ON_EACH_OF_SIX_COMPLETE_GENERIC_BOUNDED_CONES",
        "scope": {**scalar["scope"], "background": "six distinct candidates 16--21, never identified", "carrier": "one explicit finite real generic tangent per candidate"},
        "witness_rows": rows,
        "classification": {
            "all_six_scalar_pressure_null_witnesses_exact": True,
            "all_six_rotation_zero_witnesses_exact": True,
            "all_six_cross_fibre_resonance_zero_witnesses_exact": True,
            "all_six_same_fibre_nonzero_frequency_ledgers_empty": True,
            "all_six_nonzero_bounded_points_certified": True,
            "all_six_complete_bounded_cones_classified": False,
            "cross_background_mode_identification_made": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The 15/6 split is sharp: opposite-sign collision cones are bounded-trivial, whereas every same-sign collision cone contains a nonzero bounded second-order tangent. The six full cone geometries remain to be classified.",
        "next_gate": "classify the full real bounded cone on candidates 16--21; the existence question and all same-fibre source gates are closed",
        "claim_boundary": "This proves one nonzero bounded point on each of six distinct generic backgrounds, not their full cone decompositions, exceptional/global extensions, all-orders solutions, causal corrections, residual observables or quantum states.",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": sha(Path(__file__)), "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()}},
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_collision_bounded_witnesses --check", "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_collision_bounded_witnesses", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_collision_bounded_witnesses"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(json.loads(rendered))
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("same-sign bounded witnesses are stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_BOUNDED_WITNESSES: PASS")


if __name__ == "__main__":
    main()
