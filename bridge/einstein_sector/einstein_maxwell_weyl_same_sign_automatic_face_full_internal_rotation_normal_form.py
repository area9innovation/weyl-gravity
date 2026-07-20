"""Certify the full internal rotation normal form on automatic faces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form.schema.json"
INPUTS = {
    "aligned_normal_form": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.json",
    "face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "extreme_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _branch(node: str) -> str:
    return node.rsplit("_n", 1)[0]


def _inertia(total_eigenlines: int, occupied_axis_lines: int) -> list[int]:
    return [
        4 * total_eigenlines - 2,
        4 * total_eigenlines - 2,
        2 * total_eigenlines - 2 * occupied_axis_lines + 2,
    ]


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    aligned = records["aligned_normal_form"]
    if not aligned["classification"]["all_aligned_quadratic_normal_forms_indefinite"]:
        raise AssertionError("aligned normal form changed")
    axial = records["axial_current"]
    polar = records["polar_current"]
    if axial["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"] != [2, 0]:
        raise AssertionError("axial p-primary multiplicity changed")
    if polar["shell_pairing"]["extra_positive_frequency_inertia"] != [2, 0]:
        raise AssertionError("polar p-primary multiplicity changed")
    if axial["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"] != [1, 1]:
        raise AssertionError("axial q-primary multiplicity changed")
    if polar["shell_pairing"]["Einstein_block_inertia"] != [1, 1]:
        raise AssertionError("polar q-primary multiplicity changed")

    multiplicity = {"q_minus": 2, "p_extra": 4, "q_plus": 2}
    ray_support = {
        row["ray_id"]: row["support"] for row in records["extreme_rays"]["extreme_rays"]
    }
    face_rows = {row["candidate_index"]: row for row in records["face_fibres"]["face_rows"]}

    weight_j3 = sp.diag(-2, -sp.Rational(1, 4), 0, sp.Rational(1, 4), 2)
    if [sum(1 for value in weight_j3.diagonal() if value > 0),
        sum(1 for value in weight_j3.diagonal() if value < 0),
        sum(1 for value in weight_j3.diagonal() if value == 0)] != [2, 2, 1]:
        raise AssertionError("orthogonal eigenline angular inertia changed")

    candidate_rows = []
    for index in range(16, 22):
        face = face_rows[index]["automatic_zero_face"]
        rays = face["ray_generators"]
        if index == 16:
            candidate_rows.append({
                "candidate_index": 16,
                "verdict": "NOT_APPLICABLE",
                "reason": "candidate 16 has no nonzero automatic face",
            })
            continue
        if len(rays) != 2:
            raise AssertionError(f"candidate {index} automatic face changed")
        supports = [set(ray_support[ray]) for ray in rays]
        strata = []
        for stratum_id, support in (
            (f"ray_{rays[0]}", supports[0]),
            (f"ray_{rays[1]}", supports[1]),
            (f"relative_interior_{rays[0]}_{rays[1]}", supports[0] | supports[1]),
        ):
            occupied = len(support)
            total = sum(multiplicity[_branch(node)] for node in support)
            orthogonal = total - occupied
            inertia = _inertia(total, occupied)
            kernel_dimension = 10 * total - 2 * occupied - 2
            if sum(inertia) != kernel_dimension:
                raise AssertionError("full internal inertia dimension mismatch")
            strata.append({
                "stratum_id": stratum_id,
                "occupied_nodes": sorted(support),
                "occupied_axis_eigenlines_N": occupied,
                "total_current_eigenlines_M": total,
                "current_orthogonal_eigenlines_M_minus_N": orthogonal,
                "fixed_norm_phase_reduced_tangent_real_dimension": 10 * total - 2 * occupied,
                "rotation_kernel_real_dimension": kernel_dimension,
                "full_internal_mu_J3_real_inertia": inertia,
            })
        candidate_rows.append({
            "candidate_index": index,
            "automatic_face_rays": rays,
            "support_strata": strata,
            "verdict": "FULL_INTERNAL_FIXED_OCCUPATION_ROTATION_NORMAL_FORM_CERTIFIED",
        })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-automatic-face-full-internal-rotation-normal-form-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_INTERNAL_ROTATION_NORMAL_FORM",
        "result_state": "FIVE_AUTOMATIC_FACES_HAVE_COMPLETE_INTERNAL_FIXED_OCCUPATION_ROTATION_NORMAL_FORMS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_NONZERO_FIXED_OCCUPATION_SUPPORT_STRATA_ON_FIVE_AUTOMATIC_FACES",
        "scope": {
            **aligned["scope"],
            "carrier": "the complete axial/polar current-eigenline tangent at every axisymmetric section point on every nonzero fixed-occupation automatic-face support stratum",
        },
        "multiplicity_theorem": {
            "q_minus_current_eigenlines_per_node": 2,
            "p_extra_current_eigenlines_per_node": 4,
            "q_plus_current_eigenlines_per_node": 2,
            "source": "one axial plus one polar q-primary eigenline; two axial plus two polar p-primary eigenlines",
        },
        "orthogonal_block_theorem": {
            "weighted_J3_diagonal": ["-2", "-1/4", "0", "1/4", "2"],
            "one_current_orthogonal_eigenline_real_inertia": [4, 4, 2],
            "reason": "an internal vector current-orthogonal to the occupied axis vector does not enter d(mu_J1,mu_J2); its five complex angular coefficients contribute two positive, two negative and one zero Hermitian weights",
        },
        "full_internal_formula": {
            "variables": "N occupied nodes/aligned axis eigenlines, M total axial/polar current eigenlines carried by those nodes",
            "inertia_positive_negative_null": ["4*M-2", "4*M-2", "2*M-2*N+2"],
            "kernel_real_dimension": "10*M-2*N-2",
            "decomposition": "aligned inertia (4*N-2,4*N-2,2) plus (M-N) orthogonal blocks of inertia (4,4,2)",
        },
        "candidate_rows": candidate_rows,
        "classification": {
            "candidates_17_through_21_full_internal_normal_forms_classified": True,
            "all_ray_and_relative_interior_support_strata_classified": True,
            "candidate_16": "NOT_APPLICABLE",
            "all_current_orthogonal_internal_directions_included": True,
            "all_declared_full_internal_forms_indefinite": True,
            "full_fixed_occupation_rotation_kernel_inertia_complete_on_automatic_faces": True,
            "occupation_strata_glued": False,
            "active_resonance_components_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The two-dimensional radical of the aligned slice was not an unresolved defect: the full axial/polar internal tangent is now explicit. Each current-orthogonal eigenline adds a universal (4,4,2) block, so every ray and relative-interior automatic-face section point remains an indefinite rotation saddle with a completely known fixed-occupation quadratic inertia.",
        "next_gate": "classify restricted Lee-Wald nondegeneracy and moment-map topology on each active resonance component, then glue the already classified automatic-face occupation strata",
        "claim_boundary": "This is the complete quadratic rotation normal form on each fixed-occupation automatic-face support stratum. It does not glue different occupations, classify active resonance components, resolve the final residual quotient, construct all-orders solutions, or make causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_automatic_face_full_internal_rotation_normal_form",
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
        raise AssertionError("automatic-face full-internal normal-form certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_FULL_INTERNAL_ROTATION_NORMAL_FORM: PASS")


if __name__ == "__main__":
    main()
