"""Certify the rotation-moment-map singularity of the scalar-cone section."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp
from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import _rotation_representation


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity.schema.json"
INPUTS = {
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
    "moment_map": ROOT / "bridge/certificates/einstein_maxwell_weyl_moment_map_taub_bridge.json",
    "cone_sections": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
    "face_fibres": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    if not records["cone_sections"]["classification"]["all_rotation_moment_maps_zero_on_sections"]:
        raise AssertionError("axisymmetric section changed")
    if not records["fibre_product"]["classification"]["all_three_rotation_moment_maps_retained_in_formula"]:
        raise AssertionError("rotation fibre-product factor changed")
    if not records["face_fibres"]["classification"]["all_six_resonance_fibres_stratified_over_complete_scalar_cones"]:
        raise AssertionError("face-fibre theorem changed")
    if "mu_Ja=(L/4)" not in records["moment_map"]["generic_moment_maps"]["real_mode_moment_maps"]["J_a"]:
        raise AssertionError("generic rotation moment-map convention changed")

    rep = _rotation_representation(2)
    j0 = rep["J0"]
    jp = rep["Jplus"]
    jm = rep["Jminus"]
    weight = rep["angular_form"]
    imaginary = sp.I
    generators = {
        "T1": (jp + jm) / 2,
        "T2": (jp - jm) / (2 * imaginary),
        "T3": j0,
    }
    e0 = sp.Matrix([0, 0, 1, 0, 0])
    covectors = {name: sp.simplify(weight * matrix * e0) for name, matrix in generators.items()}
    if covectors["T3"] != sp.zeros(5, 1):
        raise AssertionError("m=0 acquired a T3 differential")
    real_gram = sp.Matrix(
        [
            [sp.re((covectors[left].conjugate().T * covectors[right])[0]) for right in ("T1", "T2")]
            for left in ("T1", "T2")
        ]
    )
    if real_gram.rank() != 2 or sp.factor(real_gram.det()) <= 0:
        raise AssertionError("transverse rotation gradients lost rank")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-axisymmetric-rotation-singularity-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AXISYMMETRIC_ROTATION_SINGULARITY",
        "result_state": "ALL_NONZERO_AXISYMMETRIC_SCALAR_CONE_SECTION_POINTS_HAVE_ROTATION_JACOBIAN_RANK_TWO",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G4_ALL_SIX_COMPLETE_SCALAR_CONE_SECTIONS",
        "scope": {
            **records["cone_sections"]["scope"],
            "carrier": "the certified all-m=0 amplitude section over every point of each same-sign scalar cone",
        },
        "spin_two_certificate": {
            "basis_order": [-2, -1, 0, 1, 2],
            "angular_form": [[str(item) for item in weight.row(i)] for i in range(5)],
            "T1_W_covector_at_e0": [str(item) for item in covectors["T1"]],
            "T2_W_covector_at_e0": [str(item) for item in covectors["T2"]],
            "T3_W_covector_at_e0": [str(item) for item in covectors["T3"]],
            "T1_T2_real_gram": [[str(item) for item in real_gram.row(i)] for i in range(2)],
            "T1_T2_real_gram_determinant": str(sp.factor(real_gram.det())),
        },
        "jacobian_rank_theorem": {
            "origin": {"rank_d_mu_J": 0, "reason": "the moment map is quadratic"},
            "every_nonzero_section_point": {
                "rank_d_mu_J": 2,
                "upper_bound": "T3*e0=0 in every occupied block, so d(mu_J3)=0",
                "lower_bound": "at least one occupied block has nonzero current norm; its independent real T1 and T2 covectors survive with a nonzero scalar prefactor",
                "critical_value_statement": "zero is not a regular value along the certified axisymmetric section",
            },
            "candidate_indices": [16, 17, 18, 19, 20, 21],
        },
        "classification": {
            "all_nonzero_axisymmetric_section_points_rotation_critical": True,
            "rotation_jacobian_rank_exactly_two": True,
            "origin_rotation_jacobian_rank_zero": True,
            "implicit_function_regular_seed_available_on_axisymmetric_section": False,
            "local_real_zero_set_components_classified": False,
            "singular_tangent_cone_classified": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The bounded scalar-cone section proves real nonemptiness but lies entirely in the critical locus of the lifted-rotation moment map. Therefore its points cannot seed a codimension-three implicit-function classification; the missing third rotation equation first appears quadratically in transverse nonaxisymmetric directions.",
        "next_gate": "compute the quadratic normal form of mu_J3 on the kernel of d(mu_J1,mu_J2) at the axisymmetric section, candidate and face separately",
        "claim_boundary": "This is an exact Jacobian-rank and critical-locus theorem. It does not classify the nonlinear local zero set, its tangent cone, real connected components, or any higher lifecycle.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_axisymmetric_rotation_singularity",
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
        raise AssertionError("axisymmetric rotation-singularity certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AXISYMMETRIC_ROTATION_SINGULARITY: PASS")


if __name__ == "__main__":
    main()
