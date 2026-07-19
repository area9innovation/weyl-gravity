"""Certify the rotation quadratic normal form on automatic same-sign faces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    _rotation_representation,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form.schema.json"
INPUTS = {
    "automatic_links": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_links.json",
    "critical_section": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity.json",
    "face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "cone_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    links = records["automatic_links"]
    critical = records["critical_section"]
    if not links["classification"]["all_nonzero_fixed_occupation_rotation_zero_links_connected"]:
        raise AssertionError("automatic-face link theorem changed")
    if not critical["classification"]["rotation_jacobian_rank_exactly_two"]:
        raise AssertionError("axisymmetric critical-rank theorem changed")
    if not records["face_fibres"]["classification"]["all_optional_branch_zero_faces_identified"]:
        raise AssertionError("automatic resonance faces changed")
    if not records["cone_sections"]["classification"]["all_rotation_moment_maps_zero_on_sections"]:
        raise AssertionError("axisymmetric section changed")

    rep = _rotation_representation(2)
    weight = rep["angular_form"]
    expected_weight = sp.diag(1, sp.Rational(1, 4), sp.Rational(1, 6), sp.Rational(1, 4), 1)
    if weight != expected_weight:
        raise AssertionError("spin-two angular form changed")
    j0 = rep["J0"]
    if weight * j0 != sp.diag(-2, -sp.Rational(1, 4), 0, sp.Rational(1, 4), 2):
        raise AssertionError("J3 quadratic weights changed")

    support_rows = []
    for occupied_nodes in range(1, 7):
        if occupied_nodes == 1:
            gram_minors: list[str] = []
        else:
            amplitudes = sp.symbols(f"a1:{occupied_nodes + 1}", positive=True, real=True)
            identity = sp.eye(occupied_nodes)
            basis = sp.Matrix.hstack(*[
                amplitudes[-1] * identity[:, index] - amplitudes[index] * identity[:, occupied_nodes - 1]
                for index in range(occupied_nodes - 1)
            ])
            gram = basis.T * basis
            gram_minors = [str(sp.factor(gram[:size, :size].det())) for size in range(1, occupied_nodes)]
            expected_minors = [
                sp.factor(amplitudes[-1] ** (2 * (size - 1)) * (amplitudes[-1] ** 2 + sum(amplitudes[index] ** 2 for index in range(size))))
                for size in range(1, occupied_nodes)
            ]
            if any(sp.factor(gram[:size, :size].det() - expected_minors[size - 1]) != 0 for size in range(1, occupied_nodes)):
                raise AssertionError("constraint-hyperplane Gram form changed")
        support_rows.append({
            "occupied_current_eigenlines": occupied_nodes,
            "aligned_angular_slice_real_dimension_before_linear_rotation_constraints": 8 * occupied_nodes,
            "kernel_real_dimension": 8 * occupied_nodes - 2,
            "m_plus_minus_2_real_inertia": [2 * occupied_nodes, 2 * occupied_nodes, 0],
            "m_plus_minus_1_kernel_real_inertia": [2 * occupied_nodes - 2, 2 * occupied_nodes - 2, 2],
            "complete_aligned_kernel_real_inertia": [4 * occupied_nodes - 2, 4 * occupied_nodes - 2, 2],
            "constraint_basis_gram_leading_principal_minors": gram_minors,
            "constraint_basis_gram_positivity": "every displayed minor is a positive power of a_N times a sum of positive squares",
        })

    candidate_rows = []
    for row in links["candidate_rows"]:
        index = row["candidate_index"]
        if index == 16:
            candidate_rows.append({
                "candidate_index": index,
                "verdict": "NOT_APPLICABLE",
                "reason": "candidate 16 has no nonzero automatic resonance face",
            })
        else:
            candidate_rows.append({
                "candidate_index": index,
                "automatic_face": row["automatic_face"],
                "verdict": "HYPERBOLIC_NORMAL_FORM_AND_EXACT_NONAXISYMMETRIC_ARC_CERTIFIED",
            })

    return {
        "schema": "einstein-maxwell-weyl-same-sign-automatic-face-rotation-normal-form-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_NORMAL_FORM",
        "result_state": "FIVE_AUTOMATIC_FACE_AXISYMMETRIC_POINTS_HAVE_HYPERBOLIC_ROTATION_NORMAL_FORM_AND_EXACT_NONAXISYMMETRIC_ARCS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_NONZERO_FIXED_OCCUPATIONS_ON_FIVE_AUTOMATIC_RESONANCE_FACES",
        "scope": {
            **links["scope"],
            "carrier": "the current-eigenline-aligned angular slice through every axisymmetric section point on every nonzero automatic-face support stratum",
        },
        "normal_form_theorem": {
            "angular_basis": [-2, -1, 0, 1, 2],
            "angular_form_diagonal": ["1", "1/4", "1/6", "1/4", "1"],
            "J3_form_diagonal": ["-2", "-1/4", "0", "1/4", "2"],
            "linear_kernel_coordinates": "rescale each occupied current eigenline by the square root of its nonzero current magnitude and swap its +/-1 variables when its sign is negative; then use u_j=delta z_(+1), v_j=conjugate(delta z_(-1)), so d(mu_J1,mu_J2)=0 is the single complex equation sum a_j(u_j+v_j)=0 with a_j>0",
            "quadratic_coordinate_change": "write c_j=gamma_j*a_j (all c_j nonzero), w_j=u_j+v_j and z_j=u_j-v_j. Solve w_N=-sum_(j<N)(c_j/c_N)w_j and set zeta_j=gamma_j*z_j-gamma_N*(c_j/c_N)*z_N. Then Q_J3 is proportional to Re(sum_(j<N) w_j*conjugate(zeta_j)); z_N is one complex radical. This is an invertible real congruence for arbitrary nonzero signed gamma_j and positive a_j",
            "support_strata": support_rows,
            "consequence": "the missing rotation equation is indefinite on every nonzero automatic-face support stratum; the axisymmetric critical point is neither a definite quadratic obstruction nor an isolated point of the rotation-zero link",
        },
        "exact_arc": {
            "selected_node": "any occupied current eigenline with axisymmetric coefficient a>0 after its node phase is fixed",
            "formula": "z(t)=sqrt(a^2-12*t^2)*e_0+t*e_(+2)+t*e_(-2), with 12*t^2<a^2",
            "fixed_norm_identity": "(a^2-12*t^2)/6+t^2+t^2=a^2/6",
            "rotation_identity": "mu_J1(z(t))=mu_J2(z(t))=0 because no adjacent m weights are simultaneously occupied; mu_J3(z(t))=2*t^2-2*t^2=0",
            "resonance_identity": "on an automatic face the absent resonant node remains zero, so the complete bilinear resonance factor remains zero along the arc",
            "nonaxisymmetric": "t nonzero populates m=+2 and m=-2 and is transverse to the axisymmetric section",
        },
        "candidate_rows": candidate_rows,
        "classification": {
            "candidates_17_through_21_automatic_face_normal_forms_classified": True,
            "candidate_16_nonzero_automatic_face": "NOT_APPLICABLE",
            "all_aligned_quadratic_normal_forms_indefinite": True,
            "all_aligned_quadratic_normal_forms_have_real_nullity_two": True,
            "exact_nonaxisymmetric_fixed_occupation_rotation_zero_arc_at_every_axisymmetric_point": True,
            "automatic_face_axisymmetric_points_isolated": False,
            "full_local_singular_strata_classified": False,
            "active_resonance_components_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The rank-two axisymmetric critical locus is a genuine hyperbolic crossing on every automatic face, not a hidden definite obstruction. Each point lies on an explicit nonaxisymmetric fixed-occupation arc. The two-dimensional radical, internal current-orthogonal directions and occupation-stratum gluing still prevent a complete local singular-stratum classification.",
        "next_gate": "compute the full current-orthogonal normal form, including internal polarization directions, and test the restricted current on each active resonance component",
        "claim_boundary": "This theorem is exact on the current-eigenline-aligned angular slice and supplies an exact arc in the full amplitude link. It does not classify the full normal space, glue occupation strata, treat candidate 16 or active resonance components, perform a residual quotient, or prove all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_automatic_face_rotation_normal_form",
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
        raise AssertionError("automatic-face rotation-normal-form certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_NORMAL_FORM: PASS")


if __name__ == "__main__":
    main()
