"""Glue candidate 16's connected rotation-zero fibres over its scalar cone."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing.schema.json"
INPUTS = {
    "fixed_occupation": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_candidate16_singular_rotation_zero_fibre.json",
    "scalar_cone": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_scalar_occupation_cones.json",
    "resonance_faces": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_resonance_face_fibres.json",
    "fibre_product": ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    records = {name: json.loads(path.read_text()) for name, path in INPUTS.items()}
    fixed = records["fixed_occupation"]
    if not fixed["classification"]["lifted_rotation_zero_fibre_connected"]:
        raise AssertionError("candidate-16 fixed-occupation connectedness changed")
    scalar = next(row for row in records["scalar_cone"]["candidate_rows"] if row["candidate_index"] == 16)
    if scalar["cone_dimension"] != 3 or scalar["counts"]["positive_extreme_rays"] != 4:
        raise AssertionError("candidate-16 scalar cone changed")
    face = next(row for row in records["resonance_faces"]["face_rows"] if row["candidate_index"] == 16)
    active = face["active_stratum"]
    if active["condition"] != "every nonzero scalar-cone point; both q_minus resonant norms are strictly positive":
        raise AssertionError("candidate-16 active norms changed")
    fibre = next(row for row in records["fibre_product"]["candidate_rows"] if row["candidate_index"] == 16)
    if "simultaneous vanishing equivalent" not in fibre["bounded_cone_formula"]["necessity_and_sufficiency"]:
        raise AssertionError("candidate-16 bounded fibre-product theorem changed")

    return {
        "schema": "einstein-maxwell-weyl-same-sign-candidate16-occupation-gluing-v1",
        "schema_path": str(SCHEMA.relative_to(ROOT)),
        "schema_sha256": sha(SCHEMA),
        "result_id": "EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_OCCUPATION_GLUING",
        "result_state": "CANDIDATE16_NORMALIZED_ACTIVE_ROTATION_ZERO_LINK_CONNECTED_ACROSS_ALL_NONZERO_OCCUPATIONS",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G3_COMPLETE_NORMALIZED_CANDIDATE16_ACTIVE_SCALAR_CONE",
        "scope": {
            **fixed["scope"],
            "carrier": "the complete candidate-16 nonzero scalar occupation cone, normalized by total absolute-current occupation, with every fixed-occupation active resonance link",
        },
        "normalized_scalar_base": {
            "affine_cone_dimension": scalar["cone_dimension"],
            "positive_extreme_rays": scalar["counts"]["positive_extreme_rays"],
            "normalization": "sum of the six nonnegative absolute-current occupations equals one",
            "isomorphism_type": "a compact convex two-dimensional polytope with four certified vertices",
            "compact": True,
            "connected": True,
            "all_active_q_minus_norms_strictly_positive": True,
        },
        "total_zero_link": {
            "projection": "forget amplitudes and retain the normalized six-node scalar occupation",
            "closed_in_compact_product": True,
            "projection_proper": True,
            "projection_surjective": True,
            "surjectivity_witness": "the imported axisymmetric bounded section over every scalar-cone point",
            "every_fibre_connected": True,
            "connected_fibre_input": fixed["result_id"],
            "connectedness_lemma": "a proper surjection with connected fibres over a connected base has connected total space",
            "complete_normalized_zero_link_connected": True,
        },
        "classification": {
            "candidate16_projectivized_scalar_base_classified": True,
            "candidate16_fixed_occupation_zero_fibres_connected": True,
            "candidate16_occupation_projection_proper_surjective": True,
            "candidate16_complete_normalized_rotation_zero_link_connected": True,
            "candidate16_active_occupation_gluing_closed": True,
            "origin_adjoined": False,
            "cross_candidate_gluing": False,
            "final_residual_descent": False,
            "all_orders_integrability": False,
            "causal_residual_observational_or_quantum_claim": False,
        },
        "interpretation": "Candidate 16 is now connected not only at each fixed active occupation but across its entire normalized nonzero scalar cone. The result uses the exact four-ray convex base and proper connected-fibre descent; it does not identify any other collision background or turn the singular link into an orbifold.",
        "next_gate": "combine the closed candidate-16 link with the separately certified phase-reduced candidate-17/18/20 strata in the fail-closed atlas; candidates 19/21 remain separate linear sheets",
        "claim_boundary": "This glues all nonzero candidate-16 scalar occupations after total-occupation normalization. The cone origin, other candidate backgrounds, final residual descent, all-orders integration and causal, observational or quantum transport remain outside the theorem.",
        "provenance": {
            "generator_path": str(Path(__file__).relative_to(ROOT)),
            "generator_sha256": sha(Path(__file__)),
            "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in INPUTS.items()},
        },
        "verification_commands": [
            "python3 -m bridge.einstein_sector.einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing --check",
            "python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing",
            "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_same_sign_candidate16_occupation_gluing",
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
        raise AssertionError("candidate-16 occupation-gluing certificate is stale")
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_CANDIDATE16_OCCUPATION_GLUING: PASS")


if __name__ == "__main__":
    main()
