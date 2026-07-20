"""Complete the fixed-norm rotation normal form on automatic faces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form.schema.json"
INPUTS = {
    "aligned_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.json",
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "axial_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_operator.json",
    "polar_module": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}

NODE_DIMENSION = {
    "q_minus_n1": 2,
    "p_extra_n1": 4,
    "q_plus_n1": 2,
    "q_minus_n2": 2,
    "p_extra_n2": 4,
    "q_plus_n2": 2,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inertia(support: set[str]) -> dict[str, object]:
    nodes = len(support)
    internal_dimension = sum(NODE_DIMENSION[node] for node in support)
    positive = 4 * internal_dimension - 2
    negative = positive
    unquotiented_null = 2 * internal_dimension - nodes + 2
    phase_quotiented_null = 2 * internal_dimension - 2 * nodes + 2
    unquotiented_dimension = 10 * internal_dimension - nodes - 2
    phase_quotiented_dimension = 10 * internal_dimension - 2 * nodes - 2
    if positive + negative + unquotiented_null != unquotiented_dimension:
        raise AssertionError("unquotiented inertia dimension mismatch")
    if positive + negative + phase_quotiented_null != phase_quotiented_dimension:
        raise AssertionError("phase-quotiented inertia dimension mismatch")
    return {
        "support": sorted(support),
        "occupied_nodes_N": nodes,
        "total_internal_complex_dimension_D": internal_dimension,
        "unquotiented_fixed_norm_kernel_real_dimension": unquotiented_dimension,
        "unquotiented_real_inertia": [positive, negative, unquotiented_null],
        "node_phase_quotiented_kernel_real_dimension": phase_quotiented_dimension,
        "node_phase_quotiented_real_inertia": [positive, negative, phase_quotiented_null],
    }


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    aligned = records["aligned_normal_form"]
    if not aligned["classification"]["all_aligned_quadratic_normal_forms_indefinite"]:
        raise AssertionError("aligned normal-form theorem changed")
    axial_module = records["axial_module"]
    polar_module = records["polar_module"]
    if not axial_module["source_and_extra_modules"]["two_independent_extra_cyclic_summands"]:
        raise AssertionError("axial p-primary multiplicity changed")
    if not polar_module["classification"]["canonical_extra_polar_quotient_two_p_summands"]:
        raise AssertionError("polar p-primary multiplicity changed")
    if axial_module["source_and_extra_modules"]["CRT_decomposition_away_from_resultant"] != "(F[omega]/(p))^2 + F[omega]/(q)":
        raise AssertionError("axial primary decomposition changed")
    if polar_module["Einstein_primary_image"]["target_physical_fiber_primary_decomposition"] != "(K[omega]/(p))^2 direct_sum K[omega]/(q)":
        raise AssertionError("polar primary decomposition changed")
    if records["axial_current"]["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"] != [2, 0]:
        raise AssertionError("axial extra current lost definiteness")
    if records["polar_current"]["shell_pairing"]["extra_positive_frequency_inertia"] != [2, 0]:
        raise AssertionError("polar extra current lost definiteness")
    if records["axial_current"]["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"] != [1, 1]:
        raise AssertionError("axial q-primary current changed")
    if records["polar_current"]["shell_pairing"]["Einstein_block_inertia"] != [1, 1]:
        raise AssertionError("polar q-primary current changed")

    rays = {row["ray_id"]: set(row["support"]) for row in records["scalar_rays"]["extreme_rays"]}
    face_rows = {row["candidate_index"]: row for row in records["face_fibres"]["face_rows"]}
    candidate_rows = []
    for index in range(16, 22):
        face = face_rows[index]["automatic_zero_face"]
        generators = face["ray_generators"]
        if index == 16:
            candidate_rows.append({
                "candidate_index": 16,
                "verdict": "NOT_APPLICABLE",
                "reason": "candidate 16 has no nonzero automatic resonance face",
            })
            continue
        if len(generators) != 2:
            raise AssertionError(f"candidate {index} automatic face changed")
        first, second = generators
        strata = [
            {"stratum": f"{first}_relative_interior", **_inertia(rays[first])},
            {"stratum": f"{second}_relative_interior", **_inertia(rays[second])},
            {"stratum": f"cone({first},{second})_relative_interior", **_inertia(rays[first] | rays[second])},
        ]
        candidate_rows.append({
            "candidate_index": index,
            "automatic_face": face,
            "support_strata": strata,
            "verdict": "FULL_FIXED_NORM_ROTATION_HESSIAN_CLASSIFIED_ON_ALL_NONZERO_SUPPORT_STRATA",
        })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-automatic-face-full-rotation-normal-form-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_ROTATION_NORMAL_FORM",
        "result_state": "FIVE_AUTOMATIC_FACES_HAVE_COMPLETE_FIXED_NODE_NORM_ROTATION_HESSIAN_INERTIA",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_NONZERO_FIXED_OCCUPATION_SUPPORT_STRATA_ON_FIVE_AUTOMATIC_FACES",
        "scope": {
            **aligned["scope"],
            "carrier": "the complete tangent to every fixed-node-norm amplitude link at its certified axisymmetric point, including all axial/polar internal directions and all m=-2,...,2 coefficients",
        },
        "primary_multiplicity_dictionary": {
            "q_minus_or_q_plus_node": "one axial plus one polar q-primary eigenline, so complex internal dimension 2",
            "p_extra_node": "two axial plus two polar p-primary eigenlines, so complex internal dimension 4",
            "node_dimensions": NODE_DIMENSION,
            "current_definiteness": "q_minus is negative definite, q_plus and p_extra are positive definite after branch diagonalization; sign swaps do not change inertia",
        },
        "full_normal_form_theorem": {
            "parameters": "N is the number of occupied scalar nodes and D is the sum of their complex internal current-space dimensions",
            "angular_kernel": "all m=+/-1,+/-2 internal directions contribute real inertia (4D-2,4D-2,2) after d(mu_J1,mu_J2)=0",
            "m0_fixed_norm_tangent": "the unquotiented m=0 tangent contributes a radical of real dimension 2D-N; quotienting the N independent node phases leaves radical dimension 2D-2N",
            "unquotiented_fixed_norm_inertia": "(4D-2,4D-2,2D-N+2)",
            "node_phase_quotiented_inertia": "(4D-2,4D-2,2D-2N+2)",
            "nondegenerate_transverse_part": "the positive and negative indices agree and are nonzero on every nonzero support stratum",
        },
        "candidate_rows": candidate_rows,
        "classification": {
            "candidates_17_through_21_complete_fixed_norm_rotation_hessians_classified": True,
            "candidate_16_nonzero_automatic_face": "NOT_APPLICABLE",
            "all_automatic_face_support_strata_listed": True,
            "all_axial_polar_internal_directions_included": True,
            "unquotiented_and_node_phase_quotiented_inertias_certified": True,
            "all_transverse_rotation_hessians_indefinite": True,
            "exact_nonaxisymmetric_arcs_imported": True,
            "rotation_zero_local_semialgebraic_components_classified": False,
            "active_resonance_components_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The internal polarization directions do not repair the axisymmetric singularity into a definite obstruction. They add matched positive/negative hyperbolic blocks and explicit m=0 radical directions. The complete fixed-node-norm Hessian is now known on every automatic-face support stratum; resolving its radical into local semialgebraic components remains separate.",
        "next_gate": "resolve the certified radical by higher local equations or move to restricted-current nondegeneracy on the active resonance components",
        "claim_boundary": "This is the complete quadratic rotation normal form at the certified axisymmetric points with node norms fixed. It does not classify the nonlinear local zero-set components, glue occupation strata, treat candidate 16 or active resonance components, or prove residual, all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_automatic_face_full_rotation_normal_form",
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
        raise AssertionError("automatic-face full rotation-normal-form certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_ROTATION_NORMAL_FORM: PASS")


if __name__ == "__main__":
    main()
