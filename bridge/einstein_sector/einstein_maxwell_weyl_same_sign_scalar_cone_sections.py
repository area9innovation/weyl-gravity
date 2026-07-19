"""Construct bounded amplitude sections over all six same-sign scalar cones."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_scalar_cone_sections.schema.json"
INPUTS = {
    "scalar_rays": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_extreme_rays.json",
    "ray_lifts": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_extreme_ray_lifts.json",
    "same_fibre": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_same_fibre_census.json",
    "isolated": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_isolated_candidates.json",
    "finite_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_generic_smooth_global_second_order.json",
    "standard_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json",
    "axial_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json",
    "polar_current": ROOT / "bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json",
    "candidate19": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_regular_pencil_L4_zero_varieties.json",
    "candidate21": ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L4_zero_varieties.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decomposition(record: dict, index: int) -> dict:
    value = record["decompositions"]
    rows = value if isinstance(value, list) else [item for item in value.values() if isinstance(item, dict)]
    return next(row for row in rows if row.get("candidate_index") == index)


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    scalar = records["scalar_rays"]
    if not scalar["classification"]["all_positive_rho_same_sign_scalar_cones_have_four_extreme_rays"]:
        raise AssertionError("scalar-cone theorem changed")
    if not records["ray_lifts"]["classification"]["all_24_scalar_extreme_rays_have_nonzero_bounded_lifts"]:
        raise AssertionError("extreme-ray lift theorem changed")
    if not records["same_fibre"]["classification"]["all_864_target_shell_defects_nonzero"]:
        raise AssertionError("same-fibre gate changed")
    if not records["finite_cone"]["classification"]["complete_reduced_adjoint_cokernel_decomposition_certified"]:
        raise AssertionError("finite-cone sufficiency changed")
    if "common parity-independent branch weights" not in records["standard_current"]["theorem"]["block_table"][0]["pullback_relative_operator"]:
        raise AssertionError("standard parity current convention changed")
    if not records["axial_current"]["classification"]["complete_generic_axial_target_signature_three_one"]:
        raise AssertionError("axial current classification changed")
    if not records["polar_current"]["classification"]["complete_polar_target_inertia_3_1"]:
        raise AssertionError("polar current classification changed")

    isolated = records["isolated"]["candidate_ledger"]["rows"]
    c19 = decomposition(records["candidate19"], 19)
    c21 = decomposition(records["candidate21"], 21)
    mixed19 = next(item for item in c19["zero_variety"]["irreducible_components_over_C"] if item["component_id"] == "mixed_eigenline_1")
    mixed21 = next(item for item in c21["irreducible_components_over_C"] if item["component_id"] == "mixed_plus")
    if not c19["zero_variety"]["all_mixed_components_real_supported"] or not c21["r_squared_interval"]["positive"]:
        raise AssertionError("real even-L section changed")

    rows = []
    for candidate_index in range(16, 22):
        resonance = isolated[candidate_index - 1]
        ell = resonance["output_ell"]
        if ell in (1, 3):
            if clebsch_gordan(2, 2, ell, 0, 0, 0) != 0:
                raise AssertionError("odd-L section changed")
            section = {
                "method": "ALL_AXIAL_AXISYMMETRIC_ODD_L_SECTION",
                "amplitudes": "for every occupied node j choose axial m=0 amplitude sqrt(y_j/kappa_j), with kappa_j the positive absolute-current coefficient",
                "resonance_zero": f"<2,0;2,0|{ell},0>=0 independently of the occupations",
            }
        elif candidate_index == 19:
            section = {
                "method": "REAL_REGULAR_PENCIL_L4_SECTION",
                "component_id": mixed19["component_id"],
                "amplitudes": "place the resonant p_extra(n=1),q_minus(n=2) vectors on one fixed real mixed eigenline and scale each fibre by sqrt(y_j/kappa_j); choose every spectator axial m=0",
                "resonance_zero": "bilinearity preserves the mixed-eigenline zero under independent nonnegative fibre scaling, including boundary values",
            }
        elif candidate_index == 21:
            section = {
                "method": "REAL_SCALAR_MIXED_PARITY_L4_SECTION",
                "component_id": "mixed_plus",
                "r": mixed21["r"],
                "s": mixed21["s"],
                "amplitudes": "set A_polar=r*A_axial and B_polar=s*B_axial on m=0, normalize their absolute-current norms to y_qplus1,y_qminus2, and choose every spectator axial m=0",
                "resonance_zero": "the two scalar L4 equations vanish identically on the real mixed-plus component and remain zero under independent fibre scaling",
            }
        else:
            raise AssertionError("unhandled scalar-cone section")
        rows.append({
            "candidate_index": candidate_index,
            "rho": scalar["candidate_rows"][candidate_index - 16]["rho"],
            "scalar_domain": "C=cone(R1,R2,R3,R4), including every face and the origin",
            "section": section,
            "rotation_zero": "all amplitudes have m=0, hence mu_J1=mu_J2=mu_J3=0",
            "scalar_zero": "the occupation y lies in C, hence mu_H=mu_Px=R_c=0",
            "same_fibre": "all nonzero-frequency same-fibre channels are off shell",
            "bounded_verdict": "EVERY_SCALAR_NULL_OCCUPATION_HAS_A_BOUNDED_AMPLITUDE_LIFT",
        })
    return {
        "schema": "einstein-maxwell-weyl-same-sign-scalar-cone-sections-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_CONE_SECTIONS",
        "result_state": "BOUNDED_CONE_PROJECTS_SURJECTIVELY_ONTO_EACH_COMPLETE_SCALAR_CONE",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_COMPLETE_SCALAR_CONE_SECTION_ON_SIX_DISTINCT_COLLISION_BACKGROUNDS",
        "scope": {
            **scalar["scope"],
            "background": "six distinct collision candidates 16--21, retained separately",
            "carrier": "one explicit axisymmetric amplitude section over every point of each complete four-ray scalar occupation cone",
        },
        "section_rows": rows,
        "classification": {
            "all_six_complete_scalar_cones_have_bounded_amplitude_sections": True,
            "bounded_to_scalar_occupation_projection_surjective": True,
            "all_scalar_cone_faces_and_pairwise_ray_sums_covered": True,
            "all_rotation_moment_maps_zero_on_sections": True,
            "all_cross_and_same_fibre_bounded_functionals_zero_on_sections": True,
            "every_amplitude_over_each_scalar_occupation_bounded": False,
            "six_full_phase_parity_fibres_classified": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "There is no further occupation-level obstruction on the six same-sign backgrounds: every point of the scalar H/Px/Rc cone is realized by at least one bounded second-order tangent. The remaining nonlinear geometry is entirely in the phase, parity and angular fibres of the occupation map.",
        "next_gate": "classify the complete resonance-zero phase/parity fibre over each scalar-cone face; do not re-test occupation nonemptiness",
        "claim_boundary": "This proves a bounded section and occupation-surjectivity, not that every amplitude with scalar-null occupations is bounded, not a full real component decomposition, and not an all-orders or higher-lifecycle result.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_scalar_cone_sections --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_scalar_cone_sections",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_scalar_cone_sections",
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
        raise AssertionError("same-sign scalar-cone sections certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_CONE_SECTIONS: PASS")


if __name__ == "__main__":
    main()
