"""Certify connectedness of the candidate-17/20 double-singular zero hub."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre.schema.json"
INPUTS = {
    "incidence": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_singular_component_incidence.json",
    "singular_locus": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_third_transvectant_singular_locus.json",
    "stabilizer": ROOT / "bridge/certificates/einstein_maxwell_weyl_plebanski_hacyan_stabilizer.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    incidence = records["incidence"]
    singular = records["singular_locus"]
    if singular["two_parity_product"]["intersection"] != "S_plus x S_minus":
        raise AssertionError("double-singular intersection changed")
    if singular["two_parity_product"]["intersection_complex_dimension"] != 8:
        raise AssertionError("double-singular dimension changed")
    flags = incidence["classification"]
    if not (
        flags["candidate17_positive_occupation_singular_component_images_intersect"]
        and flags["candidate20_positive_occupation_singular_component_images_intersect"]
    ):
        raise AssertionError("positive-occupation hub disappeared")
    stabilizer = records["stabilizer"]
    if stabilizer["background_stabilizer"]["connected_lie_algebra"] != "R*H direct-sum R*P_x direct-sum so(3)":
        raise AssertionError("lifted stabilizer changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate17-20-double-singular-rotation-zero-fibre-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DOUBLE_SINGULAR_ROTATION_ZERO_FIBRE",
        "result_state": "CANDIDATE17_20_DOUBLE_SINGULAR_FIXED_OCCUPATION_ROTATION_ZERO_HUB_CONNECTED",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_EVERY_POSITIVE_FIXED_ACTIVE_OCCUPATION_PAIR_ON_CANDIDATES_17_AND_20",
        "scope": {
            **incidence["scope"],
            "carrier": "the complete double-singular intersection S_plus x S_minus at fixed positive active occupations, after both common node-phase quotients",
        },
        "incidence_resolution": {
            "one_factor": "Tot(O_P2(-2) direct_sum O_P2(-2)) -> S",
            "double_singular": "the product of the two one-factor incidence resolutions over P2_plus x P2_minus",
            "affine_complex_dimension": 8,
            "base": "P2_plus x P2_minus",
            "base_complex_dimension": 4,
            "negative_amplitude_bundle": "L_plus direct_sum L_minus with L_parity=O_P2_parity(-2)",
            "positive_amplitude_bundle": "a second copy of L_plus direct_sum L_minus",
            "fixed_norm_phase_reduction": "P(L_plus direct_sum L_minus)_negative fibre_product_over_base P(L_plus direct_sum L_minus)_positive",
            "reduced_complex_dimension": 6,
            "compact": True,
            "connected": True,
            "kahler": True,
            "surjective_to_target_hub": True,
            "connected_resolution_fibres": True,
            "equivariant_for_lifted_SO3": True,
        },
        "rotation_zero_fibre": {
            "moment_map": "the lifted diagonal SO(3) moment map pulled back to the compact fixed-occupation incidence resolution",
            "nonempty_witness": incidence["incidence_theorem"]["positive_occupation_intersection_witness"],
            "connectedness_input": "Kirwan connectedness for every moment-map fibre of a compact connected Hamiltonian K-manifold",
            "resolved_zero_fibre_connected": True,
            "target_hub_zero_fibre_is_continuous_image": True,
            "target_hub_zero_fibre_connected": True,
        },
        "classification": {
            "candidate17_double_singular_rotation_zero_hub_connected": True,
            "candidate20_double_singular_rotation_zero_hub_connected": True,
            "positive_fixed_occupations_all_covered": True,
            "complete_singular_components_connected": False,
            "complete_singular_rotation_zero_quotient_connected": False,
            "occupation_strata_glued": False,
            "final_residual_descent": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "The physical intersection of the two candidate-17/20 singular components is not merely nonempty: at each positive occupation it is one connected rotation-zero hub after node-phase reduction. This supplies a common connected target for later componentwise contraction, but does not yet prove that every point of either larger singular component reaches the hub.",
        "next_gate": "prove or disprove that every rotation-zero component of S_plus x K_minus and K_plus x S_minus meets the connected double-singular hub",
        "claim_boundary": "This proves connectedness only for the complete double-singular intersection hub at each fixed positive occupation. It does not prove either larger singular component or their full union connected, glue occupations, perform final residual descent, or establish all-orders, causal, observational or quantum claims.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {
                name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                for name, path in INPUTS.items()
            },
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate17_20_double_singular_rotation_zero_fibre",
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
        raise AssertionError("candidate-17/20 double-singular hub certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE17_20_DOUBLE_SINGULAR_ROTATION_ZERO_FIBRE: PASS")


if __name__ == "__main__":
    main()
