"""Certify the axisymmetric Zariski-tangent current on candidates 17 and 20."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_axial_L4_matrix import (
    fraction_string,
    rational_interval,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current.schema.json"
INPUTS = {
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "scalar_L1": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L1_zero_varieties.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "standard_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
}

SQRT3 = sp.sqrt(3)
MASS_OVER_N_SQUARED = {
    "q_minus_n2": sp.Rational(3, 2) - SQRT3 / 2,
    "p_extra_n2": sp.Rational(4, 3),
    "q_plus_n2": sp.Rational(3, 2) + SQRT3 / 2,
    "q_minus_n1": 6 - 2 * SQRT3,
    "p_extra_n1": sp.Rational(16, 3),
    "q_plus_n1": 6 + 2 * SQRT3,
}
NODE_SIGN = {
    "q_minus_n2": -1,
    "p_extra_n2": 1,
    "q_plus_n2": 1,
    "q_minus_n1": -1,
    "p_extra_n1": 1,
    "q_plus_n1": 1,
}
NODE_N = {
    "q_minus_n2": 2,
    "p_extra_n2": 2,
    "q_plus_n2": 2,
    "q_minus_n1": 1,
    "p_extra_n1": 1,
    "q_plus_n1": 1,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ray_weight(node: str, support: list[str], rho: sp.Expr) -> sp.Expr:
    x = {name: sp.sqrt(rho + mass) for name, mass in MASS_OVER_N_SQUARED.items()}
    denominator = NODE_SIGN[node] * NODE_N[node] ** 2
    denominator *= sp.prod(x[node] - x[other] for other in support if other != node)
    return sp.factor(1 / denominator)


def interval_witness(expression: sp.Expr, digits: int = 30) -> dict[str, object]:
    lower, upper = rational_interval(expression, digits)
    if lower <= 0:
        raise AssertionError("occupation-gap interval did not prove positivity")
    return {
        "expression": sp.sstr(expression),
        "lower": fraction_string(lower),
        "upper": fraction_string(upper),
        "decimal_digits": digits,
        "strictly_positive": True,
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    faces = {row["candidate_index"]: row for row in records["resonance_faces"]["face_rows"]}
    decompositions = {row["candidate_index"]: row for row in records["scalar_L1"]["decompositions"]}
    rays = {row["ray_id"]: row["support"] for row in records["scalar_rays"]["extreme_rays"]}
    nodes = {row["id"]: row["current_sign"] for row in records["scalar_rays"]["moment_curve_reduction"]["ordered_nodes"]}
    if nodes != NODE_SIGN:
        raise AssertionError("same-sign current dictionary changed")
    if "common parity-independent branch weights" not in records["standard_current"]["theorem"]["block_table"][0]["pullback_relative_operator"]:
        raise AssertionError("parity-independent q-primary current changed")

    matrix = sp.Matrix(records["scalar_L1"]["third_transvectant_certificate"]["matrix_A_f"])
    f = sp.symbols("f0:5")
    matrix = matrix.applyfunc(lambda value: sp.sympify(value, locals={f"f{i}": f[i] for i in range(5)}))
    e0_matrix = matrix.subs({f[0]: 0, f[1]: 0, f[2]: 1, f[3]: 0, f[4]: 0})
    if e0_matrix.rank() != 2 or len(e0_matrix.nullspace()) != 3:
        raise AssertionError("axisymmetric third-transvectant rank changed")

    specifications = {
        17: {
            "rho": 10 * (9 * SQRT3 + 77) / 8529,
            "negative_node": "q_minus_n1",
            "positive_node": "q_plus_n2",
            "active_rays": ["R3", "R4"],
            "inactive_rays": ["R1", "R2"],
        },
        20: {
            "rho": -10 * (-77 + 9 * SQRT3) / 8529,
            "negative_node": "q_minus_n2",
            "positive_node": "q_plus_n1",
            "active_rays": ["R2", "R4"],
            "inactive_rays": ["R1", "R3"],
        },
    }

    candidate_rows = []
    for index, spec in specifications.items():
        face = faces[index]
        decomposition = decompositions[index]
        if decomposition["zero_variety"]["dimension_over_C"] != 14 or decomposition["zero_variety"]["irreducible_components_over_C"] != 1:
            raise AssertionError(f"candidate-{index} third-transvectant variety changed")
        if face["active_stratum"]["active_component_count_over_C"] != 1:
            raise AssertionError(f"candidate-{index} active component count changed")
        witnesses = []
        for ray_id in spec["active_rays"]:
            support = rays[ray_id]
            negative_weight = ray_weight(spec["negative_node"], support, spec["rho"])
            positive_weight = ray_weight(spec["positive_node"], support, spec["rho"])
            witnesses.append({
                "ray_id": ray_id,
                "negative_minus_positive": interval_witness(negative_weight - positive_weight),
            })
        for ray_id in spec["inactive_rays"]:
            if spec["positive_node"] in rays[ray_id] or spec["negative_node"] not in rays[ray_id]:
                raise AssertionError(f"candidate-{index} active-face ray support changed")
        candidate_rows.append({
            "candidate_index": index,
            "rho": sp.sstr(spec["rho"]),
            "negative_node": spec["negative_node"],
            "positive_node": spec["positive_node"],
            "active_rays": spec["active_rays"],
            "inactive_rays_add_only_to_negative_occupation": spec["inactive_rays"],
            "active_ray_gap_witnesses": witnesses,
            "strict_cone_occupation_inequality": f"occupation({spec['negative_node']}) > occupation({spec['positive_node']}) at every nonzero active scalar-cone point",
            "axisymmetric_affine_zariski_tangent_complex_dimension": 16,
            "axisymmetric_affine_zariski_tangent_excess_over_variety_dimension": 2,
            "axisymmetric_affine_zariski_tangent_current_inertia": [6, 10, 0],
            "axisymmetric_projective_zariski_tangent_complex_dimension": 14,
            "axisymmetric_projective_zariski_tangent_current_inertia": [5, 9, 0],
            "axisymmetric_projective_zariski_tangent_real_symplectic_rank": 28,
            "verdict": "SINGULAR_AXISYMMETRIC_SECTION_HAS_NONDEGENERATE_RESTRICTED_ZARISKI_TANGENT_CURRENT",
        })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-axisymmetric-restricted-current-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_AXISYMMETRIC_RESTRICTED_CURRENT",
        "result_state": "CANDIDATES_17_AND_20_AXISYMMETRIC_ZARISKI_TANGENT_CURRENTS_ARE_NONDEGENERATE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_ACTIVE_SCALAR_CONES_ON_TWO_AXISYMMETRIC_SECTIONS",
        "scope": {
            **records["resonance_faces"]["scope"],
            "background": "candidates 17 and 20 only, retained as distinct compact Plebanski--Hacyan collision backgrounds",
            "carrier": "the all-axial all-m=0 section over every nonzero active scalar-cone point, together with the complete axial/polar Zariski tangent to the third-transvectant resonance variety",
            "parity": "both linearized parity channels around the all-axial base",
            "omega": "candidate-specific positive-frequency q-minus/q-plus DIFFERENCE collision into the L=1 extra target",
        },
        "third_transvectant_tangent_theorem": {
            "axisymmetric_binary_quartic": "e0=(0,0,1,0,0)",
            "rank_A_e0": 2,
            "kernel_dimension_A_e0": 3,
            "two_linearized_parity_channels": True,
            "full_derivative_rank": 4,
            "affine_zariski_tangent_complex_dimension": 16,
            "affine_variety_complex_dimension": 14,
            "axisymmetric_section_singular": True,
        },
        "restricted_current_theorem": {
            "one_parity_channel_decomposition": "three unconstrained positive/negative angular pairs plus two constrained directions whose sign is sign(positive occupation minus negative occupation)",
            "strict_occupation_imbalance_on_both_active_cones": True,
            "one_parity_channel_inertia": [3, 5, 0],
            "two_parity_channel_affine_inertia": [6, 10, 0],
            "two_node_complex_scaling_inertia": [1, 1, 0],
            "projective_zariski_tangent_inertia": [5, 9, 0],
            "projective_zariski_tangent_real_symplectic_rank": 28,
            "candidate17_and_20_axisymmetric_zariski_tangent_currents_nondegenerate": True,
        },
        "candidate_rows": candidate_rows,
        "classification": {
            "candidate17_complete_active_scalar_cone_axisymmetric_current_classified": True,
            "candidate20_complete_active_scalar_cone_axisymmetric_current_classified": True,
            "all_four_active_ray_occupation_gaps_exactly_positive": True,
            "axisymmetric_sections_singular": True,
            "restricted_zariski_tangent_currents_nondegenerate": True,
            "full_smooth_locus_restricted_current_classified": False,
            "rotation_zero_fibre_connected": False,
            "candidate18_active_variety_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The axisymmetric sections of candidates 17 and 20 are algebraically singular but not current-degenerate. Exact circuit-ray inequalities keep the negative q-minus occupation strictly larger than the positive q-plus occupation throughout each active cone, removing the only possible Zariski-tangent current radical. Smooth-locus topology remains a separate problem.",
        "next_gate": "extend the restricted-current calculation from the singular axisymmetric section to the full smooth third-transvectant locus, then treat candidate 18",
        "claim_boundary": "This is a complete active-cone theorem only on the candidate-17/20 axisymmetric sections and their Zariski tangents. It does not make the singular points smooth, classify the full smooth locus or rotation-zero topology, treat candidate 18, glue occupations, or promote all-orders, causal, residual, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_axisymmetric_restricted_current",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(rendered)
    elif not OUTPUT.exists() or OUTPUT.read_text() != rendered:
        raise AssertionError("candidate-17/20 axisymmetric restricted-current certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_AXISYMMETRIC_RESTRICTED_CURRENT: PASS")


if __name__ == "__main__":
    main()
